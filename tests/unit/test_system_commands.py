"""Tests for system commands."""

import pytest
from app.cli.commands.system import (
    VersionCommand,
    HelpCommand,
    DebugCommand,
    LogsDebugCommand,
    BenchmarkCommand,
    ProfileCommand,
    ReportCommand,
    IssueCommand,
    UIThemeCommand,
    UIModeCommand,
    PluginListCommand,
    PluginInstallCommand,
)
from app.cli.commands.base import CommandContext


class TestVersionCommand:
    """Test /version command."""

    @pytest.mark.asyncio
    async def test_version(self):
        """Test getting version info."""
        cmd = VersionCommand()
        ctx = CommandContext("version", {})
        result = await cmd.execute(ctx)
        assert result.success
        assert "version" in result.data


class TestHelpCommand:
    """Test /help command."""

    @pytest.mark.asyncio
    async def test_help_all(self):
        """Test help without specific command."""
        cmd = HelpCommand()
        ctx = CommandContext("help", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_help_specific(self):
        """Test help for specific command."""
        cmd = HelpCommand()
        ctx = CommandContext("help version", {"command": "version"})
        result = await cmd.execute(ctx)
        assert result.success


class TestDebugCommand:
    """Test /debug command."""

    @pytest.mark.asyncio
    async def test_debug_on(self):
        """Test enabling debug."""
        cmd = DebugCommand()
        ctx = CommandContext("debug on", {"state": "on"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_debug_off(self):
        """Test disabling debug."""
        cmd = DebugCommand()
        ctx = CommandContext("debug off", {"state": "off"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_debug_status(self):
        """Test debug status."""
        cmd = DebugCommand()
        ctx = CommandContext("debug", {})
        result = await cmd.execute(ctx)
        assert result.success


class TestLogsDebugCommand:
    """Test /debug logs command."""

    @pytest.mark.asyncio
    async def test_logs_default(self):
        """Test getting default logs."""
        cmd = LogsDebugCommand()
        ctx = CommandContext("debug logs", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_logs_with_lines(self):
        """Test getting specific number of logs."""
        cmd = LogsDebugCommand()
        ctx = CommandContext("debug logs --lines 10", {"lines": "10"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_logs_with_level(self):
        """Test logs with specific level."""
        cmd = LogsDebugCommand()
        ctx = CommandContext("debug logs --level ERROR", {"level": "ERROR"})
        result = await cmd.execute(ctx)
        assert result.success


class TestBenchmarkCommand:
    """Test /benchmark command."""

    @pytest.mark.asyncio
    async def test_benchmark_default(self):
        """Test default benchmark."""
        cmd = BenchmarkCommand()
        ctx = CommandContext("benchmark", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_benchmark_with_test(self):
        """Test benchmark with specific test."""
        cmd = BenchmarkCommand()
        ctx = CommandContext("benchmark --test memory", {"test": "memory"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_benchmark_with_iterations(self):
        """Test benchmark with custom iterations."""
        cmd = BenchmarkCommand()
        ctx = CommandContext("benchmark --iterations 50", {"iterations": "50"})
        result = await cmd.execute(ctx)
        assert result.success


class TestProfileCommand:
    """Test /profile command."""

    @pytest.mark.asyncio
    async def test_profile_default(self):
        """Test default profiling."""
        cmd = ProfileCommand()
        ctx = CommandContext("profile", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_profile_custom_duration(self):
        """Test profiling with custom duration."""
        cmd = ProfileCommand()
        ctx = CommandContext("profile --duration 30", {"duration": "30"})
        result = await cmd.execute(ctx)
        assert result.success


class TestReportCommand:
    """Test /report command."""

    @pytest.mark.asyncio
    async def test_report_default(self):
        """Test default report."""
        cmd = ReportCommand()
        ctx = CommandContext("report", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_report_detailed(self):
        """Test detailed report."""
        cmd = ReportCommand()
        ctx = CommandContext("report --type detailed", {"type": "detailed"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_report_format(self):
        """Test report with specific format."""
        cmd = ReportCommand()
        ctx = CommandContext("report --format json", {"format": "json"})
        result = await cmd.execute(ctx)
        assert result.success


class TestIssueCommand:
    """Test /report issue command."""

    @pytest.mark.asyncio
    async def test_report_issue(self):
        """Test reporting an issue."""
        cmd = IssueCommand()
        ctx = CommandContext("report issue", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_report_issue_with_title(self):
        """Test reporting issue with title."""
        cmd = IssueCommand()
        ctx = CommandContext("report issue --title Bug", {"title": "Bug"})
        result = await cmd.execute(ctx)
        assert result.success


class TestUIThemeCommand:
    """Test /ui theme command."""

    @pytest.mark.asyncio
    async def test_theme_light(self):
        """Test setting light theme."""
        cmd = UIThemeCommand()
        ctx = CommandContext("ui theme --name light", {"name": "light"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_theme_dark(self):
        """Test setting dark theme."""
        cmd = UIThemeCommand()
        ctx = CommandContext("ui theme --name dark", {"name": "dark"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_theme_invalid(self):
        """Test setting invalid theme."""
        cmd = UIThemeCommand()
        ctx = CommandContext("ui theme --name invalid", {"name": "invalid"})
        result = await cmd.execute(ctx)
        assert not result.success


class TestUIModeCommand:
    """Test /ui mode command."""

    @pytest.mark.asyncio
    async def test_mode_simple(self):
        """Test setting simple mode."""
        cmd = UIModeCommand()
        ctx = CommandContext("ui mode --name simple", {"name": "simple"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_mode_advanced(self):
        """Test setting advanced mode."""
        cmd = UIModeCommand()
        ctx = CommandContext("ui mode --name advanced", {"name": "advanced"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_mode_expert(self):
        """Test setting expert mode."""
        cmd = UIModeCommand()
        ctx = CommandContext("ui mode --name expert", {"name": "expert"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_mode_invalid(self):
        """Test setting invalid mode."""
        cmd = UIModeCommand()
        ctx = CommandContext("ui mode --name invalid", {"name": "invalid"})
        result = await cmd.execute(ctx)
        assert not result.success


class TestPluginListCommand:
    """Test /plugin list command."""

    @pytest.mark.asyncio
    async def test_list_all_plugins(self):
        """Test listing all plugins."""
        cmd = PluginListCommand()
        ctx = CommandContext("plugin list", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_enabled_plugins(self):
        """Test listing only enabled plugins."""
        cmd = PluginListCommand()
        ctx = CommandContext("plugin list --enabled", {"enabled": True})
        result = await cmd.execute(ctx)
        assert result.success


class TestPluginInstallCommand:
    """Test /plugin install command."""

    @pytest.mark.asyncio
    async def test_install_plugin(self):
        """Test installing a plugin."""
        cmd = PluginInstallCommand()
        ctx = CommandContext("plugin install myplugin", {"name": "myplugin"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_install_plugin_with_version(self):
        """Test installing plugin with version."""
        cmd = PluginInstallCommand()
        ctx = CommandContext("plugin install myplugin --version 2.0", {"name": "myplugin", "version": "2.0"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_install_missing_name(self):
        """Test install without plugin name."""
        cmd = PluginInstallCommand()
        ctx = CommandContext("plugin install", {})
        result = await cmd.execute(ctx)
        assert not result.success
