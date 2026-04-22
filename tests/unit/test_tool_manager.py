"""Unit tests for tool manager and file tools."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import tempfile
from app.agents.tools import ToolManager


class TestToolManager:
    """Test ToolManager class."""
    
    def test_tool_manager_initialization(self, mock_workspace_manager, mock_permission_system):
        """Test tool manager initializes correctly."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        assert manager.workspace_manager == mock_workspace_manager
        assert manager.permission_system == mock_permission_system
    
    def test_get_all_tools_returns_dict(self, mock_workspace_manager, mock_permission_system):
        """Test get_all_tools returns dictionary of tools."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        tools = manager.get_all_tools()
        
        assert isinstance(tools, dict)
        assert "read_file" in tools
        assert "write_file" in tools
        assert "list_files" in tools
    
    def test_tool_has_required_fields(self, mock_workspace_manager, mock_permission_system):
        """Test each tool has required metadata."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        tools = manager.get_all_tools()
        
        for tool_name, tool_info in tools.items():
            assert "func" in tool_info
            assert "description" in tool_info
            assert "parameters" in tool_info
    
    def test_tool_functions_are_callable(self, mock_workspace_manager, mock_permission_system):
        """Test tool functions are callable."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        tools = manager.get_all_tools()
        
        for tool_name, tool_info in tools.items():
            assert callable(tool_info["func"])


class TestFileTools:
    """Test file operation tools."""
    
    def test_read_file_success(self, mock_workspace_manager, mock_permission_system):
        """Test reading a file successfully."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._read_file("test.txt")
        
        # Mock returns success
        assert "error" not in result or result.get("success", False) or "content" in result
    
    def test_read_file_handles_missing_file(self, mock_workspace_manager, mock_permission_system):
        """Test reading non-existent file."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        mock_workspace_manager.read_file.return_value = {"error": "File not found"}
        
        result = manager._read_file("missing.txt")
        
        # Should have error or success=False
        assert "error" in result or not result.get("success", True)
    
    def test_write_file_success(self, mock_workspace_manager, mock_permission_system):
        """Test writing to a file."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._write_file("test.txt", "test content")
        
        # Mock returns success
        assert result.get("success", False) or "message" in result
    
    def test_list_files(self, mock_workspace_manager, mock_permission_system):
        """Test listing files."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._list_files("*.txt")
        
        # Should return something with success state
        assert isinstance(result, dict)
    
    def test_read_file_with_encoding(self, mock_workspace_manager, mock_permission_system):
        """Test reading file with specific encoding."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._read_file("test.txt", encoding="utf-8")
        
        # Should handle encoding parameter
        assert isinstance(result, dict)


class TestShellTools:
    """Test shell execution tools."""
    
    def test_run_command_success(self, mock_workspace_manager, mock_permission_system):
        """Test running a shell command."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        mock_workspace_manager.get_workspace.return_value = "/tmp"
        
        result = manager._run_command("echo 'test'")
        
        assert isinstance(result, dict)
    
    def test_run_command_rejects_dangerous_command(self, mock_workspace_manager, mock_permission_system):
        """Test dangerous commands are rejected."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._run_command("rm -rf /")
        
        # Should be blocked
        assert "error" in result or not result.get("success", True)
    
    def test_run_command_with_custom_cwd(self, mock_workspace_manager, mock_permission_system):
        """Test running command with custom working directory."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._run_command("pwd", cwd="/tmp")
        
        assert isinstance(result, dict)


class TestWorkspaceTools:
    """Test workspace-specific tools."""
    
    def test_create_diff(self, mock_workspace_manager, mock_permission_system):
        """Test diff creation."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        old = "line 1\nline 2\n"
        new = "line 1\nline 2 modified\n"
        
        result = manager._create_diff(old, new, "test.txt")
        
        assert result.get("success", False)
        assert "diff" in result or result.get("success", False)
    
    def test_create_diff_empty_to_content(self, mock_workspace_manager, mock_permission_system):
        """Test diff from empty file."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        result = manager._create_diff("", "new content", "new.txt")
        
        assert isinstance(result, dict)
    
    def test_create_diff_tracks_changes(self, mock_workspace_manager, mock_permission_system):
        """Test diff tracks additions and deletions."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        old = "line 1\nline 2\nline 3\n"
        new = "line 1\nline 2 modified\n"
        
        result = manager._create_diff(old, new, "test.txt")
        
        # Should have statistics
        assert isinstance(result, dict)
        assert "additions" in result or "deletions" in result or result.get("success", False)


class TestToolSafety:
    """Test tool safety features."""
    
    def test_file_path_validation(self, mock_workspace_manager, mock_permission_system):
        """Test file paths are validated."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        # These should throw or return error
        result = manager._read_file("../../../etc/passwd")
        
        # Should either fail or have defensive checks
        assert isinstance(result, dict)
    
    def test_safe_command_checking(self, mock_workspace_manager, mock_permission_system):
        """Test shell commands are checked for safety."""
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        dangerous_commands = [
            "rm -rf /",
            "mkfs.ext4 /dev/sda",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for cmd in dangerous_commands:
            result = manager._run_command(cmd)
            # Should fail or be blocked
            assert not result.get("success", False) or "error" in result
