"""File operation tools for ToolManager."""

from typing import Dict, Any
from pathlib import Path
import json
from app.utils.common import create_error_response, create_success_response, validate_file_path


class FileToolsMixin:
    """Mixin for file operation tools."""
    
    def _read_file(self, filename: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents with enhanced error handling."""
        if not validate_file_path(filename):
            return create_error_response("Invalid file path")
        
        try:
            result = self.workspace_manager.read_file(filename)
            if "error" in result:
                return create_error_response(result["error"])
            
            return create_success_response("File read successfully", {
                "content": result["content"],
                "type": result.get("type", "text"),
                "size": len(result["content"]) if isinstance(result["content"], str) else 0
            })
        except Exception as e:
            return create_error_response(str(e))
    
    def _write_file(self, filename: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Write content to file with backup and diff generation."""
        try:
            # Create backup if file exists
            backup_path = None
            old_content = ""
            
            workspace = self.workspace_manager.get_workspace()
            if workspace:
                file_path = Path(workspace) / filename
                if file_path.exists():
                    backup_path = f"{filename}.backup.{int(time.time())}"
                    old_content = file_path.read_text(encoding=encoding)
                    file_path.write_text(old_content, encoding=encoding)  # Create backup
            
            # Write new content
            result = self.workspace_manager.write_file(filename, content, encoding)
            if "error" in result:
                # Restore backup if write failed
                if backup_path and old_content:
                    file_path.write_text(old_content, encoding=encoding)
                return {"success": False, "error": result["error"]}
            
            # Generate diff for reference
            diff = ""
            if old_content:
                diff_lines = list(difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    content.splitlines(keepends=True),
                    fromfile=f"old/{filename}",
                    tofile=f"new/{filename}",
                    lineterm=""
                ))
                diff = "".join(diff_lines)
            
            return {
                "success": True,
                "message": result.get("message", f"File '{filename}' written successfully"),
                "backup": backup_path,
                "diff": diff,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _list_files(self, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        """List files in directory with pattern matching."""
        try:
            workspace = self.workspace_manager.get_workspace()
            if not workspace:
                return {"success": False, "error": "No workspace set"}
            
            workspace_path = Path(workspace)
            if recursive:
                files = list(workspace_path.rglob(pattern))
            else:
                files = list(workspace_path.glob(pattern))
            
            # Filter to files only (not directories) and get relative paths
            file_list = []
            for file_path in files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(workspace_path)
                    file_info = {
                        "name": file_path.name,
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    }
                    file_list.append(file_info)
            
            return {
                "success": True,
                "files": file_list,
                "count": len(file_list),
                "pattern": pattern,
                "recursive": recursive
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
