# Development Guide

## Overview

This guide covers contributing to Hyena-3, including code quality standards, development workflow, and best practices.

## Code Quality Standards

### 1. 200-Line Limit (Strict Enforcement)

**Rule**: No Python file may exceed 200 lines
**Purpose**: Forces focused, single-purpose modules
**Enforcement**: Automated checks in CI/CD

**Example - Before (Monolithic)**:
```python
# agents/loop.py (453 lines) - [FAIL]
class AgenticLoop:
    def __init__(self):
        # 50+ lines of initialization
    
    def process_request(self):
        # 100+ lines of processing logic
    
    def _gather_context(self):
        # 50+ lines of context gathering
    
    def _create_plan(self):
        # 100+ lines of planning logic
    
    def _execute_plan(self):
        # 100+ lines of execution logic
    
    def _verify_results(self):
        # 50+ lines of verification
```

**Example - After (Modular)**:
```python
# agents/loop/__init__.py (3 lines) - [PASS]
from .base import AgenticLoop

__all__ = ['AgenticLoop']

# agents/loop/base.py (85 lines) - [PASS]
class AgenticLoop(GatherMixin, PlanMixin, ExecuteMixin, VerifyMixin, HistoryMixin):
    """Main orchestrator using focused mixins."""

# agents/loop/gather.py (19 lines) - [PASS]
class GatherMixin:
    def _gather_context(self, user_input: str, conversation_history: List) -> Dict[str, Any]:
        """Gather context for the request."""

# agents/loop/plan.py (41 lines) - [PASS]
class PlanMixin:
    def _create_plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an execution plan."""

# agents/loop/execute.py (65 lines) - [PASS]
class ExecuteMixin:
    def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the plan."""

# agents/loop/verify.py (41 lines) - [PASS]
class VerifyMixin:
    def _verify_results(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify execution results."""

# agents/loop/history.py (63 lines) - [PASS]
class HistoryMixin:
    def add_to_history(self, execution_result: Dict[str, Any]):
        """Add execution result to history."""
```

### 2. PEP 8 Compliance (95% Target)

**Import Organization**:
```python
# Standard library imports
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Third-party imports
from rich.panel import Panel
from rich.text import Text

# Local imports
from app.utils.common import create_error_response
from app.core.commands import CommandManager
```

**Line Length**: Maximum 88 characters
```python
# Too long
def very_long_function_name_that_exceeds_the_line_length_limit(parameter1, parameter2):
    pass

# Properly formatted
def very_long_function_name_that_exceeds_the_line_length_limit(
    parameter1: str, 
    parameter2: int
) -> Dict[str, Any]:
    pass
```

**Naming Conventions**:
```python
# Classes: PascalCase
class ChatSystem:
    pass

# Functions and variables: snake_case
def process_command(user_input: str) -> bool:
    command_result = process_input(user_input)
    return command_result

# Constants: UPPER_SNAKE_CASE
MAX_HISTORY_SIZE = 100
DEFAULT_TIMEOUT = 30
```

### 3. Mixin Pattern Usage

**Prefer mixins over inheritance**:
```python
# Good: Mixin pattern
class ChatSystem(AgentManagementMixin, ConversationMixin, SessionManagementMixin):
    """Main chat system combining focused functionality."""

# Avoid: Deep inheritance hierarchies
class ChatSystem(BaseChatSystem, AgentHandler, ConversationManager):
    """Avoid complex inheritance chains."""
```

**Mixin design principles**:
```python
# Focused mixin with single responsibility
class FileToolsMixin:
    """Mixin for file operation tools."""
    
    def _read_file(self, filename: str) -> Dict[str, Any]:
        """Read file contents."""
        # Implementation here
    
    def _write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Write content to file."""
        # Implementation here

# Composable mixins
class ToolManager(FileToolsMixin, ShellToolsMixin, WorkspaceToolsMixin):
    """Combines multiple tool mixins."""
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd Hyena-3

# Setup with UV
uv sync

# Run tests
uv run python -m pytest

# Run application
uv run python -m app.app
```

### 2. Create Feature Branch

```bash
# Create descriptive branch name
git checkout -b feature/add-new-tool

# Start development
```

### 3. Development Steps

#### Step 1: Understand Requirements
- Read issue description carefully
- Understand existing architecture
- Identify affected components

#### Step 2: Design Solution
- Follow 200-line limit
- Use mixin pattern
- Maintain PEP 8 compliance
- Consider backward compatibility

#### Step 3: Implementation
```python
# Example: Adding new tool
# 1. Create tool function in appropriate mixin
class CustomToolsMixin:
    def _custom_operation(self, param: str) -> Dict[str, Any]:
        """Custom tool implementation."""
        try:
            # Implementation logic
            result = perform_operation(param)
            return create_success_response("Operation completed", result)
        except Exception as e:
            return create_error_response(str(e))

# 2. Register in ToolManager
def get_all_tools(self) -> Dict[str, Dict]:
    return {
        # ... existing tools ...
        "custom_tool": {
            "func": self._custom_operation,
            "description": "Perform custom operation",
            "parameters": {"param": "string"}
        }
    }

# 3. Set permission level
# In PermissionSystem.check_permission()
if request.operation_type == "custom_tool":
    return self.current_mode == PermissionMode.AUTO
```

#### Step 4: Testing
```python
# Unit tests for new functionality
def test_custom_tool():
    """Test custom tool functionality."""
    tool_manager = ToolManager(workspace_manager, permission_system)
    result = tool_manager.execute_tool("custom_tool", param="test")
    assert result["success"] is True
```

#### Step 5: Documentation
```python
def _custom_operation(self, param: str) -> Dict[str, Any]:
    """Perform custom operation.
    
    Args:
        param: Input parameter for the operation.
        
    Returns:
        Dict containing success status and operation result.
        
    Example:
        >>> tool_manager.execute_tool("custom_tool", param="test")
        {'success': True, 'data': {...}}
    """
```

### 4. Code Quality Checks

#### Line Count Verification
```bash
# Check all files under 200 lines
find app/ -name "*.py" -exec wc -l {} + | awk '$1 > 200 {print $2 " (" $1 " lines)"}'
```

#### PEP 8 Compliance
```bash
# Install flake8
pip install flake8

# Check PEP 8 compliance
flake8 app/ --max-line-length=88 --select=E,W,F
```

#### Import Organization
```python
# Verify import order
# 1. Standard library
# 2. Third-party imports  
# 3. Local imports
```

### 5. Testing Strategy

#### Unit Tests
```python
# tests/test_agents.py
import pytest
from app.agents.loop import AgenticLoop

class TestAgenticLoop:
    def test_initialization(self):
        """Test agentic loop initialization."""
        loop = AgenticLoop(llm, workspace_manager, permission_system)
        assert loop.active is False
        assert len(loop.tool_registry) == 0
    
    def test_tool_registration(self):
        """Test tool registration."""
        loop = AgenticLoop(llm, workspace_manager, permission_system)
        loop.register_tool("test_tool", lambda: {}, "Test tool", {})
        assert "test_tool" in loop.tool_registry
```

#### Integration Tests
```python
# tests/test_integration.py
def test_full_workflow():
    """Test complete agentic workflow."""
    chat_system = ChatSystem()
    chat_system.load_agents()
    
    # Test agentic operation
    result = chat_system.agentic_loop.process_request(
        "Read config.py", 
        []
    )
    
    assert result["success"] is True
    assert len(result["results"]) > 0
```

#### Performance Tests
```python
# tests/test_performance.py
import time

def test_agentic_loop_performance():
    """Test agentic loop performance."""
    loop = AgenticLoop(llm, workspace_manager, permission_system)
    
    start_time = time.time()
    result = loop.process_request("Simple test request", [])
    execution_time = time.time() - start_time
    
    assert execution_time < 2.0  # Should complete within 2 seconds
    assert result["success"] is True
```

### 6. Documentation Updates

#### API Documentation
```markdown
# docs/api/new-feature.md
## New Tool API

### CustomToolMixin

#### Methods

##### _custom_operation(param: str) -> Dict[str, Any]
Perform custom operation with given parameter.

**Parameters:**
- `param`: Input parameter for the operation

**Returns:**
- `Dict`: Success status and operation result

**Example:**
```python
result = tool_manager.execute_tool("custom_tool", param="test")
```
```

#### User Documentation
```markdown
# README.md
## New Features

### Custom Tool Operations

New custom tool functionality added for specific operations:

```bash
/custom-tool <parameter>
```

Usage example:
```
/custom-tool test-parameter
```
```

### 7. Pull Request Process

#### PR Requirements
- [ ] All files under 200 lines
- [ ] PEP 8 compliant (95%+)
- [ ] Unit tests added
- [ ] Documentation updated
- [ ] Integration tests passing
- [ ] No breaking changes

#### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Changes Made
- Added new custom tool functionality
- Updated ToolManager with new tool registration
- Added comprehensive tests

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Code Quality
- [ ] All files under 200 lines
- [ ] PEP 8 compliant
- [ ] Documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Ready for review
```

## Adding New Components

### 1. New Mixin Creation

```python
# app/agents/loop/new_feature.py
"""New feature mixin for AgenticLoop."""

from typing import Dict, Any

class NewFeatureMixin:
    """Mixin for new feature functionality."""
    
    def _new_feature_operation(self, param: str) -> Dict[str, Any]:
        """Perform new feature operation.
        
        Args:
            param: Input parameter.
            
        Returns:
            Dict with operation result.
        """
        try:
            # Implementation logic
            result = perform_new_operation(param)
            return create_success_response("Operation completed", result)
        except Exception as e:
            return create_error_response(str(e))
```

### 2. Integration Steps

```python
# Update base.py
from .new_feature import NewFeatureMixin

class AgenticLoop(GatherMixin, PlanMixin, ExecuteMixin, 
                    VerifyMixin, HistoryMixin, NewFeatureMixin):
    """Enhanced agentic loop with new feature."""
```

### 3. Testing Integration

```python
# tests/test_new_feature.py
import pytest
from app.agents.loop import AgenticLoop

class TestNewFeature:
    def test_new_feature_functionality(self):
        """Test new feature operation."""
        loop = AgenticLoop(llm, workspace_manager, permission_system)
        result = loop._new_feature_operation("test")
        assert result["success"] is True
```

## Debugging Guidelines

### 1. Enable Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific debugging
agentic_loop.debug = True
memory_orchestrator.debug = True
```

### 2. Common Issues

#### Import Errors
```python
# Check import paths
from app.agents.loop import AgenticLoop  # [PASS] Correct
from agents.loop import AgenticLoop     # [ERROR] Incorrect
```

#### Mixin Integration
```python
# Ensure proper mixin order
class ChatSystem(AgentManagementMixin, ConversationMixin):  # [PASS]
    pass

# Avoid circular imports in mixins
class CustomMixin:  # [PASS] No circular imports
    def custom_method(self):
        from app.utils.common import helper  # Local import
        return helper()
```

#### Performance Issues
```python
# Use lazy loading
@property
def expensive_resource(self):
    """Lazy load expensive resource."""
    if not hasattr(self, '_resource'):
        self._resource = load_expensive_resource()
    return self._resource
```

## Code Review Checklist

### Before Submitting PR
- [ ] All files under 200 lines
- [ ] PEP 8 compliant (95%+)
- [ ] Comprehensive docstrings
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] No breaking changes
- [ ] Error handling implemented
- [ ] Performance considered
- [ ] Security implications reviewed
- [ ] Documentation updated

### Review Focus Areas
1. **Code Quality**: Adherence to standards
2. **Functionality**: Correct implementation
3. **Performance**: Efficiency considerations
4. **Security**: Safety implications
5. **Maintainability**: Code clarity and organization

## Contributing Examples

### Example 1: Adding New Command
```python
# Step 1: Create command method
class SystemCommandsMixin:
    def _handle_status_command(self) -> bool:
        """Handle /status command - Show system status."""
        status_text = Text()
        status_text.append("System Status\n\n", style="bold cyan")
        status_text.append(f"LLM: {'Loaded' if self.chat_system.llm else 'Not loaded'}\n")
        status_text.append(f"Memory: {'Active' if self.chat_system.auto_memory else 'Inactive'}\n")
        
        self.chat_system.tui.console.print(
            Panel(status_text, title="[bold blue]Status[/bold blue]", border_style="blue")
        )
        return True

# Step 2: Register in CommandManager
def process_command(self, user_input):
    command_handlers = {
        # ... existing commands ...
        "/status": lambda: self._handle_status_command(),
    }

# Step 3: Update help text
def _handle_help_command(self):
    help_text.append("  /status - Show system status\n", style="white")
```

### Example 2: Adding New Tool
```python
# Step 1: Create tool implementation
class WorkspaceToolsMixin:
    def _create_directory(self, dirname: str) -> Dict[str, Any]:
        """Create a new directory."""
        try:
            workspace = self.workspace_manager.get_workspace()
            if not workspace:
                return create_error_response("No workspace set")
            
            dir_path = Path(workspace) / dirname
            dir_path.mkdir(parents=True, exist_ok=True)
            
            return create_success_response("Directory created", {
                "directory": str(dir_path),
                "existed": dir_path.exists()
            })
        except Exception as e:
            return create_error_response(str(e))

# Step 2: Register tool
def get_all_tools(self):
    return {
        # ... existing tools ...
        "create_directory": {
            "func": self._create_directory,
            "description": "Create a new directory",
            "parameters": {"dirname": "string"}
        }
    }

# Step 3: Set permissions
def check_permission(self, request):
    if request.operation_type == "create_directory":
        return True  # Safe operation
```

## Resources

### Documentation
- [Architecture Overview](../architecture/overview.md)
- [Memory System](../memory-system.md)
- [Agent System](../agent-system.md)
- [API Reference](../api/)

### Tools
- **Flake8**: PEP 8 compliance checking
- **Black**: Code formatting
- **pytest**: Testing framework
- **mypy**: Type checking

### Standards
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Docstring Conventions](https://pep.python.org/pep-0257/)

This development guide ensures all contributions maintain the high code quality standards that make Hyena-3 a maintainable, extensible, and professional codebase.
