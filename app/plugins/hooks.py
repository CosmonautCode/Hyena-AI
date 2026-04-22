"""Plugin hooks system for event-driven plugin interactions."""

from typing import Callable, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


class PluginHookManager:
    """Manager for plugin-level hooks and events."""

    def __init__(self):
        """Initialize hook manager."""
        self._hooks: Dict[str, List[Callable]] = {}
        logger.info("PluginHookManager initialized")

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback.
        
        Args:
            hook_name: Name of hook (e.g., 'on_command_executed')
            callback: Callback function to invoke
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        
        self._hooks[hook_name].append(callback)
        logger.debug(f"Hook {hook_name} registered")

    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """Unregister a hook callback.
        
        Args:
            hook_name: Name of hook
            callback: Callback to remove
            
        Returns:
            True if callback was found and removed
        """
        if hook_name not in self._hooks:
            return False
        
        if callback in self._hooks[hook_name]:
            self._hooks[hook_name].remove(callback)
            logger.debug(f"Hook {hook_name} unregistered")
            return True
        
        return False

    def fire_hook(self, hook_name: str, *args, **kwargs) -> List:
        """Fire a hook and invoke all registered callbacks.
        
        Args:
            hook_name: Name of hook to fire
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
            
        Returns:
            List of results from callbacks
        """
        results = []
        
        if hook_name not in self._hooks:
            return results
        
        for callback in self._hooks[hook_name]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_name} callback failed: {e}")
        
        return results

    def get_hook_callbacks(self, hook_name: str) -> List[Callable]:
        """Get all callbacks for a hook.
        
        Args:
            hook_name: Name of hook
            
        Returns:
            List of registered callbacks
        """
        return self._hooks.get(hook_name, []).copy()

    def list_hooks(self) -> Dict[str, int]:
        """List all registered hooks and callback counts.
        
        Returns:
            Dictionary mapping hook names to callback counts
        """
        return {name: len(callbacks) for name, callbacks in self._hooks.items()}

    def clear_hooks(self, hook_name: Optional[str] = None) -> None:
        """Clear hooks.
        
        Args:
            hook_name: Specific hook to clear, all if not provided
        """
        if hook_name:
            if hook_name in self._hooks:
                self._hooks[hook_name].clear()
                logger.debug(f"Hook {hook_name} cleared")
        else:
            self._hooks.clear()
            logger.debug("All hooks cleared")


# Global hook manager instance
_global_hook_manager = PluginHookManager()


def get_global_hook_manager() -> PluginHookManager:
    """Get the global plugin hook manager.
    
    Returns:
        Global PluginHookManager instance
    """
    return _global_hook_manager


# Convenience functions for common hooks
def register_on_plugin_loaded(callback: Callable) -> None:
    """Register callback for when a plugin is loaded."""
    _global_hook_manager.register_hook("on_plugin_loaded", callback)


def register_on_plugin_enabled(callback: Callable) -> None:
    """Register callback for when a plugin is enabled."""
    _global_hook_manager.register_hook("on_plugin_enabled", callback)


def register_on_plugin_disabled(callback: Callable) -> None:
    """Register callback for when a plugin is disabled."""
    _global_hook_manager.register_hook("on_plugin_disabled", callback)


def register_on_command_executed(callback: Callable) -> None:
    """Register callback for when a command is executed."""
    _global_hook_manager.register_hook("on_command_executed", callback)


def register_on_tool_executed(callback: Callable) -> None:
    """Register callback for when a tool is executed."""
    _global_hook_manager.register_hook("on_tool_executed", callback)


def fire_plugin_loaded(plugin_name: str) -> None:
    """Fire plugin loaded hook."""
    _global_hook_manager.fire_hook("on_plugin_loaded", plugin_name)


def fire_plugin_enabled(plugin_name: str) -> None:
    """Fire plugin enabled hook."""
    _global_hook_manager.fire_hook("on_plugin_enabled", plugin_name)


def fire_plugin_disabled(plugin_name: str) -> None:
    """Fire plugin disabled hook."""
    _global_hook_manager.fire_hook("on_plugin_disabled", plugin_name)


def fire_command_executed(plugin_name: str, command_name: str, result: any) -> None:
    """Fire command executed hook."""
    _global_hook_manager.fire_hook("on_command_executed", plugin_name, command_name, result)


def fire_tool_executed(plugin_name: str, tool_name: str, result: any) -> None:
    """Fire tool executed hook."""
    _global_hook_manager.fire_hook("on_tool_executed", plugin_name, tool_name, result)
