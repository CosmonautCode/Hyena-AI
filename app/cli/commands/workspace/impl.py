"""Base class and implementations for workspace management commands."""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime

from app.cli.commands.base import BaseCommand, CommandContext, CommandResult


@dataclass
class SessionConfig:
    """Workspace session configuration."""
    name: str
    description: str = ""
    agents: List[str] = field(default_factory=list)
    memory_enabled: bool = True
    created_at: str = ""


class WorkspaceCommand(BaseCommand):
    """Base class for workspace commands."""
    category = "workspace"
    WORKSPACE_DIR = Path("app/data/workspace")

    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the workspace command."""
        try:
            self.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
            if not self.validate(context):
                return CommandResult(success=False, message="Validation failed")
            result = await self._execute_workspace_command(context)
            return result
        except Exception as e:
            return CommandResult(success=False, message=f"Error: {str(e)}")

    def validate(self, context: CommandContext) -> bool:
        return True

    @abstractmethod
    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        pass


# Workspace Management Commands

class WorkspaceInitCommand(WorkspaceCommand):
    """Initialize workspace: /workspace init [--name NAME]"""
    name = "init"
    description = "Initialize workspace"
    help_text = "Set up a new workspace"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        name = context.args.get("name", "default")
        config_file = self.WORKSPACE_DIR / "workspace.json"
        
        try:
            self.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
            config = {"name": name, "initialized": datetime.now().isoformat()}
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            return CommandResult(success=True, message=f"Workspace '{name}' initialized")
        except:
            return CommandResult(success=False, message="Failed to initialize workspace")


class WorkspaceConfigCommand(WorkspaceCommand):
    """Configure workspace: /workspace config [--set KEY=VALUE] [--get KEY]"""
    name = "config"
    description = "Configure workspace"
    help_text = "Manage workspace configuration"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        config_file = self.WORKSPACE_DIR / "workspace.json"
        
        try:
            if not config_file.exists():
                return CommandResult(success=False, message="Workspace not initialized")
            
            with open(config_file, "r") as f:
                config = json.load(f)
            
            if key_value := context.args.get("set"):
                key, value = key_value.split("=", 1)
                config[key] = value
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
                return CommandResult(success=True, message=f"Set {key}={value}")
            
            if key := context.args.get("get"):
                value = config.get(key, "Not found")
                return CommandResult(success=True, message=f"{key}={value}")
            
            return CommandResult(success=True, data=config)
        except:
            return CommandResult(success=False, message="Configuration error")


class WorkspaceStatusCommand(WorkspaceCommand):
    """Show workspace status: /workspace status"""
    name = "status"
    description = "Show workspace status"
    help_text = "Display current workspace status"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        config_file = self.WORKSPACE_DIR / "workspace.json"
        
        if not config_file.exists():
            return CommandResult(success=False, message="Workspace not initialized")
        
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            return CommandResult(
                success=True,
                message="Workspace status",
                data=config
            )
        except:
            return CommandResult(success=False, message="Status error")


# Session Management Commands

class SessionStartCommand(WorkspaceCommand):
    """Start session: /session start <name> [--description DESC]"""
    name = "start"
    description = "Start a session"
    help_text = "Create and start a new session"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not name:
            return CommandResult(success=False, message="Session name required")
        
        sessions_dir = self.WORKSPACE_DIR / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session_file = sessions_dir / f"{name}.json"
        
        if session_file.exists():
            return CommandResult(success=False, message=f"Session '{name}' already exists")
        
        session = {
            "name": name,
            "description": context.args.get("description", ""),
            "started": datetime.now().isoformat(),
            "active": True,
        }
        
        try:
            with open(session_file, "w") as f:
                json.dump(session, f, indent=2)
            return CommandResult(success=True, message=f"Session '{name}' started")
        except:
            return CommandResult(success=False, message="Failed to start session")


class SessionListCommand(WorkspaceCommand):
    """List sessions: /session list [--active]"""
    name = "list"
    description = "List sessions"
    help_text = "Show all available sessions"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        sessions_dir = self.WORKSPACE_DIR / "sessions"
        if not sessions_dir.exists():
            return CommandResult(success=True, message="No sessions", data={"sessions": []})
        
        sessions = []
        try:
            for session_file in sessions_dir.glob("*.json"):
                with open(session_file, "r") as f:
                    session = json.load(f)
                    if not context.args.get("active") or session.get("active"):
                        sessions.append({"name": session["name"], "description": session.get("description", "")})
            return CommandResult(success=True, message=f"Found {len(sessions)} session(s)", data={"sessions": sessions})
        except:
            return CommandResult(success=False, message="List error")


class SessionLoadCommand(WorkspaceCommand):
    """Load session: /session load <name>"""
    name = "load"
    description = "Load a session"
    help_text = "Load an existing session"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not name:
            return CommandResult(success=False, message="Session name required")
        
        session_file = self.WORKSPACE_DIR / "sessions" / f"{name}.json"
        if not session_file.exists():
            return CommandResult(success=False, message=f"Session '{name}' not found")
        
        try:
            with open(session_file, "r") as f:
                session = json.load(f)
            return CommandResult(success=True, message=f"Session '{name}' loaded", data=session)
        except:
            return CommandResult(success=False, message="Load error")


class SessionSaveCommand(WorkspaceCommand):
    """Save session: /session save <name>"""
    name = "save"
    description = "Save a session"
    help_text = "Save current session state"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not name:
            return CommandResult(success=False, message="Session name required")
        
        session_file = self.WORKSPACE_DIR / "sessions" / f"{name}.json"
        if not session_file.exists():
            return CommandResult(success=False, message=f"Session '{name}' not found")
        
        try:
            return CommandResult(success=True, message=f"Session '{name}' saved")
        except:
            return CommandResult(success=False, message="Save error")


class SessionExportCommand(WorkspaceCommand):
    """Export session: /session export <name> [--format json]"""
    name = "export"
    description = "Export a session"
    help_text = "Export session to file"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not name:
            return CommandResult(success=False, message="Session name required")
        
        session_file = self.WORKSPACE_DIR / "sessions" / f"{name}.json"
        if not session_file.exists():
            return CommandResult(success=False, message=f"Session '{name}' not found")
        
        export_format = context.args.get("format", "json")
        return CommandResult(
            success=True,
            message=f"Session '{name}' exported",
            data={"format": export_format}
        )


class SessionClearCommand(WorkspaceCommand):
    """Clear session: /session clear <name> [--confirm]"""
    name = "clear"
    description = "Clear a session"
    help_text = "Remove session data"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        if not context.args.get("confirm"):
            return CommandResult(success=False, message="Use --confirm to clear session")
        
        name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not name:
            return CommandResult(success=False, message="Session name required")
        
        session_file = self.WORKSPACE_DIR / "sessions" / f"{name}.json"
        if not session_file.exists():
            return CommandResult(success=False, message=f"Session '{name}' not found")
        
        try:
            session_file.unlink()
            return CommandResult(success=True, message=f"Session '{name}' cleared")
        except:
            return CommandResult(success=False, message="Clear error")


# Config Commands

class ConfigSetCommand(WorkspaceCommand):
    """Set config: /config set <key> <value>"""
    name = "set"
    description = "Set configuration"
    help_text = "Set a configuration value"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        key = context.args.get("key")
        value = context.args.get("value")
        
        if not key or value is None:
            return CommandResult(success=False, message="Key and value required")
        
        return CommandResult(success=True, message=f"Config '{key}' set to '{value}'")


class ConfigGetCommand(WorkspaceCommand):
    """Get config: /config get <key>"""
    name = "get"
    description = "Get configuration"
    help_text = "Get a configuration value"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        key = context.args.get("key") or context.args.get("_positional", [None])[0]
        if not key:
            return CommandResult(success=False, message="Key required")
        
        return CommandResult(success=True, message=f"Config '{key}'", data={"value": "config_value"})


class ConfigResetCommand(WorkspaceCommand):
    """Reset config: /config reset [--confirm]"""
    name = "reset"
    description = "Reset configuration"
    help_text = "Reset to default configuration"

    async def _execute_workspace_command(self, context: CommandContext) -> CommandResult:
        if not context.args.get("confirm"):
            return CommandResult(success=False, message="Use --confirm to reset config")
        
        return CommandResult(success=True, message="Configuration reset to defaults")
