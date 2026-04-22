"""Agent commands module."""

from app.cli.commands.agents.impl import (
    InitAgentCommand,
    ListAgentsCommand,
    LoadAgentCommand,
    RunAgentCommand,
    EditAgentCommand,
    DeleteAgentCommand,
    CloneAgentCommand,
    ExportAgentCommand,
)

__all__ = [
    "InitAgentCommand",
    "ListAgentsCommand",
    "LoadAgentCommand",
    "RunAgentCommand",
    "EditAgentCommand",
    "DeleteAgentCommand",
    "CloneAgentCommand",
    "ExportAgentCommand",
]


def register_agent_commands(registry):
    """Register all agent commands."""
    registry.register_command(InitAgentCommand())
    registry.register_command(ListAgentsCommand())
    registry.register_command(LoadAgentCommand())
    registry.register_command(RunAgentCommand())
    registry.register_command(EditAgentCommand())
    registry.register_command(DeleteAgentCommand())
    registry.register_command(CloneAgentCommand())
    registry.register_command(ExportAgentCommand())

__all__ = []
