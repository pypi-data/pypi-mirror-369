"""Configuration dataclasses for agent features."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from cogency.providers import Provider
    from cogency.tools.base import Tool

# Runtime limits
MAX_TOOL_CALLS = 3  # Limit to prevent JSON parsing issues


@dataclass
class PathsConfig:
    """Path configuration."""

    base_dir: str = ".cogency"
    sandbox: Optional[str] = None
    state: Optional[str] = None
    memory: Optional[str] = None
    logs: Optional[str] = None
    reports: Optional[str] = None
    evals: Optional[str] = None

    def __post_init__(self):
        """Set defaults under .cogency/ with environment variable override."""
        import os

        # Allow .env override of base directory
        env_base_dir = os.getenv("COGENCY_BASE_DIR")
        if env_base_dir:
            self.base_dir = os.path.expanduser(env_base_dir)

        if self.sandbox is None:
            self.sandbox = f"{self.base_dir}/sandbox"
        if self.state is None:
            self.state = f"{self.base_dir}/state"
        if self.memory is None:
            self.memory = f"{self.base_dir}/memory"
        if self.logs is None:
            self.logs = f"{self.base_dir}/logs"
        if self.reports is None:
            self.reports = f"{self.base_dir}/reports"
        if self.evals is None:
            self.evals = f"{self.base_dir}/evals"


@dataclass
class AgentConfig:
    """Agent configuration container."""

    name: str
    tools: Optional[list["Tool"]]
    memory: Optional[Any]
    max_iterations: int
    handlers: list[Any]
    identity: Optional[str] = (
        "You are Cogency, a helpful AI assistant with a knack for "
        "getting things done efficiently. Keep it concise and clear."
    )
    llm: Optional["Provider"] = None
    embed: Optional["Provider"] = None
    notify: bool = True
