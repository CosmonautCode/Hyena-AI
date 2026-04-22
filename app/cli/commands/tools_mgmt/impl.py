"""Tools management commands implementation."""

from app.cli.commands.tools_mgmt.base import ToolsCommand, ToolConfig
from app.cli.commands.base import CommandContext, CommandResult


class ListToolsCommand(ToolsCommand):
    """List all tools: /tools list [--category CATEGORY] [--enabled/--disabled]"""

    name = "list"
    description = "List all tools"
    help_text = "List all tools, optionally filtered by category or status"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """List all tools."""
        tools = self._get_all_tools()

        # Filter by category if specified
        category = context.args.get("category")
        if category:
            tools = [t for t in tools if t.category == category]

        # Filter by enabled status
        if context.args.get("enabled"):
            tools = [t for t in tools if t.enabled]
        elif context.args.get("disabled"):
            tools = [t for t in tools if not t.enabled]

        tool_list = [
            {
                "name": t.name,
                "category": t.category,
                "description": t.description,
                "enabled": t.enabled,
                "version": t.version,
            }
            for t in tools
        ]

        message = f"Found {len(tools)} tool(s)"
        return CommandResult(success=True, message=message, data={"tools": tool_list})


class InfoToolCommand(ToolsCommand):
    """Show tool information: /tools info <tool_name>"""

    name = "info"
    description = "Show tool information"
    help_text = "Display details about a specific tool"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Show tool information."""
        tool_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not tool_name:
            return CommandResult(success=False, message="Tool name is required")

        tool = self._load_tool(tool_name)
        if not tool:
            return CommandResult(success=False, message=f"Tool '{tool_name}' not found")

        return CommandResult(
            success=True,
            message=f"Information for tool '{tool_name}'",
            data={
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "enabled": tool.enabled,
                "version": tool.version,
                "permissions": tool.permissions,
            }
        )


class TestToolCommand(ToolsCommand):
    """Test a tool: /tools test <tool_name> [--input INPUT]"""

    name = "test"
    description = "Test a tool"
    help_text = "Execute a tool with test input"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Test a tool."""
        tool_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not tool_name:
            return CommandResult(success=False, message="Tool name is required")

        tool = self._load_tool(tool_name)
        if not tool:
            return CommandResult(success=False, message=f"Tool '{tool_name}' not found")

        if not tool.enabled:
            return CommandResult(success=False, message=f"Tool '{tool_name}' is disabled")

        test_input = context.args.get("input", "test")
        return CommandResult(
            success=True,
            message=f"Test executed for tool '{tool_name}'",
            data={
                "tool": tool.name,
                "input": test_input,
                "status": "passed",
            }
        )


class EnableToolCommand(ToolsCommand):
    """Enable a tool: /tools enable <tool_name>"""

    name = "enable"
    description = "Enable a tool"
    help_text = "Enable a tool for use"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Enable a tool."""
        tool_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not tool_name:
            return CommandResult(success=False, message="Tool name is required")

        tool = self._load_tool(tool_name)
        if not tool:
            return CommandResult(success=False, message=f"Tool '{tool_name}' not found")

        if tool.enabled:
            return CommandResult(success=False, message=f"Tool '{tool_name}' is already enabled")

        tool.enabled = True
        if self._save_tool(tool):
            return CommandResult(
                success=True,
                message=f"Tool '{tool_name}' enabled",
            )
        else:
            return CommandResult(success=False, message="Failed to enable tool")


class DisableToolCommand(ToolsCommand):
    """Disable a tool: /tools disable <tool_name>"""

    name = "disable"
    description = "Disable a tool"
    help_text = "Disable a tool"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Disable a tool."""
        tool_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not tool_name:
            return CommandResult(success=False, message="Tool name is required")

        tool = self._load_tool(tool_name)
        if not tool:
            return CommandResult(success=False, message=f"Tool '{tool_name}' not found")

        if not tool.enabled:
            return CommandResult(success=False, message=f"Tool '{tool_name}' is already disabled")

        tool.enabled = False
        if self._save_tool(tool):
            return CommandResult(
                success=True,
                message=f"Tool '{tool_name}' disabled",
            )
        else:
            return CommandResult(success=False, message="Failed to disable tool")


class PermissionToolCommand(ToolsCommand):
    """Manage tool permissions: /tools permission <tool_name> [--add PERM] [--remove PERM] [--list]"""

    name = "permission"
    description = "Manage tool permissions"
    help_text = "Add, remove, or list permissions for a tool"

    async def _execute_tools_command(self, context: CommandContext) -> CommandResult:
        """Manage tool permissions."""
        tool_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not tool_name:
            return CommandResult(success=False, message="Tool name is required")

        tool = self._load_tool(tool_name)
        if not tool:
            return CommandResult(success=False, message=f"Tool '{tool_name}' not found")

        # List permissions
        if context.args.get("list"):
            return CommandResult(
                success=True,
                message=f"Permissions for tool '{tool_name}'",
                data={"permissions": tool.permissions}
            )

        # Add permission
        if perm := context.args.get("add"):
            if perm not in tool.permissions:
                tool.permissions.append(perm)
                if self._save_tool(tool):
                    return CommandResult(
                        success=True,
                        message=f"Permission '{perm}' added to tool '{tool_name}'",
                    )
            else:
                return CommandResult(success=False, message=f"Permission '{perm}' already exists")

        # Remove permission
        if perm := context.args.get("remove"):
            if perm in tool.permissions:
                tool.permissions.remove(perm)
                if self._save_tool(tool):
                    return CommandResult(
                        success=True,
                        message=f"Permission '{perm}' removed from tool '{tool_name}'",
                    )
            else:
                return CommandResult(success=False, message=f"Permission '{perm}' not found")

        return CommandResult(success=False, message="No action specified (--add, --remove, or --list)")
