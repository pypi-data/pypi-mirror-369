"""Cognitive agent with zero ceremony."""

from typing import Any, Union

from cogency.config.validation import validate_config_keys
from cogency.memory import Memory
from cogency.providers import detect_embed, detect_llm
from cogency.state import State
from cogency.tools.base import Tool


class Agent:
    """Cognitive agent with zero ceremony.

    Args:
        name: Agent identifier (default "cogency")
        tools: Tool instances to enable - list of Tool objects
        memory: Enable memory - True for defaults or Memory instance for custom
        handlers: Custom event handlers for streaming, websockets, etc

    Advanced config (**kwargs):
        identity: Agent persona/identity
        max_iterations: Max reasoning iterations (default 5)
        notify: Enable progress notifications (default True)

    Examples:
        Basic: Agent("assistant")
        With memory: Agent("assistant", memory=True)
        Production: Agent("assistant", notify=False)
        With events: Agent("assistant", handlers=[websocket_handler])
        Custom memory: Agent("assistant", memory=Memory())
    """

    def __init__(
        self,
        name: str = "cogency",
        *,
        tools: list[Tool] = None,
        memory: Union[bool, Any] = False,
        handlers: list[Any] = None,
        max_iterations: int = 5,
        **config,
    ):
        from cogency.config.dataclasses import AgentConfig

        self.name = name
        self._handlers = handlers or []

        if tools is None:
            tools = []
        if handlers is None:
            handlers = []

        # Validate config keys (prevent typos)
        validate_config_keys(**config)

        # Create config with dataclass defaults
        agent_config = AgentConfig(
            name=name,
            tools=tools,
            memory=memory,
            handlers=handlers,
            max_iterations=max_iterations,
            **config,
        )

        # Setup components with canonical providers
        self.llm = detect_llm()
        self.embed = detect_embed()

        # Setup memory with canonical universal system
        if memory is True:
            self.memory = Memory()
        elif memory:
            self.memory = memory
        else:
            self.memory = None

        self.max_iterations = agent_config.max_iterations
        self.identity = getattr(agent_config, "identity", "")

        # Store tools for reasoning and execution
        self.tools = self._setup_tools(tools)

        # Initialize event system for observability
        self._init_events(agent_config)

    def _setup_tools(self, tools):
        """Setup and validate tools with registry integration."""
        if not tools:
            return []

        # Use _setup_tools from registry for validation and dependency injection
        from cogency.tools.registry import _setup_tools

        return _setup_tools(tools, self.embed)

    def _init_events(self, agent_config):
        """Initialize event system with EventBuffer for logs() method."""
        from cogency.events import EventBuffer, MessageBus, init_bus

        # Create bus with EventBuffer for capturing events
        bus = MessageBus()
        buffer = EventBuffer()
        bus.subscribe(buffer)

        # Add any custom handlers from config
        for handler in self._handlers:
            bus.subscribe(handler)

        # Initialize global bus
        init_bus(bus)

    def get_memory(self):
        """Access memory component."""
        return self.memory

    def run_sync(
        self,
        query: str,
        user_id: str = "default",
        identity: str = None,
        conversation_id: str = None,
    ) -> tuple[str, str]:
        """Execute agent query synchronously.

        Sync wrapper around run() - canonical pattern.
        Returns (response, conversation_id) for caller persistence.
        """
        import asyncio

        try:
            # Try to get running event loop
            asyncio.get_running_loop()
            # If we're in an event loop, raise error with helpful message
            raise RuntimeError("Use run() when already in an event loop")
        except RuntimeError:
            # No event loop running, safe to create new one
            return asyncio.run(self.run(query, user_id, identity, conversation_id))

    async def stream(self, query: str, user_id: str = "default", identity: str = None):
        """Execute agent query with async streaming.

        Canonical async streaming API.
        Memory and data are isolated per user_id.
        """
        from cogency.events.streaming import StreamingCoordinator

        coordinator = StreamingCoordinator(self)
        async for event in coordinator.stream_agent_run(query, user_id):
            yield event

    async def run(
        self,
        query: str,
        user_id: str = "default",
        identity: str = None,
        conversation_id: str = None,
    ) -> tuple[str, str]:
        """Execute agent query asynchronously.

        Canonical async API - returns (response, conversation_id) for persistence.
        Universal pattern for all contexts - CLI, web apps, library usage.
        """
        from cogency.agents import act, reason
        from cogency.events import emit

        # Create execution state with conversation continuity
        state = await State.start_task(
            query, user_id, conversation_id, max_iterations=self.max_iterations
        )

        try:
            # Add user query to conversation history for proper LLM context
            from cogency.state.mutations import add_message

            add_message(state, "user", query)

            # Memory operations - runtime user context
            if self.memory:
                await self.memory.load(user_id)
                await self.memory.remember(user_id, query, human=True)

            # Agent reasoning and execution loop
            for iteration in range(self.max_iterations):
                emit("agent", level="debug", state="iteration", iteration=iteration)

                # Inject memory context into state for reasoning
                if self.memory:
                    # Temporarily enhance state with memory context
                    memory_context = await self.memory.activate(user_id)
                    original_context = state.context

                    def enhanced_context(mc=memory_context, oc=original_context):
                        return f"{mc}\n\n{oc()}" if mc else oc()

                    state.context = enhanced_context

                # Reason: What should I do next?
                reasoning = await reason(state, self.llm, self.tools, identity or self.identity)

                # Restore original context method
                if self.memory:
                    state.context = original_context

                # Extract result data using clean .unwrap() pattern
                reasoning_data = reasoning.unwrap()

                # Don't add reasoning thoughts to conversation - only concrete actions and responses

                if reasoning_data.get("response"):
                    # Direct response - add to conversation and we're done
                    response = reasoning_data["response"]
                    add_message(state, "assistant", response)
                    break

                actions = reasoning_data.get("actions", [])
                if actions:
                    # Act on reasoning decisions
                    act_result = await act(actions, self.tools, state)
                    act_data = (
                        act_result.unwrap()
                        if act_result.success
                        else {"summary": f"Error: {act_result.error}"}
                    )

                    # Add tool execution results to conversation history for LLM context
                    from cogency.state.mutations import add_message

                    # Create detailed tool result summary for LLM context
                    tool_results = act_data.get("results", [])
                    if tool_results and len(tool_results) == 1:
                        # Single tool - show detailed result
                        result = tool_results[0]
                        tool_name = result.get("name", "tool")
                        if result.get("success"):
                            result_data = result.get("result", {})
                            if hasattr(result_data, "unwrap"):
                                result_content = result_data.unwrap()
                            else:
                                result_content = result_data

                            if isinstance(result_content, dict):
                                # Show key results for shell commands
                                if tool_name == "shell":
                                    stdout = result_content.get("stdout", "").strip()
                                    stderr = result_content.get("stderr", "").strip()
                                    exit_code = result_content.get("exit_code", "?")
                                    if stdout:
                                        add_message(
                                            state,
                                            "assistant",
                                            f"Command executed successfully. Output: {stdout}",
                                        )
                                    elif stderr:
                                        add_message(
                                            state,
                                            "assistant",
                                            f"Command completed with exit code {exit_code}. Error output: {stderr}",
                                        )
                                    else:
                                        add_message(
                                            state,
                                            "assistant",
                                            f"Command executed successfully (exit code {exit_code})",
                                        )
                                else:
                                    # Generic tool result
                                    add_message(
                                        state,
                                        "assistant",
                                        f"{tool_name} completed: {str(result_content)}",
                                    )
                            else:
                                add_message(
                                    state,
                                    "assistant",
                                    f"{tool_name} completed: {str(result_content)}",
                                )
                        else:
                            add_message(
                                state,
                                "assistant",
                                f"{tool_name} failed: {result.get('error', 'Unknown error')}",
                            )
                    else:
                        # Multiple tools or generic summary
                        tool_summary = act_data.get("summary", "Tools executed")
                        add_message(state, "assistant", f"Tool execution: {tool_summary}")

                    # Continue ReAct loop - LLM now has tool results in conversation context
                    continue

                # No actions and no response - shouldn't happen with proper reasoning
                response = "Unable to determine next steps for this request."
                break
            else:
                # Max iterations reached
                response = f"Task processed through {self.max_iterations} iterations."

            # Learn from response
            if self.memory and response:
                await self.memory.remember(user_id, response, human=False)

            # Domain-specific learning operations - canonical boundaries
            from cogency.knowledge import extract
            from cogency.memory import learn

            if self.memory:
                await learn(state, self.memory)  # Learn user patterns

                # Only extract knowledge from substantial conversations
                if self._should_extract_knowledge(query, response, state):
                    await extract(state, self.memory)  # Extract knowledge

            emit("agent", state="complete", response_length=len(response))

            # Return what caller needs for persistence
            return response, state.conversation.conversation_id

        except Exception as e:
            emit("agent", state="error", error=str(e))
            return f"Error: {str(e)}", state.conversation.conversation_id

    def _should_extract_knowledge(self, query: str, response: str, state) -> bool:
        """Determine if conversation is substantial enough for knowledge extraction."""
        # Skip very short interactions
        if len(query) < 20 or len(response) < 50:
            return False

        # Skip simple greetings and basic questions
        query_lower = query.lower().strip()
        simple_patterns = [
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "what time",
            "what's the weather",
            "what day",
            "who are you",
            "what are you",
            "how are you",
        ]

        if any(pattern in query_lower for pattern in simple_patterns):
            return False

        # Skip if no tools were used (likely simple factual exchange)
        if hasattr(state.execution, "completed_calls") and not state.execution.completed_calls:
            # Allow extraction for complex conceptual discussions even without tools
            return bool(len(query) > 100 or len(response) > 200)

        # Extract knowledge from substantial tool-assisted conversations
        return True

    def logs(
        self,
        *,
        type: str = None,
        errors_only: bool = False,
        last: int = None,
        include_debug: bool = False,
    ) -> list[dict[str, Any]]:
        """Get execution logs with optional filtering."""

        # Create bridge to use debug filtering
        from cogency.events.logs import create_logs_bridge

        bridge = create_logs_bridge(None)

        filters = {}
        if type:
            filters["type"] = type
        if errors_only:
            filters["errors_only"] = True

        return bridge.get_recent(
            count=last, filters=filters if filters else None, include_debug=include_debug
        )


__all__ = ["Agent"]
