"""Base command class and types for Hyena-AI command system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class CommandContext:
    """Context passed to commands during execution."""
    
    def __init__(self, user_input: str, args: Dict[str, Any], app_state: Optional[Dict] = None):
        self.user_input = user_input
        self.args = args
        self.app_state = app_state or {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, message: str) -> None:
        """Add error message."""
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """Add warning message."""
        self.warnings.append(message)


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        if self.success:
            return f"✓ {self.message}"
        else:
            return f"✗ {self.message}"


class BaseCommand(ABC):
    """Base class for all Hyena-AI commands."""
    
    # Required attributes
    name: str
    category: str  # "agents", "tools", "memory", "workspace", "system", "code"
    
    # Optional attributes
    aliases: List[str] = []
    description: str = ""
    help_text: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    requires_agent: bool = False
    requires_workspace: bool = False
    required_permissions: List[str] = []
    
    @abstractmethod
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute the command."""
        pass
    
    @abstractmethod
    def validate(self, ctx: CommandContext) -> bool:
        """Validate command arguments and state."""
        pass
    
    def format_help(self) -> str:
        """Format help text for this command."""
        aliases_str = f"Aliases: {', '.join(self.aliases)}" if self.aliases else "Aliases: None"
        
        return f"""
Command: {self.name}
Category: {self.category}
Description: {self.description}

{self.help_text}

{aliases_str}
Version: {self.version}
"""


class HelpCommand(BaseCommand):
    """Built-in help command."""
    
    name = "help"
    aliases = ["h", "?"]
    category = "system"
    description = "Show help information"
    help_text = """Show help for all commands or a specific command.

Usage:
  /help              - Show all commands
  /help <command>    - Show help for a command
"""
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Show help."""
        # Import here to avoid circular dependency
        from app.cli.commands.registry import get_registry
        
        registry = get_registry()
        command_name = ctx.args.get("command")
        
        if command_name:
            cmd = registry.get(command_name)
            if cmd:
                help_text = cmd.format_help()
                return CommandResult(success=True, message=help_text)
            else:
                return CommandResult(
                    success=False,
                    message=f"Command not found: {command_name}"
                )
        else:
            # Show all commands by category
            all_cmds = registry.list_all()
            categories: Dict[str, List[str]] = {}
            
            for cmd in all_cmds:
                if cmd.category not in categories:
                    categories[cmd.category] = []
                categories[cmd.category].append(cmd.name)
            
            help_output = "\n=== Available Commands ===\n"
            for cat in sorted(categories.keys()):
                help_output += f"\n{cat.upper()}:\n"
                for cmd_name in sorted(categories[cat]):
                    cmd = registry.get(cmd_name)
                    if cmd:
                        help_output += f"  {cmd_name:20} {cmd.description}\n"
            
            return CommandResult(success=True, message=help_output)
    
    def validate(self, ctx: CommandContext) -> bool:
        """Validate help command."""
        return True
