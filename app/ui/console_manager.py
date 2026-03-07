"""Centralized console and style management for Hyena TUI."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich import box


class ConsoleManager:
    """Centralized console and style management."""
    
    def __init__(self):
        # Initialize console with legacy Windows support disabled
        # This prevents the "No Windows console found" error in IDE terminals
        try:
            self.console = Console(
                legacy_windows=False,
                force_terminal=True,
                color_system="truecolor"
            )
            self._console_available = True
        except Exception as e:
            # Fallback for environments where Rich console fails
            print(f"Warning: Console initialization failed: {e}")
            print("Falling back to basic console output.")
            self.console = None
            self._console_available = False
        
        self.styles = {
            'user': 'bold cyan',
            'assistant': 'default',
            'tool_title': 'bold cyan',
            'success': 'green',
            'error': 'red',
            'warning': 'yellow',
            'dim': 'dim',
            'panel_border': 'blue',
            'code_theme': 'monokai'
        }
    
    def get_panel(self, content, title=None, border_style=None, **kwargs):
        """Create a standardized panel with modern formatting."""
        if not self._console_available:
            # Fallback: just return the content as string
            title_str = f"\n[{title}]\n" if title else ""
            return f"{title_str}{content}"
        
        return Panel(
            content,
            title=title,
            border_style=border_style or self.styles['panel_border'],
            box=box.ROUNDED,
            padding=(0, 1),
            **kwargs
        )
    
    def clear(self):
        """Clear the terminal screen."""
        if self._console_available:
            self.console.clear()
        else:
            # Fallback: use system clear
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def print(self, *args, **kwargs):
        """Print to console."""
        if self._console_available:
            self.console.print(*args, **kwargs)
        else:
            # Fallback: use regular print
            print(*args)
    
    def is_available(self) -> bool:
        """Check if Rich console is available."""
        return self._console_available
