"""Temporary permission grants system."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger("hyena.permissions.grants")


@dataclass
class TemporaryGrant:
    """Temporary permission grant."""
    grant_id: str
    user_id: str
    permission: str
    granted_at: float
    expires_at: float
    granted_by: str
    reason: Optional[str] = None
    auto_revoke: bool = True
    
    @property
    def is_expired(self) -> bool:
        """Check if grant is expired."""
        return datetime.utcnow().timestamp() > self.expires_at
    
    @property
    def seconds_remaining(self) -> float:
        """Get seconds until expiration."""
        remaining = self.expires_at - datetime.utcnow().timestamp()
        return max(0, remaining)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "grant_id": self.grant_id,
            "user_id": self.user_id,
            "permission": self.permission,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "granted_by": self.granted_by,
            "reason": self.reason,
            "seconds_remaining": self.seconds_remaining,
            "is_expired": self.is_expired,
        }


class TemporaryGrantManager:
    """Manages temporary permission grants."""
    
    def __init__(self):
        """Initialize grant manager."""
        self.grants: Dict[str, TemporaryGrant] = {}
        self.grant_counter = 0
        self.cleanup_task: Optional[asyncio.Task] = None
    
    def create_grant(
        self,
        user_id: str,
        permission: str,
        duration_seconds: int,
        granted_by: str,
        reason: Optional[str] = None,
        auto_revoke: bool = True
    ) -> TemporaryGrant:
        """Create temporary grant."""
        grant_id = f"grant_{self.grant_counter}"
        self.grant_counter += 1
        
        now = datetime.utcnow().timestamp()
        expires_at = now + duration_seconds
        
        grant = TemporaryGrant(
            grant_id=grant_id,
            user_id=user_id,
            permission=permission,
            granted_at=now,
            expires_at=expires_at,
            granted_by=granted_by,
            reason=reason,
            auto_revoke=auto_revoke,
        )
        
        self.grants[grant_id] = grant
        logger.info(
            f"Created temporary grant {grant_id}: {user_id} -> {permission} "
            f"({duration_seconds}s, by {granted_by})"
        )
        
        return grant
    
    def get_grant(self, grant_id: str) -> Optional[TemporaryGrant]:
        """Get grant by ID."""
        return self.grants.get(grant_id)
    
    def revoke_grant(self, grant_id: str) -> None:
        """Revoke grant."""
        if grant_id in self.grants:
            grant = self.grants[grant_id]
            del self.grants[grant_id]
            logger.info(f"Revoked grant {grant_id} ({grant.user_id} -> {grant.permission})")
    
    def revoke_all_user_grants(self, user_id: str) -> int:
        """Revoke all grants for user."""
        grant_ids = [gid for gid, g in self.grants.items() if g.user_id == user_id]
        for grant_id in grant_ids:
            self.revoke_grant(grant_id)
        return len(grant_ids)
    
    def has_grant(self, user_id: str, permission: str) -> bool:
        """Check if user has active grant."""
        for grant in self.grants.values():
            if (grant.user_id == user_id and
                grant.permission == permission and
                not grant.is_expired):
                return True
        return False
    
    def get_user_grants(self, user_id: str) -> List[TemporaryGrant]:
        """Get all active grants for user."""
        grants = [
            g for g in self.grants.values()
            if g.user_id == user_id and not g.is_expired
        ]
        return sorted(grants, key=lambda g: g.expires_at)
    
    def list_grants(self, include_expired: bool = False) -> List[TemporaryGrant]:
        """List all grants."""
        grants = list(self.grants.values())
        if not include_expired:
            grants = [g for g in grants if not g.is_expired]
        return sorted(grants, key=lambda g: g.expires_at)
    
    def cleanup_expired(self) -> int:
        """Remove expired grants."""
        expired_ids = [gid for gid, g in self.grants.items() if g.is_expired]
        
        for grant_id in expired_ids:
            grant = self.grants[grant_id]
            del self.grants[grant_id]
            logger.info(f"Expired grant {grant_id} ({grant.user_id} -> {grant.permission})")
        
        return len(expired_ids)
    
    async def start_cleanup(self, interval_seconds: int = 60) -> None:
        """Start background cleanup task."""
        while True:
            try:
                self.cleanup_expired()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_cleanup(self) -> None:
        """Stop background cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get grant statistics."""
        active = [g for g in self.grants.values() if not g.is_expired]
        expired = [g for g in self.grants.values() if g.is_expired]
        
        # Group by permission
        by_permission = {}
        for grant in active:
            if grant.permission not in by_permission:
                by_permission[grant.permission] = 0
            by_permission[grant.permission] += 1
        
        # Shortest/longest expiry
        if active:
            by_expiry = sorted(active, key=lambda g: g.expires_at)
            shortest = by_expiry[0].seconds_remaining
            longest = by_expiry[-1].seconds_remaining
        else:
            shortest = longest = 0
        
        return {
            "total_grants": len(self.grants),
            "active_grants": len(active),
            "expired_grants": len(expired),
            "by_permission": by_permission,
            "shortest_expiry_seconds": shortest,
            "longest_expiry_seconds": longest,
        }
    
    def extend_grant(self, grant_id: str, additional_seconds: int) -> Optional[TemporaryGrant]:
        """Extend grant expiration."""
        grant = self.grants.get(grant_id)
        if not grant:
            return None
        
        grant.expires_at += additional_seconds
        logger.info(f"Extended grant {grant_id} by {additional_seconds}s")
        return grant
    
    def transfer_grant(self, grant_id: str, new_user_id: str) -> Optional[TemporaryGrant]:
        """Transfer grant to different user."""
        grant = self.grants.get(grant_id)
        if not grant:
            return None
        
        old_user = grant.user_id
        grant.user_id = new_user_id
        logger.info(f"Transferred grant {grant_id} from {old_user} to {new_user_id}")
        return grant
