"""Manages a working directory for AI file operations."""

import json
import os
from pathlib import Path

from rich.panel import Panel
from rich.text import Text


class WorkspaceManager:
    """Manages a working directory for AI file operations."""
    
    def __init__(self, chat_system):
        """Initialize the workspace manager."""
        self.chat_system = chat_system
        self.working_directory = None
        self.workspace_config_file = "workspace_config.json"
        
    def set_workspace(self, directory_path):
        """Set the working directory for file operations."""
        try:
            path = Path(directory_path)
            
            if not path.exists():
                # Try to create the directory
                path.mkdir(parents=True, exist_ok=True)
                self.chat_system.tui.console.print(Panel(
                    Text(f"Created new workspace directory: {directory_path}", style="bold green"),
                    title="[bold green]Workspace Created[/bold green]",
                    border_style="green"
                ))
            
            if not path.is_dir():
                return {"error": "Path is not a directory"}
            
            self.working_directory = path.resolve()
            
            # Save workspace config
            self._save_workspace_config()
            
            return {"success": True, "path": str(self.working_directory)}
            
        except Exception as e:
            return {"error": f"Failed to set workspace: {str(e)}"}
    
    def get_workspace(self):
        """Get current working directory."""
        return str(self.working_directory) if self.working_directory else None
    
    def read_file(self, filename):
        """Read a file from the workspace."""
        if not self.working_directory:
            return {"error": "No workspace set. Use /workspace <directory> to set one"}
        
        try:
            file_path = self.working_directory / filename
            
            if not file_path.exists():
                return {"error": f"File not found: {filename}"}
            
            # Check file size (limit to 2MB)
            if file_path.stat().st_size > 2 * 1024 * 1024:
                return {"error": f"File too large: {filename}"}
            
            # Read file
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                return {"content": content, "type": "json"}
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content, "type": "text"}
                
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def write_file(self, filename, content, file_type='text'):
        """Write a file to the workspace."""
        if not self.working_directory:
            return {"error": "No workspace set. Use /workspace <directory> to set one"}
        
        try:
            file_path = self.working_directory / filename
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            if file_type == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return {"success": True, "message": f"File written: {filename}"}
            
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    def list_files(self, pattern="*"):
        """List files in the workspace."""
        if not self.working_directory:
            return {"error": "No workspace set. Use /workspace <directory> to set one"}
        
        # Handle empty or invalid patterns
        if not pattern or pattern in ("''", '""'):
            pattern = "*"
        
        try:
            files = []
            for item in self.working_directory.glob(pattern):
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "type": "file"
                    })
                elif item.is_dir():
                    files.append({
                        "name": item.name + "/",
                        "size": None,
                        "type": "directory"
                    })
            
            return {"files": sorted(files, key=lambda x: x["name"]), "path": str(self.working_directory)}
            
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
    
    def _save_workspace_config(self):
        """Save workspace configuration."""
        if self.working_directory:
            config = {"workspace": str(self.working_directory)}
            try:
                with open(self.workspace_config_file, 'w') as f:
                    json.dump(config, f)
            except:
                pass  # Ignore config save errors
    
    def _load_workspace_config(self):
        """Load workspace configuration."""
        try:
            if Path(self.workspace_config_file).exists():
                with open(self.workspace_config_file, 'r') as f:
                    config = json.load(f)
                    workspace_path = config.get("workspace")
                    if workspace_path and Path(workspace_path).exists():
                        self.working_directory = Path(workspace_path)
                        return True
        except:
            pass
        return False
