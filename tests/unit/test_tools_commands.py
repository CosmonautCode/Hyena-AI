"""Tests for tools management commands."""

import pytest
import shutil
from pathlib import Path

from app.cli.commands.tools_mgmt import (
    ListToolsCommand,
    InfoToolCommand,
    TestToolCommand,
    EnableToolCommand,
    DisableToolCommand,
    PermissionToolCommand,
)
from app.cli.commands.base import CommandContext


@pytest.fixture(autouse=True)
def cleanup_tools():
    """Clean up tools directory before and after each test."""
    tools_dir = Path("app/data/tools")
    try:
        if tools_dir.exists():
            shutil.rmtree(tools_dir)
    except:
        pass
    yield
    try:
        if tools_dir.exists():
            shutil.rmtree(tools_dir)
    except:
        pass


# Helper function to create a test tool
async def create_test_tool(cmd, name="test_tool", category="file", enabled=True):
    """Helper to create a test tool."""
    from app.cli.commands.tools_mgmt.base import ToolConfig
    tool = ToolConfig(
        name=name,
        description=f"Test {name}",
        category=category,
        enabled=enabled,
        version="1.0.0",
        permissions=[],
        config={}
    )
    cmd._save_tool(tool)
    return tool


class TestListToolsCommand:
    """Test /tools list command."""

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """Test listing tools when none exist."""
        cmd = ListToolsCommand()
        context = CommandContext("tools list", {})

        result = await cmd.execute(context)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_multiple(self):
        """Test listing multiple tools."""
        list_cmd = ListToolsCommand()
        cmd = ListToolsCommand()

        # Create test tools
        for i in range(3):
            await create_test_tool(cmd, f"tool_{i}")

        context = CommandContext("tools list", {})
        result = await list_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_list_filter_by_category(self):
        """Test listing tools filtered by category."""
        cmd = ListToolsCommand()
        await create_test_tool(cmd, "file_tool", category="file")
        await create_test_tool(cmd, "shell_tool", category="shell")

        context = CommandContext(
            "tools list --category file",
            {"category": "file"}
        )
        result = await cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_list_filter_by_status(self):
        """Test listing tools filtered by enabled status."""
        cmd = ListToolsCommand()
        await create_test_tool(cmd, "enabled_tool", enabled=True)
        await create_test_tool(cmd, "disabled_tool", enabled=False)

        context = CommandContext(
            "tools list --enabled",
            {"enabled": True}
        )
        result = await cmd.execute(context)

        assert result.success


class TestInfoToolCommand:
    """Test /tools info command."""

    @pytest.mark.asyncio
    async def test_info_existing(self):
        """Test getting info for existing tool."""
        info_cmd = InfoToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        context = CommandContext(
            "tools info test_tool",
            {"name": "test_tool"}
        )
        result = await info_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_info_nonexistent(self):
        """Test getting info for nonexistent tool."""
        cmd = InfoToolCommand()
        context = CommandContext(
            "tools info nonexistent",
            {"name": "nonexistent"}
        )

        result = await cmd.execute(context)
        assert not result.success

    @pytest.mark.asyncio
    async def test_info_missing_name(self):
        """Test info without tool name."""
        cmd = InfoToolCommand()
        context = CommandContext("tools info", {})

        result = await cmd.execute(context)
        assert not result.success


class TestTestToolCommand:
    """Test /tools test command."""

    @pytest.mark.asyncio
    async def test_test_existing(self):
        """Test testing an existing tool."""
        test_cmd = TestToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool", enabled=True)

        context = CommandContext(
            "tools test test_tool",
            {"name": "test_tool", "input": "test_input"}
        )
        result = await test_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_test_disabled(self):
        """Test testing a disabled tool."""
        test_cmd = TestToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "disabled_tool", enabled=False)

        context = CommandContext(
            "tools test disabled_tool",
            {"name": "disabled_tool"}
        )
        result = await test_cmd.execute(context)

        assert not result.success

    @pytest.mark.asyncio
    async def test_test_nonexistent(self):
        """Test testing a nonexistent tool."""
        cmd = TestToolCommand()
        context = CommandContext(
            "tools test nonexistent",
            {"name": "nonexistent"}
        )

        result = await cmd.execute(context)
        assert not result.success


class TestEnableToolCommand:
    """Test /tools enable command."""

    @pytest.mark.asyncio
    async def test_enable_disabled_tool(self):
        """Test enabling a disabled tool."""
        enable_cmd = EnableToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "disabled_tool", enabled=False)

        context = CommandContext(
            "tools enable disabled_tool",
            {"name": "disabled_tool"}
        )
        result = await enable_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_enable_already_enabled(self):
        """Test enabling an already enabled tool."""
        enable_cmd = EnableToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "enabled_tool", enabled=True)

        context = CommandContext(
            "tools enable enabled_tool",
            {"name": "enabled_tool"}
        )
        result = await enable_cmd.execute(context)

        assert not result.success

    @pytest.mark.asyncio
    async def test_enable_nonexistent(self):
        """Test enabling a nonexistent tool."""
        cmd = EnableToolCommand()
        context = CommandContext(
            "tools enable nonexistent",
            {"name": "nonexistent"}
        )

        result = await cmd.execute(context)
        assert not result.success


class TestDisableToolCommand:
    """Test /tools disable command."""

    @pytest.mark.asyncio
    async def test_disable_enabled_tool(self):
        """Test disabling an enabled tool."""
        disable_cmd = DisableToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "enabled_tool", enabled=True)

        context = CommandContext(
            "tools disable enabled_tool",
            {"name": "enabled_tool"}
        )
        result = await disable_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_disable_already_disabled(self):
        """Test disabling an already disabled tool."""
        disable_cmd = DisableToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "disabled_tool", enabled=False)

        context = CommandContext(
            "tools disable disabled_tool",
            {"name": "disabled_tool"}
        )
        result = await disable_cmd.execute(context)

        assert not result.success

    @pytest.mark.asyncio
    async def test_disable_nonexistent(self):
        """Test disabling a nonexistent tool."""
        cmd = DisableToolCommand()
        context = CommandContext(
            "tools disable nonexistent",
            {"name": "nonexistent"}
        )

        result = await cmd.execute(context)
        assert not result.success


class TestPermissionToolCommand:
    """Test /tools permission command."""

    @pytest.mark.asyncio
    async def test_list_permissions(self):
        """Test listing tool permissions."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        context = CommandContext(
            "tools permission test_tool --list",
            {"name": "test_tool", "list": True}
        )
        result = await perm_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_add_permission(self):
        """Test adding a permission to a tool."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        context = CommandContext(
            "tools permission test_tool --add read",
            {"name": "test_tool", "add": "read"}
        )
        result = await perm_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_add_duplicate_permission(self):
        """Test adding a duplicate permission."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        # Add permission first time
        ctx1 = CommandContext(
            "tools permission test_tool --add read",
            {"name": "test_tool", "add": "read"}
        )
        await perm_cmd.execute(ctx1)

        # Try to add same permission again
        ctx2 = CommandContext(
            "tools permission test_tool --add read",
            {"name": "test_tool", "add": "read"}
        )
        result = await perm_cmd.execute(ctx2)

        assert not result.success

    @pytest.mark.asyncio
    async def test_remove_permission(self):
        """Test removing a permission from a tool."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        # Add permission first
        ctx1 = CommandContext(
            "tools permission test_tool --add read",
            {"name": "test_tool", "add": "read"}
        )
        await perm_cmd.execute(ctx1)

        # Remove permission
        ctx2 = CommandContext(
            "tools permission test_tool --remove read",
            {"name": "test_tool", "remove": "read"}
        )
        result = await perm_cmd.execute(ctx2)

        assert result.success

    @pytest.mark.asyncio
    async def test_remove_nonexistent_permission(self):
        """Test removing a nonexistent permission."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        context = CommandContext(
            "tools permission test_tool --remove read",
            {"name": "test_tool", "remove": "read"}
        )
        result = await perm_cmd.execute(context)

        assert not result.success

    @pytest.mark.asyncio
    async def test_no_action_specified(self):
        """Test permission command with no action."""
        perm_cmd = PermissionToolCommand()
        list_cmd = ListToolsCommand()
        await create_test_tool(list_cmd, "test_tool")

        context = CommandContext(
            "tools permission test_tool",
            {"name": "test_tool"}
        )
        result = await perm_cmd.execute(context)

        assert not result.success
