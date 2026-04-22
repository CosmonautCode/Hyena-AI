"""Session management commands."""

from rich.panel import Panel
from rich.text import Text


class SessionCommandsMixin:
    """Mixin for session-related commands."""
    
    def _handle_clear_command(self):
        """Handle clear command."""
        self.chat_system.history.clear()
        self.chat_system.tui.console.print(Panel(Text("Conversation history cleared", style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        # Debug: Verify history is actually cleared
        print(f"DEBUG: History cleared. Current history length: {len(self.chat_system.history)}")
        # Also clear any UI state that might persist
        if hasattr(self.chat_system.tui, '_clear_display_state'):
            delattr(self.chat_system.tui, '_clear_display_state')
        return True
    
    def _handle_save_command(self, args):
        """Handle save command."""
        if args:
            filename = args[0]
            self.chat_system.save_conversation(filename)
            message = f"Conversation saved to {filename}"
        else:
            message = "Please specify a filename: /save <filename>"
        
        self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        return True
    
    def _handle_load_command(self, args):
        """Handle load command."""
        if args:
            filename = args[0]
            self.chat_system.load_conversation(filename)
            message = f"Conversation loaded from {filename}"
        else:
            message = "Please specify a filename: /load <filename>"
        
        self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        return True
    
    def _handle_export_command(self, args):
        """Handle export command."""
        if args:
            filename = args[0]
            self.chat_system.export_conversation(filename)
            message = f"Conversation exported to {filename}"
        else:
            message = "Please specify a filename: /export <filename>"
        
        self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        return True
    
    def _handle_reset_command(self):
        """Handle reset command."""
        self.chat_system.history.clear()
        self.chat_system.choose_agent(0)  # Reset to first agent
        self.chat_system.tui.console.print(Panel(Text("Session reset to default state", style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        return True
    
    def _handle_stats_command(self):
        """Handle stats command."""
        stats = self.chat_system.get_session_stats()
        stats_text = Text()
        stats_text.append("Session Statistics\n\n", style="bold cyan")
        stats_text.append(f"Total Messages: {stats['total_messages']}\n", style="white")
        stats_text.append(f"Your Messages: {stats['user_messages']}\n", style="cyan")
        stats_text.append(f"Agent Responses: {stats['assistant_messages']}\n", style="green")
        stats_text.append(f"Current Agent: {stats['current_agent']}\n", style="yellow")
        stats_text.append(f"Session Status: {stats['session_time']}\n", style="white")
        
        self.chat_system.tui.console.print(Panel(stats_text, title="[bold magenta]Statistics[/bold magenta]", border_style="magenta"))
        return True
