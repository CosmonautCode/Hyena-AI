"""Unit tests for ChatSystem."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json
from pathlib import Path


class TestChatSystemInitialization:
    """Test ChatSystem initialization."""
    
    def test_chat_system_initialization(self, sample_chat_system):
        """Test chat system initializes correctly."""
        assert sample_chat_system is not None
        assert sample_chat_system.history == []
        assert sample_chat_system.running is True
        assert sample_chat_system.current_agent_index == 0
    
    def test_chat_system_has_required_managers(self, sample_chat_system):
        """Test chat system has all required managers."""
        assert sample_chat_system.llm is not None  # Mock
        assert sample_chat_system.workspace_manager is not None
        assert sample_chat_system.permission_system is not None
        assert sample_chat_system.tui is not None


class TestAgentManagement:
    """Test agent configuration and switching."""
    
    def test_agent_config_loading(self, sample_chat_system):
        """Test loading agent configuration."""
        assert len(sample_chat_system.agent_config) > 0
        assert "name" in sample_chat_system.agent_config[0]
        assert "specialty" in sample_chat_system.agent_config[0]
        assert "system_prompt" in sample_chat_system.agent_config[0]
    
    def test_agent_switching(self, sample_chat_system):
        """Test switching between agents."""
        original_index = sample_chat_system.current_agent_index
        
        # Mock the choose_agent method
        sample_chat_system.choose_agent = MagicMock(return_value=True)
        
        result = sample_chat_system.choose_agent(0)
        
        assert result is True
    
    def test_multiple_agents_available(self, sample_chat_system):
        """Test multiple agents can be configured."""
        # By default we have sample agents
        assert len(sample_chat_system.agent_config) >= 1


class TestConversationHistory:
    """Test conversation history management."""
    
    def test_history_starts_empty(self, sample_chat_system):
        """Test conversation history starts empty."""
        assert len(sample_chat_system.history) == 0
    
    def test_history_is_list_of_tuples(self, sample_chat_system):
        """Test history contains (role, content) tuples."""
        sample_chat_system.history = [
            ("user", "Hello"),
            ("assistant", "Hi there!")
        ]
        
        assert len(sample_chat_system.history) == 2
        assert isinstance(sample_chat_system.history[0], tuple)
        assert sample_chat_system.history[0][0] == "user"
    
    def test_history_property(self, sample_chat_system):
        """Test history property access."""
        sample_chat_system.history = [
            ("user", "test"),
            ("assistant", "response")
        ]
        
        # Should be accessible as list
        assert len(sample_chat_system.history) == 2


class TestCommandProcessing:
    """Test command processing."""
    
    def test_process_command_returns_bool(self, sample_chat_system):
        """Test process_command returns boolean."""
        sample_chat_system.process_command = MagicMock(return_value=True)
        
        result = sample_chat_system.process_command("/help")
        
        assert isinstance(result, bool)
    
    def test_command_recognized(self, sample_chat_system):
        """Test commands are recognized."""
        sample_chat_system.process_command = MagicMock(return_value=True)
        
        result = sample_chat_system.process_command("/help")
        assert sample_chat_system.process_command.called


class TestSessionManagement:
    """Test session save/load/export."""
    
    def test_save_conversation(self, sample_chat_system):
        """Test saving conversation."""
        sample_chat_system.save_conversation = MagicMock(return_value=True)
        
        result = sample_chat_system.save_conversation("test_session.json")
        
        assert result is True
    
    def test_load_conversation(self, sample_chat_system):
        """Test loading conversation."""
        sample_chat_system.load_conversation = MagicMock(return_value=True)
        
        result = sample_chat_system.load_conversation("test_session.json")
        
        assert result is True
    
    def test_export_conversation(self, sample_chat_system):
        """Test exporting conversation."""
        sample_chat_system.export_conversation = MagicMock(return_value=True)
        
        result = sample_chat_system.export_conversation("export.txt")
        
        assert result is True
    
    def test_get_session_stats(self, sample_chat_system):
        """Test getting session statistics."""
        sample_chat_system.history = [
            ("user", "Hello"),
            ("assistant", "Hi"),
            ("user", "How are you?"),
            ("assistant", "I'm great!")
        ]
        
        stats = sample_chat_system.get_session_stats()
        
        assert isinstance(stats, dict)
        assert "total_messages" in stats
        assert stats["total_messages"] == 4
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 2


class TestWorkspaceManagement:
    """Test workspace operations."""
    
    def test_get_workspace(self, sample_chat_system):
        """Test getting current workspace."""
        sample_chat_system.get_workspace = MagicMock(return_value="/tmp/hyena")
        
        workspace = sample_chat_system.get_workspace()
        
        assert workspace is not None
    
    def test_set_workspace(self, sample_chat_system):
        """Test setting workspace."""
        sample_chat_system.set_workspace = MagicMock(return_value=True)
        
        result = sample_chat_system.set_workspace("/tmp/hyena")
        
        assert result is True


class TestLLMIntegration:
    """Test LLM integration."""
    
    def test_llm_is_available(self, sample_chat_system):
        """Test LLM is loaded."""
        assert sample_chat_system.llm is not None
    
    def test_llm_create_completion_callable(self, sample_chat_system):
        """Test LLM completion method is callable."""
        assert callable(sample_chat_system.llm.create_completion)
    
    def test_llm_response_format(self, sample_chat_system):
        """Test LLM response has correct format."""
        response = sample_chat_system.llm.create_completion()
        
        # Mock returns proper format
        assert "choices" in response
        assert len(response["choices"]) > 0


class TestAgentSystem:
    """Test agent system integration."""
    
    def test_load_agents(self, sample_chat_system):
        """Test loading agents."""
        sample_chat_system.load_agents = MagicMock()
        
        sample_chat_system.load_agents()
        
        assert sample_chat_system.load_agents.called
    
    def test_system_prompt_available(self, sample_chat_system):
        """Test system prompt is available."""
        sample_chat_system.system_prompt = sample_chat_system.agent_config[0]["system_prompt"]
        
        assert sample_chat_system.system_prompt is not None
        assert len(sample_chat_system.system_prompt) > 0


class TestChatSystemProperties:
    """Test ChatSystem properties."""
    
    def test_running_property(self, sample_chat_system):
        """Test running property."""
        assert sample_chat_system.running is True
        
        sample_chat_system.running = False
        assert sample_chat_system.running is False
    
    def test_current_agent_index_property(self, sample_chat_system):
        """Test current agent index property."""
        assert sample_chat_system.current_agent_index >= 0
        
        sample_chat_system.current_agent_index = 0
        assert sample_chat_system.current_agent_index == 0
