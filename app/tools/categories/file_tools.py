"""File operation tools for Hyena-AI."""

from typing import Any, Dict, List, Optional
from pathlib import Path
import os
import shutil
import re
from app.tools.base import BaseTool, ToolMetadata


class ReadFileTool(BaseTool):
    """Read file contents."""
    
    metadata = ToolMetadata(
        name="file_read",
        category="file",
        description="Read file contents with optional line range",
        parameters={
            "path": {"type": "string", "description": "File path"},
            "start_line": {"type": "integer", "description": "Start line (optional)"},
            "end_line": {"type": "integer", "description": "End line (optional)"},
        },
        returns={"content": {"type": "string", "description": "File contents"}},
        permissions=["files.read"],
    )
    
    async def execute(self, path: str, start_line: Optional[int] = None, 
                     end_line: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """Read file contents."""
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        
        if start_line is not None or end_line is not None:
            lines = content.split("\n")
            start = (start_line or 1) - 1
            end = end_line or len(lines)
            content = "\n".join(lines[start:end])
        
        return {
            "success": True,
            "path": path,
            "lines": len(content.split("\n")),
            "content": content
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "path" in kwargs and Path(kwargs["path"]).exists()


class WriteFileTool(BaseTool):
    """Write content to file."""
    
    metadata = ToolMetadata(
        name="file_write",
        category="file",
        description="Write content to file (creates or overwrites)",
        parameters={
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "Content to write"},
            "append": {"type": "boolean", "description": "Append instead of overwrite"},
        },
        returns={"success": {"type": "boolean"}, "bytes_written": {"type": "integer"}},
        permissions=["files.write"],
    )
    
    async def execute(self, path: str, content: str, append: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Write to file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if append and file_path.exists():
            with open(file_path, "a", encoding="utf-8") as f:
                bytes_written = f.write(content)
        else:
            bytes_written = file_path.write_text(content, encoding="utf-8")
        
        return {
            "success": True,
            "path": path,
            "bytes_written": bytes_written,
            "mode": "append" if append else "write"
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "path" in kwargs and "content" in kwargs


class ListDirectoryTool(BaseTool):
    """List directory contents."""
    
    metadata = ToolMetadata(
        name="file_list",
        category="file",
        description="List directory contents with optional filtering",
        parameters={
            "path": {"type": "string", "description": "Directory path"},
            "pattern": {"type": "string", "description": "Optional glob pattern"},
            "recursive": {"type": "boolean", "description": "Recursive listing"},
        },
        returns={"files": {"type": "array"}, "directories": {"type": "array"}},
        permissions=["files.read"],
    )
    
    async def execute(self, path: str, pattern: Optional[str] = None, 
                     recursive: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """List directory."""
        dir_path = Path(path)
        files = []
        directories = []
        
        if recursive and pattern:
            items = dir_path.rglob(pattern)
        elif pattern:
            items = dir_path.glob(pattern)
        else:
            items = dir_path.iterdir()
        
        for item in items:
            if item.is_file():
                files.append(str(item.relative_to(dir_path)))
            elif item.is_dir():
                directories.append(str(item.relative_to(dir_path)))
        
        return {
            "success": True,
            "path": path,
            "file_count": len(files),
            "directory_count": len(directories),
            "files": sorted(files),
            "directories": sorted(directories),
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "path" in kwargs and Path(kwargs["path"]).is_dir()


class DeleteFileTool(BaseTool):
    """Delete file or directory."""
    
    metadata = ToolMetadata(
        name="file_delete",
        category="file",
        description="Delete file or directory",
        parameters={
            "path": {"type": "string", "description": "File or directory path"},
            "recursive": {"type": "boolean", "description": "Recursive delete for directories"},
        },
        returns={"success": {"type": "boolean"}, "deleted": {"type": "string"}},
        permissions=["files.delete"],
    )
    
    async def execute(self, path: str, recursive: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Delete file or directory."""
        target = Path(path)
        
        if target.is_file():
            target.unlink()
        elif target.is_dir() and recursive:
            shutil.rmtree(target)
        elif target.is_dir():
            target.rmdir()
        
        return {
            "success": True,
            "deleted": path,
            "was_directory": target.is_dir() if target.exists() else False,
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "path" in kwargs and Path(kwargs["path"]).exists()


class CopyFileTool(BaseTool):
    """Copy file or directory."""
    
    metadata = ToolMetadata(
        name="file_copy",
        category="file",
        description="Copy file or directory",
        parameters={
            "src": {"type": "string", "description": "Source path"},
            "dest": {"type": "string", "description": "Destination path"},
            "recursive": {"type": "boolean", "description": "Recursive copy for directories"},
        },
        returns={"success": {"type": "boolean"}, "src": {"type": "string"}, "dest": {"type": "string"}},
        permissions=["files.read", "files.write"],
    )
    
    async def execute(self, src: str, dest: str, recursive: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Copy file or directory."""
        src_path = Path(src)
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if src_path.is_file():
            shutil.copy2(src_path, dest_path)
        elif src_path.is_dir() and recursive:
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        
        return {
            "success": True,
            "src": src,
            "dest": dest,
            "is_directory": src_path.is_dir(),
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "src" in kwargs and "dest" in kwargs and Path(kwargs["src"]).exists()


class MoveFileTool(BaseTool):
    """Move or rename file."""
    
    metadata = ToolMetadata(
        name="file_move",
        category="file",
        description="Move or rename file/directory",
        parameters={
            "src": {"type": "string", "description": "Source path"},
            "dest": {"type": "string", "description": "Destination path"},
        },
        returns={"success": {"type": "boolean"}, "src": {"type": "string"}, "dest": {"type": "string"}},
        permissions=["files.write"],
    )
    
    async def execute(self, src: str, dest: str, **kwargs: Any) -> Dict[str, Any]:
        """Move file."""
        src_path = Path(src)
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        src_path.rename(dest_path)
        
        return {
            "success": True,
            "src": src,
            "dest": dest,
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "src" in kwargs and "dest" in kwargs and Path(kwargs["src"]).exists()


class SearchFilesTool(BaseTool):
    """Search files by regex pattern."""
    
    metadata = ToolMetadata(
        name="file_search",
        category="file",
        description="Search files by regex pattern in content",
        parameters={
            "directory": {"type": "string", "description": "Directory to search"},
            "pattern": {"type": "string", "description": "Regex pattern to search for"},
            "file_pattern": {"type": "string", "description": "File glob pattern"},
        },
        returns={"matches": {"type": "array"}, "count": {"type": "integer"}},
        permissions=["files.read"],
    )
    
    async def execute(self, directory: str, pattern: str, file_pattern: str = "**/*", **kwargs: Any) -> Dict[str, Any]:
        """Search files."""
        dir_path = Path(directory)
        matches = []
        regex = re.compile(pattern)
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if regex.search(content):
                        matches.append(str(file_path.relative_to(dir_path)))
                except (UnicodeDecodeError, PermissionError):
                    pass
        
        return {
            "success": True,
            "directory": directory,
            "pattern": pattern,
            "match_count": len(matches),
            "matches": matches[:100],  # Limit to 100 matches
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "directory" in kwargs and "pattern" in kwargs and Path(kwargs["directory"]).is_dir()


class WatchFilesTool(BaseTool):
    """Watch file for changes."""
    
    metadata = ToolMetadata(
        name="file_watch",
        category="file",
        description="Watch file for changes (timestamp-based)",
        parameters={
            "path": {"type": "string", "description": "File path to watch"},
            "timeout": {"type": "integer", "description": "Timeout in seconds"},
        },
        returns={"changed": {"type": "boolean"}, "last_modified": {"type": "string"}},
        permissions=["files.read"],
    )
    
    async def execute(self, path: str, timeout: int = 10, **kwargs: Any) -> Dict[str, Any]:
        """Watch file."""
        file_path = Path(path)
        last_modified = file_path.stat().st_mtime
        
        import time
        elapsed = 0
        while elapsed < timeout:
            time.sleep(1)
            current_modified = file_path.stat().st_mtime
            if current_modified > last_modified:
                return {
                    "success": True,
                    "path": path,
                    "changed": True,
                    "last_modified": str(file_path.stat().st_mtime),
                }
            elapsed += 1
        
        return {
            "success": True,
            "path": path,
            "changed": False,
            "timeout": timeout,
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "path" in kwargs and Path(kwargs["path"]).exists()
