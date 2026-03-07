"""Live streaming response rendering - Modern terminal interface."""

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.text import Text


class StreamingDisplay:
    """Handle live streaming response rendering with markdown."""
    
    def __init__(self, console: Console):
        self.console = console
        self._live = None
        self._buffer = ''
        self._thinking_spinner = None
    
    def start_thinking(self, label: str = 'Thinking'):
        """Show thinking spinner while waiting for LLM."""
        if self._thinking_spinner is None:
            self._thinking_spinner = Live(
                Spinner('dots', text=f' {label}...'),
                console=self.console,
                refresh_per_second=10,
                transient=True  # This makes it disappear when stopped
            )
            self._thinking_spinner.start()
    
    def stop_thinking(self):
        """Stop the thinking spinner - it will auto-clear due to transient=True."""
        if self._thinking_spinner:
            self._thinking_spinner.stop()
            self._thinking_spinner = None
    
    def start_streaming(self):
        """Begin streaming display with live markdown rendering."""
        self.stop_thinking()
        
        if self._live is None:
            self._live = Live(
                console=self.console,
                refresh_per_second=15,
                auto_refresh=True
            )
            self._live.start()
    
    def add_token(self, token: str):
        """Add token to buffer and update display."""
        if self._live is None:
            self.start_streaming()
        
        self._buffer += token
        # Render markdown live - Rich handles this efficiently
        self._live.update(Markdown(self._buffer, code_theme='monokai'))
    
    def end_streaming(self) -> str:
        """End streaming and return final content."""
        if self._live:
            self._live.stop()
            self._live = None
        
        final_content = self._buffer
        self._buffer = ''
        return final_content
    
    def cancel(self):
        """Cancel streaming and clear buffer."""
        if self._live:
            self._live.stop()
            self._live = None
        self._buffer = ''
        
        if self._thinking_spinner:
            self._thinking_spinner.stop()
            self._thinking_spinner = None
