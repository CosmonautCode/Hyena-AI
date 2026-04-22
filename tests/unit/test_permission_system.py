"""Unit tests for permission system."""

import pytest
from unittest.mock import MagicMock, patch
from app.agents.permission_system import (
    PermissionSystem, PermissionMode, PermissionRequest
)


class TestPermissionRequest:
    """Test PermissionRequest dataclass."""
    
    def test_permission_request_creation(self):
        """Test creating a permission request."""
        request = PermissionRequest(
            operation_type="file_write",
            description="Write to config.json"
        )
        
        assert request.operation_type == "file_write"
        assert request.description == "Write to config.json"
        assert request.details is None
    
    def test_permission_request_with_details(self):
        """Test permission request with additional details."""
        details = {"filename": "config.json", "size": 1024}
        request = PermissionRequest(
            operation_type="file_write",
            description="Write to config.json",
            details=details
        )
        
        assert request.details == details
        assert request.details["filename"] == "config.json"


class TestPermissionMode:
    """Test PermissionMode enum."""
    
    def test_permission_modes_exist(self):
        """Test all permission modes are defined."""
        assert hasattr(PermissionMode, 'ASK')
        assert hasattr(PermissionMode, 'AUTO')
    
    def test_permission_mode_values(self):
        """Test permission mode values."""
        assert PermissionMode.ASK.value == "ask"
        assert PermissionMode.AUTO.value == "auto"


class TestPermissionSystem:
    """Test PermissionSystem class."""
    
    def test_permission_system_initialization(self):
        """Test permission system initializes correctly."""
        system = PermissionSystem()
        
        assert system.current_mode == PermissionMode.ASK
    
    def test_set_mode_with_string(self):
        """Test setting mode with string."""
        system = PermissionSystem()
        
        system.set_mode("auto")
        assert system.current_mode == PermissionMode.AUTO
        
        system.set_mode("ask")
        assert system.current_mode == PermissionMode.ASK
    
    def test_set_mode_with_enum(self):
        """Test setting mode with enum."""
        system = PermissionSystem()
        
        system.set_mode(PermissionMode.AUTO)
        assert system.current_mode == PermissionMode.AUTO
    
    def test_set_mode_case_insensitive(self):
        """Test mode setting is case insensitive."""
        system = PermissionSystem()
        
        system.set_mode("ASK")
        assert system.current_mode == PermissionMode.ASK
        
        system.set_mode("AUTO")
        assert system.current_mode == PermissionMode.AUTO
    
    def test_set_mode_invalid_raises_error(self):
        """Test setting invalid mode raises ValueError."""
        system = PermissionSystem()
        
        with pytest.raises(ValueError):
            system.set_mode("invalid")
        
        with pytest.raises(ValueError):
            system.set_mode(12345)
    
    def test_check_permission_auto_mode_safe_operations(self):
        """Test auto mode auto-approves safe operations."""
        system = PermissionSystem()
        system.set_mode("auto")
        
        # Safe operations
        assert system.check_permission(
            PermissionRequest("file_read", "Read file")
        ) is True
    
    @patch('builtins.input', return_value='y')
    def test_check_permission_auto_mode_prompts_dangerous(self, mock_input):
        """Test auto mode prompts for dangerous operations."""
        system = PermissionSystem()
        system.set_mode("auto")
        
        # Dangerous operations should trigger prompt
        terminal_request = PermissionRequest(
            "terminal",
            "Execute shell command"
        )
        # This will call _prompt_user which returns True (mocked input returns 'y')
        result = system.check_permission(terminal_request)
        assert result is True
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='n')
    def test_check_permission_ask_mode_always_prompts(self, mock_input):
        """Test ask mode always prompts user."""
        system = PermissionSystem()
        system.set_mode("ask")
        
        request = PermissionRequest("file_read", "Read file")
        # In ask mode, all operations go through _prompt_user
        result = system.check_permission(request)
        assert result is False  # mocked input returns 'n'
        mock_input.assert_called_once()
    
    def test_permission_request_with_callback(self):
        """Test permission request with callback."""
        callback = MagicMock()
        request = PermissionRequest(
            operation_type="shell",
            description="Run shell command",
            callback=callback
        )
        
        assert request.callback == callback


class TestPermissionIntegration:
    """Integration tests for permission system."""
    
    def test_mode_switching(self):
        """Test switching between permission modes."""
        system = PermissionSystem()
        
        # Start in ask mode
        assert system.current_mode == PermissionMode.ASK
        
        # Switch to auto
        system.set_mode("auto")
        assert system.current_mode == PermissionMode.AUTO
        
        # Switch back to ask
        system.set_mode("ask")
        assert system.current_mode == PermissionMode.ASK
    
    @patch('builtins.input', return_value='y')
    def test_permission_flow(self, mock_input):
        """Test typical permission checking flow."""
        system = PermissionSystem()
        system.set_mode("auto")
        
        # Create various permission requests
        requests = [
            PermissionRequest("file_read", "Read config.json"),
            PermissionRequest("file_write", "Write to output.txt"),
            PermissionRequest("terminal", "Execute npm install")
        ]
        
        # All should return bool
        # First two: file_read is safe (returns True), file_write is dangerous (mocked to True), terminal is dangerous (mocked to True)
        results = []
        for request in requests:
            result = system.check_permission(request)
            results.append(result)
            assert isinstance(result, bool)
        
        # Expect: True (safe read), True (dangerous write, mocked), True (dangerous terminal, mocked)
        assert all(results)
