"""Workspace-specific tools for ToolManager."""

from typing import Dict, Any
import difflib
import subprocess
import os


class WorkspaceToolsMixin:
    """Mixin for workspace-specific tools."""
    
    def _create_diff(self, old_content: str, new_content: str, filename: str) -> Dict[str, Any]:
        """Create a diff between two file versions."""
        try:
            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"old/{filename}",
                tofile=f"new/{filename}",
                lineterm=""
            ))
            
            diff = "".join(diff_lines)
            
            # Calculate statistics
            old_lines = len(old_content.splitlines())
            new_lines = len(new_content.splitlines())
            additions = 0
            deletions = 0
            
            for line in diff_lines:
                if line.startswith("+") and not line.startswith("+++"):
                    additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    deletions += 1
            
            return {
                "success": True,
                "diff": diff,
                "filename": filename,
                "old_lines": old_lines,
                "new_lines": new_lines,
                "additions": additions,
                "deletions": deletions,
                "changes": additions + deletions
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _search_files(self, pattern: str, file_pattern: str = "*") -> Dict[str, Any]:
        """Search for text patterns in files."""
        try:
            workspace = self.workspace_manager.get_workspace()
            if not workspace:
                return {"success": False, "error": "No workspace set"}
            
            workspace_path = os.path.abspath(workspace)
            matches = []
            
            # Use grep for searching (more efficient than Python for large files)
            try:
                # Construct grep command
                cmd = ["grep", "-r", "--include=" + file_pattern, pattern, workspace_path]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Parse grep output
                    for line in result.stdout.splitlines():
                        if ":" in line:
                            file_path, line_num, content = line.split(":", 2)
                            rel_path = os.path.relpath(file_path, workspace_path)
                            matches.append({
                                "file": rel_path,
                                "line": int(line_num),
                                "content": content.strip(),
                                "full_match": line.strip()
                            })
                else:
                    # Grep failed, try Python fallback
                    matches = self._search_fallback(workspace_path, pattern, file_pattern)
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Fallback to Python search
                matches = self._search_fallback(workspace_path, pattern, file_pattern)
            
            return {
                "success": True,
                "pattern": pattern,
                "file_pattern": file_pattern,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _search_fallback(self, workspace_path: str, pattern: str, file_pattern: str) -> list:
        """Fallback Python-based search when grep is not available."""
        import fnmatch
        matches = []
        
        for root, dirs, files in os.walk(workspace_path):
            for filename in fnmatch.filter(files, file_pattern):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                rel_path = os.path.relpath(file_path, workspace_path)
                                matches.append({
                                    "file": rel_path,
                                    "line": line_num,
                                    "content": line.strip(),
                                    "full_match": f"{rel_path}:{line_num}:{line.strip()}"
                                })
                except (UnicodeDecodeError, PermissionError):
                    continue  # Skip files that can't be read
        
        return matches
