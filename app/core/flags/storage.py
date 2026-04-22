"""Feature flag storage and persistence."""

import logging
import json
from typing import Dict, Optional, List
from pathlib import Path
from .definitions import ALL_FLAGS, FlagConfig
from .engine import FlagEvaluatorWithConfig, UserConfig

logger = logging.getLogger("hyena.flags.storage")


class FlagStore:
    """Persistent storage for feature flags."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize storage."""
        self.storage_path = Path(storage_path) if storage_path else None
        self.flags: Dict[str, FlagConfig] = {}
        self.assignments: Dict[str, Dict[str, bool]] = {}
        self.user_groups: Dict[str, set] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def load_flags(self) -> Dict[str, FlagConfig]:
        """Load flags."""
        self.flags = dict(ALL_FLAGS)
        logger.info(f"Loaded {len(self.flags)} flags from definitions")
        
        # Try to load from storage
        if self.storage_path and self.storage_path.exists():
            self._load_from_file()
        
        return self.flags
    
    def save_flags(self) -> bool:
        """Save flags to storage."""
        if not self.storage_path:
            return False
        
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            data = {
                "flags": {
                    flag_id: self._serialize_flag(flag)
                    for flag_id, flag in self.flags.items()
                },
                "assignments": self.assignments,
                "user_groups": {
                    user_id: list(groups)
                    for user_id, groups in self.user_groups.items()
                },
                "metadata": self.metadata
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Flags saved to {self.storage_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving flags: {e}")
            return False
    
    def _serialize_flag(self, flag: FlagConfig) -> Dict:
        """Serialize flag to dict."""
        return {
            "flag_id": flag.flag_id,
            "name": flag.name,
            "description": flag.description,
            "category": flag.category.value,
            "default_value": flag.default_value,
            "status": flag.status.value,
            "rollout_strategy": flag.rollout_strategy.value,
            "rollout_percentage": flag.rollout_percentage,
            "target_users": flag.target_users,
            "metadata": flag.metadata,
            "enabled_at": flag.enabled_at,
            "disabled_at": flag.disabled_at,
            "created_at": flag.created_at,
            "updated_at": flag.updated_at,
        }
    
    def _load_from_file(self) -> bool:
        """Load from file."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load user groups
            if "user_groups" in data:
                self.user_groups = {
                    user_id: set(groups)
                    for user_id, groups in data.get("user_groups", {}).items()
                }
            
            # Load assignments
            if "assignments" in data:
                self.assignments = data.get("assignments", {})
            
            # Load metadata
            if "metadata" in data:
                self.metadata = data.get("metadata", {})
            
            logger.info(f"Flags loaded from {self.storage_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading flags: {e}")
            return False
    
    def add_user_to_group(self, user_id: str, group: str) -> None:
        """Add user to group."""
        if user_id not in self.user_groups:
            self.user_groups[user_id] = set()
        self.user_groups[user_id].add(group)
    
    def remove_user_from_group(self, user_id: str, group: str) -> None:
        """Remove user from group."""
        if user_id in self.user_groups:
            self.user_groups[user_id].discard(group)
    
    def get_user_groups(self, user_id: str) -> set:
        """Get user's groups."""
        return self.user_groups.get(user_id, set())
    
    def set_flag_metadata(self, flag_id: str, metadata: Dict) -> None:
        """Set flag metadata."""
        if flag_id not in self.metadata:
            self.metadata[flag_id] = {}
        self.metadata[flag_id].update(metadata)
    
    def get_flag_metadata(self, flag_id: str) -> Dict:
        """Get flag metadata."""
        return self.metadata.get(flag_id, {})


class FlagManager:
    """High-level manager for feature flags."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize manager."""
        self.store = FlagStore(storage_path)
        self.evaluator = FlagEvaluatorWithConfig(self.store.load_flags())
        self.ab_tests: Dict[str, str] = {}
    
    def is_enabled(self, flag_id: str, user_id: Optional[str] = None) -> bool:
        """Check if flag is enabled."""
        return self.evaluator.is_enabled(flag_id, user_id)
    
    def enable_flag(self, flag_id: str) -> bool:
        """Enable flag for all users."""
        if flag_id not in self.evaluator.flags:
            return False
        
        flag = self.evaluator.flags[flag_id]
        flag.enabled_at = None  # Reset enabled_at
        flag.disabled_at = None
        flag.rollout_percentage = 100  # 100% rollout
        self.evaluator.clear_cache()
        self.store.save_flags()
        
        logger.info(f"Flag enabled: {flag_id}")
        return True
    
    def disable_flag(self, flag_id: str) -> bool:
        """Disable flag for all users."""
        if flag_id not in self.evaluator.flags:
            return False
        
        flag = self.evaluator.flags[flag_id]
        flag.default_value = False
        flag.disabled_at = __import__("datetime").datetime.utcnow().timestamp()
        self.evaluator.clear_cache()
        self.store.save_flags()
        
        logger.info(f"Flag disabled: {flag_id}")
        return True
    
    def set_rollout_percentage(self, flag_id: str, percentage: int) -> bool:
        """Set rollout percentage."""
        if flag_id not in self.evaluator.flags or not (0 <= percentage <= 100):
            return False
        
        flag = self.evaluator.flags[flag_id]
        flag.rollout_percentage = percentage
        self.evaluator.clear_cache()
        self.store.save_flags()
        
        logger.info(f"Flag {flag_id} rollout set to {percentage}%")
        return True
    
    def set_user_override(self, user_id: str, flag_id: str, enabled: bool) -> None:
        """Override flag for user."""
        self.evaluator.set_user_override(user_id, flag_id, enabled)
        self.store.save_flags()
        
        logger.info(f"User {user_id} override set for {flag_id}: {enabled}")
    
    def add_target_user(self, flag_id: str, user_id: str) -> bool:
        """Add user to target list."""
        if flag_id not in self.evaluator.flags:
            return False
        
        flag = self.evaluator.flags[flag_id]
        if user_id not in flag.target_users:
            flag.target_users.append(user_id)
            self.evaluator.clear_cache()
            self.store.save_flags()
        
        return True
    
    def remove_target_user(self, flag_id: str, user_id: str) -> bool:
        """Remove user from target list."""
        if flag_id not in self.evaluator.flags:
            return False
        
        flag = self.evaluator.flags[flag_id]
        if user_id in flag.target_users:
            flag.target_users.remove(user_id)
            self.evaluator.clear_cache()
            self.store.save_flags()
        
        return True
    
    def get_flag_stats(self) -> Dict:
        """Get flag statistics."""
        total_flags = len(self.evaluator.flags)
        active_flags = sum(1 for f in self.evaluator.flags.values() if f.is_active())
        
        by_category = {}
        for flag in self.evaluator.flags.values():
            cat = flag.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_flags": total_flags,
            "active_flags": active_flags,
            "by_category": by_category,
            "user_overrides": len(self.evaluator.user_configs),
            "cache_stats": self.evaluator.get_cache_stats()
        }
    
    def get_user_flags(self, user_id: str) -> Dict[str, bool]:
        """Get all flags for user."""
        return self.evaluator.get_enabled_flags(user_id)
    
    def save(self) -> bool:
        """Save state."""
        return self.store.save_flags()
    
    def sync_user_groups(self, user_id: str) -> None:
        """Sync user groups."""
        groups = self.store.get_user_groups(user_id)
        config = self.evaluator.get_or_create_user_config(user_id)
        config.groups = groups
