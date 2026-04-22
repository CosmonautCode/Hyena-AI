"""Permissions system module."""

from app.core.permissions.rbac import (
    RBACSystem,
    Role,
    PermissionName,
    PredefinedRole,
)
from app.core.permissions.resources import (
    ResourcePermissionManager,
    Resource,
    ResourcePermission,
    ResourceType,
    ResourceAction,
)
from app.core.permissions.audit import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
)
from app.core.permissions.grants import (
    TemporaryGrantManager,
    TemporaryGrant,
)
from app.core.permissions.suggestions import (
    PermissionSuggestionEngine,
    PermissionSuggestion,
    SuggestionType,
    RiskLevel,
)

__all__ = [
    "RBACSystem",
    "Role",
    "PermissionName",
    "PredefinedRole",
    "ResourcePermissionManager",
    "Resource",
    "ResourcePermission",
    "ResourceType",
    "ResourceAction",
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "TemporaryGrantManager",
    "TemporaryGrant",
    "PermissionSuggestionEngine",
    "PermissionSuggestion",
    "SuggestionType",
    "RiskLevel",
]
