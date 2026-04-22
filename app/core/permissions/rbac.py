"""Role-Based Access Control (RBAC) system."""

from enum import Enum
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("hyena.permissions.rbac")


class PermissionName(Enum):
    """All available permissions."""
    # File operations
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_DELETE = "file.delete"
    FILE_EXECUTE = "file.execute"
    
    # Command execution
    CMD_EXECUTE = "command.execute"
    CMD_DANGEROUS = "command.dangerous"
    
    # Tool operations
    TOOL_EXECUTE = "tool.execute"
    TOOL_DANGEROUS = "tool.dangerous"
    TOOL_CONFIG = "tool.config"
    
    # Git operations
    GIT_COMMIT = "git.commit"
    GIT_PUSH = "git.push"
    GIT_FORCE_PUSH = "git.force_push"
    GIT_DELETE = "git.delete"
    
    # Web operations
    WEB_REQUEST = "web.request"
    WEB_EXTERNAL = "web.external"
    
    # System operations
    SYS_SHUTDOWN = "system.shutdown"
    SYS_INSTALL = "system.install"
    SYS_CONFIG = "system.config"
    
    # Permission management
    PERM_GRANT = "permission.grant"
    PERM_REVOKE = "permission.revoke"
    PERM_MANAGE = "permission.manage"
    
    # Admin operations
    ADMIN_ALL = "admin.all"


class PredefinedRole(Enum):
    """Predefined user roles."""
    ADMIN = "admin"
    POWER_USER = "power_user"
    USER = "user"
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class Role:
    """Role definition with permissions."""
    name: str
    description: str
    permissions: Set[PermissionName] = field(default_factory=set)
    is_custom: bool = False
    
    def has_permission(self, permission: PermissionName) -> bool:
        """Check if role has permission."""
        return permission in self.permissions
    
    def grant_permission(self, permission: PermissionName) -> None:
        """Grant permission to role."""
        self.permissions.add(permission)
        logger.info(f"Granted {permission.value} to role {self.name}")
    
    def revoke_permission(self, permission: PermissionName) -> None:
        """Revoke permission from role."""
        self.permissions.discard(permission)
        logger.info(f"Revoked {permission.value} from role {self.name}")
    
    def grant_permissions(self, permissions: List[PermissionName]) -> None:
        """Grant multiple permissions."""
        for perm in permissions:
            self.grant_permission(perm)
    
    def revoke_permissions(self, permissions: List[PermissionName]) -> None:
        """Revoke multiple permissions."""
        for perm in permissions:
            self.revoke_permission(perm)


class RBACSystem:
    """Role-Based Access Control system."""
    
    def __init__(self):
        """Initialize RBAC with predefined roles."""
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}  # user_id -> {role_names}
        self._init_predefined_roles()
    
    def _init_predefined_roles(self) -> None:
        """Initialize predefined roles."""
        # Admin: all permissions
        admin_role = Role(
            name=PredefinedRole.ADMIN.value,
            description="Administrator with all permissions"
        )
        admin_role.grant_permissions(list(PermissionName))
        self.roles[PredefinedRole.ADMIN.value] = admin_role
        
        # Power User: most permissions except dangerous system operations
        power_user_role = Role(
            name=PredefinedRole.POWER_USER.value,
            description="Power user with elevated permissions"
        )
        power_user_perms = [p for p in PermissionName if p not in {
            PermissionName.SYS_SHUTDOWN,
            PermissionName.SYS_INSTALL,
            PermissionName.PERM_GRANT,
            PermissionName.PERM_REVOKE,
            PermissionName.PERM_MANAGE,
        }]
        power_user_role.grant_permissions(power_user_perms)
        self.roles[PredefinedRole.POWER_USER.value] = power_user_role
        
        # User: safe read operations and controlled execution
        user_role = Role(
            name=PredefinedRole.USER.value,
            description="Regular user with standard permissions"
        )
        user_perms = [
            PermissionName.FILE_READ,
            PermissionName.CMD_EXECUTE,
            PermissionName.TOOL_EXECUTE,
            PermissionName.WEB_REQUEST,
            PermissionName.TOOL_CONFIG,
        ]
        user_role.grant_permissions(user_perms)
        self.roles[PredefinedRole.USER.value] = user_role
        
        # Viewer: read-only access
        viewer_role = Role(
            name=PredefinedRole.VIEWER.value,
            description="Read-only viewer access"
        )
        viewer_perms = [
            PermissionName.FILE_READ,
        ]
        viewer_role.grant_permissions(viewer_perms)
        self.roles[PredefinedRole.VIEWER.value] = viewer_role
        
        # Guest: minimal access
        guest_role = Role(
            name=PredefinedRole.GUEST.value,
            description="Guest with minimal permissions"
        )
        guest_role.grant_permissions([])
        self.roles[PredefinedRole.GUEST.value] = guest_role
    
    def create_role(self, name: str, description: str, permissions: Optional[List[PermissionName]] = None) -> Role:
        """Create custom role."""
        if name in self.roles:
            raise ValueError(f"Role {name} already exists")
        
        role = Role(name=name, description=description, is_custom=True)
        if permissions:
            role.grant_permissions(permissions)
        
        self.roles[name] = role
        logger.info(f"Created custom role: {name}")
        return role
    
    def delete_role(self, name: str) -> None:
        """Delete custom role."""
        if name in self.roles:
            role = self.roles[name]
            if not role.is_custom:
                raise ValueError(f"Cannot delete predefined role: {name}")
            del self.roles[name]
            # Remove from users
            for user_id in list(self.user_roles.keys()):
                self.user_roles[user_id].discard(name)
            logger.info(f"Deleted role: {name}")
    
    def get_role(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.roles.get(name)
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        return list(self.roles.values())
    
    def assign_role(self, user_id: str, role_name: str) -> None:
        """Assign role to user."""
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} does not exist")
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_name)
        logger.info(f"Assigned role {role_name} to user {user_id}")
    
    def remove_role(self, user_id: str, role_name: str) -> None:
        """Remove role from user."""
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role_name)
            logger.info(f"Removed role {role_name} from user {user_id}")
    
    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get user roles."""
        return self.user_roles.get(user_id, set()).copy()
    
    def set_user_roles(self, user_id: str, role_names: List[str]) -> None:
        """Set user roles (replaces existing)."""
        for role_name in role_names:
            if role_name not in self.roles:
                raise ValueError(f"Role {role_name} does not exist")
        
        self.user_roles[user_id] = set(role_names)
        logger.info(f"Set roles for user {user_id}: {role_names}")
    
    def has_permission(self, user_id: str, permission: PermissionName) -> bool:
        """Check if user has permission."""
        role_names = self.user_roles.get(user_id, set())
        
        # Check all roles for permission
        for role_name in role_names:
            role = self.roles.get(role_name)
            if role and role.has_permission(permission):
                return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[PermissionName]:
        """Get all permissions for user."""
        permissions: Set[PermissionName] = set()
        role_names = self.user_roles.get(user_id, set())
        
        for role_name in role_names:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        
        return permissions
