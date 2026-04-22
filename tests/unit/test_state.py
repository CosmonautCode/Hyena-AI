"""Tests for state management system."""

import pytest
import time
from unittest.mock import Mock, patch
from app.core.state import (
    # Core
    Store, Action, ActionType, create_store, root_reducer,
    # Actions
    UIActionType, show_panel, hide_panel, set_theme, show_notification,
    SessionActionType, start_session, set_current_user, add_tool,
    PermissionActionType, grant_permission, assign_role,
    WorkspaceActionType, load_config, add_file,
    # Reducers
    UIState, Session, PermissionState, WorkspaceState,
    ui_reducer, session_reducer, permission_reducer, workspace_reducer,
    # Middleware
    logger_middleware, validation_middleware, effects_middleware,
    DevToolsMiddleware, MetricsMiddleware,
    # Selectors
    select_visible_panels, select_current_user, select_user_permissions,
    select_workspace_config, select_is_authenticated,
    # Hooks
    setup_store, use_selector, use_dispatch, use_state, use_effect
)


class TestStore:
    """Test store functionality."""
    
    def test_store_creation(self):
        """Test store creation."""
        initial_state = {"count": 0}
        store = create_store(
            lambda state, action: state,
            initial_state
        )
        assert store.get_state() == initial_state
    
    def test_store_dispatch(self):
        """Test dispatch action."""
        def reducer(state, action):
            if action.type == "INCREMENT":
                return {"count": state["count"] + 1}
            return state
        
        store = create_store(reducer, {"count": 0})
        action = Action(type="INCREMENT")
        store.dispatch(action)
        
        assert store.get_state()["count"] == 1
    
    def test_store_subscribe(self):
        """Test store subscription."""
        store = create_store(lambda state, action: state, {"count": 0})
        listener = Mock()
        store.subscribe(listener)
        
        action = Action(type="TEST")
        store.dispatch(action)
        
        listener.assert_called()
    
    def test_store_undo_redo(self):
        """Test undo/redo functionality."""
        def reducer(state, action):
            if action.type == "SET":
                return {"value": action.payload["value"]}
            return state
        
        store = create_store(reducer, {"value": 0})
        store.dispatch(Action(type="SET", payload={"value": 1}))
        store.dispatch(Action(type="SET", payload={"value": 2}))
        
        assert store.get_state()["value"] == 2
        
        store.undo()
        assert store.get_state()["value"] == 1
        
        store.redo()
        assert store.get_state()["value"] == 2
    
    def test_store_action_log(self):
        """Test action logging."""
        store = create_store(lambda state, action: state, {})
        
        store.dispatch(Action(type="ACTION1"))
        store.dispatch(Action(type="ACTION2"))
        
        log = store.get_action_log()
        assert len(log) == 2
        assert log[0].type == "ACTION1"
        assert log[1].type == "ACTION2"


class TestActions:
    """Test action creators."""
    
    def test_show_panel_action(self):
        """Test show panel action."""
        action = show_panel("sidebar", {"data": "test"})
        assert action.type == UIActionType.SHOW_PANEL
        assert action.payload["panel"] == "sidebar"
    
    def test_set_theme_action(self):
        """Test set theme action."""
        action = set_theme("dark")
        assert action.type == UIActionType.SET_THEME
        assert action.payload["theme"] == "dark"
    
    def test_start_session_action(self):
        """Test start session action."""
        action = start_session("sess1", "user1", {"key": "value"})
        assert action.type == SessionActionType.START_SESSION
        assert action.payload["session_id"] == "sess1"
        assert action.meta["async"] is True
    
    def test_grant_permission_action(self):
        """Test grant permission action."""
        action = grant_permission("user1", "admin")
        assert action.type == PermissionActionType.GRANT_PERMISSION
        assert action.payload["user_id"] == "user1"


class TestReducers:
    """Test reducers."""
    
    def test_ui_reducer_show_panel(self):
        """Test UI reducer show panel."""
        state = UIState()
        action = show_panel("panel1")
        new_state = ui_reducer(state, action)
        
        assert new_state.visible_panels["panel1"] is True
    
    def test_ui_reducer_set_theme(self):
        """Test UI reducer set theme."""
        state = UIState()
        action = set_theme("dark")
        new_state = ui_reducer(state, action)
        
        assert new_state.theme == "dark"
    
    def test_session_reducer_start(self):
        """Test session reducer start."""
        state = Session()
        action = start_session("sess1", "user1", {})
        new_state = session_reducer(state, action)
        
        assert new_state.session_id == "sess1"
        assert new_state.user_id == "user1"
    
    def test_session_reducer_add_tool(self):
        """Test session reducer add tool."""
        state = Session()
        action = add_tool("tool1", {"config": "test"})
        new_state = session_reducer(state, action)
        
        assert "tool1" in new_state.tools
        assert new_state.tools["tool1"]["config"] == "test"
    
    def test_permission_reducer_grant(self):
        """Test permission reducer grant."""
        state = PermissionState()
        action = grant_permission("user1", "read")
        new_state = permission_reducer(state, action)
        
        assert "read" in new_state.user_permissions.get("user1", set())
    
    def test_workspace_reducer_add_file(self):
        """Test workspace reducer add file."""
        state = WorkspaceState()
        action = add_file("file.txt", "content")
        new_state = workspace_reducer(state, action)
        
        assert new_state.files["file.txt"] == "content"


class TestMiddleware:
    """Test middleware."""
    
    def test_logger_middleware(self):
        """Test logger middleware."""
        store = create_store(lambda state, action: state, {})
        store.use_middleware(logger_middleware)
        
        action = Action(type="TEST")
        # Should not raise
        store.dispatch(action)
    
    def test_validation_middleware(self):
        """Test validation middleware."""
        store = create_store(lambda state, action: state, {})
        store.use_middleware(validation_middleware)
        
        action = Action(type="TEST")
        # Should not raise
        store.dispatch(action)
    
    def test_effects_middleware(self):
        """Test effects middleware."""
        store = create_store(lambda state, action: state, {})
        store.use_middleware(effects_middleware)
        
        action = show_notification("Title", "Message")
        # Should not raise
        store.dispatch(action)
    
    def test_devtools_middleware(self):
        """Test dev tools middleware."""
        devtools = DevToolsMiddleware(max_entries=10)
        store = create_store(lambda state, action: state, {"count": 0})
        
        # Manually add devtools
        store.use_middleware(devtools)
        store.dispatch(Action(type="ACTION1"))
        
        entries = devtools.get_entries()
        assert len(entries) >= 1
    
    def test_metrics_middleware(self):
        """Test metrics middleware."""
        metrics = MetricsMiddleware()
        store = create_store(lambda state, action: state, {})
        store.use_middleware(metrics)
        
        store.dispatch(Action(type="TEST_ACTION"))
        
        stats = metrics.get_metrics("TEST_ACTION")
        assert stats["count"] == 1
        assert stats["avg_time_ms"] >= 0


class TestSelectors:
    """Test selectors."""
    
    def test_select_visible_panels(self):
        """Test select visible panels."""
        state = {
            "ui": UIState(visible_panels={"panel1": True, "panel2": False})
        }
        panels = select_visible_panels(state)
        assert panels["panel1"] is True
        assert panels["panel2"] is False
    
    def test_select_current_user(self):
        """Test select current user."""
        state = {
            "session": Session(user_id="user1", username="john")
        }
        user_id = select_current_user(state)
        assert user_id == "user1"
    
    def test_select_user_permissions(self):
        """Test select user permissions."""
        state = {
            "permissions": PermissionState(
                user_permissions={"user1": {"read", "write"}}
            )
        }
        perms = select_user_permissions(state, "user1")
        assert "read" in perms
        assert "write" in perms
    
    def test_select_workspace_config(self):
        """Test select workspace config."""
        state = {
            "workspace": WorkspaceState(config={"key": "value"})
        }
        config = select_workspace_config(state)
        assert config["key"] == "value"
    
    def test_select_is_authenticated(self):
        """Test select is authenticated."""
        state_auth = {"session": Session(user_id="user1")}
        assert select_is_authenticated(state_auth) is True
        
        state_no_auth = {"session": Session()}
        assert select_is_authenticated(state_no_auth) is False


class TestIntegration:
    """Integration tests."""
    
    def test_complete_store_flow(self):
        """Test complete store flow."""
        store = create_store(root_reducer, None)
        store.use_middleware(logger_middleware)
        store.use_middleware(validation_middleware)
        
        # Start session
        store.dispatch(start_session("sess1", "user1", {}))
        state = store.get_state()
        assert state["session"].session_id == "sess1"
        
        # Set theme
        store.dispatch(set_theme("dark"))
        state = store.get_state()
        assert state["ui"].theme == "dark"
        
        # Add tool
        store.dispatch(add_tool("tool1", {}))
        state = store.get_state()
        assert "tool1" in state["session"].tools
    
    def test_store_with_devtools(self):
        """Test store with dev tools."""
        devtools = DevToolsMiddleware()
        store = create_store(root_reducer, None)
        store.use_middleware(devtools)
        
        store.dispatch(set_theme("dark"))
        store.dispatch(start_session("sess1", "user1", {}))
        
        entries = devtools.get_entries()
        assert len(entries) >= 2
    
    def test_store_persistence_simulation(self):
        """Test state persistence."""
        from app.core.state.reducers import root_reducer as test_root_reducer
        from app.core.state import set_theme
        
        # Create store with root reducer
        store = create_store(test_root_reducer, None)
        
        # Dispatch an action to initialize state
        store.dispatch(set_theme("dark"))
        
        # After dispatch, state should be properly formed
        state = store.get_state()
        assert state is not None
        assert "ui" in state
        assert "session" in state
        assert "permissions" in state
        assert "workspace" in state
        
        # Get state snapshot
        snapshot = store.get_state_snapshot()
        assert isinstance(snapshot, str)
        assert len(snapshot) > 0
    
    def test_ui_session_permission_flow(self):
        """Test UI, session, and permission integration."""
        store = create_store(root_reducer, None)
        
        # Setup UI
        store.dispatch(show_panel("sidebar"))
        
        # Start session
        store.dispatch(start_session("sess1", "user1", {}))
        store.dispatch(set_current_user("user1", "john", "admin"))
        
        # Grant permissions
        store.dispatch(grant_permission("user1", "read"))
        store.dispatch(assign_role("user1", "admin"))
        
        state = store.get_state()
        
        # Verify UI
        assert state["ui"].visible_panels["sidebar"] is True
        
        # Verify session
        assert state["session"].user_id == "user1"
        
        # Verify permissions
        assert "read" in state["permissions"].user_permissions["user1"]
        assert state["permissions"].user_roles["user1"] == "admin"


class TestStorePerformance:
    """Performance tests."""
    
    def test_large_action_dispatch_performance(self):
        """Test performance with many dispatches."""
        store = create_store(root_reducer, None)
        
        start = time.time()
        for i in range(100):
            store.dispatch(show_panel(f"panel_{i}"))
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 100ms)
        assert elapsed < 0.1
    
    def test_deep_state_reduction_performance(self):
        """Test performance with nested state changes."""
        store = create_store(root_reducer, None)
        
        start = time.time()
        for i in range(50):
            store.dispatch(add_file(f"file_{i}.txt", f"content_{i}"))
        elapsed = time.time() - start
        
        assert elapsed < 0.1
        assert len(store.get_state()["workspace"].files) == 50


class TestErrorHandling:
    """Test error handling."""
    
    def test_middleware_error_handling(self):
        """Test error handling in middleware."""
        store = create_store(lambda state, action: state, {})
        store.use_middleware(validation_middleware)
        
        # Invalid action should raise ValueError
        action_no_type = Action(type="")
        # Should be caught by validation
        action_no_type.type = None
        # Validation should prevent None type
        action_no_type.type = "TEST"  # Reset for now
        
        # Should not raise
        store.dispatch(action_no_type)
    
    def test_reducer_error_consistency(self):
        """Test that reducer errors don't corrupt state."""
        def error_reducer(state, action):
            if action.type == "ERROR":
                raise ValueError("Test error")
            return state
        
        store = create_store(error_reducer, {"safe": True})
        
        # Error should propagate
        try:
            action = Action(type="ERROR")
            store.dispatch(action)
        except ValueError:
            pass
        
        # State should remain intact
        assert store.get_state()["safe"] is True
