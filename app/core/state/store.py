"""Redux-like state management store for Hyena-AI."""

from typing import Dict, List, Any, Optional, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json

logger = logging.getLogger("hyena.state.store")

T = TypeVar('T')
S = TypeVar('S')


class ActionType(Enum):
    """Standard action types."""
    STATE_INIT = "@@INIT"
    STATE_UPDATE = "@@UPDATE"
    STATE_REPLACE = "@@REPLACE"
    HISTORY_UNDO = "@@UNDO"
    HISTORY_REDO = "@@REDO"
    MIDDLEWARE_EFFECT = "@@EFFECT"


@dataclass
class Action:
    """Redux-style action."""
    type: str
    payload: Any = None
    meta: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "payload": self.payload,
            "meta": self.meta,
            "error": self.error,
            "timestamp": self.timestamp,
        }


Reducer = Callable[[S, Action], S]
Middleware = Callable[[Dict[str, Any]], Callable[[Callable], Callable]]
Selector = Callable[[S], Any]


class Store:
    """Redux-like state management store."""
    
    def __init__(self, reducer: Reducer, initial_state: Any):
        """Initialize store."""
        self.reducer = reducer
        self.state = initial_state
        self.listeners: List[Callable] = []
        self.middlewares: List[Middleware] = []
        self.history: List[Any] = [initial_state]
        self.history_index = 0
        self.action_log: List[Action] = []
        
        logger.info("Store initialized with state")
    
    def dispatch(self, action: Action) -> Action:
        """Dispatch action to store."""
        try:
            # Run middleware chain
            for middleware in self.middlewares:
                action = middleware(self._get_store_api())(self._dispatch_next)(action)
            
            # Apply reducer
            self.state = self.reducer(self.state, action)
            
            # Update history
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.state)
            self.history_index = len(self.history) - 1
            
            # Log action
            self.action_log.append(action)
            if len(self.action_log) > 1000:
                self.action_log.pop(0)
            
            # Notify subscribers
            self._notify_subscribers()
            
            logger.debug(f"Dispatched action: {action.type}")
            return action
            
        except Exception as e:
            logger.error(f"Error dispatching action {action.type}: {e}")
            raise
    
    def _dispatch_next(self, action: Action) -> Action:
        """Next in middleware chain."""
        self.state = self.reducer(self.state, action)
        return action
    
    def _get_store_api(self) -> Dict[str, Any]:
        """Get store API for middleware."""
        return {
            "getState": self.get_state,
            "dispatch": self.dispatch,
        }
    
    def get_state(self) -> Any:
        """Get current state."""
        return self.state
    
    def subscribe(self, listener: Callable) -> Callable:
        """Subscribe to state changes."""
        self.listeners.append(listener)
        
        def unsubscribe():
            self.listeners.remove(listener)
        
        return unsubscribe
    
    def _notify_subscribers(self) -> None:
        """Notify all subscribers of state change."""
        for listener in self.listeners:
            try:
                listener(self.state)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def use_middleware(self, middleware: Middleware) -> 'Store':
        """Register middleware."""
        self.middlewares.append(middleware)
        logger.info(f"Middleware registered")
        return self
    
    def undo(self) -> bool:
        """Undo to previous state."""
        if self.history_index > 0:
            self.history_index -= 1
            self.state = self.history[self.history_index]
            self._notify_subscribers()
            logger.info("Undo")
            return True
        return False
    
    def redo(self) -> bool:
        """Redo to next state."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.state = self.history[self.history_index]
            self._notify_subscribers()
            logger.info("Redo")
            return True
        return False
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.history_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.history_index < len(self.history) - 1
    
    def get_history_depth(self) -> int:
        """Get history depth."""
        return len(self.history)
    
    def get_action_log(self, limit: int = 50) -> List[Action]:
        """Get action log."""
        return self.action_log[-limit:]
    
    def select(self, selector: Selector) -> Any:
        """Select part of state."""
        return selector(self.state)
    
    def get_state_snapshot(self) -> str:
        """Get JSON snapshot of current state."""
        from dataclasses import asdict
        
        def serializer(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            elif isinstance(obj, set):
                return list(obj)
            return str(obj)
        
        return json.dumps(self.state, default=serializer)


class CombineReducers:
    """Combines multiple reducers into one."""
    
    def __init__(self, reducers: Dict[str, Reducer]):
        """Initialize combined reducer."""
        self.reducers = reducers
    
    def __call__(self, state: Dict[str, Any], action: Action) -> Dict[str, Any]:
        """Apply reducers."""
        new_state = {}
        for key, reducer in self.reducers.items():
            new_state[key] = reducer(state.get(key), action)
        return new_state


def create_store(reducer: Reducer, initial_state: Any) -> Store:
    """Factory function to create store."""
    return Store(reducer, initial_state)


def combine_reducers(reducers: Dict[str, Reducer]) -> Reducer:
    """Combine multiple reducers."""
    combined = CombineReducers(reducers)
    return combined
