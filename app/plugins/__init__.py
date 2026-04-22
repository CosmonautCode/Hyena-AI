"""Plugin system module - enables extensibility through plugins."""

from .base import (
    BasePlugin,
    PluginStatus,
    PluginHookType,
    PluginMetadata,
    PluginConfig,
    PluginInfo,
)
from .registry import PluginRegistry
from .loader import PluginManager
from .hooks import (
    PluginHookManager,
    get_global_hook_manager,
    register_on_plugin_loaded,
    register_on_plugin_enabled,
    register_on_plugin_disabled,
    register_on_command_executed,
    register_on_tool_executed,
    fire_plugin_loaded,
    fire_plugin_enabled,
    fire_plugin_disabled,
    fire_command_executed,
    fire_tool_executed,
)

__all__ = [
    # Base classes
    "BasePlugin",
    "PluginStatus",
    "PluginHookType",
    "PluginMetadata",
    "PluginConfig",
    "PluginInfo",
    # Registry
    "PluginRegistry",
    # Manager/Loader
    "PluginManager",
    # Hooks
    "PluginHookManager",
    "get_global_hook_manager",
    "register_on_plugin_loaded",
    "register_on_plugin_enabled",
    "register_on_plugin_disabled",
    "register_on_command_executed",
    "register_on_tool_executed",
    "fire_plugin_loaded",
    "fire_plugin_enabled",
    "fire_plugin_disabled",
    "fire_command_executed",
    "fire_tool_executed",
]
