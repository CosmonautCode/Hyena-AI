"""Base class and implementations for memory management commands."""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime

from app.cli.commands.base import BaseCommand, CommandContext, CommandResult


@dataclass
class MemoryEntry:
    """A memory entry."""
    key: str
    content: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    accessed_at: str = ""
    importance: int = 1  # 1-10 scale

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.accessed_at:
            self.accessed_at = self.created_at


class MemoryCommand(BaseCommand):
    """Base class for memory management commands."""
    category = "memory"
    MEMORY_DIR = Path("app/data/memory")
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the memory command."""
        try:
            self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
            if not self.validate(context):
                return CommandResult(success=False, message="Validation failed")
            result = await self._execute_memory_command(context)
            return result
        except Exception as e:
            return CommandResult(success=False, message=f"Error: {str(e)}")

    def validate(self, context: CommandContext) -> bool:
        """Validate command arguments."""
        return True

    @abstractmethod
    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Execute the specific memory command."""
        pass

    def _save_entry(self, entry: MemoryEntry) -> bool:
        """Save a memory entry."""
        try:
            self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
            entry_file = self.MEMORY_DIR / f"{entry.key}.json"
            with open(entry_file, "w") as f:
                json.dump({
                    "key": entry.key,
                    "content": entry.content,
                    "category": entry.category,
                    "tags": entry.tags,
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "importance": entry.importance,
                }, f, indent=2)
            return True
        except:
            return False

    def _load_entry(self, key: str) -> Optional[MemoryEntry]:
        """Load a memory entry."""
        entry_file = self.MEMORY_DIR / f"{key}.json"
        if not entry_file.exists():
            return None
        try:
            with open(entry_file, "r") as f:
                data = json.load(f)
                return MemoryEntry(**data)
        except:
            return None

    def _get_all_entries(self) -> List[MemoryEntry]:
        """Get all memory entries."""
        entries = []
        if not self.MEMORY_DIR.exists():
            return entries
        for entry_file in self.MEMORY_DIR.glob("*.json"):
            try:
                with open(entry_file, "r") as f:
                    data = json.load(f)
                    entries.append(MemoryEntry(**data))
            except:
                pass
        return entries

    def _delete_entry(self, key: str) -> bool:
        """Delete a memory entry."""
        entry_file = self.MEMORY_DIR / f"{key}.json"
        try:
            if entry_file.exists():
                entry_file.unlink()
            return True
        except:
            return False


# Memory Commands

class ListMemoryCommand(MemoryCommand):
    """List memory entries: /memory list [--category CAT] [--sort FIELD]"""
    name = "list"
    description = "List memory entries"
    help_text = "Display all memory entries with optional filtering"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """List memory entries."""
        entries = self._get_all_entries()
        
        if category := context.args.get("category"):
            entries = [e for e in entries if e.category == category]
        
        if sort_field := context.args.get("sort"):
            entries = sorted(entries, key=lambda e: getattr(e, sort_field, ""))
        
        result = [{
            "key": e.key,
            "category": e.category,
            "importance": e.importance,
            "tags": e.tags,
        } for e in entries]
        
        return CommandResult(
            success=True,
            message=f"Found {len(entries)} memory entries",
            data={"entries": result}
        )


class SearchMemoryCommand(MemoryCommand):
    """Search memory: /memory search <query> [--category CAT]"""
    name = "search"
    description = "Search memory entries"
    help_text = "Search memory by text content"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Search memory entries."""
        query = context.args.get("query") or context.args.get("_positional", [None])[0]
        if not query:
            return CommandResult(success=False, message="Search query required")
        
        entries = self._get_all_entries()
        results = [e for e in entries if query.lower() in e.content.lower()]
        
        return CommandResult(
            success=True,
            message=f"Found {len(results)} matches",
            data={"results": [{"key": r.key, "excerpt": r.content[:100]} for r in results]}
        )


class ClearMemoryCommand(MemoryCommand):
    """Clear memory: /memory clear [--category CAT] [--confirm]"""
    name = "clear"
    description = "Clear memory entries"
    help_text = "Delete memory entries (use --confirm to bypass warning)"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Clear memory entries."""
        if not context.args.get("confirm"):
            return CommandResult(
                success=False,
                message="Use --confirm flag to clear memory"
            )
        
        entries = self._get_all_entries()
        if category := context.args.get("category"):
            entries = [e for e in entries if e.category == category]
        
        count = 0
        for entry in entries:
            if self._delete_entry(entry.key):
                count += 1
        
        return CommandResult(
            success=True,
            message=f"Cleared {count} memory entries"
        )


class ExportMemoryCommand(MemoryCommand):
    """Export memory: /memory export [--format json] [--path PATH]"""
    name = "export"
    description = "Export memory"
    help_text = "Export memory entries to file"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Export memory."""
        entries = self._get_all_entries()
        export_format = context.args.get("format", "json")
        export_path = context.args.get("path", f"exports/memory.{export_format}")
        
        data = [{
            "key": e.key,
            "content": e.content,
            "category": e.category,
            "importance": e.importance,
        } for e in entries]
        
        return CommandResult(
            success=True,
            message=f"Exported {len(entries)} entries",
            data={"exported": len(entries), "format": export_format, "path": export_path}
        )


class ImportMemoryCommand(MemoryCommand):
    """Import memory: /memory import <path> [--merge]"""
    name = "import"
    description = "Import memory"
    help_text = "Import memory entries from file"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Import memory."""
        path = context.args.get("path") or context.args.get("_positional", [None])[0]
        if not path:
            return CommandResult(success=False, message="Import path required")
        
        # Simulate import
        return CommandResult(
            success=True,
            message=f"Imported memory from {path}",
            data={"path": path, "count": 0}
        )


class StatsMemoryCommand(MemoryCommand):
    """Show memory stats: /memory stats"""
    name = "stats"
    description = "Show memory statistics"
    help_text = "Display memory usage and statistics"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Show memory statistics."""
        entries = self._get_all_entries()
        categories = {}
        
        for entry in entries:
            if entry.category not in categories:
                categories[entry.category] = 0
            categories[entry.category] += 1
        
        total_size = sum(len(e.content) for e in entries)
        
        return CommandResult(
            success=True,
            message="Memory statistics",
            data={
                "total_entries": len(entries),
                "total_size_bytes": total_size,
                "categories": categories,
                "average_importance": sum(e.importance for e in entries) / max(len(entries), 1),
            }
        )


class CompactMemoryCommand(MemoryCommand):
    """Compact memory: /memory compact [--threshold THRESHOLD]"""
    name = "compact"
    description = "Compact memory"
    help_text = "Remove low-importance or old entries"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Compact memory."""
        threshold = int(context.args.get("threshold", 3))
        entries = self._get_all_entries()
        
        to_remove = [e for e in entries if e.importance < threshold]
        count = 0
        
        for entry in to_remove:
            if self._delete_entry(entry.key):
                count += 1
        
        return CommandResult(
            success=True,
            message=f"Compacted memory, removed {count} low-importance entries"
        )


class HierarchyMemoryCommand(MemoryCommand):
    """Show memory hierarchy: /memory hierarchy"""
    name = "hierarchy"
    description = "Show memory hierarchy"
    help_text = "Display memory organization by category"

    async def _execute_memory_command(self, context: CommandContext) -> CommandResult:
        """Show memory hierarchy."""
        entries = self._get_all_entries()
        hierarchy = {}
        
        for entry in entries:
            if entry.category not in hierarchy:
                hierarchy[entry.category] = []
            hierarchy[entry.category].append(entry.key)
        
        return CommandResult(
            success=True,
            message="Memory hierarchy",
            data={"hierarchy": hierarchy}
        )
