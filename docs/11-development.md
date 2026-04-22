# Development Guide

Guide for developers contributing to Hyena-AI.

## Project Structure

```
Hyena-AI/
├── app/                  # Main application
│   ├── __init__.py
│   ├── app.py           # Entry point
│   ├── config.py        # Configuration loading
│   ├── exceptions.py    # Exception definitions
│   ├── agents/          # Agent system
│   ├── cli/             # CLI commands (60+)
│   ├── core/            # Core functionality
│   ├── llm/             # LLM integration
│   ├── memory/          # Memory system
│   ├── plugins/         # Plugin system
│   ├── services/        # Service registry
│   ├── state/           # State management
│   ├── tools/           # Tool framework
│   ├── ui/              # UI components
│   ├── utils/           # Utilities
│   └── workspace/       # Workspace management
├── tests/               # Test suite (495+ tests)
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docs/                # Documentation
├── pyproject.toml       # Project configuration
├── README.md            # This file (overview)
└── run_app.bat          # Windows launcher
```

## Setting Up Development Environment

### 1. Clone Repository

```bash
git clone <repo-url>
cd Hyena-AI
```

### 2. Create Virtual Environment

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate

# Or using venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

### 3. Install Development Dependencies

```bash
# UV sync installs dev dependencies too
uv sync

# Or traditional pip
pip install -e ".[dev]"
```

### 4. Download Model

```bash
mkdir -p app/models
cd app/models
# Download Qwen model from Hugging Face
cd ../..
```

### 5. Run Tests

```bash
# Run full test suite
uv run pytest

# Run specific test
uv run pytest tests/unit/test_cli_commands.py

# Run with coverage
uv run pytest --cov=app

# Run integration tests only
uv run pytest tests/integration/
```

### 6. Start Development

```bash
# Run application
python -m app.app

# Enable debug logging
/debug on

# Check available commands
/help
```

---

## Code Style

### Python Standards

- **PEP 8**: Follow Python Enhancement Proposal 8
- **Type Hints**: Use throughout (95%+ coverage)
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Line Length**: 88 characters (Black formatter)

### Example Code Style

```python
from typing import Optional, List
from app.core.base import BaseComponent


class MyComponent(BaseComponent):
    """Short description.
    
    Longer description explaining the component's purpose and usage.
    """
    
    def __init__(self, name: str, enabled: bool = True) -> None:
        """Initialize component.
        
        Args:
            name: Component name
            enabled: Whether component is enabled, default True
        """
        self.name = name
        self.enabled = enabled
    
    def process(self, data: str) -> Optional[List[str]]:
        """Process data.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed result or None if processing fails
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        result = data.split()
        return result if self.enabled else None
```

### Format Code

```bash
# Format with Black
black app/ tests/

# Check formatting
black --check app/

# Format to specific line length
black --line-length 88 app/
```

### Lint Code

```bash
# Check with flake8
flake8 app/ tests/

# Check with pylint
pylint app/

# Check types with mypy
mypy app/
```

---

## Adding Features

### Adding a CLI Command

1. **Define Command Handler**

```python
# app/cli/commands/my_command.py

from app.cli.base import BaseCommand
from typing import Any, Dict

class MyCommand(BaseCommand):
    """My custom command."""
    
    name = "my_command"
    description = "Does something interesting"
    
    def __init__(self):
        super().__init__()
        self.register_subcommand("action1", self.action1)
        self.register_subcommand("action2", self.action2)
    
    async def action1(self, *args, **kwargs) -> str:
        """Perform action 1."""
        return "Result from action1"
    
    async def action2(self, *args, **kwargs) -> str:
        """Perform action 2."""
        return "Result from action2"
```

2. **Register in CLI Parser**

```python
# app/cli/parser.py

from app.cli.commands.my_command import MyCommand

class CommandParser:
    def __init__(self):
        # ... existing code ...
        self.commands["my_command"] = MyCommand()
```

3. **Add Tests**

```python
# tests/unit/test_my_command.py

import pytest
from app.cli.commands.my_command import MyCommand

@pytest.fixture
def my_command():
    return MyCommand()

@pytest.mark.asyncio
async def test_action1(my_command):
    result = await my_command.action1()
    assert result == "Result from action1"
```

### Adding a Tool

1. **Define Tool**

```python
# app/agents/tools/my_tool.py

from app.agents.tools.base import BaseTool
from typing import Any, Dict

class MyTool(BaseTool):
    """My custom tool."""
    
    name = "my_tool"
    description = "Does something useful"
    category = "custom"
    
    def __init__(self):
        super().__init__()
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool."""
        # Implementation
        return {"status": "success"}
```

2. **Register Tool**

```python
# app/agents/tools/registry.py

from app.agents.tools.my_tool import MyTool

class ToolRegistry:
    def __init__(self):
        # ... existing tools ...
        self.register(MyTool())
```

3. **Test Tool**

```python
# tests/unit/test_tools.py

@pytest.mark.asyncio
async def test_my_tool():
    tool = MyTool()
    result = await tool.execute(param="value")
    assert result["status"] == "success"
```

### Adding a Plugin

1. **Create Plugin**

```python
# app/plugins/my_plugin.py

from app.plugins.base import BasePlugin
from app.plugins.hooks import HookType

class MyPlugin(BasePlugin):
    """My custom plugin."""
    
    name = "my_plugin"
    version = "1.0.0"
    
    def activate(self):
        """Activate plugin."""
        self.register_hook("before_execute", self.before_execute)
        self.register_hook("after_execute", self.after_execute)
    
    def before_execute(self, context: Dict) -> Dict:
        """Hook before tool execution."""
        return context
    
    def after_execute(self, context: Dict, result: Any) -> Any:
        """Hook after tool execution."""
        return result
    
    def deactivate(self):
        """Deactivate plugin."""
        self.unregister_handlers()
```

2. **Register Plugin**

```python
# Place in app/plugins/my_plugin.py
# Automatic discovery: plugins/__init__.py loads all files
```

3. **Test Plugin**

```python
# tests/unit/test_plugins.py

from app.plugins.registry import PluginRegistry
from app.plugins.my_plugin import MyPlugin

def test_plugin_activation():
    plugin = MyPlugin()
    plugin.activate()
    assert plugin.is_active
```

---

## Running Tests

### Full Test Suite

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/

# Specific test file
pytest tests/unit/test_cli_commands.py

# Specific test
pytest tests/unit/test_cli_commands.py::test_agent_init
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html

# Coverage targets (current: ~85%)
pytest --cov=app --cov-fail-under=80
```

---

## Debugging

### Enable Debug Mode

```bash
# In application
/debug on

# Check logs
/logs --filter debug
```

### Use Python Debugger

```python
# Add breakpoint
import pdb
pdb.set_trace()

# Or use newer syntax (Python 3.7+)
breakpoint()
```

### View Logs

```bash
# Last 50 logs
/logs 50

# Filter by level
/logs --filter error

# Filter by module
/logs --filter "agents.permission"

# Export logs
/logs --export logs.json
```

### Performance Profiling

```bash
# Profile for 30 seconds
/profile 30

# View results
/logs --filter profile
```

---

## Documentation

### Adding Documentation

1. **Update Docstrings**
   - Google-style for functions/classes
   - Type hints in docstrings

2. **Update Guide Files**
   - Edit relevant file in `docs/`
   - Follow Markdown formatting
   - Include code examples

3. **Add Architecture Diagrams**
   - Use Mermaid format
   - Place in `docs/diagrams/`
   - Reference in docs

### Documentation Standards

```python
def my_function(param1: str, param2: int = 5) -> bool:
    """Brief description of function.
    
    Longer description explaining what the function does,
    its behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2, default is 5
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not int
        
    Example:
        >>> result = my_function("test", 10)
        >>> assert result is True
    """
    pass
```

---

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-feature

# Create bugfix branch  
git checkout -b bugfix/my-bug

# Create release branch
git checkout -b release/v1.0.0
```

### Commit Messages

```
[Type] Brief description

Longer explanation of the change, why it was made,
and any important context.

Fixes: #123
Related: #124
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. Create feature branch
2. Write tests for new code
3. Ensure all tests pass (`pytest`)
4. Ensure code is formatted (`black`, `flake8`, `mypy`)
5. Write clear commit messages
6. Create pull request with description
7. Address review comments
8. Merge after approval

---

## Release Process

### Version Bumping

```bash
# Update version in pyproject.toml
# Major.Minor.Patch (e.g., 1.2.3)
```

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Tag with git (`git tag v1.0.0`)
- [ ] Push tag (`git push --tags`)

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile code
cProfile.run('my_function()', 'profile_output')

# Analyze results
p = pstats.Stats('profile_output')
p.strip_dirs().sort_stats('cumulative').print_stats(10)
```

### Common Optimizations

1. **Use Type Hints**
   - Enables better IDE support
   - Helps find bugs early

2. **Cache Results**
   - Use `@functools.lru_cache`
   - Cache expensive operations

3. **Async Operations**
   - Use `async/await` for I/O
   - Improves responsiveness

4. **Memory Optimization**
   - Use generators for large datasets
   - Profile memory usage

---

## Common Development Tasks

### Add a Configuration Option

1. Update `app/config/base.py`
2. Add default in config template
3. Add unit test
4. Document in `docs/configuration.md` (if it exists)

### Add a Permission Resource Type

1. Update `app/agents/permission_system.py`
2. Add to permission checks
3. Add tests
4. Document in `docs/05-permission-system.md`

### Add a Memory Feature

1. Update `app/memory/` components
2. Integrate with `UnifiedSessionManager`
3. Add tests
4. Document in `docs/06-memory-system.md`

---

## Useful Resources

- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [asyncio Guide](https://docs.python.org/3/library/asyncio.html)

---

## Getting Help

- Read [Architecture Overview](01-overview.md)
- Check existing tests for examples
- Review similar existing code
- Ask in issue/discussion
- Check [Troubleshooting Guide](13-troubleshooting.md)

