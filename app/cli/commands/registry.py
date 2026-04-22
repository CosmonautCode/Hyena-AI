"""Command registry and management system."""

from typing import Dict, List, Optional
from app.cli.commands.base import BaseCommand, CommandResult, CommandContext


class CommandRegistry:
    """Registry for all available commands."""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, command: BaseCommand) -> None:
        """Register a command and its aliases."""
        self._commands[command.name] = command
        
        # Register aliases
        for alias in getattr(command, 'aliases', []):
            self._commands[alias] = command
        
        # Track by category
        category = getattr(command, 'category', 'uncategorized')
        if category not in self._categories:
            self._categories[category] = []
        
        # Only add primary name once
        if command.name not in self._categories[category]:
            self._categories[category].append(command.name)
    
    def get(self, name: str) -> Optional[BaseCommand]:
        """Get command by name or alias."""
        return self._commands.get(name)
    
    def list_all(self) -> List[BaseCommand]:
        """List all unique commands (no duplicates for aliases)."""
        seen = set()
        result = []
        for cmd in self._commands.values():
            if cmd.name not in seen:
                result.append(cmd)
                seen.add(cmd.name)
        return result
    
    def get_by_category(self, category: str) -> List[BaseCommand]:
        """Get commands by category."""
        if category not in self._categories:
            return []
        
        names = self._categories[category]
        cmds = []
        seen = set()
        
        for name in names:
            cmd = self._commands.get(name)
            if cmd and cmd.name not in seen:
                cmds.append(cmd)
                seen.add(cmd.name)
        
        return cmds
    
    def search(self, query: str) -> List[BaseCommand]:
        """Search commands by name or description."""
        query = query.lower()
        results = []
        seen = set()
        
        for cmd in self._commands.values():
            if cmd.name in seen:
                continue
            
            if (query in cmd.name or 
                query in getattr(cmd, 'description', '').lower() or
                query in getattr(cmd, 'help_text', '').lower()):
                results.append(cmd)
                seen.add(cmd.name)
        
        return results
    
    async def execute(self, name: str, ctx: CommandContext) -> CommandResult:
        """Execute a command by name."""
        cmd = self.get(name)
        if not cmd:
            return CommandResult(
                success=False,
                message=f"Command not found: {name}"
            )
        
        if not cmd.validate(ctx):
            return CommandResult(
                success=False,
                message=f"Invalid arguments for command: {name}"
            )
        
        return await cmd.execute(ctx)
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        unique_cmds = len(self.list_all())
        total_entries = len(self._commands)
        categories = len(self._categories)
        
        return {
            "unique_commands": unique_cmds,
            "total_entries": total_entries,
            "categories": categories,
            "aliases": total_entries - unique_cmds
        }


# Global registry instance
_global_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """Get or create the global command registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CommandRegistry()
        # Register built-in commands
        from app.cli.commands.base import HelpCommand
        _global_registry.register(HelpCommand())
    return _global_registry


def register_command(command: BaseCommand) -> None:
    """Register a command with the global registry."""
    get_registry().register(command)
