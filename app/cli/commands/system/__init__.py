"""System commands module."""

from app.cli.commands.system.impl import (
    VersionCommand,
    HelpCommand,
    DebugCommand,
    LogsDebugCommand,
    BenchmarkCommand,
    ProfileCommand,
    ReportCommand,
    IssueCommand,
    UIThemeCommand,
    UIModeCommand,
    PluginListCommand,
    PluginInstallCommand,
)

__all__ = [
    "VersionCommand",
    "HelpCommand",
    "DebugCommand",
    "LogsDebugCommand",
    "BenchmarkCommand",
    "ProfileCommand",
    "ReportCommand",
    "IssueCommand",
    "UIThemeCommand",
    "UIModeCommand",
    "PluginListCommand",
    "PluginInstallCommand",
]


def register_system_commands(registry):
    """Register all system commands."""
    registry.register_command(VersionCommand())
    registry.register_command(HelpCommand())
    registry.register_command(DebugCommand())
    registry.register_command(LogsDebugCommand())
    registry.register_command(BenchmarkCommand())
    registry.register_command(ProfileCommand())
    registry.register_command(ReportCommand())
    registry.register_command(IssueCommand())
    registry.register_command(UIThemeCommand())
    registry.register_command(UIModeCommand())
    registry.register_command(PluginListCommand())
    registry.register_command(PluginInstallCommand())

__all__ = []
