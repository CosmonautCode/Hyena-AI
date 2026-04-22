"""Workspace management commands module."""

from app.cli.commands.workspace.impl import (
    WorkspaceInitCommand,
    WorkspaceConfigCommand,
    WorkspaceStatusCommand,
    SessionStartCommand,
    SessionListCommand,
    SessionLoadCommand,
    SessionSaveCommand,
    SessionExportCommand,
    SessionClearCommand,
    ConfigSetCommand,
    ConfigGetCommand,
    ConfigResetCommand,
)

__all__ = [
    "WorkspaceInitCommand",
    "WorkspaceConfigCommand",
    "WorkspaceStatusCommand",
    "SessionStartCommand",
    "SessionListCommand",
    "SessionLoadCommand",
    "SessionSaveCommand",
    "SessionExportCommand",
    "SessionClearCommand",
    "ConfigSetCommand",
    "ConfigGetCommand",
    "ConfigResetCommand",
]


def register_workspace_commands(registry):
    """Register all workspace commands."""
    registry.register_command(WorkspaceInitCommand())
    registry.register_command(WorkspaceConfigCommand())
    registry.register_command(WorkspaceStatusCommand())
    registry.register_command(SessionStartCommand())
    registry.register_command(SessionListCommand())
    registry.register_command(SessionLoadCommand())
    registry.register_command(SessionSaveCommand())
    registry.register_command(SessionExportCommand())
    registry.register_command(SessionClearCommand())
    registry.register_command(ConfigSetCommand())
    registry.register_command(ConfigGetCommand())
    registry.register_command(ConfigResetCommand())

__all__ = []
