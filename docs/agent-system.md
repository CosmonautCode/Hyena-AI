# Agent System Documentation

## Overview

The agent system implements **agentic tool execution** with comprehensive safety controls. It enables AI to plan and execute multi-step operations through a **Gather → Plan → Act → Verify** loop.

## Architecture

```
Agent System
├── AgenticLoop           # Main orchestrator
├── ToolManager           # Tool registry and execution
├── PermissionSystem       # Safety controls
└── Tool Mixins           # Specialized tool implementations
    ├── FileToolsMixin    # File operations
    ├── ShellToolsMixin   # Shell commands
    └── WorkspaceToolsMixin # Workspace management
```

## Core Components

### 1. AgenticLoop (`app/agents/loop/`)
**Purpose**: Main orchestrator for agentic operations
**Key Features**:
- Implements Gather → Plan → Act → Verify cycle
- Modular design using mixins
- Execution history tracking
- Tool registry management

**Mixin Architecture**:
```python
class AgenticLoop(GatherMixin, PlanMixin, ExecuteMixin, VerifyMixin, HistoryMixin):
    """Combines focused mixins for complete agentic functionality."""
```

**Core Workflow**:
```python
def process_request(self, user_input: str, conversation_history: List) -> Dict[str, Any]:
    """Process user request through agentic loop."""
    
    # 1. Gather context
    context = self._gather_context(user_input, conversation_history)
    
    # 2. Create plan
    plan = self._create_plan(context)
    
    # 3. Execute plan
    results = self._execute_plan(plan)
    
    # 4. Verify results
    verification = self._verify_results(results, context)
    
    # 5. Store in history
    self.add_to_history({
        "plan": plan,
        "results": results,
        "verification": verification,
        "success": verification["overall_success"]
    })
    
    return {
        "success": verification["overall_success"],
        "plan": plan,
        "results": results,
        "verification": verification
    }
```

### 2. Mixin Components

#### GatherMixin (`app/agents/loop/gather.py`)
**Purpose**: Context gathering for agentic operations
**Key Features**:
- Analyzes user input
- Collects conversation history
- Identifies available tools
- Provides workspace context

**Context Collection**:
```python
def _gather_context(self, user_input: str, conversation_history: List) -> Dict[str, Any]:
    """Gather comprehensive context for request processing."""
    
    return {
        "user_input": user_input,
        "conversation_history": conversation_history[-5:],  # Last 5 messages
        "workspace": self.workspace_manager.get_workspace(),
        "available_tools": list(self.tool_registry.keys()),
        "timestamp": time.time()
    }
```

#### PlanMixin (`app/agents/loop/plan.py`)
**Purpose**: AI-powered planning and strategy
**Key Features**:
- Pattern recognition for operation types
- Step-by-step plan creation
- Tool selection logic
- Request analysis

**Planning Logic**:
```python
def _create_plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create execution plan based on context."""
    
    user_input = context["user_input"]
    plan = []
    
    # Check if file operations are needed
    if any(keyword in user_input.lower() for keyword in ["read", "write", "file", "save", "load"]):
        plan.append({
            "tool": "file_operations",
            "action": "analyze_file_request",
            "description": "Analyze file operation request"
        })
    
    # Check if shell commands are needed
    if any(keyword in user_input.lower() for keyword in ["run", "execute", "command", "shell"]):
        plan.append({
            "tool": "shell_operations",
            "action": "analyze_shell_request",
            "description": "Analyze shell command request"
        })
    
    # Default action if no specific patterns found
    if not plan:
        plan.append({
            "tool": "general_analysis",
            "action": "analyze_request",
            "description": "General request analysis"
        })
    
    return plan
```

#### ExecuteMixin (`app/agents/loop/execute.py`)
**Purpose**: Tool execution and result management
**Key Features**:
- Executes planned steps
- Tracks execution time
- Handles errors gracefully
- Standardizes result format

**Execution Process**:
```python
def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute the plan with timing and error handling."""
    
    results = []
    
    for step in plan:
        tool_name = step.get("tool")
        action = step.get("action")
        
        try:
            start_time = time.time()
            
            # Execute based on tool type
            if tool_name == "file_operations":
                result = self._execute_file_operation(action)
            elif tool_name == "shell_operations":
                result = self._execute_shell_operation(action)
            else:
                result = self._execute_general_operation(action)
            
            execution_time = time.time() - start_time
            
            results.append({
                "tool": tool_name,
                "action": action,
                "success": result.get("success", False),
                "data": result.get("data"),
                "error": result.get("error"),
                "execution_time": execution_time
            })
            
        except Exception as e:
            results.append({
                "tool": tool_name,
                "action": action,
                "success": False,
                "error": str(e),
                "execution_time": 0.0
            })
    
    return results
```

#### VerifyMixin (`app/agents/loop/verify.py`)
**Purpose**: Result verification and validation
**Key Features**:
- Validates execution success
- Compiles execution statistics
- Identifies issues and errors
- Generates verification summary

**Verification Process**:
```python
def _verify_results(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
    """Verify execution results and compile statistics."""
    
    verification = {
        "overall_success": True,
        "successful_steps": 0,
        "failed_steps": 0,
        "total_execution_time": 0.0,
        "issues": []
    }
    
    total_time = 0.0
    
    for result in results:
        if result.get("success", False):
            verification["successful_steps"] += 1
        else:
            verification["failed_steps"] += 1
            verification["overall_success"] = False
            verification["issues"].append({
                "tool": result.get("tool"),
                "action": result.get("action"),
                "error": result.get("error")
            })
        
        total_time += result.get("execution_time", 0.0)
    
    verification["total_execution_time"] = total_time
    verification["summary"] = f"Executed {len(results)} steps: {verification['successful_steps']} successful, {verification['failed_steps']} failed"
    
    return verification
```

#### HistoryMixin (`app/agents/loop/history.py`)
**Purpose**: Execution history tracking and statistics
**Key Features**:
- Stores complete execution records
- Maintains rolling history (max 100 entries)
- Provides execution statistics
- Performance tracking

**History Management**:
```python
def add_to_history(self, execution_result: Dict[str, Any]):
    """Add execution result to history with automatic cleanup."""
    
    history_entry = {
        "timestamp": time.time(),
        "plan": execution_result.get("plan", []),
        "results": execution_result.get("results", []),
        "verification": execution_result.get("verification", {}),
        "success": execution_result.get("success", False),
        "execution_time": execution_result.get("verification", {}).get("total_execution_time", 0.0)
    }
    
    self.execution_history.append(history_entry)
    
    # Keep history size manageable
    MAX_HISTORY = 100
    if len(self.execution_history) > MAX_HISTORY:
        self.execution_history = self.execution_history[-MAX_HISTORY:]
```

### 3. ToolManager (`app/agents/tools/`)
**Purpose**: Tool registry and execution management
**Key Features**:
- Centralized tool registration
- Permission integration
- Standardized tool interface
- Error handling and validation

**Tool Registration**:
```python
def get_all_tools(self) -> Dict[str, Dict]:
    """Get all available tools with descriptions and parameters."""
    
    return {
        "read_file": {
            "func": self._read_file,
            "description": "Read the contents of a file",
            "parameters": {"filename": "string", "encoding": "string (optional)"}
        },
        "write_file": {
            "func": self._write_file,
            "description": "Write content to a file",
            "parameters": {"filename": "string", "content": "string", "encoding": "string (optional)"}
        },
        "run_command": {
            "func": self._run_command,
            "description": "Execute a shell command in the workspace",
            "parameters": {"command": "string", "cwd": "string (optional)"}
        },
        "list_files": {
            "func": self._list_files,
            "description": "List files in directory with pattern matching",
            "parameters": {"pattern": "string (optional)", "recursive": "boolean (optional)"}
        }
    }
```

### 4. PermissionSystem (`app/agents/permission_system.py`)
**Purpose**: Safety controls and user approval workflow
**Key Features**:
- Permission modes (ASK/AUTO)
- Operation categorization
- User approval prompts
- Safety validation

**Permission Modes**:
```python
class PermissionMode(Enum):
    """Permission modes for AI operations."""
    ASK = "ask"          # Prompt for dangerous operations
    AUTO = "auto"        # Auto-accept safe operations, ask for dangerous ones
```

**Permission Logic**:
```python
def check_permission(self, request: PermissionRequest) -> bool:
    """Check if operation is permitted based on current mode."""
    
    if self.current_mode == PermissionMode.AUTO:
        # Auto-allow file operations
        if request.operation_type in ["file_read", "file_write"]:
            return True
        # Ask for shell commands
        elif request.operation_type == "terminal":
            return self._prompt_user(request)
    
    # ASK mode - always prompt user
    return self._prompt_user(request)
```

## Tool Implementation

### FileToolsMixin (`app/agents/tools/file_tools.py`)
**Purpose**: Safe file operations with backup and validation
**Key Features**:
- Path validation and safety checks
- Automatic backup before modifications
- Enhanced error handling
- File type detection

**File Operations**:
```python
def _read_file(self, filename: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read file contents with enhanced error handling."""
    
    if not validate_file_path(filename):
        return create_error_response("Invalid file path")
    
    try:
        result = self.workspace_manager.read_file(filename)
        if "error" in result:
            return create_error_response(result["error"])
        
        return create_success_response("File read successfully", {
            "content": result["content"],
            "type": result.get("type", "text"),
            "size": len(result["content"]) if isinstance(result["content"], str) else 0
        })
    except Exception as e:
        return create_error_response(str(e))

def _write_file(self, filename: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Write content to file with backup and diff generation."""
    
    try:
        # Create backup if file exists
        backup_path = None
        old_content = ""
        
        workspace = self.workspace_manager.get_workspace()
        if workspace:
            file_path = Path(workspace) / filename
            if file_path.exists():
                backup_path = f"{filename}.backup.{int(time.time())}"
                old_content = file_path.read_text(encoding=encoding)
                file_path.write_text(old_content, encoding=encoding)  # Create backup
        
        # Write new content
        result = self.workspace_manager.write_file(filename, content, encoding)
        if "error" in result:
            # Restore backup if write failed
            if backup_path and old_content:
                file_path.write_text(old_content, encoding=encoding)
            return create_error_response(result["error"])
        
        return create_success_response("File written successfully", {
            "backup_created": backup_path,
            "bytes_written": len(content)
        })
        
    except Exception as e:
        return create_error_response(str(e))
```

### ShellToolsMixin (`app/agents/tools/shell_tools.py`)
**Purpose**: Safe shell command execution
**Key Features**:
- Command validation and safety checks
- Timeout protection
- Execution in workspace directory
- Comprehensive result reporting

**Shell Operations**:
```python
def _run_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
    """Execute a shell command in the workspace."""
    
    if not validate_command(command):
        return create_error_response("Command blocked for safety")
    
    try:
        # Use provided cwd or workspace directory
        work_dir = cwd or self.workspace_manager.get_workspace()
        if not work_dir:
            return create_error_response("No working directory specified")
        
        # Execute command with timeout
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            return create_success_response("Command executed successfully", {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time": execution_time,
                "working_directory": work_dir
            })
        else:
            return create_error_response(f"Command failed with return code {result.returncode}", {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time": execution_time
            })
            
    except subprocess.TimeoutExpired:
        return create_error_response("Command timed out after 30 seconds")
    except Exception as e:
        return create_error_response(str(e))
```

### WorkspaceToolsMixin (`app/agents/tools/workspace_tools.py`)
**Purpose**: Workspace and directory management
**Key Features**:
- Directory listing with patterns
- Workspace operations
- File system navigation
- Project structure analysis

**Workspace Operations**:
```python
def _list_files(self, pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
    """List files in directory with pattern matching."""
    
    try:
        workspace = self.workspace_manager.get_workspace()
        if not workspace:
            return create_error_response("No workspace set")
        
        workspace_path = Path(workspace)
        
        if recursive:
            files = list(workspace_path.rglob(pattern))
        else:
            files = list(workspace_path.glob(pattern))
        
        file_list = []
        for file_path in files:
            file_info = {
                "name": file_path.name,
                "path": str(file_path.relative_to(workspace_path)),
                "type": "directory" if file_path.is_dir() else "file",
                "size": file_path.stat().st_size if file_path.is_file() else 0
            }
            file_list.append(file_info)
        
        return create_success_response(f"Found {len(file_list)} items", {
            "files": file_list,
            "workspace": workspace,
            "pattern": pattern,
            "recursive": recursive
        })
        
    except Exception as e:
        return create_error_response(str(e))
```

## API Reference

### AgenticLoop
```python
class AgenticLoop:
    def __init__(self, llm, workspace_manager, permission_system, tui=None)
    def activate(self) -> bool
    def deactivate(self) -> bool
    def register_tool(self, name: str, func: callable, description: str, parameters: Dict[str, str])
    def process_request(self, user_input: str, conversation_history: List) -> Dict[str, Any]
    def get_execution_stats(self) -> Dict[str, Any]
```

### ToolManager
```python
class ToolManager:
    def __init__(self, workspace_manager, permission_system)
    def get_all_tools(self) -> Dict[str, Dict]
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]
```

### PermissionSystem
```python
class PermissionSystem:
    def __init__(self)
    def set_mode(self, mode: str) -> None
    def check_permission(self, request: PermissionRequest) -> bool
    def prompt_user(self, request: PermissionRequest) -> bool
```

## Usage Examples

### Basic Agentic Operations
```python
# Initialize agentic loop
agentic_loop = AgenticLoop(llm, workspace_manager, permission_system, tui)

# Register tools
tools = tool_manager.get_all_tools()
for name, info in tools.items():
    agentic_loop.register_tool(name, info["func"], info["description"], info["parameters"])

# Process user request
result = agentic_loop.process_request("Read config.py and analyze the database setup", conversation_history)

# Check results
if result["success"]:
    print(f"Plan executed with {result['verification']['successful_steps']} successful steps")
else:
    print(f"Execution failed: {result['verification']['issues']}")
```

### Tool Execution
```python
# Execute specific tool
result = tool_manager.execute_tool("read_file", filename="config.py")

if result["success"]:
    print(f"File content: {result['data']['content']}")
else:
    print(f"Error: {result['error']}")
```

### Permission Management
```python
# Set permission mode
permission_system.set_mode("auto")

# Check permission for operation
request = PermissionRequest(
    operation_type="file_write",
    description="Write to config.py",
    details={"content": "new configuration"}
)

if permission_system.check_permission(request):
    # Execute operation
    pass
```

## Configuration

### Agentic Loop Settings
```python
# In AgenticLoop.__init__
self.active = False
self.tool_registry = {}
self.execution_history = []
self.current_plan = None
```

### Permission System Settings
```python
# Available permission modes
 PermissionMode.ASK    # Prompt for all operations
 PermissionMode.AUTO   # Auto-allow safe operations
```

### Tool Registration
```python
# Custom tool registration
agentic_loop.register_tool(
    name="custom_tool",
    func=my_custom_function,
    description="Custom tool for specific task",
    parameters={"param1": "string", "param2": "boolean"}
)
```

## Performance and Safety

### Execution Tracking
- **Timing**: All operations tracked with execution time
- **History**: Rolling history of last 100 executions
- **Statistics**: Success rates and performance metrics

### Safety Features
- **Command Validation**: Dangerous commands blocked
- **Path Validation**: Path traversal attacks prevented
- **Timeout Protection**: Commands timeout after 30 seconds
- **Backup System**: Automatic file backups before modifications

### Error Handling
- **Graceful Degradation**: Continue despite individual failures
- **Detailed Error Reporting**: Comprehensive error information
- **Rollback Capabilities**: Restore from backups on failure

## Troubleshooting

### Common Issues

**Agentic Loop Not Active**
```python
if not agentic_loop.active:
    agentic_loop.activate()
```

**Tool Registration Failed**
```python
# Check tool function signature
def tool_function(param1: str, param2: bool = False) -> Dict[str, Any]:
    """Tool functions must return Dict with success/data/error keys."""
```

**Permission Denied**
```python
# Check permission mode
if permission_system.current_mode == PermissionMode.ASK:
    print("User approval required for this operation")
```

### Debug Information
```python
# Enable debug mode
agentic_loop.debug = True

# Get detailed statistics
stats = agentic_loop.get_execution_stats()
print(f"Execution stats: {stats}")
```

## Future Enhancements

### Planned Features
- **Advanced Planning**: AI-powered plan optimization
- **Parallel Execution**: Concurrent tool execution
- **Tool Chaining**: Automatic tool composition
- **Learning System**: Adaptive tool selection

### Extension Points
- **Custom Tools**: Domain-specific tool implementations
- **Alternative Permissions**: Different permission models
- **Advanced Verification**: Custom verification strategies

The agent system provides **autonomous operations** with comprehensive safety controls, making Hyena-3 a powerful and trustworthy AI assistant for complex tasks.
