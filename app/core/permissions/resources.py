"""Resource-level permissions system."""

from enum import Enum
from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("hyena.permissions.resources")


class ResourceType(Enum):
    """Types of resources."""
    FILE = "file"
    DIRECTORY = "directory"
    TOOL = "tool"
    COMMAND = "command"
    PROJECT = "project"
    WORKSPACE = "workspace"
    AGENT = "agent"
    MEMORY = "memory"


class ResourceAction(Enum):
    """Actions on resources."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIG = "config"
    SHARE = "share"


@dataclass
class Resource:
    """Resource definition."""
    id: str
    type: ResourceType
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    owner_id: Optional[str] = None
    is_public: bool = False


@dataclass
class ResourcePermission:
    """Permission for a specific resource."""
    resource_id: str
    user_id: str
    actions: Set[ResourceAction] = field(default_factory=set)
    granted_by: Optional[str] = None
    created_at: Optional[float] = None
    
    def has_action(self, action: ResourceAction) -> bool:
        """Check if permission has action."""
        return action in self.actions
    
    def grant_action(self, action: ResourceAction) -> None:
        """Grant action."""
        self.actions.add(action)
    
    def revoke_action(self, action: ResourceAction) -> None:
        """Revoke action."""
        self.actions.discard(action)


class ResourcePermissionManager:
    """Manages resource-level permissions."""
    
    def __init__(self):
        """Initialize resource permission manager."""
        self.resources: Dict[str, Resource] = {}
        self.permissions: Dict[str, Dict[str, ResourcePermission]] = {}  # resource_id -> user_id -> permission
    
    def create_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        name: str,
        owner_id: Optional[str] = None,
        description: Optional[str] = None,
        is_public: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Resource:
        """Create resource."""
        if resource_id in self.resources:
            raise ValueError(f"Resource {resource_id} already exists")
        
        resource = Resource(
            id=resource_id,
            type=resource_type,
            name=name,
            description=description,
            metadata=metadata or {},
            owner_id=owner_id,
            is_public=is_public
        )
        
        self.resources[resource_id] = resource
        self.permissions[resource_id] = {}
        
        # Owner gets all actions by default
        if owner_id:
            self.grant_permission(
                resource_id,
                owner_id,
                list(ResourceAction),
                granted_by="system"
            )
        
        logger.info(f"Created resource: {resource_id} ({resource_type.value})")
        return resource
    
    def delete_resource(self, resource_id: str) -> None:
        """Delete resource."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            if resource_id in self.permissions:
                del self.permissions[resource_id]
            logger.info(f"Deleted resource: {resource_id}")
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource."""
        return self.resources.get(resource_id)
    
    def list_resources(self, resource_type: Optional[ResourceType] = None) -> List[Resource]:
        """List resources."""
        resources = list(self.resources.values())
        if resource_type:
            resources = [r for r in resources if r.type == resource_type]
        return resources
    
    def grant_permission(
        self,
        resource_id: str,
        user_id: str,
        actions: List[ResourceAction],
        granted_by: Optional[str] = None
    ) -> ResourcePermission:
        """Grant permission on resource."""
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} does not exist")
        
        if resource_id not in self.permissions:
            self.permissions[resource_id] = {}
        
        perm = self.permissions[resource_id].get(user_id)
        if not perm:
            perm = ResourcePermission(
                resource_id=resource_id,
                user_id=user_id,
                granted_by=granted_by
            )
            self.permissions[resource_id][user_id] = perm
        
        for action in actions:
            perm.grant_action(action)
        
        logger.info(f"Granted {[a.value for a in actions]} on {resource_id} to {user_id}")
        return perm
    
    def revoke_permission(
        self,
        resource_id: str,
        user_id: str,
        actions: Optional[List[ResourceAction]] = None
    ) -> None:
        """Revoke permission on resource."""
        if resource_id not in self.permissions:
            return
        
        if user_id not in self.permissions[resource_id]:
            return
        
        perm = self.permissions[resource_id][user_id]
        
        if actions:
            for action in actions:
                perm.revoke_action(action)
            logger.info(f"Revoked {[a.value for a in actions]} on {resource_id} from {user_id}")
        else:
            # Revoke all permissions
            del self.permissions[resource_id][user_id]
            logger.info(f"Revoked all permissions on {resource_id} from {user_id}")
    
    def has_permission(
        self,
        resource_id: str,
        user_id: str,
        action: ResourceAction
    ) -> bool:
        """Check if user has permission on resource."""
        resource = self.resources.get(resource_id)
        if not resource:
            return False
        
        # Owner always has permission
        if resource.owner_id == user_id:
            return True
        
        # Public resources readable by all
        if resource.is_public and action == ResourceAction.READ:
            return True
        
        # Check explicit permission
        if resource_id in self.permissions:
            perm = self.permissions[resource_id].get(user_id)
            if perm and perm.has_action(action):
                return True
        
        return False
    
    def get_resource_permissions(self, resource_id: str, user_id: str) -> Optional[ResourcePermission]:
        """Get permission object for resource."""
        if resource_id not in self.permissions:
            return None
        return self.permissions[resource_id].get(user_id)
    
    def list_user_resources(self, user_id: str, action: Optional[ResourceAction] = None) -> List[Resource]:
        """List resources user has access to."""
        resources = []
        
        for resource_id, resource in self.resources.items():
            if self.has_permission(resource_id, user_id, action or ResourceAction.READ):
                resources.append(resource)
        
        return resources
    
    def list_resource_permissions(self, resource_id: str) -> Dict[str, ResourcePermission]:
        """List all permissions on resource."""
        return self.permissions.get(resource_id, {}).copy()
    
    def transfer_ownership(self, resource_id: str, from_user: str, to_user: str) -> None:
        """Transfer resource ownership."""
        resource = self.resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} does not exist")
        
        if resource.owner_id != from_user:
            raise ValueError(f"User {from_user} is not owner of {resource_id}")
        
        # Remove old owner permissions
        self.revoke_permission(resource_id, from_user)
        
        # Set new owner
        resource.owner_id = to_user
        
        # Grant new owner all permissions
        self.grant_permission(
            resource_id,
            to_user,
            list(ResourceAction),
            granted_by="system"
        )
        
        logger.info(f"Transferred ownership of {resource_id} from {from_user} to {to_user}")
