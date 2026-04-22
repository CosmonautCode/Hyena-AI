"""Base plugin abstraction for plugin system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin lifecycle status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNLOADED = "unloaded"
    ERROR = "error"


class PluginHookType(Enum):
    """Types of plugin hooks available."""
    PRE_INIT = "pre_init"
    POST_INIT = "post_init"
    PRE_LOAD = "pre_load"
    POST_LOAD = "post_load"
    PRE_ENABLE = "pre_enable"
    POST_ENABLE = "post_enable"
    PRE_DISABLE = "pre_disable"
    POST_DISABLE = "post_disable"
    PRE_UNLOAD = "pre_unload"
    POST_UNLOAD = "post_unload"
    ON_ERROR = "on_error"


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration."""
    name: str
    version: str
    description: str
    author: str = ""
    author_email: str = ""
    url: str = ""
    license: str = "MIT"
    keywords: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    min_version: str = "0.0.0"
    max_version: Optional[str] = None


@dataclass
class PluginConfig:
    """Plugin runtime configuration."""
    enabled: bool = True
    auto_load: bool = True
    load_order: int = 0
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginInfo:
    """Plugin runtime information."""
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.UNINITIALIZED
    config: PluginConfig = field(default_factory=PluginConfig)
    initialized_at: Optional[datetime] = None
    loaded_at: Optional[datetime] = None
    enabled_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    init_duration_ms: float = 0.0
    load_duration_ms: float = 0.0


class BasePlugin(ABC):
    """Abstract base class for all plugins."""

    def __init__(self, metadata: PluginMetadata):
        """Initialize plugin with metadata.
        
        Args:
            metadata: Plugin metadata and configuration
        """
        self.metadata = metadata
        self.info = PluginInfo(metadata=metadata)
        self._hooks: Dict[PluginHookType, List[Callable]] = {}
        self._registered_commands: Dict[str, Callable] = {}
        self._registered_tools: Dict[str, Callable] = {}
        logger.info(f"Plugin {metadata.name} created")

    @abstractmethod
    def init(self) -> None:
        """Initialize plugin resources and register hooks."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load plugin functionality."""
        pass

    @abstractmethod
    def enable(self) -> None:
        """Enable plugin features."""
        pass

    @abstractmethod
    def disable(self) -> None:
        """Disable plugin features."""
        pass

    @abstractmethod
    def unload(self) -> None:
        """Unload plugin and cleanup resources."""
        pass

    # Hook management
    def register_hook(self, hook_type: PluginHookType, callback: Callable) -> None:
        """Register a hook callback.
        
        Args:
            hook_type: Type of hook to register
            callback: Callback function to call when hook fires
        """
        if hook_type not in self._hooks:
            self._hooks[hook_type] = []
        self._hooks[hook_type].append(callback)
        logger.debug(f"Hook {hook_type.value} registered for {self.metadata.name}")

    def fire_hook(self, hook_type: PluginHookType, *args, **kwargs) -> List[Any]:
        """Fire a hook and return results from all callbacks.
        
        Args:
            hook_type: Type of hook to fire
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
            
        Returns:
            List of results from hook callbacks
        """
        results = []
        for callback in self._hooks.get(hook_type, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_type.value} failed: {e}")
                self.fire_hook(PluginHookType.ON_ERROR, hook_type, e)
        return results

    # Command registration
    def register_command(self, command_name: str, handler: Callable) -> None:
        """Register a command handler.
        
        Args:
            command_name: Name of command (e.g., 'my_command')
            handler: Callable to handle the command
        """
        self._registered_commands[command_name] = handler
        logger.info(f"Command {command_name} registered for {self.metadata.name}")

    def get_commands(self) -> Dict[str, Callable]:
        """Get all registered commands."""
        return self._registered_commands.copy()

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a registered command.
        
        Args:
            command_name: Name of command to execute
            *args: Positional arguments for command
            **kwargs: Keyword arguments for command
            
        Returns:
            Result from command handler
            
        Raises:
            KeyError: If command not found
        """
        if command_name not in self._registered_commands:
            raise KeyError(f"Command {command_name} not found in {self.metadata.name}")
        return self._registered_commands[command_name](*args, **kwargs)

    # Tool registration
    def register_tool(self, tool_name: str, handler: Callable) -> None:
        """Register a tool handler.
        
        Args:
            tool_name: Name of tool (e.g., 'my_tool')
            handler: Callable to handle the tool
        """
        self._registered_tools[tool_name] = handler
        logger.info(f"Tool {tool_name} registered for {self.metadata.name}")

    def get_tools(self) -> Dict[str, Callable]:
        """Get all registered tools."""
        return self._registered_tools.copy()

    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute a registered tool.
        
        Args:
            tool_name: Name of tool to execute
            *args: Positional arguments for tool
            **kwargs: Keyword arguments for tool
            
        Returns:
            Result from tool handler
            
        Raises:
            KeyError: If tool not found
        """
        if tool_name not in self._registered_tools:
            raise KeyError(f"Tool {tool_name} not found in {self.metadata.name}")
        return self._registered_tools[tool_name](*args, **kwargs)

    # Status tracking
    def get_status(self) -> PluginStatus:
        """Get current plugin status."""
        return self.info.status

    def set_status(self, status: PluginStatus) -> None:
        """Set plugin status."""
        self.info.status = status
        logger.debug(f"{self.metadata.name} status: {status.value}")

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.info.status == PluginStatus.ENABLED

    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.info.status in [PluginStatus.LOADED, PluginStatus.ENABLED]

    def get_info(self) -> PluginInfo:
        """Get plugin info."""
        return self.info

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata
