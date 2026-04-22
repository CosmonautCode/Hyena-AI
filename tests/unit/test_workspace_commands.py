"""Tests for workspace management commands."""

import pytest
import shutil
from pathlib import Path

from app.cli.commands.workspace import (
    WorkspaceInitCommand,
    WorkspaceConfigCommand,
    WorkspaceStatusCommand,
    SessionStartCommand,
    SessionListCommand,
    SessionLoadCommand,
    SessionSaveCommand,
    SessionExportCommand,
    SessionClearCommand,
    ConfigSetCommand,
    ConfigGetCommand,
    ConfigResetCommand,
)
from app.cli.commands.base import CommandContext


@pytest.fixture(autouse=True)
def cleanup_workspace():
    """Clean up workspace directory."""
    ws_dir = Path("app/data/workspace")
    try:
        if ws_dir.exists():
            shutil.rmtree(ws_dir)
    except:
        pass
    yield
    try:
        if ws_dir.exists():
            shutil.rmtree(ws_dir)
    except:
        pass


# Workspace Commands Tests

class TestWorkspaceInitCommand:
    """Test /workspace init command."""

    @pytest.mark.asyncio
    async def test_init_default(self):
        """Test initializing with default name."""
        cmd = WorkspaceInitCommand()
        ctx = CommandContext("workspace init", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_init_custom_name(self):
        """Test initializing with custom name."""
        cmd = WorkspaceInitCommand()
        ctx = CommandContext("workspace init --name myworkspace", {"name": "myworkspace"})
        result = await cmd.execute(ctx)
        assert result.success


class TestWorkspaceConfigCommand:
    """Test /workspace config command."""

    @pytest.mark.asyncio
    async def test_config_before_init(self):
        """Test config before workspace initialization."""
        cmd = WorkspaceConfigCommand()
        ctx = CommandContext("workspace config", {})
        result = await cmd.execute(ctx)
        assert not result.success

    @pytest.mark.asyncio
    async def test_config_set_after_init(self):
        """Test setting config after init."""
        init_cmd = WorkspaceInitCommand()
        config_cmd = WorkspaceConfigCommand()
        
        await init_cmd.execute(CommandContext("workspace init", {}))
        
        ctx = CommandContext("workspace config --set key=value", {"set": "key=value"})
        result = await config_cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_config_get(self):
        """Test getting config value."""
        init_cmd = WorkspaceInitCommand()
        config_cmd = WorkspaceConfigCommand()
        
        await init_cmd.execute(CommandContext("workspace init", {}))
        
        ctx = CommandContext("workspace config --get name", {"get": "name"})
        result = await config_cmd.execute(ctx)
        assert result.success


class TestWorkspaceStatusCommand:
    """Test /workspace status command."""

    @pytest.mark.asyncio
    async def test_status_before_init(self):
        """Test status before initialization."""
        cmd = WorkspaceStatusCommand()
        ctx = CommandContext("workspace status", {})
        result = await cmd.execute(ctx)
        assert not result.success

    @pytest.mark.asyncio
    async def test_status_after_init(self):
        """Test status after initialization."""
        init_cmd = WorkspaceInitCommand()
        status_cmd = WorkspaceStatusCommand()
        
        await init_cmd.execute(CommandContext("workspace init", {}))
        
        ctx = CommandContext("workspace status", {})
        result = await status_cmd.execute(ctx)
        assert result.success


# Session Commands Tests

class TestSessionStartCommand:
    """Test /session start command."""

    @pytest.mark.asyncio
    async def test_start_session(self):
        """Test starting a session."""
        cmd = SessionStartCommand()
        ctx = CommandContext("session start test_session", {"name": "test_session"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_start_duplicate_session(self):
        """Test starting duplicate session."""
        cmd = SessionStartCommand()
        
        await cmd.execute(CommandContext("session start test", {"name": "test"}))
        result = await cmd.execute(CommandContext("session start test", {"name": "test"}))
        assert not result.success

    @pytest.mark.asyncio
    async def test_start_missing_name(self):
        """Test starting without name."""
        cmd = SessionStartCommand()
        ctx = CommandContext("session start", {})
        result = await cmd.execute(ctx)
        assert not result.success


class TestSessionListCommand:
    """Test /session list command."""

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """Test listing when no sessions."""
        cmd = SessionListCommand()
        ctx = CommandContext("session list", {})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_multiple(self):
        """Test listing multiple sessions."""
        start_cmd = SessionStartCommand()
        list_cmd = SessionListCommand()
        
        for i in range(3):
            await start_cmd.execute(CommandContext(f"session start s{i}", {"name": f"s{i}"}))
        
        ctx = CommandContext("session list", {})
        result = await list_cmd.execute(ctx)
        assert result.success


class TestSessionLoadCommand:
    """Test /session load command."""

    @pytest.mark.asyncio
    async def test_load_existing(self):
        """Test loading existing session."""
        start_cmd = SessionStartCommand()
        load_cmd = SessionLoadCommand()
        
        await start_cmd.execute(CommandContext("session start test", {"name": "test"}))
        
        ctx = CommandContext("session load test", {"name": "test"})
        result = await load_cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_load_nonexistent(self):
        """Test loading nonexistent session."""
        cmd = SessionLoadCommand()
        ctx = CommandContext("session load nonexistent", {"name": "nonexistent"})
        result = await cmd.execute(ctx)
        assert not result.success


class TestSessionSaveCommand:
    """Test /session save command."""

    @pytest.mark.asyncio
    async def test_save_existing(self):
        """Test saving existing session."""
        start_cmd = SessionStartCommand()
        save_cmd = SessionSaveCommand()
        
        await start_cmd.execute(CommandContext("session start test", {"name": "test"}))
        
        ctx = CommandContext("session save test", {"name": "test"})
        result = await save_cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_save_nonexistent(self):
        """Test saving nonexistent session."""
        cmd = SessionSaveCommand()
        ctx = CommandContext("session save nonexistent", {"name": "nonexistent"})
        result = await cmd.execute(ctx)
        assert not result.success


class TestSessionExportCommand:
    """Test /session export command."""

    @pytest.mark.asyncio
    async def test_export_existing(self):
        """Test exporting existing session."""
        start_cmd = SessionStartCommand()
        export_cmd = SessionExportCommand()
        
        await start_cmd.execute(CommandContext("session start test", {"name": "test"}))
        
        ctx = CommandContext("session export test", {"name": "test"})
        result = await export_cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_export_nonexistent(self):
        """Test exporting nonexistent session."""
        cmd = SessionExportCommand()
        ctx = CommandContext("session export nonexistent", {"name": "nonexistent"})
        result = await cmd.execute(ctx)
        assert not result.success


class TestSessionClearCommand:
    """Test /session clear command."""

    @pytest.mark.asyncio
    async def test_clear_without_confirm(self):
        """Test clear without confirmation."""
        cmd = SessionClearCommand()
        ctx = CommandContext("session clear test", {"name": "test"})
        result = await cmd.execute(ctx)
        assert not result.success

    @pytest.mark.asyncio
    async def test_clear_with_confirm(self):
        """Test clear with confirmation."""
        start_cmd = SessionStartCommand()
        clear_cmd = SessionClearCommand()
        
        await start_cmd.execute(CommandContext("session start test", {"name": "test"}))
        
        ctx = CommandContext("session clear test --confirm", {"name": "test", "confirm": True})
        result = await clear_cmd.execute(ctx)
        assert result.success


# Config Commands Tests

class TestConfigSetCommand:
    """Test /config set command."""

    @pytest.mark.asyncio
    async def test_set_config(self):
        """Test setting a config value."""
        cmd = ConfigSetCommand()
        ctx = CommandContext("config set key value", {"key": "key", "value": "value"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_set_missing_key(self):
        """Test set without key."""
        cmd = ConfigSetCommand()
        ctx = CommandContext("config set", {})
        result = await cmd.execute(ctx)
        assert not result.success


class TestConfigGetCommand:
    """Test /config get command."""

    @pytest.mark.asyncio
    async def test_get_config(self):
        """Test getting a config value."""
        cmd = ConfigGetCommand()
        ctx = CommandContext("config get key", {"key": "key"})
        result = await cmd.execute(ctx)
        assert result.success

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        """Test get without key."""
        cmd = ConfigGetCommand()
        ctx = CommandContext("config get", {})
        result = await cmd.execute(ctx)
        assert not result.success


class TestConfigResetCommand:
    """Test /config reset command."""

    @pytest.mark.asyncio
    async def test_reset_without_confirm(self):
        """Test reset without confirmation."""
        cmd = ConfigResetCommand()
        ctx = CommandContext("config reset", {})
        result = await cmd.execute(ctx)
        assert not result.success

    @pytest.mark.asyncio
    async def test_reset_with_confirm(self):
        """Test reset with confirmation."""
        cmd = ConfigResetCommand()
        ctx = CommandContext("config reset --confirm", {"confirm": True})
        result = await cmd.execute(ctx)
        assert result.success
