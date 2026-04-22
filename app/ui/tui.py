"""Main TUI class that orchestrates all UI components."""

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional

from .console_manager import ConsoleManager
from .banner import Banner
from .prompt import Prompt
from .panels import PanelRenderer
from .streaming import StreamingDisplay
from .permission_prompt import PermissionPrompt


class TUI:
    """Main Terminal UI orchestrator - Modern interface for Hyena."""
    
    def __init__(
        self,
        history_file: Optional[Path] = None,
        version: str = "0.2.0",
        model: str = "Hyena3-4B",
        backend: str = "Local LLM"
    ):
        # Initialize all components
        self.console_manager = ConsoleManager()
        self.console = self.console_manager.console
        self.banner = Banner(version=version, model=model, backend=backend)
        self.prompt = Prompt(history_file=history_file)
        self.panels = PanelRenderer()
        
        # Initialize streaming only if console is available
        self.streaming = StreamingDisplay(self.console) if self.console_manager.is_available() else None
        self.permission = PermissionPrompt()
        
        # Track state
        self.cwd = Path.cwd()
    
    def show_welcome_banner(self):
        """Display the welcome banner."""
        self.banner.print(self.console, str(self.cwd))
    
    async def get_input(self, cwd: str = None) -> str:
        """Get user input with modern prompt."""
        display_cwd = cwd or str(self.cwd)
        return await self.prompt.get_input(display_cwd)
    
    def get_input_sync(self, cwd: str = None) -> str:
        """Synchronous input for non-async contexts."""
        display_cwd = cwd or str(self.cwd)
        return self.prompt.get_input_sync(display_cwd)
    
    def show_user_message(self, content: str):
        """Display user message."""
        self.console.print()
        self.console.print(self.panels.render_user_message(content))
        self.console.print()
    
    def show_assistant_panel(self, content: str, title: str = "Assistant"):
        """Display assistant message in a panel."""
        self.console.print()
        self.console.print(self.panels.render_assistant_panel(content, title))
    
    def start_thinking(self, label: str = "Thinking"):
        """Show thinking spinner."""
        if self.streaming:
            self.streaming.start_thinking(label)
        else:
            # Fallback: simple text indicator
            self.console_manager.print(f"[{label}...]")
    
    def stop_thinking(self):
        """Stop thinking spinner."""
        if self.streaming:
            self.streaming.stop_thinking()
        else:
            # Fallback: clear the thinking line
            self.console_manager.print("\r" + " " * 50 + "\r")
    
    def stream_token(self, token: str):
        """Stream a token to the display."""
        if self.streaming:
            self.streaming.add_token(token)
        else:
            # Fallback: print token directly
            self.console_manager.print(token, end="")
    
    def end_stream(self) -> str:
        """End streaming and return final content."""
        if self.streaming:
            return self.streaming.end_streaming()
        else:
            # Fallback: return empty string
            self.console_manager.print()  # New line after streaming
            return ""
    
    def show_tool_call(self, tool_name: str, args: dict):
        """Display tool call panel."""
        self.console.print()
        self.console.print(self.panels.render_tool_call(tool_name, args))
    
    def show_tool_result(self, tool_name: str, result: str, success: bool):
        """Display tool result panel."""
        self.console.print()
        self.console.print(self.panels.render_tool_result(tool_name, result, success))
    
    async def request_permission(self, tool_name: str, args: dict) -> str:
        """Request permission for a tool action."""
        if self.console:
            return await self.permission.request_approval(self.console, tool_name, args)
        else:
            # Fallback: basic text prompt
            self.console_manager.print(f"\nAllow {tool_name} action? [Y] Yes  [N] No  [A] Always  [D] Deny")
            response = input("Your choice: ").lower()
            valid_choices = {
                'y': 'yes', 'yes': 'yes', 'n': 'no', 'no': 'no',
                'a': 'always', 'always': 'always', 'd': 'deny', 'deny': 'deny'
            }
            return valid_choices.get(response, 'no')
    
    def request_permission_sync(self, tool_name: str, args: dict) -> str:
        """Synchronous permission request."""
        if self.console:
            return self.permission.request_approval_sync(self.console, tool_name, args)
        else:
            # Fallback: basic text prompt
            self.console_manager.print(f"\nAllow {tool_name} action? [Y] Yes  [N] No  [A] Always  [D] Deny")
            response = input("Your choice: ").lower()
            valid_choices = {
                'y': 'yes', 'yes': 'yes', 'n': 'no', 'no': 'no',
                'a': 'always', 'always': 'always', 'd': 'deny', 'deny': 'deny'
            }
            return valid_choices.get(response, 'no')
    
    def show_slash_feedback(self, command: str, message: str, success: bool = True):
        """Show slash command confirmation."""
        self.console.print()
        self.console.print(self.panels.render_slash_feedback(command, message, success))
        self.console.print()
    
    def show_error(self, error: str):
        """Display error message."""
        self.console.print()
        self.console.print(self.panels.render_error(error))
    
    def show_info(self, message: str):
        """Display info message."""
        self.console.print()
        self.console.print(self.panels.render_info(message))
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console_manager.clear()
    
    def set_cwd(self, cwd: Path):
        """Update current working directory."""
        self.cwd = cwd
