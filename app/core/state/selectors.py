"""Selectors for state management - memoized state slices."""

from typing import Any, Dict, Callable, Optional
from functools import lru_cache


# UI Selectors
def select_visible_panels(state: Dict[str, Any]) -> Dict[str, bool]:
    """Select visible panels."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'visible_panels'):
        return ui_state.visible_panels
    return {}


def select_panel_state(state: Dict[str, Any], panel_name: str) -> Dict[str, Any]:
    """Select specific panel state."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'panel_states'):
        return ui_state.panel_states.get(panel_name, {})
    return {}


def select_active_tab(state: Dict[str, Any]) -> Optional[str]:
    """Select active tab."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'active_tab'):
        return ui_state.active_tab
    return None


def select_theme(state: Dict[str, Any]) -> str:
    """Select theme."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'theme'):
        return ui_state.theme
    return "light"


def select_loading_state(state: Dict[str, Any]) -> tuple:
    """Select loading state (is_loading, message)."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'loading'):
        return (ui_state.loading, ui_state.loading_message)
    return (False, None)


def select_notifications(state: Dict[str, Any]) -> list:
    """Select notifications."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'notifications'):
        return ui_state.notifications
    return []


def select_sidebar_collapsed(state: Dict[str, Any]) -> bool:
    """Select sidebar collapsed state."""
    ui_state = state.get("ui", {})
    if hasattr(ui_state, 'sidebar_collapsed'):
        return ui_state.sidebar_collapsed
    return False


# Session Selectors
def select_current_user(state: Dict[str, Any]) -> Optional[str]:
    """Select current user ID."""
    session = state.get("session", {})
    if hasattr(session, 'user_id'):
        return session.user_id
    return None


def select_current_username(state: Dict[str, Any]) -> Optional[str]:
    """Select current username."""
    session = state.get("session", {})
    if hasattr(session, 'username'):
        return session.username
    return None


def select_current_role(state: Dict[str, Any]) -> Optional[str]:
    """Select current user role."""
    session = state.get("session", {})
    if hasattr(session, 'role'):
        return session.role
    return None


def select_session_id(state: Dict[str, Any]) -> Optional[str]:
    """Select session ID."""
    session = state.get("session", {})
    if hasattr(session, 'session_id'):
        return session.session_id
    return None


def select_available_tools(state: Dict[str, Any]) -> Dict[str, Dict]:
    """Select available tools."""
    session = state.get("session", {})
    if hasattr(session, 'tools'):
        return session.tools
    return {}


def select_session_config(state: Dict[str, Any]) -> Dict[str, Any]:
    """Select session config."""
    session = state.get("session", {})
    if hasattr(session, 'config'):
        return session.config
    return {}


def select_is_authenticated(state: Dict[str, Any]) -> bool:
    """Check if user is authenticated."""
    return select_current_user(state) is not None


# Permission Selectors
def select_user_role(state: Dict[str, Any], user_id: str) -> Optional[str]:
    """Select user role."""
    perm_state = state.get("permissions", {})
    if hasattr(perm_state, 'user_roles'):
        return perm_state.user_roles.get(user_id)
    return None


def select_user_permissions(state: Dict[str, Any], user_id: str) -> set:
    """Select user permissions."""
    perm_state = state.get("permissions", {})
    if hasattr(perm_state, 'user_permissions'):
        return perm_state.user_permissions.get(user_id, set())
    return set()


def select_has_permission(state: Dict[str, Any], user_id: str, permission: str) -> bool:
    """Check if user has permission."""
    permissions = select_user_permissions(state, user_id)
    return permission in permissions


def select_audit_log(state: Dict[str, Any], limit: int = 100) -> list:
    """Select audit log."""
    perm_state = state.get("permissions", {})
    if hasattr(perm_state, 'audit_log'):
        return perm_state.audit_log[-limit:]
    return []


def select_user_actions(state: Dict[str, Any], user_id: str) -> list:
    """Select user actions from audit log."""
    audit_log = select_audit_log(state)
    user_actions = [
        event for event in audit_log
        if event.get("details", {}).get("user_id") == user_id
    ]
    return user_actions


def select_permission_stats(state: Dict[str, Any]) -> Dict[str, int]:
    """Select permission statistics."""
    perm_state = state.get("permissions", {})
    stats = {
        "total_roles": 0,
        "total_permissions": 0,
        "audit_events": 0
    }
    
    if hasattr(perm_state, 'user_roles'):
        stats["total_roles"] = len(perm_state.user_roles)
    
    if hasattr(perm_state, 'user_permissions'):
        total_perms = sum(len(p) for p in perm_state.user_permissions.values())
        stats["total_permissions"] = total_perms
    
    if hasattr(perm_state, 'audit_log'):
        stats["audit_events"] = len(perm_state.audit_log)
    
    return stats


# Workspace Selectors
def select_workspace_config(state: Dict[str, Any]) -> Dict[str, Any]:
    """Select workspace config."""
    workspace = state.get("workspace", {})
    if hasattr(workspace, 'config'):
        return workspace.config
    return {}


def select_workspace_files(state: Dict[str, Any]) -> Dict[str, str]:
    """Select workspace files."""
    workspace = state.get("workspace", {})
    if hasattr(workspace, 'files'):
        return workspace.files
    return {}


def select_file_content(state: Dict[str, Any], file_path: str) -> Optional[str]:
    """Select file content."""
    files = select_workspace_files(state)
    return files.get(file_path)


def select_current_project(state: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Select current project."""
    workspace = state.get("workspace", {})
    return {
        "id": workspace.current_project if hasattr(workspace, 'current_project') else None,
        "name": workspace.project_name if hasattr(workspace, 'project_name') else None
    }


def select_workspace_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Select workspace summary."""
    workspace = state.get("workspace", {})
    config = select_workspace_config(state)
    files = select_workspace_files(state)
    project = select_current_project(state)
    
    return {
        "config": config,
        "file_count": len(files),
        "current_project": project,
        "config_keys": list(config.keys())
    }


# Combined Selectors
def select_app_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Select complete app state snapshot."""
    return {
        "ui": {
            "visible_panels": select_visible_panels(state),
            "active_tab": select_active_tab(state),
            "theme": select_theme(state),
            "loading": select_loading_state(state),
            "notifications": select_notifications(state),
            "sidebar_collapsed": select_sidebar_collapsed(state)
        },
        "session": {
            "user_id": select_current_user(state),
            "username": select_current_username(state),
            "role": select_current_role(state),
            "is_authenticated": select_is_authenticated(state),
            "tools": select_available_tools(state)
        },
        "permissions": select_permission_stats(state),
        "workspace": select_workspace_summary(state)
    }


class SelectorCache:
    """Memoized selector cache."""
    
    def __init__(self):
        """Initialize cache."""
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str, selector: Callable, state: Dict[str, Any], ttl: int = 1) -> Any:
        """Get cached selector result."""
        import time
        
        now = time.time()
        if key in self._cache:
            cached_time = self._timestamps.get(key, 0)
            if now - cached_time < ttl:
                return self._cache[key]
        
        result = selector(state)
        self._cache[key] = result
        self._timestamps[key] = now
        return result
    
    def clear(self):
        """Clear cache."""
        self._cache.clear()
        self._timestamps.clear()


def create_memoized_selector(selector: Callable) -> Callable:
    """Create memoized selector."""
    cache = {}
    
    def memoized(*args, **kwargs):
        key = str((args, tuple(sorted(kwargs.items()))))
        if key not in cache:
            cache[key] = selector(*args, **kwargs)
        return cache[key]
    
    return memoized
