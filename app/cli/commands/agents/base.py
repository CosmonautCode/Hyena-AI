"""Base class for agent-related commands."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, List
import json
from pathlib import Path

from app.cli.commands.base import BaseCommand, CommandContext, CommandResult


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    name: str
    description: str
    type: str  # "simple", "advanced", "expert"
    enabled: bool = True
    config: dict = None
    created_at: str = ""
    modified_at: str = ""

    def __post_init__(self):
        if self.config is None:
            self.config = {}


class AgentCommand(BaseCommand):
    """Base class for agent-related commands."""

    AGENTS_DIR = Path("app/data/agents")
    category = "agents"
    aliases: List[str] = []

    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the agent command."""
        try:
            # Ensure agents directory exists
            self.AGENTS_DIR.mkdir(parents=True, exist_ok=True)

            # Validate first
            if not self.validate(context):
                return CommandResult(success=False, message="Validation failed")

            # Call the specific agent command implementation
            result = await self._execute_agent_command(context)
            return result
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}"
            )

    def validate(self, context: CommandContext) -> bool:
        """Validate command arguments. Override in subclasses if needed."""
        return True

    @abstractmethod
    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Execute the specific agent command. Must be implemented by subclasses."""
        pass

    def _load_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Load an agent configuration from disk."""
        agents_file = self.AGENTS_DIR / f"{agent_name}.json"
        if not agents_file.exists():
            return None

        try:
            with open(agents_file, "r") as f:
                data = json.load(f)
                return AgentConfig(**data)
        except Exception:
            return None

    def _save_agent(self, agent: AgentConfig) -> bool:
        """Save an agent configuration to disk."""
        try:
            self.AGENTS_DIR.mkdir(parents=True, exist_ok=True)
            agents_file = self.AGENTS_DIR / f"{agent.name}.json"
            with open(agents_file, "w") as f:
                json.dump(
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "type": agent.type,
                        "enabled": agent.enabled,
                        "config": agent.config,
                        "created_at": agent.created_at,
                        "modified_at": agent.modified_at,
                    },
                    f,
                    indent=2,
                )
            return True
        except Exception:
            return False

    def _get_all_agents(self) -> List[AgentConfig]:
        """Get all agents."""
        agents = []
        if not self.AGENTS_DIR.exists():
            return agents

        for agent_file in self.AGENTS_DIR.glob("*.json"):
            try:
                with open(agent_file, "r") as f:
                    data = json.load(f)
                    agents.append(AgentConfig(**data))
            except Exception:
                pass

        return agents

    def _delete_agent(self, agent_name: str) -> bool:
        """Delete an agent configuration."""
        agents_file = self.AGENTS_DIR / f"{agent_name}.json"
        try:
            if agents_file.exists():
                agents_file.unlink()
            return True
        except Exception:
            return False

    def _load_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Load an agent configuration from disk."""
        agents_file = self.AGENTS_DIR / f"{agent_name}.json"
        if not agents_file.exists():
            return None

        try:
            with open(agents_file, "r") as f:
                data = json.load(f)
                return AgentConfig(**data)
        except Exception:
            return None

    def _save_agent(self, agent: AgentConfig) -> bool:
        """Save an agent configuration to disk."""
        agents_file = self.AGENTS_DIR / f"{agent.name}.json"
        try:
            with open(agents_file, "w") as f:
                json.dump(
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "type": agent.type,
                        "enabled": agent.enabled,
                        "config": agent.config,
                        "created_at": agent.created_at,
                        "modified_at": agent.modified_at,
                    },
                    f,
                    indent=2,
                )
            return True
        except Exception:
            return False

    def _get_all_agents(self) -> list[AgentConfig]:
        """Get all agents."""
        agents = []
        if not self.AGENTS_DIR.exists():
            return agents

        for agent_file in self.AGENTS_DIR.glob("*.json"):
            try:
                with open(agent_file, "r") as f:
                    data = json.load(f)
                    agents.append(AgentConfig(**data))
            except Exception:
                pass

        return agents

    def _delete_agent(self, agent_name: str) -> bool:
        """Delete an agent configuration."""
        agents_file = self.AGENTS_DIR / f"{agent_name}.json"
        try:
            if agents_file.exists():
                agents_file.unlink()
            return True
        except Exception:
            return False
