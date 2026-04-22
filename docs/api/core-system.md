# Core System API Reference

## ChatSystem

The main orchestrator for the entire Hyena-3 application.

### Class Definition
```python
class ChatSystem(ChatLoopMixin):
    """Main chat system with modern terminal interface."""
```

### Constructor
```python
def __init__(self):
    """Initialize the chat system with all components."""
```

### Key Methods

#### Agent Management
```python
def load_agents(self) -> None:
    """Load the AI agents and initialize systems.
    
    Initializes:
    - LLM engine
    - Auto-memory system
    - Agentic loop
    - Tool registry
    - Project memory
    """

def choose_agent(self, index: Optional[int] = None) -> bool:
    """Choose an agent by index.
    
    Args:
        index: Agent index (0-based). If None, keeps current agent.
    
    Returns:
        bool: True if agent chosen successfully, False otherwise.
    """
```

#### Session Management
```python
def save_conversation(self, filename: str) -> bool:
    """Save conversation to file.
    
    Args:
        filename: Name for the saved conversation.
    
    Returns:
        bool: True if saved successfully.
    """

def load_conversation(self, filename: str) -> bool:
    """Load conversation from file.
    
    Args:
        filename: Name of the conversation file to load.
    
    Returns:
        bool: True if loaded successfully.
    """

def get_session_stats(self) -> Dict[str, Any]:
    """Get session statistics.
    
    Returns:
        Dict containing:
        - total_messages: int
        - user_messages: int
        - assistant_messages: int
        - current_agent: str
        - session_time: str
    """
```

#### Command Processing
```python
def process_command(self, user_input: str) -> bool:
    """Process a command and return whether to continue.
    
    Args:
        user_input: Command string starting with '/'.
    
    Returns:
        bool: True if application should continue running.
    """
```

### Properties
```python
@property
def history(self) -> List[Tuple[str, str]]:
    """Conversation history as list of (role, content) tuples."""

@property
def current_agent_index(self) -> int:
    """Index of currently active agent."""

@property
def running(self) -> bool:
    """Whether the chat system is currently running."""
```

## CommandManager

Handles all slash commands and command routing.

### Class Definition
```python
class CommandManager(AgentCommandsMixin, SessionCommandsMixin, 
                    WorkspaceCommandsMixin, SystemCommandsMixin,
                    MemoryCommandsMixin, ToolsCommandsMixin):
    """Main command manager combining all command mixins."""
```

### Constructor
```python
def __init__(self, chat_system: ChatSystem):
    """Initialize the command manager.
    
    Args:
        chat_system: The main ChatSystem instance.
    """
```

### Core Method
```python
def process_command(self, user_input: str) -> bool:
    """Process commands and return the result.
    
    Args:
        user_input: User input string.
    
    Returns:
        bool: Whether to continue the application.
    """
```

### Available Commands

#### Agent Commands
```python
def _handle_agents_command(self) -> bool:
    """Handle /agents command - List available agents."""

def _handle_switch_command(self, args: List[str]) -> bool:
    """Handle /switch command - Switch to specific agent.
    
    Args:
        args: Command arguments (agent number).
    """
```

#### Memory Commands
```python
def _handle_memory_command(self, args: List[str]) -> bool:
    """Handle /memory command - Memory system management.
    
    Args:
        args: Command arguments (list, load, delete, etc.).
    """

def _handle_compact_command(self) -> bool:
    """Handle /compact command - Compact conversation history."""
```

#### System Commands
```python
def _handle_help_command(self) -> bool:
    """Handle /help command - Show help menu."""

def _handle_status_command(self) -> bool:
    """Handle /status command - Show system status."""

def _handle_clear_command(self) -> bool:
    """Handle /clear command - Clear screen."""
```

#### Tools Commands
```python
def _handle_tools_command(self, args: List[str]) -> bool:
    """Handle /tools command - Tool management.
    
    Args:
        args: Command arguments (list, activate, etc.).
    """

def _handle_agentic_command(self, args: List[str]) -> bool:
    """Handle /agentic command - Agentic loop management."""
```

## Chat Mixins

### AgentManagementMixin
```python
class AgentManagementMixin:
    """Mixin for agent management functionality."""
```

### ConversationMixin
```python
class ConversationMixin:
    """Mixin for conversation handling functionality."""
    
    def chat_display(self) -> None:
        """Main chat loop with modern terminal interface."""
    
    async def _chat_loop_async(self) -> None:
        """Async chat loop with modern terminal interface."""
```

### SessionManagementMixin
```python
class SessionManagementMixin:
    """Mixin for session management functionality."""
    
    def save_conversation(self, filename: str) -> bool:
        """Save conversation to file."""
    
    def load_conversation(self, filename: str) -> bool:
        """Load conversation from file."""
    
    def export_conversation(self, filename: str) -> bool:
        """Export conversation to text file."""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
```

### WorkspaceOperationsMixin
```python
class WorkspaceOperationsMixin:
    """Mixin for workspace operations functionality."""
    
    def get_workspace(self) -> Optional[str]:
        """Get current workspace directory."""
    
    def set_workspace(self, directory: str) -> bool:
        """Set workspace directory."""
```

## Usage Examples

### Basic Chat System Usage
```python
# Initialize chat system
chat_system = ChatSystem()

# Load agents and start
chat_system.load_agents()
chat_system.chat_display()
```

### Command Processing
```python
# Process commands
result = chat_system.process_command("/help")
if not result:
    # User wants to exit
    pass

# Get session statistics
stats = chat_system.get_session_stats()
print(f"Total messages: {stats['total_messages']}")
```

### Agent Management
```python
# List available agents
chat_system.process_command("/agents")

# Switch to agent 2
chat_system.process_command("/switch 2")

# Get current agent info
current_agent = chat_system.agent_config[chat_system.current_agent_index]
print(f"Current agent: {current_agent['name']}")
```

### Session Management
```python
# Save conversation
chat_system.save_conversation("my-session")

# Load conversation
chat_system.load_conversation("my-session")

# Export conversation
chat_system.export_conversation("session-export.txt")

# Get session stats
stats = chat_system.get_session_stats()
print(f"Session stats: {stats}")
```

## Error Handling

### Common Exceptions
```python
try:
    chat_system.load_agents()
except Exception as e:
    print(f"Failed to load agents: {e}")
    # Handle initialization failure
```

### Command Processing Errors
```python
result = chat_system.process_command("/invalid-command")
if not result:
    print("Unknown command or application exit")
```

### Session Management Errors
```python
try:
    chat_system.save_conversation("session-name")
except Exception as e:
    print(f"Failed to save session: {e}")
```

## Configuration

### Agent Configuration
```python
# Load agent configuration
agent_config = chat_system._load_agent_config()

# Access current agent
current_agent = chat_system.agent_config[chat_system.current_agent_index]
system_prompt = current_agent["system_prompt"]
```

### Command Configuration
```python
# Available commands
commands = chat_system.commands
print(f"Available commands: {commands}")
```

## Integration Points

### With Memory System
```python
# Auto-memory is automatically integrated
if chat_system.auto_memory:
    stats = chat_system.auto_memory.get_stats()
    print(f"Memory stats: {stats}")
```

### With Agent System
```python
# Agentic loop integration
if chat_system.agentic_loop:
    result = chat_system.agentic_loop.process_request(
        "Read config.py", 
        chat_system.history
    )
    print(f"Agentic result: {result}")
```

### With Tool Manager
```python
# Tool access through chat system
tools = chat_system.tool_manager.get_all_tools()
print(f"Available tools: {list(tools.keys())}")
```

## Event Hooks

### Message Processing
```python
# Override in subclasses for custom behavior
def _process_chat_message(self, user_input: str) -> str:
    """Process user message and return AI response."""
    
    # Custom preprocessing
    processed_input = self._preprocess_input(user_input)
    
    # Get AI response
    response = self._get_ai_response(processed_input)
    
    # Custom postprocessing
    processed_response = self._postprocess_response(response)
    
    return processed_response
```

### Command Hooks
```python
# Custom command handling
def _handle_custom_command(self, args: List[str]) -> bool:
    """Handle custom command."""
    
    # Custom command logic
    self.tui.console.print("Custom command executed")
    return True
```

## Performance Considerations

### Memory Management
- Conversation history automatically managed
- Session statistics cached for performance
- Command processing optimized for speed

### Resource Usage
- Lazy loading of components
- Efficient string processing
- Minimal memory footprint

## Thread Safety

### Async Operations
```python
# Chat loop is async-safe
async def _chat_loop_async(self) -> None:
    """Async chat loop with proper concurrency handling."""
    
    while self.running:
        # Non-blocking input handling
        user_input = await self.tui.get_input(workspace)
        
        # Async command processing
        if user_input.startswith('/'):
            async with self._processing_lock:
                result = self.process_command(user_input)
        else:
            # Async AI processing
            response = await self._process_message_async(user_input)
```

### Lock Management
```python
# Processing lock prevents concurrent operations
self._processing_lock = asyncio.Lock()
```

This core system API provides the foundation for all Hyena-3 operations, with comprehensive command handling, session management, and agent control while maintaining strict code quality standards.
