"""Action creators for state management."""

from typing import Any, Dict, Optional
from enum import Enum
from .store import Action, ActionType
import json


class UIActionType(str, Enum):
    """UI-related action types."""
    SHOW_PANEL = "ui/SHOW_PANEL"
    HIDE_PANEL = "ui/HIDE_PANEL"
    UPDATE_PANEL_STATE = "ui/UPDATE_PANEL_STATE"
    SET_ACTIVE_TAB = "ui/SET_ACTIVE_TAB"
    SET_THEME = "ui/SET_THEME"
    SET_LOADING = "ui/SET_LOADING"
    SHOW_NOTIFICATION = "ui/SHOW_NOTIFICATION"
    HIDE_NOTIFICATION = "ui/HIDE_NOTIFICATION"
    SET_SIDEBAR_COLLAPSED = "ui/SET_SIDEBAR_COLLAPSED"


class SessionActionType(str, Enum):
    """Session-related action types."""
    START_SESSION = "session/START_SESSION"
    END_SESSION = "session/END_SESSION"
    UPDATE_SESSION_CONFIG = "session/UPDATE_SESSION_CONFIG"
    SET_CURRENT_USER = "session/SET_CURRENT_USER"
    ADD_TOOL = "session/ADD_TOOL"
    REMOVE_TOOL = "session/REMOVE_TOOL"


class PermissionActionType(str, Enum):
    """Permission-related action types."""
    GRANT_PERMISSION = "permission/GRANT_PERMISSION"
    REVOKE_PERMISSION = "permission/REVOKE_PERMISSION"
    UPDATE_ROLE = "permission/UPDATE_ROLE"
    AUDIT_EVENT = "permission/AUDIT_EVENT"
    ASSIGN_ROLE = "permission/ASSIGN_ROLE"


class WorkspaceActionType(str, Enum):
    """Workspace-related action types."""
    LOAD_CONFIG = "workspace/LOAD_CONFIG"
    UPDATE_CONFIG = "workspace/UPDATE_CONFIG"
    ADD_FILE = "workspace/ADD_FILE"
    DELETE_FILE = "workspace/DELETE_FILE"
    UPDATE_FILE = "workspace/UPDATE_FILE"
    SET_CURRENT_PROJECT = "workspace/SET_CURRENT_PROJECT"


class NotificationType(str, Enum):
    """Notification types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# UI Action Creators
def show_panel(panel_name: str, data: Optional[Dict] = None) -> Action:
    """Show a panel."""
    return Action(
        type=UIActionType.SHOW_PANEL,
        payload={"panel": panel_name, "data": data or {}},
        meta={"async": False}
    )


def hide_panel(panel_name: str) -> Action:
    """Hide a panel."""
    return Action(
        type=UIActionType.HIDE_PANEL,
        payload={"panel": panel_name},
        meta={"async": False}
    )


def update_panel_state(panel_name: str, state: Dict) -> Action:
    """Update panel state."""
    return Action(
        type=UIActionType.UPDATE_PANEL_STATE,
        payload={"panel": panel_name, "state": state},
        meta={"async": False}
    )


def set_active_tab(tab_name: str) -> Action:
    """Set active tab."""
    return Action(
        type=UIActionType.SET_ACTIVE_TAB,
        payload={"tab": tab_name},
        meta={"async": False}
    )


def set_theme(theme_name: str) -> Action:
    """Set theme."""
    return Action(
        type=UIActionType.SET_THEME,
        payload={"theme": theme_name},
        meta={"async": False}
    )


def set_loading(is_loading: bool, message: Optional[str] = None) -> Action:
    """Set loading state."""
    return Action(
        type=UIActionType.SET_LOADING,
        payload={"loading": is_loading, "message": message},
        meta={"async": False}
    )


def show_notification(title: str, message: str, notification_type: NotificationType = NotificationType.INFO) -> Action:
    """Show notification."""
    return Action(
        type=UIActionType.SHOW_NOTIFICATION,
        payload={
            "title": title,
            "message": message,
            "type": notification_type.value,
            "timestamp": None
        },
        meta={"async": False}
    )


def set_sidebar_collapsed(collapsed: bool) -> Action:
    """Set sidebar collapsed state."""
    return Action(
        type=UIActionType.SET_SIDEBAR_COLLAPSED,
        payload={"collapsed": collapsed},
        meta={"async": False}
    )


# Session Action Creators
def start_session(session_id: str, user_id: str, config: Dict[str, Any]) -> Action:
    """Start session."""
    return Action(
        type=SessionActionType.START_SESSION,
        payload={
            "session_id": session_id,
            "user_id": user_id,
            "config": config
        },
        meta={"async": True}
    )


def end_session(session_id: str, reason: Optional[str] = None) -> Action:
    """End session."""
    return Action(
        type=SessionActionType.END_SESSION,
        payload={
            "session_id": session_id,
            "reason": reason
        },
        meta={"async": True}
    )


def update_session_config(session_id: str, config: Dict[str, Any]) -> Action:
    """Update session config."""
    return Action(
        type=SessionActionType.UPDATE_SESSION_CONFIG,
        payload={
            "session_id": session_id,
            "config": config
        },
        meta={"async": False}
    )


def set_current_user(user_id: str, username: str, role: str) -> Action:
    """Set current user."""
    return Action(
        type=SessionActionType.SET_CURRENT_USER,
        payload={
            "user_id": user_id,
            "username": username,
            "role": role
        },
        meta={"async": False}
    )


def add_tool(tool_name: str, tool_config: Dict[str, Any]) -> Action:
    """Add tool to session."""
    return Action(
        type=SessionActionType.ADD_TOOL,
        payload={
            "tool_name": tool_name,
            "config": tool_config
        },
        meta={"async": False}
    )


def remove_tool(tool_name: str) -> Action:
    """Remove tool from session."""
    return Action(
        type=SessionActionType.REMOVE_TOOL,
        payload={"tool_name": tool_name},
        meta={"async": False}
    )


# Permission Action Creators
def grant_permission(user_id: str, permission: str, resource_id: Optional[str] = None) -> Action:
    """Grant permission."""
    return Action(
        type=PermissionActionType.GRANT_PERMISSION,
        payload={
            "user_id": user_id,
            "permission": permission,
            "resource_id": resource_id
        },
        meta={"async": True}
    )


def revoke_permission(user_id: str, permission: str, resource_id: Optional[str] = None) -> Action:
    """Revoke permission."""
    return Action(
        type=PermissionActionType.REVOKE_PERMISSION,
        payload={
            "user_id": user_id,
            "permission": permission,
            "resource_id": resource_id
        },
        meta={"async": True}
    )


def audit_event(event_type: str, details: Dict[str, Any]) -> Action:
    """Log audit event."""
    return Action(
        type=PermissionActionType.AUDIT_EVENT,
        payload={
            "event_type": event_type,
            "details": details
        },
        meta={"async": False}
    )


def assign_role(user_id: str, role: str) -> Action:
    """Assign role to user."""
    return Action(
        type=PermissionActionType.ASSIGN_ROLE,
        payload={
            "user_id": user_id,
            "role": role
        },
        meta={"async": True}
    )


# Workspace Action Creators
def load_config(config_path: str) -> Action:
    """Load workspace config."""
    return Action(
        type=WorkspaceActionType.LOAD_CONFIG,
        payload={"config_path": config_path},
        meta={"async": True}
    )


def update_config(config: Dict[str, Any]) -> Action:
    """Update workspace config."""
    return Action(
        type=WorkspaceActionType.UPDATE_CONFIG,
        payload={"config": config},
        meta={"async": True}
    )


def add_file(file_path: str, content: str) -> Action:
    """Add file to workspace."""
    return Action(
        type=WorkspaceActionType.ADD_FILE,
        payload={
            "file_path": file_path,
            "content": content
        },
        meta={"async": True}
    )


def delete_file(file_path: str) -> Action:
    """Delete file from workspace."""
    return Action(
        type=WorkspaceActionType.DELETE_FILE,
        payload={"file_path": file_path},
        meta={"async": True}
    )


def update_file(file_path: str, content: str) -> Action:
    """Update file in workspace."""
    return Action(
        type=WorkspaceActionType.UPDATE_FILE,
        payload={
            "file_path": file_path,
            "content": content
        },
        meta={"async": True}
    )


def set_current_project(project_id: str, project_name: str) -> Action:
    """Set current project."""
    return Action(
        type=WorkspaceActionType.SET_CURRENT_PROJECT,
        payload={
            "project_id": project_id,
            "project_name": project_name
        },
        meta={"async": False}
    )
