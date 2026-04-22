"""Hooks for state management."""

from typing import Any, Dict, Callable, Optional, TypeVar, List
from dataclasses import dataclass
import logging
from .store import Store, Action, Selector

logger = logging.getLogger("hyena.state.hooks")

T = TypeVar('T')


@dataclass
class HookState:
    """Hook state container."""
    store: Optional[Store] = None
    subscribers: Dict[str, List[Callable]] = None
    
    def __post_init__(self):
        if self.subscribers is None:
            self.subscribers = {}


# Global hook state
_hook_state = HookState()


def setup_store(store: Store) -> None:
    """Setup global store for hooks."""
    _hook_state.store = store
    logger.info("Store setup for hooks")


def get_store() -> Optional[Store]:
    """Get global store."""
    return _hook_state.store


class UseStateHook:
    """useState hook implementation."""
    
    def __init__(self, initial_value: T):
        """Initialize state hook."""
        self.value = initial_value
        self.listeners: List[Callable] = []
    
    def get_value(self) -> T:
        """Get current value."""
        return self.value
    
    def set_value(self, new_value: T) -> None:
        """Set new value."""
        if self.value != new_value:
            self.value = new_value
            self._notify_listeners()
    
    def subscribe(self, listener: Callable) -> Callable:
        """Subscribe to updates."""
        self.listeners.append(listener)
        
        def unsubscribe():
            self.listeners.remove(listener)
        
        return unsubscribe
    
    def _notify_listeners(self) -> None:
        """Notify listeners of change."""
        for listener in self.listeners:
            try:
                listener(self.value)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")


def use_state(initial_value: T) -> tuple[T, Callable]:
    """useState hook."""
    hook = UseStateHook(initial_value)
    return (hook.get_value(), hook.set_value)


class UseEffectHook:
    """useEffect hook implementation."""
    
    def __init__(self, effect: Callable, dependencies: Optional[List[Any]] = None):
        """Initialize effect hook."""
        self.effect = effect
        self.dependencies = dependencies or []
        self.last_deps = None
        self.cleanup = None
    
    def run_effect(self) -> None:
        """Run effect if dependencies changed."""
        deps_changed = (
            self.last_deps is None or
            len(self.dependencies) != len(self.last_deps) or
            any(d1 != d2 for d1, d2 in zip(self.dependencies, self.last_deps))
        )
        
        if deps_changed:
            # Run cleanup from previous effect
            if self.cleanup:
                try:
                    self.cleanup()
                except Exception as e:
                    logger.error(f"Error running cleanup: {e}")
            
            # Run new effect
            try:
                self.cleanup = self.effect()
            except Exception as e:
                logger.error(f"Error running effect: {e}")
            
            self.last_deps = self.dependencies.copy()
    
    def cleanup_effect(self) -> None:
        """Cleanup effect."""
        if self.cleanup:
            try:
                self.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up effect: {e}")


def use_effect(effect: Callable, dependencies: Optional[List[Any]] = None) -> None:
    """useEffect hook."""
    hook = UseEffectHook(effect, dependencies)
    hook.run_effect()


class UseSelectorHook:
    """useSelector hook implementation."""
    
    def __init__(self, store: Store, selector: Selector):
        """Initialize selector hook."""
        self.store = store
        self.selector = selector
        self.current_value = None
        self.listeners: List[Callable] = []
        self._setup_subscription()
    
    def _setup_subscription(self) -> None:
        """Setup store subscription."""
        self.current_value = self.store.select(self.selector)
        
        def on_state_change(new_state: Any) -> None:
            new_value = self.selector(new_state)
            if new_value != self.current_value:
                self.current_value = new_value
                self._notify_listeners()
        
        self.store.subscribe(on_state_change)
    
    def get_value(self) -> Any:
        """Get selected value."""
        return self.current_value
    
    def subscribe(self, listener: Callable) -> Callable:
        """Subscribe to selector changes."""
        self.listeners.append(listener)
        
        def unsubscribe():
            self.listeners.remove(listener)
        
        return unsubscribe
    
    def _notify_listeners(self) -> None:
        """Notify listeners."""
        for listener in self.listeners:
            try:
                listener(self.current_value)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")


def use_selector(selector: Selector) -> Any:
    """useSelector hook."""
    store = get_store()
    if not store:
        raise RuntimeError("Store not initialized. Call setup_store() first.")
    
    hook = UseSelectorHook(store, selector)
    return hook.get_value()


class UseDispatchHook:
    """useDispatch hook implementation."""
    
    def __init__(self, store: Store):
        """Initialize dispatch hook."""
        self.store = store
    
    def dispatch(self, action: Action) -> Action:
        """Dispatch action."""
        return self.store.dispatch(action)


def use_dispatch() -> Callable:
    """useDispatch hook."""
    store = get_store()
    if not store:
        raise RuntimeError("Store not initialized. Call setup_store() first.")
    
    hook = UseDispatchHook(store)
    return hook.dispatch


class UseCallbackHook:
    """useCallback hook implementation."""
    
    def __init__(self, callback: Callable, dependencies: List[Any]):
        """Initialize callback hook."""
        self.callback = callback
        self.dependencies = dependencies
        self.last_deps = None
        self.memoized_callback = callback
    
    def get_callback(self) -> Callable:
        """Get memoized callback."""
        deps_changed = (
            self.last_deps is None or
            len(self.dependencies) != len(self.last_deps) or
            any(d1 != d2 for d1, d2 in zip(self.dependencies, self.last_deps))
        )
        
        if deps_changed:
            self.memoized_callback = self.callback
            self.last_deps = self.dependencies.copy()
        
        return self.memoized_callback


def use_callback(callback: Callable, dependencies: List[Any]) -> Callable:
    """useCallback hook."""
    hook = UseCallbackHook(callback, dependencies)
    return hook.get_callback()


class UseMemoHook:
    """useMemo hook implementation."""
    
    def __init__(self, compute: Callable, dependencies: List[Any]):
        """Initialize memo hook."""
        self.compute = compute
        self.dependencies = dependencies
        self.last_deps = None
        self.memoized_value = None
    
    def get_value(self) -> Any:
        """Get memoized value."""
        deps_changed = (
            self.last_deps is None or
            len(self.dependencies) != len(self.last_deps) or
            any(d1 != d2 for d1, d2 in zip(self.dependencies, self.last_deps))
        )
        
        if deps_changed:
            self.memoized_value = self.compute()
            self.last_deps = self.dependencies.copy()
        
        return self.memoized_value


def use_memo(compute: Callable, dependencies: List[Any]) -> Any:
    """useMemo hook."""
    hook = UseMemoHook(compute, dependencies)
    return hook.get_value()


class UseReducerHook:
    """useReducer hook implementation."""
    
    def __init__(self, reducer: Callable, initial_state: Any):
        """Initialize reducer hook."""
        self.reducer = reducer
        self.state = initial_state
        self.listeners: List[Callable] = []
    
    def dispatch(self, action: Action) -> None:
        """Dispatch action."""
        self.state = self.reducer(self.state, action)
        self._notify_listeners()
    
    def get_state(self) -> Any:
        """Get current state."""
        return self.state
    
    def subscribe(self, listener: Callable) -> Callable:
        """Subscribe to state changes."""
        self.listeners.append(listener)
        
        def unsubscribe():
            self.listeners.remove(listener)
        
        return unsubscribe
    
    def _notify_listeners(self) -> None:
        """Notify listeners."""
        for listener in self.listeners:
            try:
                listener(self.state)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")


def use_reducer(reducer: Callable, initial_state: Any) -> tuple[Any, Callable]:
    """useReducer hook."""
    hook = UseReducerHook(reducer, initial_state)
    return (hook.get_state(), hook.dispatch)


class UseContextHook:
    """useContext hook implementation."""
    
    def __init__(self):
        """Initialize context hook."""
        self.contexts: Dict[str, Any] = {}
        self.listeners: Dict[str, List[Callable]] = {}
    
    def create_context(self, context_id: str, initial_value: Any) -> None:
        """Create context."""
        self.contexts[context_id] = initial_value
        self.listeners[context_id] = []
    
    def get_context(self, context_id: str) -> Any:
        """Get context value."""
        return self.contexts.get(context_id)
    
    def set_context(self, context_id: str, value: Any) -> None:
        """Set context value."""
        self.contexts[context_id] = value
        self._notify_listeners(context_id)
    
    def subscribe(self, context_id: str, listener: Callable) -> Callable:
        """Subscribe to context changes."""
        if context_id not in self.listeners:
            self.listeners[context_id] = []
        
        self.listeners[context_id].append(listener)
        
        def unsubscribe():
            self.listeners[context_id].remove(listener)
        
        return unsubscribe
    
    def _notify_listeners(self, context_id: str) -> None:
        """Notify listeners."""
        value = self.contexts.get(context_id)
        for listener in self.listeners.get(context_id, []):
            try:
                listener(value)
            except Exception as e:
                logger.error(f"Error notifying context listener: {e}")


_context_hook = UseContextHook()


def create_context(context_id: str, initial_value: Any = None) -> None:
    """Create new context."""
    _context_hook.create_context(context_id, initial_value)


def use_context(context_id: str) -> Any:
    """useContext hook."""
    return _context_hook.get_context(context_id)


def set_context(context_id: str, value: Any) -> None:
    """Set context value."""
    _context_hook.set_context(context_id, value)


def clear_all_hooks() -> None:
    """Clear all hook state."""
    _context_hook.contexts.clear()
    _context_hook.listeners.clear()
    logger.info("All hooks cleared")
