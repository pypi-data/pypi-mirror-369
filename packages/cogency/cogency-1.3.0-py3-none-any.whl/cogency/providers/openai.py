"""OpenAI provider - LLM and embedding with streaming, caching, key rotation."""

from collections.abc import AsyncIterator
from typing import Union

import numpy as np
import openai
from resilient_result import Err, Ok, Result

from cogency.events import emit, lifecycle
from cogency.providers.tokens import cost, count

from .base import Provider, rotate_retry, setup_rotator


class OpenAI(Provider):
    def __init__(
        self,
        api_keys: Union[str, list[str]] = None,
        llm_model: str = "gpt-4o-mini",
        embed_model: str = "text-embedding-3-small",
        dimensionality: int = 1536,
        temperature: float = 0.7,
        max_tokens: int = 16384,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs,
    ):
        rotator = setup_rotator("openai", api_keys, required=True)

        super().__init__(
            rotator=rotator,
            model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        # Provider-specific params
        self.embed_model = embed_model
        self.dimensionality = dimensionality
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def _get_client(self):
        return openai.AsyncOpenAI(
            api_key=self.next_key(),
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @lifecycle("llm", operation="generate")
    @rotate_retry
    async def generate(self, messages: list[dict[str, str]], **kwargs) -> Result:
        """Generate LLM response with metrics and caching."""
        tin = count(messages, self.model)

        # Check cache first
        if self._cache:
            cached_response = await self._cache.get(messages, **kwargs)
            if cached_response:
                return Ok(cached_response)

        client = self._get_client()
        res = await client.chat.completions.create(
            model=self.model,
            messages=self._format(messages),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            **kwargs,
        )
        response = res.choices[0].message.content

        tout = count([{"role": "assistant", "content": response}], self.model)
        emit(
            "provider",
            level="debug",
            provider=self.provider_name,
            model=self.model,
            tin=tin,
            tout=tout,
            cost=cost(tin, tout, self.model),
        )

        # Cache response
        if self._cache:
            await self._cache.set(messages, response, cache_type="llm", **kwargs)

        return Ok(response)

    @lifecycle("llm", operation="stream")
    async def stream(self, messages: list[dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """Generate streaming LLM response."""
        client = self._get_client()
        stream = await client.chat.completions.create(
            model=self.model,
            messages=self._format(messages),
            stream=True,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            **kwargs,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    @lifecycle("embedding", operation="embed")
    @rotate_retry
    async def embed(self, text: Union[str, list[str]], **kwargs) -> Result:
        """Generate embeddings using OpenAI embedding API."""
        # Check cache first
        if self._cache:
            cached_response = await self._cache.get(text, model=self.embed_model, **kwargs)
            if cached_response:
                return Ok(cached_response)

        try:
            client = self._get_client()

            # Build embedding parameters
            api_kwargs = {
                "input": text,
                "model": self.embed_model,
            }

            # Add dimensions for text-embedding-3 models
            if "text-embedding-3" in self.embed_model:
                api_kwargs["dimensions"] = self.dimensionality

            response = await client.embeddings.create(**api_kwargs, **kwargs)

            if isinstance(text, str):
                result = [np.array(response.data[0].embedding)]
            else:
                result = [np.array(data.embedding) for data in response.data]

            # Cache result
            if self._cache:
                await self._cache.set(
                    text, result, cache_type="embed", model=self.embed_model, **kwargs
                )

            return Ok(result)

        except Exception as e:
            return Err(e)
