"""Base class for tools management commands."""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, List
import json
from pathlib import Path

from app.cli.commands.base import BaseCommand, CommandContext, CommandResult


@dataclass
class ToolConfig:
    """Configuration for a tool."""

    name: str
    description: str
    category: str  # "file", "shell", "workspace", "code", etc.
    enabled: bool = True
    version: str = "1.0.0"
    permissions: List[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.config is None:
            self.config = {}


class ToolsCommand(BaseCommand):
    """Base class for tools management commands."""

    TOOLS_DIR = Path("app/data/tools")
    category = "tools"
    aliases: List[str] = []

    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the tools command."""
        try:
            # Ensure tools directory exists
            self.TOOLS_DIR.mkdir(parents=True, exist_ok=True)

            # Validate first
            if not self.validate(context):
                return CommandResult(success=False, message="Validation failed")

            # Call the specific tools command implementation
            result = await self._execute_tools_command(context)
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
    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Execute the specific tools command. Must be implemented by subclasses."""
        pass

    def _load_tool(self, tool_name: str) -> Optional[ToolConfig]:
        """Load a tool configuration from disk."""
        tool_file = self.TOOLS_DIR / f"{tool_name}.json"
        if not tool_file.exists():
            return None

        try:
            with open(tool_file, "r") as f:
                data = json.load(f)
                return ToolConfig(**data)
        except Exception:
            return None

    def _save_tool(self, tool: ToolConfig) -> bool:
        """Save a tool configuration to disk."""
        try:
            self.TOOLS_DIR.mkdir(parents=True, exist_ok=True)
            tool_file = self.TOOLS_DIR / f"{tool.name}.json"
            with open(tool_file, "w") as f:
                json.dump(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "category": tool.category,
                        "enabled": tool.enabled,
                        "version": tool.version,
                        "permissions": tool.permissions,
                        "config": tool.config,
                    },
                    f,
                    indent=2,
                )
            return True
        except Exception:
            return False

    def _get_all_tools(self) -> List[ToolConfig]:
        """Get all tools."""
        tools = []
        if not self.TOOLS_DIR.exists():
            return tools

        for tool_file in self.TOOLS_DIR.glob("*.json"):
            try:
                with open(tool_file, "r") as f:
                    data = json.load(f)
                    tools.append(ToolConfig(**data))
            except Exception:
                pass

        return tools

    def _delete_tool(self, tool_name: str) -> bool:
        """Delete a tool configuration."""
        tool_file = self.TOOLS_DIR / f"{tool_name}.json"
        try:
            if tool_file.exists():
                tool_file.unlink()
            return True
        except Exception:
            return False
