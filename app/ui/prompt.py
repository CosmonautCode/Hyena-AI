"""Modern input handling with prompt_toolkit."""

import re
import asyncio
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


class Prompt:
    """Modern input with multi-line support and autocomplete."""
    
    SLASH_COMMANDS = [
        '/help', '/?', '/clear', '/compact', '/plan', '/memory',
        '/tasks', '/status', '/config',
        '/exit', '/quit', '/agents', '/switch', '/save', '/load',
        '/export', '/stats', '/reset', '/workspace', '/permissions',
        '/tools', '/session', '/agentic'
    ]
    
    def __init__(self, history_file: Path = None):
        self.history_file = history_file or Path.home() / '.hyena' / 'history.txt'
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
        })
        
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=WordCompleter(self.SLASH_COMMANDS),
            multiline=True,
            key_bindings=self._setup_key_bindings(),
            style=self.style
        )
    
    def _setup_key_bindings(self) -> KeyBindings:
        """Setup modern key bindings."""
        bindings = KeyBindings()
        
        @bindings.add('enter')
        def submit(event):
            """Enter always submits the input immediately."""
            event.current_buffer.validate_and_handle()
        
        @bindings.add('escape')
        def cancel_input(event):
            """Escape cancels current input."""
            event.current_buffer.reset()
        
        @bindings.add('c-c')
        def interrupt(event):
            """Ctrl+C raises KeyboardInterrupt."""
            event.app.exit(exception=KeyboardInterrupt())
        
        return bindings
    
    async def get_input(self, cwd: str = '') -> str:
        """Get user input with modern prompt."""
        # Simple ❯ prompt without CWD (path shown in banner)
        prompt_text = "❯ "
        
        try:
            user_input = await self.session.prompt_async(prompt_text)
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            raise
    
    def get_input_sync(self, cwd: str = '') -> str:
        """Synchronous version for non-async contexts."""
        
        try:
            return asyncio.run(self.get_input(cwd))
        except RuntimeError:
            # If already in async context, use the session directly
            prompt_text = "❯ "
            user_input = self.session.prompt(prompt_text)
            return user_input.strip()
