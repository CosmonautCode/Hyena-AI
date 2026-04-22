"""Tools management commands module."""

from app.cli.commands.tools_mgmt.impl import (
    ListToolsCommand,
    InfoToolCommand,
    TestToolCommand,
    EnableToolCommand,
    DisableToolCommand,
    PermissionToolCommand,
)

__all__ = [
    "ListToolsCommand",
    "InfoToolCommand",
    "TestToolCommand",
    "EnableToolCommand",
    "DisableToolCommand",
    "PermissionToolCommand",
]


def register_tools_commands(registry):
    """Register all tools commands."""
    registry.register_command(ListToolsCommand())
    registry.register_command(InfoToolCommand())
    registry.register_command(TestToolCommand())
    registry.register_command(EnableToolCommand())
    registry.register_command(DisableToolCommand())
    registry.register_command(PermissionToolCommand())

__all__ = []
