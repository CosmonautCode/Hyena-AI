"""Plugin registry for managing registered plugins."""

from typing import Dict, List, Optional
import logging
from .base import BasePlugin, PluginStatus


logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for managing plugins."""

    def __init__(self):
        """Initialize plugin registry."""
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_order: List[str] = []
        logger.info("PluginRegistry initialized")

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin.
        
        Args:
            plugin: Plugin instance to register
            
        Raises:
            ValueError: If plugin with same name already registered
        """
        plugin_name = plugin.metadata.name
        if plugin_name in self._plugins:
            raise ValueError(f"Plugin {plugin_name} already registered")
        
        self._plugins[plugin_name] = plugin
        # Insert by load order
        insert_pos = len(self._plugin_order)
        for i, existing_name in enumerate(self._plugin_order):
            existing = self._plugins[existing_name]
            if plugin.info.config.load_order < existing.info.config.load_order:
                insert_pos = i
                break
        
        self._plugin_order.insert(insert_pos, plugin_name)
        logger.info(f"Plugin {plugin_name} registered (order: {plugin.info.config.load_order})")

    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin.
        
        Args:
            plugin_name: Name of plugin to unregister
            
        Raises:
            KeyError: If plugin not found
        """
        if plugin_name not in self._plugins:
            raise KeyError(f"Plugin {plugin_name} not found")
        
        plugin = self._plugins[plugin_name]
        if plugin.is_enabled():
            raise RuntimeError(f"Cannot unregister enabled plugin {plugin_name}")
        
        del self._plugins[plugin_name]
        self._plugin_order.remove(plugin_name)
        logger.info(f"Plugin {plugin_name} unregistered")

    def get(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_name)

    def list_all(self) -> List[BasePlugin]:
        """List all registered plugins.
        
        Returns:
            List of all plugin instances in load order
        """
        return [self._plugins[name] for name in self._plugin_order]

    def list_by_name(self) -> List[str]:
        """List all plugin names in load order.
        
        Returns:
            List of plugin names
        """
        return self._plugin_order.copy()

    def list_enabled(self) -> List[BasePlugin]:
        """List all enabled plugins.
        
        Returns:
            List of enabled plugin instances in load order
        """
        return [p for p in self.list_all() if p.is_enabled()]

    def list_disabled(self) -> List[BasePlugin]:
        """List all disabled plugins.
        
        Returns:
            List of disabled plugin instances
        """
        return [p for p in self.list_all() if not p.is_enabled()]

    def find_by_status(self, status: PluginStatus) -> List[BasePlugin]:
        """Find plugins by status.
        
        Args:
            status: Plugin status to search for
            
        Returns:
            List of plugins with matching status
        """
        return [p for p in self.list_all() if p.get_status() == status]

    def count_all(self) -> int:
        """Count total registered plugins.
        
        Returns:
            Total number of plugins
        """
        return len(self._plugins)

    def count_enabled(self) -> int:
        """Count enabled plugins.
        
        Returns:
            Number of enabled plugins
        """
        return len(self.list_enabled())

    def count_by_status(self, status: PluginStatus) -> int:
        """Count plugins by status.
        
        Args:
            status: Plugin status to count
            
        Returns:
            Number of plugins with status
        """
        return len(self.find_by_status(status))

    # Command aggregation
    def get_all_commands(self) -> Dict[str, tuple]:
        """Get all commands from all plugins.
        
        Returns:
            Dict mapping command names to (plugin_name, handler) tuples
        """
        commands = {}
        for plugin in self.list_enabled():
            plugin_commands = plugin.get_commands()
            for cmd_name, handler in plugin_commands.items():
                full_name = f"{plugin.metadata.name}:{cmd_name}"
                commands[full_name] = (plugin.metadata.name, handler)
        return commands

    def execute_plugin_command(self, plugin_name: str, command_name: str, *args, **kwargs):
        """Execute command from specific plugin.
        
        Args:
            plugin_name: Name of plugin
            command_name: Name of command
            *args: Arguments for command
            **kwargs: Keyword arguments for command
            
        Returns:
            Result from command handler
            
        Raises:
            KeyError: If plugin or command not found
        """
        plugin = self.get(plugin_name)
        if not plugin:
            raise KeyError(f"Plugin {plugin_name} not found")
        return plugin.execute_command(command_name, *args, **kwargs)

    # Tool aggregation
    def get_all_tools(self) -> Dict[str, tuple]:
        """Get all tools from all plugins.
        
        Returns:
            Dict mapping tool names to (plugin_name, handler) tuples
        """
        tools = {}
        for plugin in self.list_enabled():
            plugin_tools = plugin.get_tools()
            for tool_name, handler in plugin_tools.items():
                full_name = f"{plugin.metadata.name}:{tool_name}"
                tools[full_name] = (plugin.metadata.name, handler)
        return tools

    def execute_plugin_tool(self, plugin_name: str, tool_name: str, *args, **kwargs):
        """Execute tool from specific plugin.
        
        Args:
            plugin_name: Name of plugin
            tool_name: Name of tool
            *args: Arguments for tool
            **kwargs: Keyword arguments for tool
            
        Returns:
            Result from tool handler
            
        Raises:
            KeyError: If plugin or tool not found
        """
        plugin = self.get(plugin_name)
        if not plugin:
            raise KeyError(f"Plugin {plugin_name} not found")
        return plugin.execute_tool(tool_name, *args, **kwargs)

    # Statistics
    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics.
        
        Returns:
            Dictionary with various statistics
        """
        return {
            "total_plugins": self.count_all(),
            "enabled_plugins": self.count_enabled(),
            "disabled_plugins": len(self.list_disabled()),
            "initialized": self.count_by_status(PluginStatus.INITIALIZED),
            "loaded": self.count_by_status(PluginStatus.LOADED),
            "enabled": self.count_by_status(PluginStatus.ENABLED),
            "disabled": self.count_by_status(PluginStatus.DISABLED),
            "error": self.count_by_status(PluginStatus.ERROR),
            "total_commands": len(self.get_all_commands()),
            "total_tools": len(self.get_all_tools()),
        }
