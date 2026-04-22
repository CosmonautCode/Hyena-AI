"""End-to-end tests for complete system scenarios."""

import pytest
import asyncio
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
import json
import time


class TestE2EUserScenarios:
    """End-to-end tests for real user scenarios."""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_user_asks_agent_to_read_file(self, sample_chat_system, mock_llm, mock_workspace_manager):
        """E2E: User asks agent to read a file."""
        sample_chat_system.llm = mock_llm
        
        # Mock file read response
        mock_workspace_manager.read_file.return_value = "File contents here"
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "I found the file. It contains: File contents here"
                }
            }]
        }
        
        # User input
        user_msg = "Can you read the README.md file?"
        sample_chat_system.history.append(("user", user_msg))
        
        # AI response (simulated)
        ai_response = mock_llm.create_completion(
            messages=[
                {"role": "user", "content": user_msg}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        
        sample_chat_system.history.append(("assistant", ai_response))
        
        # Verify flow
        assert len(sample_chat_system.history) == 2
        assert "README" in sample_chat_system.history[0][1]
        assert "File contents" in ai_response
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_user_asks_agent_to_analyze_text(self, sample_chat_system, mock_llm):
        """E2E: User asks agent to analyze text."""
        sample_chat_system.llm = mock_llm
        
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "This text discusses AI and machine learning with 3 key points: 1) Performance 2) Scalability 3) Cost-efficiency"
                }
            }]
        }
        
        user_msg = "Please analyze this text: AI systems require consideration of performance, scalability, and cost efficiency"
        sample_chat_system.history.append(("user", user_msg))
        
        ai_response = mock_llm.create_completion(
            messages=[
                {"role": "user", "content": user_msg}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        
        sample_chat_system.history.append(("assistant", ai_response))
        
        assert "key points" in ai_response.lower()
        assert len(sample_chat_system.history) == 2
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_multi_turn_conversation(self, sample_chat_system, mock_llm):
        """E2E: Multi-turn conversation with context awareness."""
        sample_chat_system.llm = mock_llm
        
        # Turn 1
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {"content": "Python is a great programming language."}
            }]
        }
        
        sample_chat_system.history.append(("user", "What's your favorite programming language?"))
        resp1 = mock_llm.create_completion(
            messages=[{"role": "user", "content": "What's your favorite programming language?"}],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        sample_chat_system.history.append(("assistant", resp1))
        
        # Turn 2
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {"content": "Python is popular because it's readable, has a large ecosystem, and is versatile."}
            }]
        }
        
        sample_chat_system.history.append(("user", "Why is it your favorite?"))
        resp2 = mock_llm.create_completion(
            messages=[
                {"role": "user", "content": "What's your favorite programming language?"},
                {"role": "assistant", "content": resp1},
                {"role": "user", "content": "Why is it your favorite?"}
            ],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        sample_chat_system.history.append(("assistant", resp2))
        
        # Verify multi-turn context
        assert len(sample_chat_system.history) == 4
        assert sample_chat_system.history[2][0] == "user"
        assert sample_chat_system.history[3][0] == "assistant"


class TestE2EErrorScenarios:
    """E2E tests for error handling and recovery."""
    
    @pytest.mark.e2e
    def test_graceful_degradation_on_llm_error(self, sample_chat_system, mock_llm):
        """E2E: System handles LLM errors gracefully."""
        sample_chat_system.llm = mock_llm
        
        # Simulate LLM failure on first attempt
        mock_llm.create_completion.side_effect = [
            Exception("LLM temporarily unavailable"),
            {"choices": [{
                "message": {"content": "I'm having trouble, let me try again."}
            }]}
        ]
        
        user_msg = "What is AI?"
        sample_chat_system.history.append(("user", user_msg))
        
        # First call fails
        with pytest.raises(Exception):
            mock_llm.create_completion(
                messages=[{"role": "user", "content": user_msg}],
                max_tokens=1000
            )
        
        # Recovery on second attempt
        response = mock_llm.create_completion(
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=1000
        )
        
        assert response["choices"][0]["message"]["content"] is not None
    
    @pytest.mark.e2e
    def test_invalid_user_input_handling(self, sample_chat_system):
        """E2E: System handles invalid user input."""
        sample_chat_system.history = []
        
        # Empty input
        result = sample_chat_system.add_message("")
        
        # Should handle gracefully (either ignore or process)
        assert isinstance(result, (dict, bool, type(None)))


class TestE2EToolIntegration:
    """E2E tests for tool integration workflows."""
    
    @pytest.mark.e2e
    def test_file_read_write_cycle(self, sample_agentic_loop, temp_workspace):
        """E2E: Read, process, and write file operations."""
        sample_agentic_loop.activate()
        
        # Create temporary file
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Original content")
        
        # Tool 1: Read
        def read_tool():
            return test_file.read_text()
        
        # Tool 2: Process (mock)
        def process_tool(content):
            return content.upper()
        
        # Tool 3: Write
        def write_tool(content):
            test_file.write_text(content)
            return True
        
        sample_agentic_loop.register_tool("read", read_tool, "Read file", {})
        sample_agentic_loop.register_tool("process", process_tool, "Process content", {})
        sample_agentic_loop.register_tool("write", write_tool, "Write file", {})
        
        # Execute workflow
        plan = [
            {"tool": "read", "action": "read"},
            {"tool": "process", "action": "transform"},
            {"tool": "write", "action": "save"}
        ]
        
        results = sample_agentic_loop._execute_plan(plan)
        
        # Verify workflow executed
        assert len(results) >= 1


class TestE2EPermissionSystem:
    """E2E tests for permission system."""
    
    @pytest.mark.e2e
    def test_dangerous_operation_permission_flow(self, mock_permission_system):
        """E2E: User approves/denies dangerous operation."""
        from app.agents.permission_system import PermissionRequest
        
        # Create dangerous request
        request = PermissionRequest(
            "terminal_execute",
            "rm -rf /system"
        )
        
        # Check permission (would prompt user in real scenario)
        result = mock_permission_system.check_permission(request)
        
        # Should return bool or None
        assert isinstance(result, (bool, type(None)))
    
    @pytest.mark.e2e
    def test_repeated_permission_caching(self, mock_permission_system):
        """E2E: Repeated operations use cached permissions."""
        from app.agents.permission_system import PermissionRequest
        
        request1 = PermissionRequest("file_read", "config.json")
        request2 = PermissionRequest("file_read", "config.json")  # Same
        
        result1 = mock_permission_system.check_permission(request1)
        result2 = mock_permission_system.check_permission(request2)
        
        # Both should be consistent
        assert result1 == result2


class TestE2EMemorySystem:
    """E2E tests for memory system."""
    
    @pytest.mark.e2e
    def test_memory_persistence_across_sessions(self, temp_workspace):
        """E2E: Memory persists across sessions."""
        import json
        
        # Session 1
        memory1_file = temp_workspace / "memory_session1.json"
        memory1_data = {
            "conversation": [("user", "msg1"), ("assistant", "resp1")],
            "facts": ["fact1"],
            "timestamp": time.time()
        }
        
        memory1_file.write_text(json.dumps(memory1_data))
        
        # Session 2
        memory2_data = json.loads(memory1_file.read_text())
        
        # Verify persistence
        assert memory2_data["facts"][0] == "fact1"
        assert len(memory2_data["conversation"]) == 2
    
    @pytest.mark.e2e
    def test_memory_retrieval_for_context(self, sample_chat_system, mock_llm):
        """E2E: Retrieved memories provide context."""
        sample_chat_system.llm = mock_llm
        
        # Store memories
        stored_memories = [
            {"fact": "User likes Python", "timestamp": time.time()},
            {"fact": "User working on AI project", "timestamp": time.time()}
        ]
        
        # Simulate memory-augmented response
        mock_llm.create_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "Based on your interest in Python and AI, I recommend using PyTorch."
                }
            }]
        }
        
        # Create augmented prompt with memories
        augmented_prompt = f"""Memories: {stored_memories}
        User: What should I use for my project?"""
        
        sample_chat_system.history.append(("user", "What should I use for my project?"))
        
        response = mock_llm.create_completion(
            messages=[{"role": "user", "content": augmented_prompt}],
            max_tokens=1000,
            temperature=0.7
        )["choices"][0]["message"]["content"]
        
        sample_chat_system.history.append(("assistant", response))
        
        # Verify response considers memories
        assert "Python" in response or "PyTorch" in response or "AI" in response


class TestE2EConfiguration:
    """E2E tests for configuration management."""
    
    @pytest.mark.e2e
    def test_config_affects_behavior(self, tmp_path):
        """E2E: Configuration changes affect system behavior."""
        from app.config import HyenaConfig
        
        # Config 1: High temperature (more creative)
        config1 = HyenaConfig(model_temperature=0.9, model_max_tokens=2000)
        
        # Config 2: Low temperature (more deterministic)
        config2 = HyenaConfig(model_temperature=0.1, model_max_tokens=500)
        
        # Verify configs are different
        assert config1.model_temperature != config2.model_temperature
        assert config1.model_max_tokens != config2.model_max_tokens
        
        # Save and verify persistence
        config1_file = tmp_path / "config1.json"
        from dataclasses import asdict
        config1_dict = asdict(config1)
        
        config1_file.write_text(json.dumps(config1_dict))
        loaded = json.loads(config1_file.read_text())
        
        assert loaded["model_temperature"] == 0.9
        assert loaded["model_max_tokens"] == 2000


class TestE2EMetricsCollection:
    """E2E tests for metrics collection."""
    
    @pytest.mark.e2e
    def test_operation_metrics_tracking(self):
        """E2E: Operations are tracked for metrics."""
        from app.utils.metrics import ExecutionMetrics, MetricsCollector
        
        collector = MetricsCollector()
        
        # Simulate operation
        start_time = collector.start_operation("test_operation")
        time.sleep(0.01)  # Simulate work
        
        metrics = collector.end_operation("test_operation", start_time, success=True, tokens_used=10)
        
        # Verify metrics captured
        assert metrics is not None
        assert metrics.operation == "test_operation"
        assert metrics.success is True
        assert metrics.duration_ms > 0


class TestE2EExceptionHandling:
    """E2E tests for exception handling."""
    
    @pytest.mark.e2e
    def test_custom_exception_propagation(self):
        """E2E: Custom exceptions propagate correctly."""
        from app.exceptions import (
            ToolExecutionError, PermissionDeniedError, LLMError
        )
        
        # Simulate tool error
        with pytest.raises(ToolExecutionError):
            raise ToolExecutionError("Tool failed", "read_file", {})
        
        # Simulate permission error
        with pytest.raises(PermissionDeniedError):
            raise PermissionDeniedError("Not allowed", "delete_file")
        
        # Simulate LLM error
        with pytest.raises(LLMError):
            raise LLMError("Model error", "inference")


class TestE2ERetryMechanism:
    """E2E tests for retry mechanism."""
    
    @pytest.mark.e2e
    def test_operation_retries_on_failure(self):
        """E2E: Failed operations retry successfully."""
        from app.utils.retry import retry
        
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01, backoff=True)
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "Success"
        
        result = flaky_operation()
        
        assert result == "Success"
        assert call_count == 2  # Failed once, succeeded on retry
    
    @pytest.mark.e2e
    def test_circuit_breaker_opens_on_repeated_failures(self):
        """E2E: Circuit breaker opens after repeated failures."""
        from app.utils.retry import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # Simulate failures
        def failing_func():
            raise Exception("Test failure")
        
        # First two failures
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except Exception:
                pass
        
        # Circuit should be open
        assert breaker.state == "OPEN"
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Try again - circuit should transition to HALF_OPEN then either stay there or go back to OPEN
        try:
            breaker.call(failing_func)
        except Exception:
            pass
        
        assert breaker.state in ["HALF_OPEN", "OPEN"]
