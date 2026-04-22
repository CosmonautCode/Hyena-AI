"""Permission management utilities and command handlers.

This module provides utilities for permission operations that can be
integrated with the ChatLoop command system.
"""

from typing import Dict, List, Any, Optional
from app.core.permissions.rbac import RBACSystem, PredefinedRole, PermissionName
from app.core.permissions.resources import ResourcePermissionManager, ResourceType, ResourceAction
from app.core.permissions.audit import AuditLogger
from app.core.permissions.grants import TemporaryGrantManager


class PermissionCommandHandler:
    """Handles permission-related command operations."""
    
    def __init__(self):
        """Initialize permission command handler."""
        self.rbac = RBACSystem()
        self.resource_mgr = ResourcePermissionManager()
        self.audit = AuditLogger()
        self.grants = TemporaryGrantManager()
    
    def list_roles(self) -> Dict[str, Any]:
        """List all roles."""
        roles = self.rbac.list_roles()
        return {
            "success": True,
            "roles": [
                {
                    "name": role.name,
                    "description": role.description,
                    "is_custom": role.is_custom,
                    "permission_count": len(role.permissions),
                }
                for role in roles
            ],
            "total": len(roles)
        }
    
    def create_role(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create custom role."""
        try:
            role = self.rbac.create_role(name, description)
            return {"success": True, "role": name, "description": description}
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    def assign_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """Assign role to user."""
        try:
            self.rbac.assign_role(user_id, role)
            self.audit.log_role_assigned("system", user_id, role)
            return {"success": True, "user": user_id, "role": role}
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get user permissions."""
        roles = self.rbac.get_user_roles(user_id)
        permissions = self.rbac.get_user_permissions(user_id)
        return {
            "success": True,
            "user": user_id,
            "roles": list(roles),
            "permissions": [p.value for p in permissions],
            "permission_count": len(permissions),
        }
    
    def check_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """Check if user has permission."""
        try:
            perm_enum = PermissionName[permission.upper()]
            has_perm = self.rbac.has_permission(user_id, perm_enum)
            return {
                "success": True,
                "user": user_id,
                "permission": permission,
                "has_permission": has_perm,
            }
        except KeyError:
            return {"success": False, "error": f"Unknown permission: {permission}"}
    
    def create_temp_grant(
        self,
        user_id: str,
        permission: str,
        duration_seconds: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create temporary permission grant."""
        grant = self.grants.create_grant(
            user_id,
            permission,
            duration_seconds,
            granted_by="system",
            reason=reason
        )
        self.audit.log_temp_grant_created("system", user_id, permission, duration_seconds)
        return {
            "success": True,
            "grant_id": grant.grant_id,
            "user": user_id,
            "permission": permission,
            "duration_seconds": duration_seconds,
        }
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get audit log."""
        if user_id:
            events = self.audit.get_user_activity(user_id, limit)
        else:
            events = self.audit.get_events(limit=limit)
        
        return {
            "success": True,
            "events": [e.to_dict() for e in events],
            "total": len(events),
        }
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        stats = self.audit.get_stats()
        grant_stats = self.grants.get_stats()
        
        return {
            "success": True,
            "audit": stats,
            "grants": grant_stats,
        }


# Singleton instance for command system
_permission_handler: Optional[PermissionCommandHandler] = None


def get_permission_handler() -> PermissionCommandHandler:
    """Get or create permission command handler."""
    global _permission_handler
    if _permission_handler is None:
        _permission_handler = PermissionCommandHandler()
    return _permission_handler

