"""Tool call and result panel rendering - Modern terminal interface."""

from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import Dict, Any


class PanelRenderer:
    """Render tool call and result panels with modern formatting."""
    
    MAX_RESULT_CHARS = 10000
    
    def render_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Panel:
        """Render tool invocation panel with cyan border."""
        if args:
            args_str = '\n'.join(f'[dim]{k}:[/] {v}' for k, v in args.items())
        else:
            args_str = '[dim]No arguments[/dim]'
        
        return Panel(
            args_str,
            title=f'[bold cyan]{tool_name}[/bold cyan]',
            border_style='cyan',
            box=box.ROUNDED,
            padding=(0, 1)
        )
    
    def render_tool_result(self, tool_name: str, result: str, success: bool) -> Panel:
        """Render tool result panel with success/failure styling."""
        icon = '✓' if success else '✗'
        style = 'green' if success else 'red'
        
        # Truncate very long results
        if len(result) > self.MAX_RESULT_CHARS:
            result = result[:self.MAX_RESULT_CHARS] + '\n... (truncated)'
        
        return Panel(
            result,
            title=f'[{style}]{icon} {tool_name} completed[/{style}]',
            border_style=style,
            box=box.ROUNDED,
            padding=(0, 1)
        )
    
    def render_user_message(self, content: str, width: int = None) -> Text:
        """Render user message without prefix (cleaner display)."""
        # Just return the content directly - no "You:" prefix
        return Text(content, style='white', overflow='fold', no_wrap=False)
    
    def render_assistant_panel(self, content: str, title: str = 'Assistant', width: int = None) -> Panel:
        """Render assistant message panel with markdown support and smart wrapping."""
        from rich.markdown import Markdown
        
        # Calculate appropriate width
        if width is None:
            width = min(100, 80)  # Default max width for readability
        
        return Panel(
            Markdown(content, code_theme='monokai'),
            title=f'[bold blue]{title}[/bold blue]',
            border_style='blue',
            box=box.ROUNDED,
            padding=(0, 1),
            width=width,
            safe_box=True
        )
    
    def render_slash_feedback(self, command: str, message: str, success: bool = True) -> Panel:
        """Render slash command confirmation."""
        style = 'green' if success else 'red'
        return Panel(
            message,
            title=f'[bold {style}]/{command}[/bold {style}]',
            border_style=style,
            box=box.ROUNDED,
            padding=(0, 1)
        )
    
    def render_error(self, error: str) -> Panel:
        """Render error panel."""
        return Panel(
            error,
            title='[bold red]Error[/bold red]',
            border_style='red',
            box=box.ROUNDED,
            padding=(0, 1)
        )
    
    def render_info(self, message: str) -> Text:
        """Render info message."""
        return Text(message, style='dim')
