"""Plugin loader and manager for plugin lifecycle."""

import time
import importlib
import traceback
import logging
from typing import Optional, Type, List
from pathlib import Path

from .base import BasePlugin, PluginStatus, PluginHookType, PluginMetadata
from .registry import PluginRegistry


logger = logging.getLogger(__name__)


class PluginManager:
    """Manager for plugin lifecycle and operations."""

    def __init__(self, registry: Optional[PluginRegistry] = None):
        """Initialize plugin manager.
        
        Args:
            registry: Optional existing registry, creates new if not provided
        """
        self.registry = registry or PluginRegistry()
        logger.info("PluginManager initialized")

    def init_plugin(self, plugin: BasePlugin) -> bool:
        """Initialize a plugin.
        
        Args:
            plugin: Plugin to initialize
            
        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = time.time()
            
            # Fire pre-init hook
            plugin.fire_hook(PluginHookType.PRE_INIT)
            
            # Call plugin init
            plugin.init()
            
            # Record timing
            plugin.info.init_duration_ms = (time.time() - start_time) * 1000
            plugin.info.initialized_at = time.time()
            plugin.set_status(PluginStatus.INITIALIZED)
            
            # Fire post-init hook
            plugin.fire_hook(PluginHookType.POST_INIT)
            
            logger.info(f"Plugin {plugin.metadata.name} initialized in {plugin.info.init_duration_ms:.2f}ms")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin.metadata.name}: {e}")
            plugin.info.error_message = str(e)
            plugin.info.error_trace = traceback.format_exc()
            plugin.set_status(PluginStatus.ERROR)
            plugin.fire_hook(PluginHookType.ON_ERROR, PluginStatus.INITIALIZED, e)
            return False

    def load_plugin(self, plugin: BasePlugin) -> bool:
        """Load a plugin.
        
        Args:
            plugin: Plugin to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not plugin.is_loaded() and plugin.get_status() != PluginStatus.INITIALIZED:
                # Initialize if not already done
                if not self.init_plugin(plugin):
                    return False
            
            start_time = time.time()
            
            # Fire pre-load hook
            plugin.fire_hook(PluginHookType.PRE_LOAD)
            
            # Call plugin load
            plugin.load()
            
            # Record timing
            plugin.info.load_duration_ms = (time.time() - start_time) * 1000
            plugin.info.loaded_at = time.time()
            plugin.set_status(PluginStatus.LOADED)
            
            # Fire post-load hook
            plugin.fire_hook(PluginHookType.POST_LOAD)
            
            logger.info(f"Plugin {plugin.metadata.name} loaded in {plugin.info.load_duration_ms:.2f}ms")
            return True
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin.metadata.name}: {e}")
            plugin.info.error_message = str(e)
            plugin.info.error_trace = traceback.format_exc()
            plugin.set_status(PluginStatus.ERROR)
            plugin.fire_hook(PluginHookType.ON_ERROR, PluginStatus.LOADED, e)
            return False

    def enable_plugin(self, plugin: BasePlugin) -> bool:
        """Enable a plugin.
        
        Args:
            plugin: Plugin to enable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not plugin.is_loaded():
                # Load if not already done
                if not self.load_plugin(plugin):
                    return False
            
            # Fire pre-enable hook
            plugin.fire_hook(PluginHookType.PRE_ENABLE)
            
            # Call plugin enable
            plugin.enable()
            
            # Update status
            plugin.info.enabled_at = time.time()
            plugin.set_status(PluginStatus.ENABLED)
            
            # Fire post-enable hook
            plugin.fire_hook(PluginHookType.POST_ENABLE)
            
            logger.info(f"Plugin {plugin.metadata.name} enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin.metadata.name}: {e}")
            plugin.info.error_message = str(e)
            plugin.info.error_trace = traceback.format_exc()
            plugin.set_status(PluginStatus.ERROR)
            plugin.fire_hook(PluginHookType.ON_ERROR, PluginStatus.ENABLED, e)
            return False

    def disable_plugin(self, plugin: BasePlugin) -> bool:
        """Disable a plugin.
        
        Args:
            plugin: Plugin to disable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not plugin.is_enabled():
                logger.warning(f"Plugin {plugin.metadata.name} is not enabled")
                return True
            
            # Fire pre-disable hook
            plugin.fire_hook(PluginHookType.PRE_DISABLE)
            
            # Call plugin disable
            plugin.disable()
            
            # Update status
            plugin.set_status(PluginStatus.DISABLED)
            
            # Fire post-disable hook
            plugin.fire_hook(PluginHookType.POST_DISABLE)
            
            logger.info(f"Plugin {plugin.metadata.name} disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin.metadata.name}: {e}")
            plugin.info.error_message = str(e)
            plugin.info.error_trace = traceback.format_exc()
            plugin.set_status(PluginStatus.ERROR)
            plugin.fire_hook(PluginHookType.ON_ERROR, PluginStatus.DISABLED, e)
            return False

    def unload_plugin(self, plugin: BasePlugin) -> bool:
        """Unload a plugin.
        
        Args:
            plugin: Plugin to unload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Disable if enabled
            if plugin.is_enabled():
                if not self.disable_plugin(plugin):
                    # Continue with unload attempt
                    pass
            
            # Fire pre-unload hook
            plugin.fire_hook(PluginHookType.PRE_UNLOAD)
            
            # Call plugin unload
            plugin.unload()
            
            # Update status
            plugin.set_status(PluginStatus.UNLOADED)
            
            # Fire post-unload hook
            plugin.fire_hook(PluginHookType.POST_UNLOAD)
            
            logger.info(f"Plugin {plugin.metadata.name} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin.metadata.name}: {e}")
            plugin.info.error_message = str(e)
            plugin.info.error_trace = traceback.format_exc()
            plugin.set_status(PluginStatus.ERROR)
            plugin.fire_hook(PluginHookType.ON_ERROR, PluginStatus.UNLOADED, e)
            return False

    def load_and_register(self, plugin: BasePlugin) -> bool:
        """Load, initialize and register a plugin.
        
        Args:
            plugin: Plugin to load and register
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Register first
            self.registry.register(plugin)
            
            # Then initialize
            if not self.init_plugin(plugin):
                return False
            
            # Enable if auto_load is true
            if plugin.info.config.auto_load:
                if not self.enable_plugin(plugin):
                    logger.warning(f"Plugin {plugin.metadata.name} loaded but not enabled")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load and register plugin: {e}")
            return False

    def load_plugin_from_module(self, module_path: str, class_name: str) -> Optional[BasePlugin]:
        """Load a plugin from a module path.
        
        Args:
            module_path: Module import path (e.g., 'app.plugins.examples.github_plugin')
            class_name: Name of plugin class (e.g., 'GitHubPlugin')
            
        Returns:
            Plugin instance or None if failed
        """
        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            if not issubclass(plugin_class, BasePlugin):
                logger.error(f"{class_name} is not a BasePlugin subclass")
                return None
            
            # Instantiate with metadata
            plugin = plugin_class()
            logger.info(f"Loaded plugin {plugin.metadata.name} from {module_path}")
            return plugin
        except Exception as e:
            logger.error(f"Failed to load plugin from {module_path}.{class_name}: {e}")
            return None

    def load_plugin_from_file(self, file_path: str, class_name: str) -> Optional[BasePlugin]:
        """Load a plugin from a file path.
        
        Args:
            file_path: Path to Python file containing plugin
            class_name: Name of plugin class
            
        Returns:
            Plugin instance or None if failed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Plugin file {file_path} not found")
                return None
            
            # Convert path to module path
            module_path = path.stem
            spec = importlib.util.spec_from_file_location(module_path, path)
            if not spec or not spec.loader:
                logger.error(f"Cannot load spec from {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            plugin_class = getattr(module, class_name)
            if not issubclass(plugin_class, BasePlugin):
                logger.error(f"{class_name} is not a BasePlugin subclass")
                return None
            
            plugin = plugin_class()
            logger.info(f"Loaded plugin {plugin.metadata.name} from {file_path}")
            return plugin
        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")
            return None

    def discover_plugins(self, directory: str) -> List[BasePlugin]:
        """Discover and load plugins from a directory.
        
        Args:
            directory: Directory to search for plugins
            
        Returns:
            List of discovered plugin instances
        """
        plugins = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"Plugin directory {directory} does not exist")
            return plugins
        
        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Try to load plugin from file
                module_path = py_file.stem
                spec = importlib.util.spec_from_file_location(module_path, py_file)
                if not spec or not spec.loader:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find BasePlugin subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr is not BasePlugin):
                        
                        plugin = attr()
                        plugins.append(plugin)
                        logger.info(f"Discovered plugin: {plugin.metadata.name}")
            except Exception as e:
                logger.warning(f"Failed to discover plugins in {py_file}: {e}")
        
        return plugins

    def get_plugin_status_summary(self, plugin_name: Optional[str] = None) -> dict:
        """Get status summary for plugins.
        
        Args:
            plugin_name: Optional specific plugin name, all if not provided
            
        Returns:
            Dictionary with status information
        """
        if plugin_name:
            plugin = self.registry.get(plugin_name)
            if not plugin:
                return {"error": f"Plugin {plugin_name} not found"}
            
            return {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "status": plugin.get_status().value,
                "initialized_at": plugin.info.initialized_at,
                "loaded_at": plugin.info.loaded_at,
                "enabled_at": plugin.info.enabled_at,
                "init_duration_ms": plugin.info.init_duration_ms,
                "load_duration_ms": plugin.info.load_duration_ms,
                "error": plugin.info.error_message,
            }
        
        return self.registry.get_stats()
