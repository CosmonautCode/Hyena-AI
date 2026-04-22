"""Hello World plugin - example of a command-based plugin."""

import logging
from ..base import BasePlugin, PluginMetadata, PluginStatus


logger = logging.getLogger(__name__)


class HelloWorldPlugin(BasePlugin):
    """Simple plugin that demonstrates command registration."""

    def __init__(self):
        """Initialize hello world plugin."""
        metadata = PluginMetadata(
            name="hello_world",
            version="1.0.0",
            description="Example plugin with hello world commands",
            author="Hyena AI",
            author_email="team@hyena.ai",
            url="https://github.com/hyena-ai/hello-world-plugin",
            keywords=["example", "demo", "hello"],
            commands=["hello", "greet", "hello_extended"],
        )
        super().__init__(metadata)

    def init(self) -> None:
        """Initialize plugin - register commands."""
        logger.info("Hello World plugin initializing")
        
        # Register commands
        self.register_command("hello", self._cmd_hello)
        self.register_command("greet", self._cmd_greet)
        self.register_command("hello_extended", self._cmd_hello_extended)
        
        self.set_status(PluginStatus.INITIALIZED)
        logger.info("Hello World plugin initialized with 3 commands")

    def load(self) -> None:
        """Load plugin."""
        logger.info("Hello World plugin loading")
        self.set_status(PluginStatus.LOADED)
        logger.info("Hello World plugin loaded")

    def enable(self) -> None:
        """Enable plugin."""
        logger.info("Hello World plugin enabling")
        self.set_status(PluginStatus.ENABLED)
        logger.info("Hello World plugin enabled")

    def disable(self) -> None:
        """Disable plugin."""
        logger.info("Hello World plugin disabling")
        self.set_status(PluginStatus.DISABLED)
        logger.info("Hello World plugin disabled")

    def unload(self) -> None:
        """Unload plugin."""
        logger.info("Hello World plugin unloading")
        self.set_status(PluginStatus.UNLOADED)
        logger.info("Hello World plugin unloaded")

    def _cmd_hello(self) -> dict:
        """Simple hello command."""
        return {
            "success": True,
            "message": "Hello from Hyena AI!",
            "plugin": self.metadata.name,
        }

    def _cmd_greet(self, name: str = "User") -> dict:
        """Greet a user."""
        return {
            "success": True,
            "message": f"Hello, {name}! Welcome to Hyena AI.",
            "name": name,
            "plugin": self.metadata.name,
        }

    def _cmd_hello_extended(self, name: str = "User", formal: bool = False) -> dict:
        """Extended greeting command."""
        if formal:
            greeting = f"Greetings, {name}. Welcome to the Hyena AI system."
        else:
            greeting = f"Hey {name}! Nice to see you here."
        
        return {
            "success": True,
            "message": greeting,
            "name": name,
            "formal": formal,
            "plugin": self.metadata.name,
        }
