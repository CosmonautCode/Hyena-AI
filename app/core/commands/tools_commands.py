"""Tools and agentic commands."""

from rich.panel import Panel
from rich.text import Text


class ToolsCommandsMixin:
    """Mixin for tools and agentic-related commands."""
    
    def _handle_tools_command(self, args):
        """Handle tools command."""
        if not args:
            # List available tools
            tools_text = Text()
            tools_text.append("Available Tools\n\n", style="bold cyan")
            tools_text.append("• file_operations - Read, write, list files\n", style="white")
            tools_text.append("• terminal - Execute shell commands\n", style="white")
            tools_text.append("• search - Search in files\n", style="white")
            tools_text.append("\nUsage: /tools <tool_name> <args>\n", style="dim")
            
            self.chat_system.tui.console.print(Panel(tools_text, title="[bold blue]Tools[/bold blue]", border_style="blue"))
        else:
            tool_name = args[0].lower()
            if tool_name == "list":
                # Detailed tool listing
                if self.chat_system.tool_manager:
                    tools = self.chat_system.tool_manager.get_all_tools()
                    tools_text = Text()
                    tools_text.append("Registered Tools\n\n", style="bold cyan")
                    
                    for tool_name, tool_info in tools.items():
                        tools_text.append(f"• {tool_name}\n", style="bold green")
                        tools_text.append(f"  {tool_info['description']}\n", style="dim")
                        if 'parameters' in tool_info:
                            tools_text.append(f"  Parameters: {tool_info['parameters']}\n", style="dim")
                        tools_text.append("\n", style="white")
                    
                    self.chat_system.tui.console.print(Panel(tools_text, title="[bold blue]Tool Registry[/bold blue]", border_style="blue"))
                else:
                    self.chat_system.tui.console.print(Panel(Text("Tool manager not available", style="red"), title="[bold red]Tools Error[/bold red]", border_style="red"))
            else:
                message = f"Unknown tool: {tool_name}. Use /tools list to see available tools"
                self.chat_system.tui.console.print(Panel(Text(message, style="yellow"), title="[bold yellow]Tools[/bold yellow]", border_style="yellow"))
        
        return True
    
    def _handle_agentic_command(self, args):
        """Handle agentic command."""
        if not args:
            # Show agentic loop status
            if self.chat_system.agentic_loop:
                agentic_text = Text()
                agentic_text.append("Agentic Loop System\n\n", style="bold cyan")
                
                if self.chat_system.agentic_loop.active:
                    agentic_text.append("Status: [bold green]Active[/bold green]\n", style="white")
                else:
                    agentic_text.append("Status: [dim]Inactive[/dim]\n", style="white")
                
                agentic_text.append(f"Registered Tools: {len(self.chat_system.agentic_loop.tool_registry)}\n", style="white")
                agentic_text.append(f"Execution History: {len(self.chat_system.agentic_loop.execution_history)}\n", style="white")
                
                if self.chat_system.agentic_loop.current_plan:
                    agentic_text.append(f"Current Plan: {self.chat_system.agentic_loop.current_plan}\n", style="yellow")
                
                agentic_text.append("\nCommands:\n", style="white")
                agentic_text.append("  /agentic activate - Enable agentic loop\n", style="green")
                agentic_text.append("  /agentic deactivate - Disable agentic loop\n", style="red")
                agentic_text.append("  /agentic status - Show detailed status\n", style="cyan")
                
                self.chat_system.tui.console.print(Panel(agentic_text, title="[bold magenta]Agentic Loop[/bold magenta]", border_style="magenta"))
            else:
                self.chat_system.tui.console.print(Panel(Text("Agentic loop not initialized", style="yellow"), title="[bold yellow]Agentic Loop[/bold yellow]", border_style="yellow"))
        else:
            action = args[0].lower()
            if action == "activate" and self.chat_system.agentic_loop:
                try:
                    self.chat_system.agentic_loop.activate()
                    message = "Agentic loop activated"
                except Exception as e:
                    message = f"Failed to activate: {str(e)}"
            elif action == "deactivate" and self.chat_system.agentic_loop:
                try:
                    self.chat_system.agentic_loop.deactivate()
                    message = "Agentic loop deactivated"
                except Exception as e:
                    message = f"Failed to deactivate: {str(e)}"
            elif action == "status" and self.chat_system.agentic_loop:
                # Detailed status output
                status_text = Text()
                status_text.append("Agentic Loop Detailed Status\n\n", style="bold cyan")
                status_text.append(f"Active: {self.chat_system.agentic_loop.active}\n", style="white")
                status_text.append(f"Tools Registered: {len(self.chat_system.agentic_loop.tool_registry)}\n", style="white")
                status_text.append(f"Executions: {len(self.chat_system.agentic_loop.execution_history)}\n", style="white")
                
                if self.chat_system.agentic_loop.execution_history:
                    status_text.append("\nRecent Executions:\n", style="white")
                    for i, exec_item in enumerate(self.chat_system.agentic_loop.execution_history[-3:]):
                        status_text.append(f"  {i+1}. {exec_item.get('tool', 'Unknown')}\n", style="dim")
                
                self.chat_system.tui.console.print(Panel(status_text, title="[bold blue]Agentic Status[/bold blue]", border_style="blue"))
                return True
            else:
                message = "Invalid agentic command. Use: activate, deactivate, or status"
            
            self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Agentic Loop[/bold green]", border_style="green"))
        
        return True
    
    def _handle_session_command(self, args):
        """Handle session command."""
        if not args:
            # Show session information
            session_text = Text()
            session_text.append("Session Management\n\n", style="bold cyan")
            session_text.append(f"Messages: {len(self.chat_system.history)}\n", style="white")
            session_text.append(f"Current Agent: {self.chat_system.current_agent_index + 1}\n", style="white")
            session_text.append(f"Session Active: Yes\n", style="green")
            session_text.append("Commands: save, load, list, clear\n", style="dim")
            
            self.chat_system.tui.console.print(Panel(session_text, title="[bold magenta]Session[/bold magenta]", border_style="magenta"))
        else:
            action = args[0].lower()
            if action == "list":
                # List available sessions
                if self.chat_system.session_manager:
                    try:
                        sessions = self.chat_system.session_manager.list_sessions()
                        if sessions:
                            list_text = Text()
                            list_text.append("Available Sessions\n\n", style="bold cyan")
                            for session in sessions[:10]:  # Show last 10
                                list_text.append(f"• {session}\n", style="white")
                            
                            self.chat_system.tui.console.print(Panel(list_text, title="[bold blue]Sessions[/bold blue]", border_style="blue"))
                        else:
                            self.chat_system.tui.console.print(Panel(Text("No saved sessions found", style="yellow"), title="[bold yellow]Sessions[/bold yellow]", border_style="yellow"))
                    except Exception as e:
                        self.chat_system.tui.console.print(Panel(Text(f"Failed to list sessions: {str(e)}", style="red"), title="[bold red]Session Error[/bold red]", border_style="red"))
                else:
                    self.chat_system.tui.console.print(Panel(Text("Session manager not available", style="yellow"), title="[bold yellow]Sessions[/bold yellow]", border_style="yellow"))
            else:
                message = f"Unknown session command: {action}. Use: list"
                self.chat_system.tui.console.print(Panel(Text(message, style="yellow"), title="[bold yellow]Session[/bold yellow]", border_style="yellow"))
        
        return True
