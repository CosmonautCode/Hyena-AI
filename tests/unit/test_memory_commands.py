"""Tests for memory management commands."""

import pytest
import shutil
from pathlib import Path

from app.cli.commands.memory import (
    ListMemoryCommand,
    SearchMemoryCommand,
    ClearMemoryCommand,
    ExportMemoryCommand,
    ImportMemoryCommand,
    StatsMemoryCommand,
    CompactMemoryCommand,
    HierarchyMemoryCommand,
)
from app.cli.commands.base import CommandContext


@pytest.fixture(autouse=True)
def cleanup_memory():
    """Clean up memory directory."""
    memory_dir = Path("app/data/memory")
    try:
        if memory_dir.exists():
            shutil.rmtree(memory_dir)
    except:
        pass
    yield
    try:
        if memory_dir.exists():
            shutil.rmtree(memory_dir)
    except:
        pass


async def create_test_entry(cmd, key="test", content="Test content", category="general", importance=5):
    """Helper to create test memory entry."""
    from app.cli.commands.memory.impl import MemoryEntry
    entry = MemoryEntry(key=key, content=content, category=category, importance=importance)
    cmd._save_entry(entry)
    return entry


class TestListMemoryCommand:
    """Test /memory list command."""

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """Test listing when memory is empty."""
        cmd = ListMemoryCommand()
        ctx = CommandContext("memory list", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_multiple(self):
        """Test listing multiple entries."""
        cmd = ListMemoryCommand()
        for i in range(3):
            await create_test_entry(cmd, f"entry_{i}", f"Content {i}")
        
        ctx = CommandContext("memory list", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_filter_category(self):
        """Test listing with category filter."""
        cmd = ListMemoryCommand()
        await create_test_entry(cmd, "entry1", category="work")
        await create_test_entry(cmd, "entry2", category="personal")
        
        ctx = CommandContext("memory list --category work", {"category": "work"})
        result = await cmd.execute(ctx)
        assert result.success


class TestSearchMemoryCommand:
    """Test /memory search command."""

    @pytest.mark.asyncio
    async def test_search_found(self):
        """Test searching for existing content."""
        cmd = SearchMemoryCommand()
        search_cmd = SearchMemoryCommand()
        await create_test_entry(cmd, "test", "Important Python concept")
        
        ctx = CommandContext("memory search Python", {"query": "Python"})
        result = await search_cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_search_not_found(self):
        """Test searching for non-existent content."""
        cmd = SearchMemoryCommand()
        await create_test_entry(cmd, "test", "Some content")
        
        ctx = CommandContext("memory search NonExistent", {"query": "NonExistent"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_search_missing_query(self):
        """Test search without query."""
        cmd = SearchMemoryCommand()
        ctx = CommandContext("memory search", {})
        result = await cmd.execute(ctx)
        assert not result.success


class TestClearMemoryCommand:
    """Test /memory clear command."""

    @pytest.mark.asyncio
    async def test_clear_without_confirm(self):
        """Test clear without confirmation."""
        cmd = ClearMemoryCommand()
        ctx = CommandContext("memory clear", {})
        result = await cmd.execute(ctx)
        assert not result.success

    @pytest.mark.asyncio
    async def test_clear_with_confirm(self):
        """Test clear with confirmation."""
        cmd = ClearMemoryCommand()
        list_cmd = ListMemoryCommand()
        await create_test_entry(list_cmd, "test")
        
        ctx = CommandContext("memory clear --confirm", {"confirm": True})
        result = await cmd.execute(ctx)
        assert result.success


class TestExportMemoryCommand:
    """Test /memory export command."""

    @pytest.mark.asyncio
    async def test_export_json(self):
        """Test exporting as JSON."""
        cmd = ExportMemoryCommand()
        list_cmd = ListMemoryCommand()
        await create_test_entry(list_cmd, "test")
        
        ctx = CommandContext("memory export --format json", {"format": "json"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_export_empty(self):
        """Test exporting empty memory."""
        cmd = ExportMemoryCommand()
        ctx = CommandContext("memory export", {})
        result = await cmd.execute(ctx)
        assert result.success


class TestImportMemoryCommand:
    """Test /memory import command."""

    @pytest.mark.asyncio
    async def test_import_with_path(self):
        """Test importing with path."""
        cmd = ImportMemoryCommand()
        ctx = CommandContext("memory import /path/to/file", {"path": "/path/to/file"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_import_missing_path(self):
        """Test import without path."""
        cmd = ImportMemoryCommand()
        ctx = CommandContext("memory import", {})
        result = await cmd.execute(ctx)
        assert not result.success


class TestStatsMemoryCommand:
    """Test /memory stats command."""

    @pytest.mark.asyncio
    async def test_stats_empty(self):
        """Test stats for empty memory."""
        cmd = StatsMemoryCommand()
        ctx = CommandContext("memory stats", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_stats_with_entries(self):
        """Test stats with entries."""
        cmd = StatsMemoryCommand()
        list_cmd = ListMemoryCommand()
        for i in range(3):
            await create_test_entry(list_cmd, f"entry_{i}", importance=i+1)
        
        ctx = CommandContext("memory stats", {})
        result = await cmd.execute(ctx)
        assert result.success


class TestCompactMemoryCommand:
    """Test /memory compact command."""

    @pytest.mark.asyncio
    async def test_compact_removes_low_importance(self):
        """Test that compact removes low importance entries."""
        cmd = CompactMemoryCommand()
        list_cmd = ListMemoryCommand()
        await create_test_entry(list_cmd, "low", importance=1)
        await create_test_entry(list_cmd, "high", importance=5)
        
        ctx = CommandContext("memory compact --threshold 3", {"threshold": "3"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_compact_empty_memory(self):
        """Test compact on empty memory."""
        cmd = CompactMemoryCommand()
        ctx = CommandContext("memory compact", {})
        result = await cmd.execute(ctx)
        assert result.success


class TestHierarchyMemoryCommand:
    """Test /memory hierarchy command."""

    @pytest.mark.asyncio
    async def test_hierarchy_empty(self):
        """Test hierarchy for empty memory."""
        cmd = HierarchyMemoryCommand()
        ctx = CommandContext("memory hierarchy", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_hierarchy_multiple_categories(self):
        """Test hierarchy with multiple categories."""
        cmd = HierarchyMemoryCommand()
        list_cmd = ListMemoryCommand()
        await create_test_entry(list_cmd, "work1", category="work")
        await create_test_entry(list_cmd, "work2", category="work")
        await create_test_entry(list_cmd, "personal1", category="personal")
        
        ctx = CommandContext("memory hierarchy", {})
        result = await cmd.execute(ctx)
        assert result.success
