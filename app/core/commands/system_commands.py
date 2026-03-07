"""System status and permission commands."""

from rich.panel import Panel
from rich.text import Text


class SystemCommandsMixin:
    """Mixin for system-related commands."""
    
    def _handle_permissions_command(self, args):
        """Handle permissions command."""
        if not args:
            # Show current permission mode
            current_mode = self.chat_system.permission_system.current_mode
            modes_text = Text()
            modes_text.append("Permission System\n\n", style="bold cyan")
            mode_value = current_mode.value if hasattr(current_mode, 'value') else str(current_mode)
            modes_text.append(f"Current Mode: {mode_value.upper()}\n\n", style="bold green")
            modes_text.append("Available Modes:\n", style="white")
            modes_text.append("  • ASK - Prompt for permission before operations\n", style="yellow")
            modes_text.append("  • AUTO - Automatically approve operations\n", style="green")
            modes_text.append("  • PLAN - Show plan before execution\n", style="cyan")
            modes_text.append("\nUsage: /permissions <ask|auto|plan|toggle>\n", style="dim")
            
            self.chat_system.tui.console.print(Panel(modes_text, title="[bold magenta]Permissions[/bold magenta]", border_style="magenta"))
        else:
            mode = args[0].lower()
            if mode == "toggle":
                new_mode = self.chat_system.permission_system.toggle_mode()
                message = f"Permission mode toggled to: {new_mode.upper()}"
            elif mode in ["ask", "auto", "plan"]:
                self.chat_system.permission_system.set_mode(mode)
                message = f"Permission mode set to: {mode.upper()}"
            else:
                message = "Invalid mode. Use: ask, auto, plan, or toggle"
            
            self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Permissions[/bold green]", border_style="green"))
        
        return True
    
    def _handle_status_command(self, args):
        """Handle status command."""
        status_type = args[0].lower() if args else "general"
        
        if status_type == "context":
            # Show context usage
            context_text = Text()
            context_text.append("Context Usage\n\n", style="bold cyan")
            total_messages = len(self.chat_system.history)
            estimated_tokens = total_messages * 300  # Rough estimate
            context_text.append(f"Messages: {total_messages}\n", style="white")
            context_text.append(f"Estimated tokens: {estimated_tokens}\n", style="white")
            context_text.append(f"Context limit: 8192\n", style="white")
            context_text.append(f"Usage: {(estimated_tokens/8192)*100:.1f}%\n", style="white")
            
            self.chat_system.tui.console.print(Panel(context_text, title="[bold blue]Context Status[/bold blue]", border_style="blue"))
        else:
            # Show general system status
            status_text = Text()
            status_text.append("System Status\n\n", style="bold cyan")
            current_mode = self.chat_system.permission_system.current_mode
            mode_value = current_mode.value if hasattr(current_mode, 'value') else str(current_mode)
            status_text.append(f"Permission Mode: {mode_value.upper()}\n", style="green")
            status_text.append(f"Workspace: {self.chat_system.get_workspace() or 'Not set'}\n", style="white")
            status_text.append(f"Messages: {len(self.chat_system.history)}\n", style="white")
            status_text.append(f"Session Active: Yes\n", style="green")
            
            self.chat_system.tui.console.print(Panel(status_text, title="[bold green]System Status[/bold green]", border_style="green"))
        
        return True
