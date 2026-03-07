"""Base ToolManager class and initialization."""

from typing import Dict
from pathlib import Path

from .file_tools import FileToolsMixin
from .shell_tools import ShellToolsMixin
from .workspace_tools import WorkspaceToolsMixin


class ToolManager(FileToolsMixin, ShellToolsMixin, WorkspaceToolsMixin):
    """Enhanced tool manager for AI operations."""
    
    def __init__(self, workspace_manager, permission_system):
        """Initialize the tool manager."""
        self.workspace_manager = workspace_manager
        self.permission_system = permission_system
        
        # Initialize terminal manager if available
        try:
            from app.utils.terminal import TerminalExecutor
            self.terminal_executor = TerminalExecutor()
        except ImportError:
            self.terminal_executor = None
    
    def get_all_tools(self) -> Dict[str, Dict]:
        """Get all available tools with their descriptions."""
        return {
            "read_file": {
                "func": self._read_file,
                "description": "Read the contents of a file",
                "parameters": {"filename": "string", "encoding": "string (optional)"}
            },
            "write_file": {
                "func": self._write_file,
                "description": "Write content to a file",
                "parameters": {"filename": "string", "content": "string", "encoding": "string (optional)"}
            },
            "list_files": {
                "func": self._list_files,
                "description": "List files in directory with pattern matching",
                "parameters": {"pattern": "string (optional, default: '*')", "recursive": "boolean (optional)"}
            },
            "run_command": {
                "func": self._run_command,
                "description": "Execute a shell command in the workspace",
                "parameters": {"command": "string", "cwd": "string (optional)"}
            },
            "create_diff": {
                "func": self._create_diff,
                "description": "Create a diff between two file versions",
                "parameters": {"old_content": "string", "new_content": "string", "filename": "string"}
            },
            "search_files": {
                "func": self._search_files,
                "description": "Search for text patterns in files",
                "parameters": {"pattern": "string", "file_pattern": "string (optional)"}
            }
        }
