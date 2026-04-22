"""Comprehensive tests for plugin system."""

import pytest
import time
from app.plugins import (
    BasePlugin,
    PluginStatus,
    PluginHookType,
    PluginMetadata,
    PluginConfig,
    PluginRegistry,
    PluginManager,
    PluginHookManager,
)
from app.plugins.examples.hello_world import HelloWorldPlugin
from app.plugins.examples.math_tools import MathToolsPlugin
from app.plugins.examples.github_integration import GitHubIntegrationPlugin


# Test fixtures
@pytest.fixture
def hello_plugin():
    """Hello world plugin fixture."""
    return HelloWorldPlugin()


@pytest.fixture
def math_plugin():
    """Math tools plugin fixture."""
    return MathToolsPlugin()


@pytest.fixture
def github_plugin():
    """GitHub integration plugin fixture."""
    return GitHubIntegrationPlugin()


@pytest.fixture
def registry():
    """Plugin registry fixture."""
    return PluginRegistry()


@pytest.fixture
def manager():
    """Plugin manager fixture."""
    return PluginManager()


# Plugin Base Tests
class TestPluginMetadata:
    """Tests for plugin metadata."""

    def test_plugin_metadata_creation(self, hello_plugin):
        """Test plugin metadata is created correctly."""
        metadata = hello_plugin.metadata
        assert metadata.name == "hello_world"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Hyena AI"

    def test_plugin_metadata_dependencies(self, github_plugin):
        """Test plugin can declare dependencies."""
        metadata = github_plugin.metadata
        assert "requests>=2.28.0" in metadata.dependencies

    def test_plugin_metadata_permissions(self, github_plugin):
        """Test plugin can declare permissions."""
        metadata = github_plugin.metadata
        assert "tools.http" in metadata.permissions
        assert "tools.file.read" in metadata.permissions

    def test_plugin_metadata_commands(self, hello_plugin):
        """Test plugin can declare commands."""
        assert "hello" in hello_plugin.metadata.commands
        assert "greet" in hello_plugin.metadata.commands

    def test_plugin_metadata_tools(self, math_plugin):
        """Test plugin can declare tools."""
        assert "basic_arithmetic" in math_plugin.metadata.tools
        assert "advanced_math" in math_plugin.metadata.tools


class TestPluginInitialization:
    """Tests for plugin initialization."""

    def test_plugin_init(self, hello_plugin):
        """Test plugin can be initialized."""
        hello_plugin.init()
        assert hello_plugin.get_status() == PluginStatus.INITIALIZED

    def test_plugin_commands_registered(self, hello_plugin):
        """Test commands are registered during init."""
        hello_plugin.init()
        commands = hello_plugin.get_commands()
        assert "hello" in commands
        assert "greet" in commands
        assert "hello_extended" in commands

    def test_plugin_tools_registered(self, math_plugin):
        """Test tools are registered during init."""
        math_plugin.init()
        tools = math_plugin.get_tools()
        assert "basic_arithmetic" in tools
        assert "advanced_math" in tools
        assert "statistics" in tools

    def test_plugin_init_duration(self, hello_plugin):
        """Test plugin init duration is recorded."""
        hello_plugin.init()
        assert hello_plugin.info.init_duration_ms >= 0


class TestPluginLifecycle:
    """Tests for plugin lifecycle management."""

    def test_plugin_load(self, hello_plugin):
        """Test plugin loading."""
        hello_plugin.init()
        hello_plugin.load()
        assert hello_plugin.get_status() == PluginStatus.LOADED

    def test_plugin_enable(self, hello_plugin):
        """Test plugin enabling."""
        hello_plugin.init()
        hello_plugin.load()
        hello_plugin.enable()
        assert hello_plugin.is_enabled()

    def test_plugin_disable(self, hello_plugin):
        """Test plugin disabling."""
        hello_plugin.init()
        hello_plugin.load()
        hello_plugin.enable()
        hello_plugin.disable()
        assert not hello_plugin.is_enabled()

    def test_plugin_unload(self, hello_plugin):
        """Test plugin unloading."""
        hello_plugin.init()
        hello_plugin.load()
        hello_plugin.enable()
        hello_plugin.disable()
        hello_plugin.unload()
        assert hello_plugin.get_status() == PluginStatus.UNLOADED

    def test_plugin_full_lifecycle(self, math_plugin):
        """Test complete plugin lifecycle."""
        assert math_plugin.get_status() == PluginStatus.UNINITIALIZED
        
        math_plugin.init()
        assert math_plugin.get_status() == PluginStatus.INITIALIZED
        
        math_plugin.load()
        assert math_plugin.is_loaded()
        
        math_plugin.enable()
        assert math_plugin.is_enabled()
        
        math_plugin.disable()
        assert math_plugin.get_status() == PluginStatus.DISABLED


class TestPluginCommands:
    """Tests for plugin command execution."""

    def test_command_registration(self, hello_plugin):
        """Test command registration."""
        hello_plugin.init()
        cmd = hello_plugin.get_commands()["hello"]
        assert callable(cmd)

    def test_command_execution(self, hello_plugin):
        """Test command execution."""
        hello_plugin.init()
        result = hello_plugin.execute_command("hello")
        assert result["success"]
        assert "Hello" in result["message"]

    def test_command_with_args(self, hello_plugin):
        """Test command execution with arguments."""
        hello_plugin.init()
        result = hello_plugin.execute_command("greet", name="Alice")
        assert result["success"]
        assert "Alice" in result["message"]

    def test_command_not_found(self, hello_plugin):
        """Test command not found error."""
        hello_plugin.init()
        with pytest.raises(KeyError):
            hello_plugin.execute_command("nonexistent")

    def test_github_commands(self, github_plugin):
        """Test GitHub plugin commands."""
        github_plugin.init()
        
        # Test repo_info command
        result = github_plugin.execute_command("repo_info", owner="python", repo="cpython")
        assert result["success"]
        assert result["owner"] == "python"
        
        # Test search_repos command
        result = github_plugin.execute_command("search_repos", query="machine learning")
        assert result["success"]
        assert "machine learning" in result["query"]


class TestPluginTools:
    """Tests for plugin tool execution."""

    def test_tool_registration(self, math_plugin):
        """Test tool registration."""
        math_plugin.init()
        tool = math_plugin.get_tools()["basic_arithmetic"]
        assert callable(tool)

    def test_tool_execution(self, math_plugin):
        """Test tool execution."""
        math_plugin.init()
        result = math_plugin.execute_tool("basic_arithmetic", operation="add", a=5, b=3)
        assert result["success"]
        assert result["result"] == 8

    def test_tool_add(self, math_plugin):
        """Test addition tool."""
        math_plugin.init()
        result = math_plugin.execute_tool("basic_arithmetic", operation="add", a=10, b=20)
        assert result["result"] == 30

    def test_tool_multiply(self, math_plugin):
        """Test multiplication tool."""
        math_plugin.init()
        result = math_plugin.execute_tool("basic_arithmetic", operation="multiply", a=7, b=6)
        assert result["result"] == 42

    def test_tool_divide_by_zero(self, math_plugin):
        """Test division by zero error handling."""
        math_plugin.init()
        result = math_plugin.execute_tool("basic_arithmetic", operation="divide", a=10, b=0)
        assert not result["success"]
        assert "Division by zero" in result["error"]

    def test_tool_sqrt(self, math_plugin):
        """Test square root tool."""
        math_plugin.init()
        result = math_plugin.execute_tool("advanced_math", operation="sqrt", value=16)
        assert result["success"]
        assert result["result"] == 4.0

    def test_tool_statistics(self, math_plugin):
        """Test statistics tool."""
        math_plugin.init()
        values = [1, 2, 3, 4, 5]
        result = math_plugin.execute_tool("statistics", operation="mean", values=values)
        assert result["success"]
        assert result["result"] == 3.0

    def test_tool_not_found(self, math_plugin):
        """Test tool not found error."""
        math_plugin.init()
        with pytest.raises(KeyError):
            math_plugin.execute_tool("nonexistent")

    def test_github_tools(self, github_plugin):
        """Test GitHub plugin tools."""
        github_plugin.init()
        
        # Test fetch user repos
        result = github_plugin.execute_tool("fetch_user_repos", username="torvalds")
        assert result["success"]
        assert "torvalds" in result["username"]
        
        # Test get repo details
        result = github_plugin.execute_tool("get_repo_details", owner="python", repo="cpython")
        assert result["success"]


class TestPluginRegistry:
    """Tests for plugin registry."""

    def test_registry_creation(self, registry):
        """Test registry creation."""
        assert registry.count_all() == 0

    def test_register_plugin(self, registry, hello_plugin):
        """Test plugin registration."""
        registry.register(hello_plugin)
        assert registry.count_all() == 1
        assert registry.get("hello_world") == hello_plugin

    def test_register_multiple_plugins(self, registry, hello_plugin, math_plugin, github_plugin):
        """Test registering multiple plugins."""
        registry.register(hello_plugin)
        registry.register(math_plugin)
        registry.register(github_plugin)
        
        assert registry.count_all() == 3
        assert len(registry.list_by_name()) == 3

    def test_register_duplicate_plugin(self, registry, hello_plugin):
        """Test duplicate plugin registration error."""
        registry.register(hello_plugin)
        with pytest.raises(ValueError):
            registry.register(hello_plugin)

    def test_unregister_plugin(self, registry, hello_plugin):
        """Test plugin unregistration."""
        registry.register(hello_plugin)
        hello_plugin.init()
        hello_plugin.load()
        hello_plugin.enable()
        hello_plugin.disable()
        
        registry.unregister("hello_world")
        assert registry.count_all() == 0

    def test_list_all_plugins(self, registry, hello_plugin, math_plugin):
        """Test listing all plugins."""
        registry.register(hello_plugin)
        registry.register(math_plugin)
        
        plugins = registry.list_all()
        assert len(plugins) == 2

    def test_list_enabled_plugins(self, registry, hello_plugin, math_plugin, manager):
        """Test listing enabled plugins."""
        registry.register(hello_plugin)
        registry.register(math_plugin)
        
        manager.registry = registry
        manager.enable_plugin(hello_plugin)
        
        enabled = registry.list_enabled()
        assert len(enabled) == 1
        assert enabled[0].metadata.name == "hello_world"


class TestPluginManager:
    """Tests for plugin manager."""

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager.registry is not None

    def test_manager_init_plugin(self, manager, hello_plugin):
        """Test manager plugin initialization."""
        result = manager.init_plugin(hello_plugin)
        assert result
        assert hello_plugin.get_status() == PluginStatus.INITIALIZED

    def test_manager_load_plugin(self, manager, hello_plugin):
        """Test manager plugin loading."""
        manager.init_plugin(hello_plugin)
        result = manager.load_plugin(hello_plugin)
        assert result
        assert hello_plugin.is_loaded()

    def test_manager_enable_plugin(self, manager, hello_plugin):
        """Test manager plugin enabling."""
        manager.init_plugin(hello_plugin)
        manager.load_plugin(hello_plugin)
        result = manager.enable_plugin(hello_plugin)
        assert result
        assert hello_plugin.is_enabled()

    def test_manager_disable_plugin(self, manager, hello_plugin):
        """Test manager plugin disabling."""
        manager.init_plugin(hello_plugin)
        manager.load_plugin(hello_plugin)
        manager.enable_plugin(hello_plugin)
        result = manager.disable_plugin(hello_plugin)
        assert result
        assert not hello_plugin.is_enabled()

    def test_manager_load_and_register(self, manager, hello_plugin):
        """Test manager load and register."""
        result = manager.load_and_register(hello_plugin)
        assert result
        assert manager.registry.get("hello_world") == hello_plugin
        assert hello_plugin.is_enabled()

    def test_manager_plugin_status_summary(self, manager, hello_plugin):
        """Test plugin status summary."""
        manager.load_and_register(hello_plugin)
        stats = manager.get_plugin_status_summary()
        assert stats["total_plugins"] == 1
        assert stats["enabled_plugins"] == 1


class TestPluginAggregation:
    """Tests for command and tool aggregation."""

    def test_get_all_commands(self, registry, hello_plugin, github_plugin, manager):
        """Test getting all commands from plugins."""
        registry.register(hello_plugin)
        registry.register(github_plugin)
        
        manager.enable_plugin(hello_plugin)
        manager.enable_plugin(github_plugin)
        
        commands = registry.get_all_commands()
        assert len(commands) > 0
        assert any("hello" in cmd for cmd in commands)

    def test_get_all_tools(self, registry, math_plugin, github_plugin, manager):
        """Test getting all tools from plugins."""
        registry.register(math_plugin)
        registry.register(github_plugin)
        
        manager.enable_plugin(math_plugin)
        manager.enable_plugin(github_plugin)
        
        tools = registry.get_all_tools()
        assert len(tools) > 0
        assert any("basic_arithmetic" in tool for tool in tools)

    def test_execute_plugin_command(self, registry, hello_plugin, manager):
        """Test executing plugin command via registry."""
        registry.register(hello_plugin)
        manager.enable_plugin(hello_plugin)
        
        result = registry.execute_plugin_command("hello_world", "hello")
        assert result["success"]

    def test_execute_plugin_tool(self, registry, math_plugin, manager):
        """Test executing plugin tool via registry."""
        registry.register(math_plugin)
        manager.enable_plugin(math_plugin)
        
        result = registry.execute_plugin_tool(
            "math_tools", "basic_arithmetic",
            operation="add", a=5, b=3
        )
        assert result["result"] == 8


class TestPluginPerformance:
    """Tests for plugin performance."""

    def test_plugin_init_speed(self, hello_plugin):
        """Test plugin init is fast."""
        start = time.time()
        hello_plugin.init()
        duration = (time.time() - start) * 1000
        
        assert hello_plugin.info.init_duration_ms < 100
        assert duration < 100

    def test_command_execution_speed(self, hello_plugin):
        """Test command execution is fast."""
        hello_plugin.init()
        
        start = time.time()
        hello_plugin.execute_command("hello")
        duration = (time.time() - start) * 1000
        
        assert duration < 50

    def test_tool_execution_speed(self, math_plugin):
        """Test tool execution is fast."""
        math_plugin.init()
        
        start = time.time()
        math_plugin.execute_tool("basic_arithmetic", operation="add", a=10, b=20)
        duration = (time.time() - start) * 1000
        
        assert duration < 50

    def test_multiple_plugin_load_speed(self, manager, hello_plugin, math_plugin, github_plugin):
        """Test loading multiple plugins is reasonably fast."""
        start = time.time()
        
        manager.load_and_register(hello_plugin)
        manager.load_and_register(math_plugin)
        manager.load_and_register(github_plugin)
        
        duration = (time.time() - start) * 1000
        assert duration < 500  # All 3 should load under 500ms


class TestPluginHooks:
    """Tests for plugin hook system."""

    def test_hook_registration(self, hello_plugin):
        """Test hook registration."""
        def callback():
            pass
        
        hello_plugin.register_hook(PluginHookType.POST_INIT, callback)
        hooks = hello_plugin._hooks[PluginHookType.POST_INIT]
        assert callback in hooks

    def test_hook_firing(self, hello_plugin):
        """Test hook firing."""
        callback_called = []
        
        def callback(value):
            callback_called.append(value)
        
        hello_plugin.register_hook(PluginHookType.POST_INIT, callback)
        results = hello_plugin.fire_hook(PluginHookType.POST_INIT, "test_value")
        
        assert len(callback_called) == 1
        assert callback_called[0] == "test_value"

    def test_multiple_hooks(self, hello_plugin):
        """Test multiple hooks."""
        results = []
        
        def callback1():
            results.append(1)
            return 1
        
        def callback2():
            results.append(2)
            return 2
        
        hello_plugin.register_hook(PluginHookType.POST_INIT, callback1)
        hello_plugin.register_hook(PluginHookType.POST_INIT, callback2)
        
        hello_plugin.fire_hook(PluginHookType.POST_INIT)
        assert results == [1, 2]


class TestPluginIntegration:
    """Integration tests for plugin system."""

    def test_full_plugin_workflow(self, manager, registry, hello_plugin):
        """Test complete plugin workflow."""
        # Create a new registry for this test
        test_registry = PluginRegistry()
        manager.registry = test_registry
        
        # Load and register
        result = manager.load_and_register(hello_plugin)
        assert result
        
        # Verify in registry
        assert test_registry.count_all() == 1
        assert test_registry.count_enabled() == 1
        
        # Execute command
        cmd_result = test_registry.execute_plugin_command("hello_world", "hello")
        assert cmd_result["success"]
        
        # Get stats
        stats = test_registry.get_stats()
        assert stats["total_plugins"] == 1
        assert stats["enabled_plugins"] == 1

    def test_mixed_plugin_types(self, manager, hello_plugin, math_plugin, github_plugin):
        """Test managing different plugin types together."""
        manager.load_and_register(hello_plugin)
        manager.load_and_register(math_plugin)
        manager.load_and_register(github_plugin)
        
        stats = manager.registry.get_stats()
        assert stats["total_plugins"] == 3
        assert stats["enabled_plugins"] == 3
        assert stats["total_commands"] > 0
        assert stats["total_tools"] > 0


class TestExamplePlugins:
    """Tests specific to example plugins."""

    def test_hello_world_plugin_complete(self, hello_plugin):
        """Test hello world plugin fully."""
        hello_plugin.init()
        hello_plugin.load()
        hello_plugin.enable()
        
        r1 = hello_plugin.execute_command("hello")
        r2 = hello_plugin.execute_command("greet", name="Bob")
        r3 = hello_plugin.execute_command("hello_extended", name="Charlie", formal=True)
        
        assert all(r["success"] for r in [r1, r2, r3])

    def test_math_plugin_all_operations(self, math_plugin):
        """Test all math operations."""
        math_plugin.init()
        
        # Basic arithmetic
        add_result = math_plugin.execute_tool("basic_arithmetic", operation="add", a=5, b=3)
        assert add_result["result"] == 8
        
        # Advanced math
        sqrt_result = math_plugin.execute_tool("advanced_math", operation="sqrt", value=9)
        assert sqrt_result["result"] == 3.0
        
        # Statistics
        stats_result = math_plugin.execute_tool("statistics", operation="mean", values=[1, 2, 3, 4, 5])
        assert stats_result["result"] == 3.0

    def test_github_plugin_complete(self, github_plugin):
        """Test GitHub plugin fully."""
        github_plugin.init()
        github_plugin.load()
        github_plugin.enable()
        
        # Test commands
        repo_info = github_plugin.execute_command("repo_info", owner="golang", repo="go")
        assert repo_info["success"]
        
        # Test tools
        user_repos = github_plugin.execute_tool("fetch_user_repos", username="guido")
        assert user_repos["success"]
