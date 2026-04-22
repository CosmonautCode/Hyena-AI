"""Middleware for state management."""

from typing import Callable, Optional, Any, Dict
import logging
import json
from datetime import datetime
from .store import Action
from .actions import ActionType

logger = logging.getLogger("hyena.state.middleware")


def logger_middleware(store_api: Dict[str, Callable]):
    """Logging middleware."""
    def middleware(next_func: Callable) -> Callable:
        def dispatch(action: Action) -> Action:
            logger.info(f"Action dispatched: {action.type}")
            try:
                result = next_func(action)
                logger.debug(f"Dispatched action successfully: {action.type}")
                return result
            except Exception as e:
                logger.error(f"Error dispatching {action.type}: {e}")
                raise
        return dispatch
    return middleware


def validation_middleware(store_api: Dict[str, Callable]):
    """Validation middleware."""
    def middleware(next_func: Callable) -> Callable:
        def dispatch(action: Action) -> Action:
            # Validate action structure
            if not action.type:
                raise ValueError("Action must have a type")
            
            if action.payload is not None and not isinstance(action.payload, dict):
                # Payload should be dict or None
                pass
            
            return next_func(action)
        return dispatch
    return middleware


def persistence_middleware(storage_path: str):
    """Persistence middleware for saving state."""
    def middleware_func(store_api: Dict[str, Callable]):
        def middleware(next_func: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                result = next_func(action)
                
                # Save state after certain action types
                persistent_actions = [
                    "workspace/UPDATE_CONFIG",
                    "session/UPDATE_SESSION_CONFIG",
                    "permission/ASSIGN_ROLE"
                ]
                
                if action.type in persistent_actions:
                    try:
                        state = store_api["getState"]()
                        with open(storage_path, 'w') as f:
                            json.dump(state, f, default=str)
                        logger.debug(f"State persisted to {storage_path}")
                    except Exception as e:
                        logger.error(f"Error persisting state: {e}")
                
                return result
            return dispatch
        return middleware_func
    return middleware_func


def effects_middleware(store_api: Dict[str, Callable]):
    """Effects middleware for side effects."""
    def middleware(next_func: Callable) -> Callable:
        def dispatch(action: Action) -> Action:
            result = next_func(action)
            
            # Handle async effects metadata
            if action.meta.get("async"):
                logger.debug(f"Async effect for action: {action.type}")
                # Effects are handled by middleware consumers
            
            # Handle specific effects
            if action.type == "ui/SHOW_NOTIFICATION":
                # Could trigger sound, animation, etc.
                logger.debug(f"Notification effect: {action.payload.get('title')}")
            
            elif action.type == "session/START_SESSION":
                # Setup session resources
                logger.debug(f"Session started: {action.payload.get('session_id')}")
            
            elif action.type == "session/END_SESSION":
                # Cleanup session resources
                logger.debug(f"Session ended: {action.payload.get('session_id')}")
            
            return result
        return dispatch
    return middleware


def undo_redo_middleware(store_api: Dict[str, Callable]):
    """Undo/Redo middleware."""
    def middleware(next_func: Callable) -> Callable:
        def dispatch(action: Action) -> Action:
            # Skip recording action history for these special actions
            skip_history = ["@@UNDO", "@@REDO", "@@EFFECT"]
            
            if action.type not in skip_history:
                result = next_func(action)
                return result
            else:
                return next_func(action)
        return dispatch
    return middleware


class DevToolsMiddleware:
    """Development tools middleware."""
    
    def __init__(self, max_entries: int = 100):
        """Initialize dev tools."""
        self.max_entries = max_entries
        self.entries: list = []
    
    def __call__(self, store_api: Dict[str, Callable]):
        """Middleware function."""
        def middleware(next_func: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                # Record state before
                state_before = store_api["getState"]()
                
                result = next_func(action)
                
                # Record state after
                state_after = store_api["getState"]()
                
                entry = {
                    "action": action.to_dict(),
                    "state_before": state_before,
                    "state_after": state_after,
                    "timestamp": datetime.utcnow().timestamp()
                }
                
                self.entries.append(entry)
                if len(self.entries) > self.max_entries:
                    self.entries.pop(0)
                
                return result
            return dispatch
        return middleware
    
    def get_entries(self, limit: int = 20) -> list:
        """Get dev tool entries."""
        return self.entries[-limit:]
    
    def export_session(self) -> str:
        """Export session data."""
        return json.dumps(self.entries, default=str)


class MetricsMiddleware:
    """Metrics tracking middleware."""
    
    def __init__(self):
        """Initialize metrics."""
        self.dispatch_times: Dict[str, list] = {}
        self.dispatch_count: Dict[str, int] = {}
    
    def __call__(self, store_api: Dict[str, Callable]):
        """Middleware function."""
        def middleware(next_func: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                import time
                start_time = time.time()
                
                result = next_func(action)
                
                elapsed = (time.time() - start_time) * 1000  # Convert to ms
                
                if action.type not in self.dispatch_times:
                    self.dispatch_times[action.type] = []
                    self.dispatch_count[action.type] = 0
                
                self.dispatch_times[action.type].append(elapsed)
                self.dispatch_count[action.type] += 1
                
                # Keep last 100 entries per action type
                if len(self.dispatch_times[action.type]) > 100:
                    self.dispatch_times[action.type].pop(0)
                
                return result
            return dispatch
        return middleware
    
    def get_metrics(self, action_type: Optional[str] = None) -> Dict[str, Any]:
        """Get dispatch metrics."""
        if action_type:
            if action_type not in self.dispatch_times:
                return {}
            
            times = self.dispatch_times[action_type]
            return {
                "action_type": action_type,
                "count": self.dispatch_count.get(action_type, 0),
                "avg_time_ms": sum(times) / len(times) if times else 0,
                "min_time_ms": min(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
                "total_time_ms": sum(times)
            }
        
        metrics = {}
        for action_type in self.dispatch_times:
            metrics[action_type] = self.get_metrics(action_type)
        return metrics


def create_middleware_chain(*middlewares: Callable) -> Callable:
    """Create middleware chain."""
    def combined_middleware(store_api: Dict[str, Callable]):
        def middleware(next_func: Callable) -> Callable:
            for mw in reversed(middlewares):
                next_func = mw(store_api)(next_func)
            return next_func
        return middleware
    return combined_middleware
