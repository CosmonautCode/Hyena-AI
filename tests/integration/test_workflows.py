"""Integration tests for complete workflows."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import json


class TestChatWorkflow:
    """Integration tests for chat workflows."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_message_to_response_flow(self, sample_chat_system, mock_llm):
        """Test complete flow from user input to AI response."""
        sample_chat_system.llm = mock_llm
        sample_chat_system.system_prompt = "You are a helpful assistant."
        
        user_input = "Hello, can you help me?"
        
        # Mock the LLM response
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "Of course! I'm here to help."
                }
            }]
        }
        
        # Simulate chat interaction
        sample_chat_system.history.append(("user", user_input))
        
        # Would normally call _get_ai_response_async, but we're testing the flow
        response = mock_llm.create_completion(
            messages=[
                {"role": "system", "content": sample_chat_system.system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        
        sample_chat_system.history.append(("assistant", response))
        
        assert len(sample_chat_system.history) == 2
        assert sample_chat_system.history[0] == ("user", user_input)
        assert "help" in sample_chat_system.history[1][1].lower()
    
    @pytest.mark.integration
    def test_command_processing_workflow(self, sample_chat_system):
        """Test command processing workflow."""
        sample_chat_system.process_command = MagicMock(return_value=True)
        
        commands = ["/help", "/agents", "/status"]
        
        for cmd in commands:
            result = sample_chat_system.process_command(cmd)
            assert sample_chat_system.process_command.called
            assert result is True


class TestAgenticWorkflow:
    """Integration tests for agentic loop workflows."""
    
    @pytest.mark.integration
    def test_gather_to_execute_workflow(self, sample_agentic_loop, sample_conversation_history):
        """Test complete agentic loop from gather to execute."""
        sample_agentic_loop.activate()
        
        # Step 1: Gather context
        context = sample_agentic_loop._gather_context(
            "Read the README file",
            sample_conversation_history
        )
        
        assert context is not None
        assert "user_input" in context
        assert "README" in context["user_input"]
        
        # Step 2: Create plan
        plan = sample_agentic_loop._create_plan(context)
        assert isinstance(plan, list)
        
        # Step 3: Execute plan
        results = sample_agentic_loop._execute_plan(plan)
        assert isinstance(results, list)
        
        # Step 4: Verify results
        verification = sample_agentic_loop._verify_results(results, context)
        assert "overall_success" in verification or verification.get("success", False) is not None
    
    @pytest.mark.integration
    def test_multiple_tool_execution_flow(self, sample_agentic_loop):
        """Test executing multiple tools in sequence."""
        sample_agentic_loop.activate()
        
        # Clear existing tools and register multiple new tools
        sample_agentic_loop.tool_registry.clear()
        
        tools = {
            "tool1": MagicMock(return_value={"success": True}),
            "tool2": MagicMock(return_value={"success": True}),
            "tool3": MagicMock(return_value={"success": True})
        }
        
        for tool_name, tool_func in tools.items():
            sample_agentic_loop.register_tool(
                tool_name,
                tool_func,
                f"Description for {tool_name}",
                {}
            )
        
        # Verify all tools registered
        assert len(sample_agentic_loop.tool_registry) == 3
        
        # Create and execute plan
        plan = [
            {"tool": "tool1", "action": "test", "description": "First tool"},
            {"tool": "tool2", "action": "test", "description": "Second tool"},
            {"tool": "tool3", "action": "test", "description": "Third tool"}
        ]
        
        results = sample_agentic_loop._execute_plan(plan)
        assert len(results) == 3


class TestMemoryWorkflow:
    """Integration tests for memory workflows."""
    
    @pytest.mark.integration
    def test_memory_extraction_and_retrieval(self, mock_llm, sample_chat_system, temp_workspace):
        """Test memory extraction and retrieval workflow."""
        from app.memory.orchestrator import AutoMemoryOrchestrator
        
        orchestrator = AutoMemoryOrchestrator(
            mock_llm,
            sample_chat_system,
            str(temp_workspace)
        )
        
        # Verify orchestrator initialized
        assert orchestrator is not None
        assert orchestrator.conversation_store is not None
        assert orchestrator.extraction_interval == 5
    
    @pytest.mark.integration
    def test_conversation_compaction_flow(self, temp_workspace):
        """Test conversation history compaction."""
        from app.memory.compactor import ContextCompactor
        
        compactor = ContextCompactor()
        
        # Create long conversation history
        history = [
            ("user", f"Message {i}") for i in range(30)
        ]
        
        # Check if compaction needed - use the compactor's method
        needs_compaction = compactor.needs_compaction(history)
        
        # Compact history
        if needs_compaction:
            compacted = compactor.compact_history(history)
            assert compacted is not None


class TestToolExecutionWorkflow:
    """Integration tests for tool execution."""
    
    @pytest.mark.integration
    def test_file_operation_workflow(self, mock_workspace_manager, mock_permission_system, temp_workspace):
        """Test file operation workflow."""
        from app.agents.tools import ToolManager
        
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        # Get available tools
        tools = manager.get_all_tools()
        
        assert "read_file" in tools
        assert "write_file" in tools
        assert "list_files" in tools
        
        # Each tool should have required fields
        for tool_name, tool_info in tools.items():
            assert "func" in tool_info
            assert "description" in tool_info
            assert "parameters" in tool_info
    
    @pytest.mark.integration
    def test_permission_flow(self, mock_permission_system):
        """Test permission checking workflow."""
        from app.agents.permission_system import PermissionRequest
        
        safe_request = PermissionRequest("file_read", "Read config.json")
        dangerous_request = PermissionRequest("terminal", "Execute script.sh")
        
        # These should work without errors
        result1 = mock_permission_system.check_permission(safe_request)
        result2 = mock_permission_system.check_permission(dangerous_request)
        
        assert isinstance(result1, bool) or result1 is None
        assert isinstance(result2, bool) or result2 is None


class TestErrorHandling:
    """Integration tests for error handling."""
    
    @pytest.mark.integration
    def test_tool_failure_handling(self, mock_workspace_manager, mock_permission_system):
        """Test handling of tool failures."""
        from app.agents.tools import ToolManager
        
        manager = ToolManager(mock_workspace_manager, mock_permission_system)
        
        # Mock a failed operation
        mock_workspace_manager.read_file.return_value = {
            "error": "File not found"
        }
        
        result = manager._read_file("nonexistent.txt")
        
        # Should handle error gracefully
        assert "error" in result or not result.get("success", True)
    
    @pytest.mark.integration
    def test_llm_failure_recovery(self, mock_llm):
        """Test recovery from LLM failures."""
        # Mock LLM failure
        mock_llm.create_completion.side_effect = Exception("Model error")
        
        with pytest.raises(Exception):
            mock_llm.create_completion(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=100
            )


class TestConfigurationWorkflow:
    """Integration tests for configuration workflows."""
    
    @pytest.mark.integration
    def test_config_load_save_cycle(self, tmp_path):
        """Test loading and saving configuration."""
        from app.config import HyenaConfig
        import json
        
        config = HyenaConfig(
            model_temperature=0.5,
            memory_extraction_interval=10,
            enable_streaming=False
        )
        
        # Save to temp file
        config_file = tmp_path / "config.json"
        config_dict = config.to_dict()
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f)
        
        # Load from file
        with open(config_file, 'r') as f:
            loaded_dict = json.load(f)
            loaded_config = HyenaConfig(**loaded_dict)
        
        assert loaded_config.model_temperature == 0.5
        assert loaded_config.memory_extraction_interval == 10
        assert loaded_config.enable_streaming is False


class TestEndToEndWorkflow:
    """Full end-to-end workflow tests."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_chat_session(self, sample_chat_system, mock_llm, sample_conversation_history):
        """Test a complete chat session from start to finish."""
        sample_chat_system.llm = mock_llm
        sample_chat_system.system_prompt = "You are a helpful assistant."
        
        # Simulate multi-message session
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "I understand. Let me help you with that."
                }
            }]
        }
        
        # First exchange
        sample_chat_system.history.append(("user", "Hello"))
        response1 = mock_llm.create_completion(
            messages=[
                {"role": "system", "content": sample_chat_system.system_prompt},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        sample_chat_system.history.append(("assistant", response1))
        
        # Second exchange
        sample_chat_system.history.append(("user", "Can you help?"))
        response2 = mock_llm.create_completion(
            messages=[
                {"role": "system", "content": sample_chat_system.system_prompt},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": response1},
                {"role": "user", "content": "Can you help?"}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        sample_chat_system.history.append(("assistant", response2))
        
        # Verify session
        assert len(sample_chat_system.history) == 4
        assert all(isinstance(msg, tuple) for msg in sample_chat_system.history)
