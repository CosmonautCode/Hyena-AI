"""Memory management commands module."""

from app.cli.commands.memory.impl import (
    ListMemoryCommand,
    SearchMemoryCommand,
    ClearMemoryCommand,
    ExportMemoryCommand,
    ImportMemoryCommand,
    StatsMemoryCommand,
    CompactMemoryCommand,
    HierarchyMemoryCommand,
)

__all__ = [
    "ListMemoryCommand",
    "SearchMemoryCommand",
    "ClearMemoryCommand",
    "ExportMemoryCommand",
    "ImportMemoryCommand",
    "StatsMemoryCommand",
    "CompactMemoryCommand",
    "HierarchyMemoryCommand",
]


def register_memory_commands(registry):
    """Register all memory commands."""
    registry.register_command(ListMemoryCommand())
    registry.register_command(SearchMemoryCommand())
    registry.register_command(ClearMemoryCommand())
    registry.register_command(ExportMemoryCommand())
    registry.register_command(ImportMemoryCommand())
    registry.register_command(StatsMemoryCommand())
    registry.register_command(CompactMemoryCommand())
    registry.register_command(HierarchyMemoryCommand())
