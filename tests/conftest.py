"""Pytest configuration and fixtures for Hyena-AI tests."""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment after each test."""
    yield
    # Cleanup happens here
    pass


@pytest.fixture
def temp_workspace():
    """Provide a temporary workspace directory for tests.
    
    Yields:
        Path: Temporary directory path
    """
    temp_dir = tempfile.mkdtemp(prefix="hyena_test_")
    yield Path(temp_dir)
    # Cleanup
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_llm():
    """Provide a mock LLM instance."""
    llm = MagicMock()
    llm.create_completion.return_value = {
        "choices": [{
            "message": {
                "content": "Mock AI response"
            }
        }]
    }
    return llm


@pytest.fixture
def mock_workspace_manager():
    """Provide a mock workspace manager."""
    manager = MagicMock()
    manager.working_directory = Path(tempfile.gettempdir())
    manager.get_workspace.return_value = str(manager.working_directory)
    manager.read_file.return_value = {"content": "test content", "type": "text"}
    manager.write_file.return_value = {"success": True, "message": "File written"}
    return manager


@pytest.fixture
def mock_permission_system():
    """Provide a mock permission system."""
    system = MagicMock()
    system.check_permission.return_value = True
    system.current_mode = "ask"
    return system


@pytest.fixture
def mock_tui():
    """Provide a mock TUI instance."""
    tui = MagicMock()
    tui.show_error = MagicMock()
    tui.show_info = MagicMock()
    tui.show_assistant_response = MagicMock()
    tui.show_tool_call = MagicMock()
    tui.show_tool_result = MagicMock()
    return tui


@pytest.fixture
def sample_conversation_history():
    """Provide sample conversation history for tests.
    
    Returns:
        List: Conversation history tuples
    """
    return [
        ("user", "Hello, can you help me with Python?"),
        ("assistant", "Of course! I'd be happy to help with Python."),
        ("user", "How do I read a file?"),
        ("assistant", "You can use the built-in open() function..."),
        ("user", "Thanks, that was helpful")
    ]


@pytest.fixture
def sample_chat_system(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
    """Provide a mock ChatSystem instance for tests.
    
    Returns:
        MagicMock: Mock chat system
    """
    from app.core.chat import ChatSystem
    
    chat_system = MagicMock(spec=ChatSystem)
    chat_system.llm = mock_llm
    chat_system.workspace_manager = mock_workspace_manager
    chat_system.permission_system = mock_permission_system
    chat_system.tui = mock_tui
    chat_system.history = []
    chat_system.running = True
    chat_system.current_agent_index = 0
    chat_system.agent_config = [
        {
            "name": "Default Agent",
            "specialty": "General purpose AI assistant",
            "system_prompt": "You are a helpful AI assistant."
        }
    ]
    
    def add_message(content, role="user"):
        if not content or not content.strip():
            return None
        chat_system.history.append((role, content))
        return {"role": role, "content": content}
    
    def get_session_stats():
        user_count = sum(1 for role, _ in chat_system.history if role == "user")
        assistant_count = sum(1 for role, _ in chat_system.history if role == "assistant")
        return {
            "total_messages": len(chat_system.history),
            "user_messages": user_count,
            "assistant_messages": assistant_count
        }
    
    chat_system.add_message = add_message
    chat_system.get_session_stats = get_session_stats
    
    return chat_system


@pytest.fixture
def sample_agentic_loop(mock_llm, mock_workspace_manager, mock_permission_system, mock_tui):
    """Provide a mock AgenticLoop instance for tests.
    
    Returns:
        MagicMock: Mock agentic loop
    """
    from app.agents.loop import AgenticLoop
    import time
    
    loop = MagicMock(spec=AgenticLoop)
    loop.llm = mock_llm
    loop.workspace_manager = mock_workspace_manager
    loop.permission_system = mock_permission_system
    loop.tui = mock_tui
    loop.tool_registry = {
        "read_file": {
            "func": MagicMock(),
            "description": "Read a file",
            "parameters": {"filename": "string"}
        },
        "write_file": {
            "func": MagicMock(),
            "description": "Write a file",
            "parameters": {"filename": "string", "content": "string"}
        }
    }
    loop.active = True
    loop.execution_history = []
    
    # Implement actual methods that tests call
    def gather_context(user_input, conversation_history):
        return {
            "user_input": user_input,
            "conversation_history": conversation_history[-5:],
            "workspace": mock_workspace_manager.get_workspace(),
            "available_tools": list(loop.tool_registry.keys()),
            "timestamp": time.time()
        }
    
    def register_tool(name, func, description, parameters):
        loop.tool_registry[name] = {
            "func": func,
            "description": description,
            "parameters": parameters
        }
    
    def activate():
        loop.active = True
    
    def create_plan(context):
        return [
            {"tool": "read_file", "action": "read"},
            {"tool": "write_file", "action": "write"}
        ]
    
    def execute_plan(plan):
        # Return one result for each item in the plan
        return [{"success": True, "tool": item.get("tool", "unknown")} for item in plan]
    
    def verify_results(results, context):
        return {"overall_success": True, "success": True}
    
    loop._gather_context = gather_context
    loop.register_tool = register_tool
    loop.activate = activate
    loop._create_plan = create_plan
    loop._execute_plan = execute_plan
    loop._verify_results = verify_results
    
    return loop


@pytest.fixture
def cli_runner():
    """Provide a CLI test runner (Click CLI testing).
    
    Returns:
        CliRunner: Click CLI test runner
    """
    from click.testing import CliRunner
    return CliRunner()


# Pytest hooks for better output and debugging

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
