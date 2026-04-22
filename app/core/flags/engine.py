"""Feature flag evaluation engine."""

import logging
import hashlib
from typing import Dict, Optional, List, Set
from datetime import datetime
from .definitions import FlagConfig, RolloutStrategy, FlagStatus

logger = logging.getLogger("hyena.flags.engine")


class FlagEvaluator:
    """Evaluates feature flags for users."""
    
    def __init__(self, flags: Dict[str, FlagConfig]):
        """Initialize evaluator."""
        self.flags = flags
        self.user_assignments: Dict[str, Dict[str, bool]] = {}
        self.evaluation_cache: Dict[tuple, bool] = {}
    
    def is_enabled(self, flag_id: str, user_id: Optional[str] = None) -> bool:
        """Check if flag is enabled for user."""
        if flag_id not in self.flags:
            logger.warning(f"Flag not found: {flag_id}")
            return False
        
        flag = self.flags[flag_id]
        
        # Check cache first
        cache_key = (flag_id, user_id)
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        # Flag must be active to be evaluated
        if not flag.is_active():
            return False
        
        # Evaluate based on strategy
        result = self._evaluate_strategy(flag, user_id)
        
        # Cache result
        self.evaluation_cache[cache_key] = result
        return result
    
    def _evaluate_strategy(self, flag: FlagConfig, user_id: Optional[str]) -> bool:
        """Evaluate flag based on strategy."""
        # Start with default value
        result = flag.default_value
        
        if flag.rollout_strategy == RolloutStrategy.INSTANT:
            # Instant rollout at specified percentage
            if flag.rollout_percentage >= 100:
                return True
            return flag.default_value
        
        elif flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
            # Percentage-based rollout using consistent hashing
            if user_id is None:
                return flag.default_value
            
            hash_input = f"{flag.flag_id}:{user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 100) + 1
            
            return percentage <= flag.rollout_percentage
        
        elif flag.rollout_strategy == RolloutStrategy.USER_LIST:
            # User list-based targeting
            if user_id is None:
                return flag.default_value
            
            return user_id in flag.target_users
        
        elif flag.rollout_strategy == RolloutStrategy.GRADUAL:
            # Gradual rollout (ramping up percentage)
            if user_id is None:
                return flag.default_value
            
            # Increase percentage over time
            current_percentage = self._calculate_gradual_percentage(flag)
            
            hash_input = f"{flag.flag_id}:{user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 100) + 1
            
            return percentage <= current_percentage
        
        elif flag.rollout_strategy == RolloutStrategy.CANARY:
            # Canary release to small percentage
            if user_id is None:
                return flag.default_value
            
            hash_input = f"{flag.flag_id}:{user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 100) + 1
            
            return percentage <= flag.rollout_percentage
        
        return result
    
    def _calculate_gradual_percentage(self, flag: FlagConfig) -> int:
        """Calculate rollout percentage for gradual strategy."""
        if flag.enabled_at is None:
            return flag.rollout_percentage
        
        now = datetime.utcnow().timestamp()
        days_elapsed = (now - flag.enabled_at) / (24 * 3600)
        
        # Increase 10% per day up to rollout_percentage
        current_percentage = min(int(days_elapsed * 10), flag.rollout_percentage)
        return current_percentage
    
    def get_flag_config(self, flag_id: str) -> Optional[FlagConfig]:
        """Get flag configuration."""
        return self.flags.get(flag_id)
    
    def get_enabled_flags(self, user_id: Optional[str] = None) -> Dict[str, bool]:
        """Get all enabled flags for user."""
        enabled = {}
        for flag_id, flag in self.flags.items():
            enabled[flag_id] = self.is_enabled(flag_id, user_id)
        return enabled
    
    def get_disabled_flags(self, user_id: Optional[str] = None) -> Dict[str, bool]:
        """Get all disabled flags for user."""
        disabled = {}
        for flag_id, flag in self.flags.items():
            if not self.is_enabled(flag_id, user_id):
                disabled[flag_id] = False
        return disabled
    
    def assign_user_to_variant(self, flag_id: str, user_id: str, variant: str) -> bool:
        """Assign user to specific variant."""
        if flag_id not in self.user_assignments:
            self.user_assignments[flag_id] = {}
        
        # For A/B testing, store variant assignment
        self.user_assignments[flag_id][user_id] = variant == "control"
        self.evaluation_cache.clear()
        
        logger.info(f"User {user_id} assigned to variant {variant} for flag {flag_id}")
        return True
    
    def get_user_variant(self, flag_id: str, user_id: str) -> str:
        """Get user's variant for flag."""
        if flag_id not in self.user_assignments or user_id not in self.user_assignments[flag_id]:
            # Determine variant based on flag evaluation
            is_control = self.is_enabled(flag_id, user_id)
            return "control" if is_control else "treatment"
        
        is_control = self.user_assignments[flag_id][user_id]
        return "control" if is_control else "treatment"
    
    def clear_cache(self) -> None:
        """Clear evaluation cache."""
        self.evaluation_cache.clear()
        logger.debug("Evaluation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.evaluation_cache),
            "user_assignments": len(self.user_assignments),
            "flags_cached": len(set(key[0] for key in self.evaluation_cache.keys()))
        }


class UserConfig:
    """User configuration and override."""
    
    def __init__(self, user_id: str):
        """Initialize user config."""
        self.user_id = user_id
        self.overrides: Dict[str, bool] = {}
        self.groups: Set[str] = set()
        self.metadata: Dict[str, str] = {}
    
    def set_override(self, flag_id: str, enabled: bool) -> None:
        """Override flag for user."""
        self.overrides[flag_id] = enabled
    
    def remove_override(self, flag_id: str) -> None:
        """Remove override."""
        self.overrides.pop(flag_id, None)
    
    def add_group(self, group: str) -> None:
        """Add user to group."""
        self.groups.add(group)
    
    def remove_group(self, group: str) -> None:
        """Remove user from group."""
        self.groups.discard(group)
    
    def is_in_group(self, group: str) -> bool:
        """Check if user is in group."""
        return group in self.groups
    
    def set_metadata(self, key: str, value: str) -> None:
        """Set user metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get user metadata."""
        return self.metadata.get(key, default)


class FlagEvaluatorWithConfig(FlagEvaluator):
    """Flag evaluator with user configurations."""
    
    def __init__(self, flags: Dict[str, FlagConfig]):
        """Initialize."""
        super().__init__(flags)
        self.user_configs: Dict[str, UserConfig] = {}
    
    def is_enabled(self, flag_id: str, user_id: Optional[str] = None) -> bool:
        """Check if flag is enabled, considering user overrides."""
        # Check user override first
        if user_id and user_id in self.user_configs:
            override = self.user_configs[user_id].overrides.get(flag_id)
            if override is not None:
                return override
        
        # Fall back to normal evaluation
        return super().is_enabled(flag_id, user_id)
    
    def get_or_create_user_config(self, user_id: str) -> UserConfig:
        """Get or create user config."""
        if user_id not in self.user_configs:
            self.user_configs[user_id] = UserConfig(user_id)
        return self.user_configs[user_id]
    
    def set_user_override(self, user_id: str, flag_id: str, enabled: bool) -> None:
        """Set user override."""
        config = self.get_or_create_user_config(user_id)
        config.set_override(flag_id, enabled)
        self.evaluation_cache.clear()
        logger.info(f"Override set for user {user_id}, flag {flag_id}: {enabled}")
    
    def remove_user_override(self, user_id: str, flag_id: str) -> None:
        """Remove user override."""
        if user_id in self.user_configs:
            self.user_configs[user_id].remove_override(flag_id)
            self.evaluation_cache.clear()
    
    def add_user_to_group(self, user_id: str, group: str) -> None:
        """Add user to group."""
        config = self.get_or_create_user_config(user_id)
        config.add_group(group)
    
    def remove_user_from_group(self, user_id: str, group: str) -> None:
        """Remove user from group."""
        if user_id in self.user_configs:
            self.user_configs[user_id].remove_group(group)


def create_evaluator(flags: Dict[str, FlagConfig]) -> FlagEvaluatorWithConfig:
    """Factory to create evaluator."""
    return FlagEvaluatorWithConfig(flags)
