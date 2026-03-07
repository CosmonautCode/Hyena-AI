"""Workspace management commands."""

from rich.panel import Panel
from rich.text import Text


class WorkspaceCommandsMixin:
    """Mixin for workspace-related commands."""
    
    def _handle_workspace_command(self, args):
        """Handle workspace command."""
        if args:
            directory = " ".join(args)
            result = self.chat_system.set_workspace(directory)
            if "error" in result:
                message = f"Error: {result['error']}"
            else:
                message = f"Workspace set to: {result['path']}"
        else:
            current_workspace = self.chat_system.get_workspace()
            if current_workspace:
                message = f"Current workspace: {current_workspace}"
            else:
                message = "No workspace set. Usage: /workspace <directory>"
        
        self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold yellow]Workspace[/bold yellow]", border_style="yellow"))
        return True
