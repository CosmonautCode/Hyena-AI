"""Unit tests for agentic loop."""

import pytest
from unittest.mock import MagicMock, patch
from app.agents.loop import AgenticLoop


class TestAgenticLoopBasics:
    """Test basic AgenticLoop functionality."""
    
    def test_agentic_loop_initialization(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test agentic loop initializes correctly."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        assert loop.llm == mock_llm
        assert loop.workspace_manager == mock_workspace_manager
        assert loop.permission_system == mock_permission_system
        assert loop.tui == mock_tui
        assert loop.tool_registry == {}
        assert loop.active is False
    
    def test_activate_agentic_loop(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test activating the agentic loop."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        result = loop.activate()
        
        assert result is True
        assert loop.active is True
    
    def test_deactivate_agentic_loop(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test deactivating the agentic loop."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        loop.activate()
        
        result = loop.deactivate()
        
        assert result is True
        assert loop.active is False


class TestToolRegistry:
    """Test tool registration."""
    
    def test_register_tool(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test registering a tool."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        mock_func = MagicMock()
        loop.register_tool(
            "test_tool",
            mock_func,
            "Test tool description",
            {"param": "string"}
        )
        
        assert "test_tool" in loop.tool_registry
        assert loop.tool_registry["test_tool"]["func"] == mock_func
    
    def test_tool_registry_has_metadata(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test registered tools have required metadata."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        mock_func = MagicMock()
        loop.register_tool(
            "test_tool",
            mock_func,
            "Description",
            {"param": "type"}
        )
        
        tool = loop.tool_registry["test_tool"]
        assert "func" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert tool["description"] == "Description"
    
    def test_multiple_tool_registration(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test registering multiple tools."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        for i in range(3):
            loop.register_tool(
                f"tool_{i}",
                MagicMock(),
                f"Tool {i}",
                {}
            )
        
        assert len(loop.tool_registry) == 3


class TestContextGathering:
    """Test context gathering phase."""
    
    def test_gather_context(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test gathering context for request."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        context = loop._gather_context("What files are in the workspace?", sample_conversation_history)
        
        assert isinstance(context, dict)
        assert "user_input" in context
        assert "conversation_history" in context
        assert context["user_input"] == "What files are in the workspace?"
    
    def test_gathered_context_includes_workspace(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test gathered context includes workspace information."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        context = loop._gather_context("test", sample_conversation_history)
        
        assert "workspace" in context
        assert "available_tools" in context
        assert "timestamp" in context


class TestPlanCreation:
    """Test planning phase."""
    
    def test_create_plan(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test creating an execution plan."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        context = loop._gather_context("read the README file", sample_conversation_history)
        plan = loop._create_plan(context)
        
        assert isinstance(plan, list)
        assert len(plan) > 0
    
    def test_plan_contains_action_items(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test plan contains executable action items."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        context = loop._gather_context("write a file", sample_conversation_history)
        plan = loop._create_plan(context)
        
        for step in plan:
            assert "tool" in step or "action" in step


class TestExecution:
    """Test execution phase."""
    
    def test_execute_plan(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test executing a plan."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        plan = [
            {"tool": "general_analysis", "action": "test", "description": "test"}
        ]
        
        results = loop._execute_plan(plan)
        
        assert isinstance(results, list)
        assert len(results) == len(plan)
    
    def test_execution_results_have_status(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test execution results include status info."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        plan = [{"tool": "test", "action": "test", "description": "test"}]
        results = loop._execute_plan(plan)
        
        for result in results:
            assert "success" in result or "tool" in result


class TestVerification:
    """Test verification phase."""
    
    def test_verify_results(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui, sample_conversation_history):
        """Test verifying execution results."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        results = [
            {"tool": "file_ops", "success": True, "execution_time": 0.5},
            {"tool": "shell_ops", "success": True, "execution_time": 1.0}
        ]
        
        context = loop._gather_context("test", sample_conversation_history)
        verification = loop._verify_results(results, context)
        
        assert isinstance(verification, dict)
        assert "overall_success" in verification
        assert "successful_steps" in verification or "failed_steps" in verification


class TestProcessRequest:
    """Test full request processing."""
    
    def test_process_request_inactive_loop(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test processing request with inactive loop."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        
        result = loop.process_request("test", [])
        
        assert result.get("success", False) is False
    
    def test_process_request_active_loop(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test processing request with active loop."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        loop.activate()
        
        result = loop.process_request("test request", [])
        
        assert isinstance(result, dict)
        assert "success" in result or "plan" in result
    
    def test_process_request_includes_all_phases(self, mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
        """Test request processing goes through all phases."""
        loop = AgenticLoop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui)
        loop.activate()
        
        result = loop.process_request("test", [])
        
        # Successful processing should include plan or error
        assert "error" in result or "plan" in result or "success" in result
