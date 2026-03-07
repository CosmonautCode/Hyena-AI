"""Workspace operations methods for ChatSystem."""

from pathlib import Path


class WorkspaceOperationsMixin:
    """Mixin for workspace operations functionality."""
    
    def set_workspace(self, directory):
        """Set working directory."""
        result = self.workspace_manager.set_workspace(directory)
        if result:
            self.tui.set_cwd(Path(directory))
        return result
    
    def get_workspace(self):
        """Get current working directory."""
        return self.workspace_manager.get_workspace()
