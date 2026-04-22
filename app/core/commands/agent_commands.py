"""Agent management commands."""

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box


class AgentCommandsMixin:
    """Mixin for agent-related commands."""
    
    def _handle_agents_command(self):
        """Handle agents command."""
        table = Table(title="Available Agents", box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=4)
        table.add_column("Agent Name", style="bold green")
        table.add_column("Status", style="yellow")
        
        for i, agent in enumerate(self.chat_system.agent_config):
            status = "[bold green]● Active[/bold green]" if i == self.chat_system.current_agent_index else "○ Available"
            table.add_row(str(i + 1), agent["name"], status)
        
        self.chat_system.tui.console.print(Panel(table, title="[bold blue]Agent Selection[/bold blue]", border_style="blue"))
        return True
    
    def _handle_switch_command(self, args):
        """Handle switch command."""
        if args:
            # Switch to specific agent number
            try:
                agent_num = int(args[0]) - 1
                if self.chat_system.choose_agent(agent_num):
                    message = f"Switched to {self.chat_system.agent_config[self.chat_system.current_agent_index]['name']}"
                else:
                    message = "Invalid agent number"
            except ValueError:
                message = "Please enter a valid number"
            
            self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Status[/bold green]", border_style="green"))
        else:
            # Show agent selection menu
            table = Table(title="Available Agents", box=box.ROUNDED)
            table.add_column("No.", style="cyan", width=4)
            table.add_column("Agent Name", style="bold green")
            table.add_column("Status", style="yellow")
            
            for i, agent in enumerate(self.chat_system.agent_config):
                status = "[bold green]● Active[/bold green]" if i == self.chat_system.current_agent_index else "○ Available"
                table.add_row(str(i + 1), agent["name"], status)
            
            self.chat_system.tui.console.print(Panel(table, title="[bold blue]Agent Selection[/bold blue]", border_style="blue"))
            self.chat_system.tui.console.print("[dim]Usage: /switch <number> (e.g., /switch 2)[/dim]")
        
        return True
