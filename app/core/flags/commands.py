"""Feature flag management commands."""

import logging
from typing import Dict, Optional, List, Any
from .storage import FlagManager
from .definitions import FlagCategory, RolloutStrategy, FlagStatus

logger = logging.getLogger("hyena.flags.commands")


class FlagCommandHandler:
    """Handles feature flag commands."""
    
    def __init__(self, manager: FlagManager):
        """Initialize handler."""
        self.manager = manager
    
    def list_flags(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List feature flags."""
        flags = []
        
        for flag_id, flag in self.manager.evaluator.flags.items():
            # Apply filters
            if category and flag.category.value != category:
                continue
            if status and flag.status.value != status:
                continue
            
            flags.append({
                "flag_id": flag.flag_id,
                "name": flag.name,
                "category": flag.category.value,
                "status": flag.status.value,
                "is_active": flag.is_active(),
                "rollout_percentage": flag.rollout_percentage,
                "default_value": flag.default_value
            })
        
        return {
            "success": True,
            "count": len(flags[:limit]),
            "total": len(flags),
            "flags": flags[:limit]
        }
    
    def get_flag_info(self, flag_id: str) -> Dict[str, Any]:
        """Get detailed flag information."""
        flag = self.manager.evaluator.flags.get(flag_id)
        if not flag:
            return {"success": False, "error": f"Flag not found: {flag_id}"}
        
        return {
            "success": True,
            "flag": {
                "flag_id": flag.flag_id,
                "name": flag.name,
                "description": flag.description,
                "category": flag.category.value,
                "status": flag.status.value,
                "default_value": flag.default_value,
                "rollout_strategy": flag.rollout_strategy.value,
                "rollout_percentage": flag.rollout_percentage,
                "target_users": flag.target_users,
                "is_active": flag.is_active(),
                "enabled_at": flag.enabled_at,
                "disabled_at": flag.disabled_at,
                "created_at": flag.created_at,
                "updated_at": flag.updated_at,
                "metadata": flag.metadata
            }
        }
    
    def enable_flag(self, flag_id: str) -> Dict[str, Any]:
        """Enable flag."""
        if self.manager.enable_flag(flag_id):
            return {
                "success": True,
                "message": f"Flag enabled: {flag_id}"
            }
        return {
            "success": False,
            "error": f"Failed to enable flag: {flag_id}"
        }
    
    def disable_flag(self, flag_id: str) -> Dict[str, Any]:
        """Disable flag."""
        if self.manager.disable_flag(flag_id):
            return {
                "success": True,
                "message": f"Flag disabled: {flag_id}"
            }
        return {
            "success": False,
            "error": f"Failed to disable flag: {flag_id}"
        }
    
    def set_rollout(self, flag_id: str, percentage: int) -> Dict[str, Any]:
        """Set rollout percentage."""
        if not (0 <= percentage <= 100):
            return {
                "success": False,
                "error": "Percentage must be 0-100"
            }
        
        if self.manager.set_rollout_percentage(flag_id, percentage):
            return {
                "success": True,
                "message": f"Rollout set to {percentage}% for {flag_id}"
            }
        return {
            "success": False,
            "error": f"Failed to set rollout for {flag_id}"
        }
    
    def check_flag(self, flag_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if flag is enabled."""
        is_enabled = self.manager.is_enabled(flag_id, user_id)
        
        result = {
            "success": True,
            "flag_id": flag_id,
            "is_enabled": is_enabled
        }
        
        if user_id:
            result["user_id"] = user_id
            result["variant"] = self.manager.evaluator.get_user_variant(flag_id, user_id)
        
        return result
    
    def set_user_override(self, flag_id: str, user_id: str, enabled: bool) -> Dict[str, Any]:
        """Set user override."""
        self.manager.set_user_override(user_id, flag_id, enabled)
        return {
            "success": True,
            "message": f"Override set for user {user_id}, flag {flag_id}: {enabled}"
        }
    
    def add_target_user(self, flag_id: str, user_id: str) -> Dict[str, Any]:
        """Add user to target list."""
        if self.manager.add_target_user(flag_id, user_id):
            return {
                "success": True,
                "message": f"User {user_id} added to target list for {flag_id}"
            }
        return {
            "success": False,
            "error": f"Failed to add user to {flag_id}"
        }
    
    def remove_target_user(self, flag_id: str, user_id: str) -> Dict[str, Any]:
        """Remove user from target list."""
        if self.manager.remove_target_user(flag_id, user_id):
            return {
                "success": True,
                "message": f"User {user_id} removed from target list for {flag_id}"
            }
        return {
            "success": False,
            "error": f"Failed to remove user from {flag_id}"
        }
    
    def get_user_flags(self, user_id: str, enabled_only: bool = False) -> Dict[str, Any]:
        """Get flags for user."""
        flags = self.manager.get_user_flags(user_id)
        
        if enabled_only:
            flags = {k: v for k, v in flags.items() if v}
        
        return {
            "success": True,
            "user_id": user_id,
            "enabled_count": sum(1 for v in flags.values() if v),
            "disabled_count": sum(1 for v in flags.values() if not v),
            "flags": flags
        }
    
    def add_user_to_group(self, user_id: str, group: str) -> Dict[str, Any]:
        """Add user to group."""
        self.manager.store.add_user_to_group(user_id, group)
        self.manager.evaluator.add_user_to_group(user_id, group)
        self.manager.save()
        
        return {
            "success": True,
            "message": f"User {user_id} added to group {group}"
        }
    
    def get_flag_stats(self) -> Dict[str, Any]:
        """Get flag statistics."""
        stats = self.manager.get_flag_stats()
        return {
            "success": True,
            "stats": stats
        }
    
    def get_flags_by_category(self, category: str) -> Dict[str, Any]:
        """Get flags by category."""
        result = self.list_flags(category=category)
        return result
    
    def get_rolling_out_flags(self) -> Dict[str, Any]:
        """Get flags in rollout status."""
        result = self.list_flags(status=FlagStatus.ROLLOUT.value)
        return result
    
    def get_beta_flags(self) -> Dict[str, Any]:
        """Get flags in beta status."""
        result = self.list_flags(status=FlagStatus.BETA.value)
        return result
    
    def save_flags(self) -> Dict[str, Any]:
        """Save flags."""
        if self.manager.save():
            return {
                "success": True,
                "message": "Flags saved successfully"
            }
        return {
            "success": False,
            "error": "Failed to save flags"
        }


def create_flag_handler(manager: FlagManager) -> FlagCommandHandler:
    """Factory to create flag command handler."""
    return FlagCommandHandler(manager)
