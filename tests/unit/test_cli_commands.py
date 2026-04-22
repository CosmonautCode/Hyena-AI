"""Unit tests for command registry system."""

import pytest
from app.cli.commands.base import BaseCommand, CommandContext, CommandResult
from app.cli.commands.registry import CommandRegistry


class TestCommand(BaseCommand):
    """Test command for unit tests."""
    name = "test"
    category = "test"
    description = "Test command"
    aliases = ["t"]
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        return CommandResult(success=True, message="Test executed")
    
    def validate(self, ctx: CommandContext) -> bool:
        return True


class TestCommandRegistry:
    """Tests for CommandRegistry."""
    
    def test_register_command(self):
        """Test registering a command."""
        registry = CommandRegistry()
        cmd = TestCommand()
        registry.register(cmd)
        
        assert registry.get("test") == cmd
    
    def test_register_command_aliases(self):
        """Test that aliases are registered."""
        registry = CommandRegistry()
        cmd = TestCommand()
        registry.register(cmd)
        
        assert registry.get("t") == cmd
        assert registry.get("test") == cmd
    
    def test_list_all_commands(self):
        """Test listing all commands."""
        registry = CommandRegistry()
        cmd1 = TestCommand()
        cmd2 = TestCommand()
        cmd2.name = "test2"
        
        registry.register(cmd1)
        registry.register(cmd2)
        
        all_cmds = registry.list_all()
        assert len(all_cmds) == 2
        assert any(c.name == "test" for c in all_cmds)
        assert any(c.name == "test2" for c in all_cmds)
    
    def test_get_by_category(self):
        """Test getting commands by category."""
        registry = CommandRegistry()
        cmd = TestCommand()
        registry.register(cmd)
        
        cmds = registry.get_by_category("test")
        assert len(cmds) == 1
        assert cmds[0].name == "test"
    
    def test_search_commands(self):
        """Test searching commands."""
        registry = CommandRegistry()
        cmd = TestCommand()
        registry.register(cmd)
        
        results = registry.search("test")
        assert len(results) >= 1
        assert any(c.name == "test" for c in results)
    
    def test_get_nonexistent_command(self):
        """Test getting nonexistent command."""
        registry = CommandRegistry()
        assert registry.get("nonexistent") is None
    
    def test_registry_stats(self):
        """Test registry statistics."""
        registry = CommandRegistry()
        cmd = TestCommand()
        registry.register(cmd)
        
        stats = registry.get_stats()
        assert stats["unique_commands"] == 1
        assert stats["categories"] == 1
        assert stats["aliases"] == 1  # "t" is an alias


@pytest.mark.asyncio
async def test_execute_command():
    """Test executing a command."""
    registry = CommandRegistry()
    cmd = TestCommand()
    registry.register(cmd)
    
    ctx = CommandContext("test", {})
    result = await registry.execute("test", ctx)
    
    assert result.success
    assert result.message == "Test executed"


@pytest.mark.asyncio
async def test_execute_nonexistent_command():
    """Test executing nonexistent command."""
    registry = CommandRegistry()
    ctx = CommandContext("nonexistent", {})
    result = await registry.execute("nonexistent", ctx)
    
    assert not result.success
    assert "not found" in result.message.lower()
