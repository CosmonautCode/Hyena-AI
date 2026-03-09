"""Base CommandManager class and common utilities."""

from rich.panel import Panel
from rich.text import Text
from .agent_commands import AgentCommandsMixin
from .session_commands import SessionCommandsMixin
from .workspace_commands import WorkspaceCommandsMixin
from .system_commands import SystemCommandsMixin
from .memory_commands import MemoryCommandsMixin
from .tools_commands import ToolsCommandsMixin


class CommandManager(
    AgentCommandsMixin, 
    SessionCommandsMixin, 
    WorkspaceCommandsMixin, 
    SystemCommandsMixin, 
    MemoryCommandsMixin, 
    ToolsCommandsMixin
):
    """Main command manager combining all command mixins."""
    
    def __init__(self, chat_system):
        """Initialize the command manager."""
        self.chat_system = chat_system
    
    def process_command(self, user_input):
        """Process commands and return the result."""
        parts = user_input.strip().split()
        command = parts[0].lower()
        
        # Command handlers dictionary (switch case pattern)
        command_handlers = {
            "/help": lambda: self._handle_help_command(),
            "/?": lambda: self._handle_help_command(),
            "/agents": lambda: self._handle_agents_command(),
            "/switch": lambda: self._handle_switch_command(parts[1:]),
            "/clear": lambda: self._handle_clear_command(),
            "/save": lambda: self._handle_save_command(parts[1:]),
            "/load": lambda: self._handle_load_command(parts[1:]),
            "/export": lambda: self._handle_export_command(parts[1:]),
            "/stats": lambda: self._handle_stats_command(),
            "/reset": lambda: self._handle_reset_command(),
            "/workspace": lambda: self._handle_workspace_command(parts[1:]),
            "/permissions": lambda: self._handle_permissions_command(parts[1:]),
            "/status": lambda: self._handle_status_command(parts[1:]),
            "/tools": lambda: self._handle_tools_command(parts[1:]),
            "/session": lambda: self._handle_session_command(parts[1:]),
            "/compact": lambda: self._handle_compact_command(),
            "/memory": lambda: self._handle_memory_command(parts[1:]),
            "/agentic": lambda: self._handle_agentic_command(parts[1:]),
            "/exit": lambda: self._handle_exit_command(),
            "/quit": lambda: self._handle_exit_command(),
        }
        
        # Execute command handler
        handler = command_handlers.get(command)
        if handler:
            return handler()
        else:
            return self._handle_unknown_command(command)
    
    def _handle_exit_command(self):
        """Handle exit/quit commands."""
        self.chat_system.running = False
        return True
    
    def _handle_unknown_command(self, command):
        """Handle unknown commands."""
        
        message = f"Unknown command: {command}. Use /help for available commands."
        self.chat_system.tui.console.print(
            Panel(Text(message, style="yellow"), title="[bold red]Command Error[/bold red]", border_style="red")
        )
        return False
    
    def _handle_help_command(self):
        """Handle help command."""
        help_text = Text()
        help_text.append("Commands:\n", style="bold cyan")
        help_text.append("  /help or /? - Show this help menu\n", style="white")
        help_text.append("  /agents - Show agent selection menu\n", style="white")
        help_text.append("  /switch <number> - Switch to agent by number\n", style="white")
        help_text.append("  /clear - Clear conversation history\n", style="white")
        help_text.append("  /save <filename> - Save conversation\n", style="white")
        help_text.append("  /load <filename> - Load conversation\n", style="white")
        help_text.append("  /export <filename> - Export to text file\n", style="white")
        help_text.append("  /stats - Show session statistics\n", style="white")
        help_text.append("  /reset - Reset session to default\n", style="white")
        help_text.append("  /workspace [dir] - Set or show workspace\n", style="white")
        help_text.append("  /permissions [mode] - Show or set permission mode\n", style="white")
        help_text.append("  /status [type] - Show system status\n", style="white")
        help_text.append("  /tools [command] - Tool operations\n", style="white")
        help_text.append("  /session [action] - Session management\n", style="white")
        help_text.append("  /compact - Compact conversation context\n", style="white")
        help_text.append("  /memory [action] - Project memory operations\n", style="white")
        help_text.append("  /agentic [action] - Agentic loop control\n", style="white")
        help_text.append("  /exit or /quit - Exit the application\n", style="white")
        help_text.append("\n", style="white")
        help_text.append("Features:\n", style="bold cyan")
        help_text.append("  • Type '/' and press Tab for auto-completion\n", style="green")
        help_text.append("  • Use Ctrl+C to exit quickly\n", style="green")
        help_text.append("  • Any other text will be sent to the current agent", style="italic dim")
        help_text.append("\n", style="white")
        help_text.append("Hyena CLI - Local AI Assistant\n", style="bold yellow")
        
        self.chat_system.tui.console.print(Panel(help_text, title="[bold yellow]Help[/bold yellow]", border_style="yellow"))
        return True
