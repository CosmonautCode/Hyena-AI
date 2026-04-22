"""Welcome banner component for Hyena CLI - Modern terminal interface."""

from rich.panel import Panel
from rich.text import Text
from pathlib import Path


class Banner:
    """Modern welcome banner with Hyena branding."""
    
    HYENA_ASCII = """[bold blue] ▐▙   ▟▌[/bold blue]   [bold green]Hyena CLI[/bold green] [dim]v{version}[/dim]
[bold blue] █▛███▜█[/bold blue]  [dim]{model} · {backend}[/dim]
[bold blue]▝▜█████▛▘[/bold blue]    [cyan]{cwd}[/cyan]"""


    
    def __init__(self, version="0.2.0", model="Hyena3-4B", backend="Local LLM"):
        self.version = version
        self.model = model
        self.backend = backend
    
    def render(self, cwd: str = None) -> Panel:
        """Render the welcome banner panel."""
        if cwd is None:
            cwd = str(Path.cwd())
        
        content = self.HYENA_ASCII.format(
            version=self.version,
            model=self.model,
            backend=self.backend,
            cwd=cwd
        )
        
        # Add hint for help
        help_text = "\n\n[dim]Type [bold]/help[/bold] for commands or just start chatting[/dim]"
        content += help_text
        
        return Panel(
            content,
            border_style='blue',
            padding=(1, 2)
        )
    
    def print(self, console, cwd: str = None):
        """Print the banner to console."""
        console.print(self.render(cwd))
        console.print()
