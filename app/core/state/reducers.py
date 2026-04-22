"""Reducers for state management."""

from typing import Any, Dict, Optional
from dataclasses import dataclass, replace, asdict
from copy import deepcopy
from .store import Action
from .actions import (
    UIActionType, SessionActionType, PermissionActionType, WorkspaceActionType
)


@dataclass
class UIState:
    """UI state."""
    visible_panels: Dict[str, bool] = None
    panel_states: Dict[str, Dict] = None
    active_tab: Optional[str] = None
    theme: str = "light"
    loading: bool = False
    loading_message: Optional[str] = None
    notifications: list = None
    sidebar_collapsed: bool = False
    
    def __post_init__(self):
        if self.visible_panels is None:
            self.visible_panels = {}
        if self.panel_states is None:
            self.panel_states = {}
        if self.notifications is None:
            self.notifications = []


@dataclass
class Session:
    """Session data."""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    config: Dict[str, Any] = None
    tools: Dict[str, Dict] = None
    started_at: Optional[float] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.tools is None:
            self.tools = {}


@dataclass
class PermissionState:
    """Permission state."""
    user_roles: Dict[str, str] = None
    user_permissions: Dict[str, set] = None
    resource_permissions: Dict[str, Dict] = None
    audit_log: list = None
    
    def __post_init__(self):
        if self.user_roles is None:
            self.user_roles = {}
        if self.user_permissions is None:
            self.user_permissions = {}
        if self.resource_permissions is None:
            self.resource_permissions = {}
        if self.audit_log is None:
            self.audit_log = []


@dataclass
class WorkspaceState:
    """Workspace state."""
    config: Dict[str, Any] = None
    files: Dict[str, str] = None
    current_project: Optional[str] = None
    project_name: Optional[str] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.files is None:
            self.files = {}


def ui_reducer(state: Optional[UIState], action: Action) -> UIState:
    """UI reducer."""
    if state is None:
        state = UIState()
    
    if action.type == UIActionType.SHOW_PANEL:
        new_state = deepcopy(state)
        panel_name = action.payload.get("panel")
        data = action.payload.get("data", {})
        new_state.visible_panels[panel_name] = True
        new_state.panel_states[panel_name] = data
        return new_state
    
    elif action.type == UIActionType.HIDE_PANEL:
        new_state = deepcopy(state)
        panel_name = action.payload.get("panel")
        new_state.visible_panels[panel_name] = False
        return new_state
    
    elif action.type == UIActionType.UPDATE_PANEL_STATE:
        new_state = deepcopy(state)
        panel_name = action.payload.get("panel")
        panel_state = action.payload.get("state", {})
        if panel_name in new_state.panel_states:
            new_state.panel_states[panel_name].update(panel_state)
        else:
            new_state.panel_states[panel_name] = panel_state
        return new_state
    
    elif action.type == UIActionType.SET_ACTIVE_TAB:
        new_state = deepcopy(state)
        new_state.active_tab = action.payload.get("tab")
        return new_state
    
    elif action.type == UIActionType.SET_THEME:
        new_state = deepcopy(state)
        new_state.theme = action.payload.get("theme", "light")
        return new_state
    
    elif action.type == UIActionType.SET_LOADING:
        new_state = deepcopy(state)
        new_state.loading = action.payload.get("loading", False)
        new_state.loading_message = action.payload.get("message")
        return new_state
    
    elif action.type == UIActionType.SHOW_NOTIFICATION:
        new_state = deepcopy(state)
        notification = {
            "title": action.payload.get("title"),
            "message": action.payload.get("message"),
            "type": action.payload.get("type", "info"),
            "timestamp": action.timestamp
        }
        new_state.notifications.append(notification)
        if len(new_state.notifications) > 50:
            new_state.notifications.pop(0)
        return new_state
    
    elif action.type == UIActionType.HIDE_NOTIFICATION:
        new_state = deepcopy(state)
        new_state.notifications.pop(0)
        return new_state
    
    elif action.type == UIActionType.SET_SIDEBAR_COLLAPSED:
        new_state = deepcopy(state)
        new_state.sidebar_collapsed = action.payload.get("collapsed", False)
        return new_state
    
    return state


def session_reducer(state: Optional[Session], action: Action) -> Session:
    """Session reducer."""
    if state is None:
        state = Session()
    
    if action.type == SessionActionType.START_SESSION:
        new_state = deepcopy(state)
        new_state.session_id = action.payload.get("session_id")
        new_state.user_id = action.payload.get("user_id")
        new_state.config = action.payload.get("config", {})
        new_state.started_at = action.timestamp
        return new_state
    
    elif action.type == SessionActionType.END_SESSION:
        return Session()
    
    elif action.type == SessionActionType.UPDATE_SESSION_CONFIG:
        new_state = deepcopy(state)
        config_update = action.payload.get("config", {})
        new_state.config.update(config_update)
        return new_state
    
    elif action.type == SessionActionType.SET_CURRENT_USER:
        new_state = deepcopy(state)
        new_state.user_id = action.payload.get("user_id")
        new_state.username = action.payload.get("username")
        new_state.role = action.payload.get("role")
        return new_state
    
    elif action.type == SessionActionType.ADD_TOOL:
        new_state = deepcopy(state)
        tool_name = action.payload.get("tool_name")
        tool_config = action.payload.get("config", {})
        new_state.tools[tool_name] = tool_config
        return new_state
    
    elif action.type == SessionActionType.REMOVE_TOOL:
        new_state = deepcopy(state)
        tool_name = action.payload.get("tool_name")
        if tool_name in new_state.tools:
            del new_state.tools[tool_name]
        return new_state
    
    return state


def permission_reducer(state: Optional[PermissionState], action: Action) -> PermissionState:
    """Permission reducer."""
    if state is None:
        state = PermissionState()
    
    if action.type == PermissionActionType.GRANT_PERMISSION:
        new_state = deepcopy(state)
        user_id = action.payload.get("user_id")
        permission = action.payload.get("permission")
        if user_id not in new_state.user_permissions:
            new_state.user_permissions[user_id] = set()
        new_state.user_permissions[user_id].add(permission)
        return new_state
    
    elif action.type == PermissionActionType.REVOKE_PERMISSION:
        new_state = deepcopy(state)
        user_id = action.payload.get("user_id")
        permission = action.payload.get("permission")
        if user_id in new_state.user_permissions:
            new_state.user_permissions[user_id].discard(permission)
        return new_state
    
    elif action.type == PermissionActionType.ASSIGN_ROLE:
        new_state = deepcopy(state)
        user_id = action.payload.get("user_id")
        role = action.payload.get("role")
        new_state.user_roles[user_id] = role
        return new_state
    
    elif action.type == PermissionActionType.AUDIT_EVENT:
        new_state = deepcopy(state)
        event = {
            "type": action.payload.get("event_type"),
            "details": action.payload.get("details"),
            "timestamp": action.timestamp
        }
        new_state.audit_log.append(event)
        if len(new_state.audit_log) > 10000:
            new_state.audit_log.pop(0)
        return new_state
    
    return state


def workspace_reducer(state: Optional[WorkspaceState], action: Action) -> WorkspaceState:
    """Workspace reducer."""
    if state is None:
        state = WorkspaceState()
    
    if action.type == WorkspaceActionType.LOAD_CONFIG:
        new_state = deepcopy(state)
        new_state.config = action.payload.get("config", {})
        return new_state
    
    elif action.type == WorkspaceActionType.UPDATE_CONFIG:
        new_state = deepcopy(state)
        config_update = action.payload.get("config", {})
        new_state.config.update(config_update)
        return new_state
    
    elif action.type == WorkspaceActionType.ADD_FILE:
        new_state = deepcopy(state)
        file_path = action.payload.get("file_path")
        content = action.payload.get("content")
        new_state.files[file_path] = content
        return new_state
    
    elif action.type == WorkspaceActionType.DELETE_FILE:
        new_state = deepcopy(state)
        file_path = action.payload.get("file_path")
        if file_path in new_state.files:
            del new_state.files[file_path]
        return new_state
    
    elif action.type == WorkspaceActionType.UPDATE_FILE:
        new_state = deepcopy(state)
        file_path = action.payload.get("file_path")
        content = action.payload.get("content")
        if file_path in new_state.files:
            new_state.files[file_path] = content
        return new_state
    
    elif action.type == WorkspaceActionType.SET_CURRENT_PROJECT:
        new_state = deepcopy(state)
        new_state.current_project = action.payload.get("project_id")
        new_state.project_name = action.payload.get("project_name")
        return new_state
    
    return state


# Root reducer combining all
def root_reducer(state: Optional[Dict[str, Any]], action: Action) -> Dict[str, Any]:
    """Root reducer."""
    if state is None:
        state = {
            "ui": UIState(),
            "session": Session(),
            "permissions": PermissionState(),
            "workspace": WorkspaceState()
        }
    
    return {
        "ui": ui_reducer(state.get("ui"), action),
        "session": session_reducer(state.get("session"), action),
        "permissions": permission_reducer(state.get("permissions"), action),
        "workspace": workspace_reducer(state.get("workspace"), action),
    }
