# Architecture Overview

High-level architecture and design principles of Hyena-AI.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                    │
│              (CLI, TUI, Commands)                    │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                   ChatSystem                         │
│         (Core Orchestrator & Router)                │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌──────────┐  ┌──────────┐
    │ CLI    │  │Permission│  │ Agentic  │
    │Parser  │  │ System   │  │ Loop     │
    └────────┘  └──────────┘  └──────────┘
                     │              │
                     ▼              ▼
              ┌─────────────────────────┐
              │    Tool Execution       │
              │  (40+ Integrated Tools) │
              └────────┬────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌────────┐   ┌──────────┐   ┌──────────┐
    │ State  │   │ Memory   │   │Streaming │
    │Store   │   │ System   │   │Response  │
    └────────┘   └──────────┘   └──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  LLM Inference   │
              │  (Qwen 3.5-9B)   │
              └──────────────────┘
```

## Core Components

### 1. **ChatSystem** (`app/core/chat.py`)
The central orchestrator that:
- Initializes all subsystems (LLM, permissions, memory, tools)
- Routes commands through the CLI parser
- Manages agent lifecycle
- Coordinates request/response flow

**Key Methods:**
- `load_agents()` - Initialize available agents
- `execute_command()` - Route and execute CLI commands
- `run_agentic_loop()` - Execute planning/execution/verification cycle

### 2. **CLI Parser** (`app/cli/parser.py`)
Handles command parsing and routing:
- 60+ slash-based commands organized by category
- Command validation and help system
- Parameter parsing and type checking
- Command categorization (agents, tools, memory, workspace, system, code)

**Command Categories:**
```
/agent          - Agent management
/tools          - Tool operations
/memory         - Memory search/export
/workspace      - Project operations
/session        - Session management
/config         - Configuration
/help, /debug   - System commands
```

### 3. **Permission System** (`app/agents/permission_system.py`)
Enterprise RBAC with audit logging:
- **8 Resource Types**: files, directories, shell, network, memory, config, plugins, extensions
- **3 Operation Classes**:
  - Safe: `read`, `glob`, `grep` (auto-approved)
  - Dangerous: `write`, `delete`, `execute`, `modify` (require approval)
  - Administrative: Config, audit operations
- **Approval Modes**: auto, ask, manual
- **Temporary Grants**: Time-limited permission grants
- **Audit Logging**: All operations logged for security review

### 4. **Agentic Loop** (`app/agents/loop/`)
Implements the AI planning cycle:

```
1. GATHER CONTEXT
   ├─ Current request
   ├─ Available tools
   ├─ Memory context
   └─ Permission constraints

2. PLAN
   ├─ Decompose task
   ├─ Select tools
   └─ Create execution plan

3. EXECUTE
   ├─ Permission check
   ├─ Tool invocation
   ├─ Result collection
   └─ Error handling

4. VERIFY
   ├─ Validate results
   ├─ Update memory
   ├─ Stream response
   └─ Log operation
```

### 5. **Tool System** (`app/agents/tools/`)
40+ integrated tools across categories:

**File Operations:**
- `read_file`, `write_file`, `delete_file`, `copy_file`, `move_file`
- `list_directory`, `search_directory`, `watch_file`

**Shell Operations:**
- `execute_shell`, `process_manager`

**Workspace Operations:**
- `project_operations`, `workspace_manager`
- File analysis and refactoring

**Search Tools:**
- Full-text search, regex search, semantic search (Phase 7)

All tools are permission-gated and audited.

### 6. **Memory System** (`app/memory/`)
Multi-level memory architecture:

```
┌──────────────────────────────────────┐
│     UnifiedSessionManager            │
│  (Multi-session support, persistence)│
└──────────────┬───────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌─────────┐
│Context │ │Project │ │Semantic │
│Manager │ │Memory  │ │Search   │
└────────┘ └────────┘ └─────────┘
    │          │          │
    └──────────┼──────────┘
               │
        ┌──────▼───────┐
        │ Auto Memory  │
        │ Persistence  │
        └──────────────┘
```

**Features:**
- Automatic context extraction every 5 messages
- Semantic search with vector embeddings
- Hybrid keyword + semantic retrieval
- Multi-session management
- Project-specific memory isolation
- Compression for context optimization

### 7. **LLM Integration** (`app/llm/`)
Local inference engine:
- **Model**: Qwen 3.5-9B (GGUF Q8_0 quantization)
- **Framework**: llama-cpp-python
- **Context Window**: 8192 tokens
- **Features**:
  - Retry logic with exponential backoff
  - Token streaming support
  - Temperature/max_tokens control
  - Error recovery

### 8. **State Management** (`app/core/state/`)
Redux-like state store:
- **Actions**: Dispatched state changes
- **Reducers**: Pure functions for state transitions
- **Persistence**: Automatic state serialization
- **Subscribers**: State change notifications

**Managed State:**
- Agent registry
- Tool availability
- Permission grants
- Memory indices
- Session data

### 9. **Plugin System** (`app/plugins/`)
Extensibility framework:
- **BasePlugin**: Abstract plugin interface
- **PluginRegistry**: Plugin lifecycle management
- **Hooks**: Extension points (before_execute, after_execute, etc.)
- **Dynamic Loading**: Runtime plugin discovery

**Plugin Capabilities:**
- Custom tool registration
- Command extensions
- State middleware
- Event handlers

### 10. **Streaming Infrastructure** (`app/core/streaming.py`)
Responsive async streaming:
- Token-by-token output
- Performance metrics
- Multiple stream callbacks
- Backpressure handling
- Real-time response display

## Data Flow

### Command Execution Flow

```
1. User Input
   └─→ /command arg1 arg2

2. CLI Parsing
   └─→ CommandParser.parse() → Command object

3. Permission Check
   └─→ PermissionSystem.check_permission()
       ├─ Safe operation? → Auto-approve
       ├─ Dangerous operation? → Prompt user
       ├─ Audit log

4. Command Execution
   └─→ ChatSystem.execute_command(command)
       ├─ Gather context from memory
       ├─ Invoke tool/operation
       ├─ Capture result

5. Response Processing
   ├─ Format response
   ├─ Stream tokens
   ├─ Update state
   └─ Persist to memory

6. Logging & Audit
   └─→ Record operation (timestamp, user, action, result, permissions)
```

### Agentic Loop Flow

```
User Request
    │
    ▼
Parse Natural Language
    │
    ├─ Extract intent
    ├─ Identify tools needed
    └─ Retrieve memory context
    │
    ▼
Generate Execution Plan
    │
    ├─ Decompose into subtasks
    ├─ Order dependencies
    └─ Validate with permission system
    │
    ▼
Execute Tools (with permission gates)
    │
    ├─ For each tool:
    │   ├─ Check permission
    │   ├─ Execute
    │   ├─ Capture output
    │   └─ Log operation
    │
    ▼
Verify & Aggregate Results
    │
    ├─ Validate outputs
    ├─ Format response
    └─ Stream to user
    │
    ▼
Auto-Update Memory
    │
    ├─ Extract insights
    ├─ Update indices
    └─ Persist session
```

## Design Principles

### 1. **Security-First**
- All operations go through permission gates
- RBAC with fine-grained resource control
- Comprehensive audit logging
- Temporary permission grants with expiration

### 2. **Flexibility**
- Extensible plugin architecture
- Custom tool registration
- Configurable strategies for memory, streaming, permissions
- Multiple LLM support via drop-in replacement

### 3. **Reliability**
- Comprehensive error handling and recovery
- Retry logic with exponential backoff
- Transaction-like state updates
- Full state persistence

### 4. **Performance**
- Streaming infrastructure for responsive UX
- Efficient memory management with compaction
- Lazy loading and caching
- Async operations throughout

### 5. **Maintainability**  
- Clear separation of concerns
- Type hints for IDE support
- Comprehensive test coverage
- Well-documented code

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **LLM Inference** | llama-cpp-python + Qwen 3.5-9B |
| **Async Runtime** | asyncio |
| **CLI Framework** | prompt-toolkit |
| **UI** | Rich + Textual |
| **State Management** | Custom Redux-like store |
| **Caching** | diskcache |
| **Testing** | pytest + pytest-asyncio |
| **Type Checking** | mypy |
| **Linting** | flake8 |

## Next Steps

- 📖 Explore [CLI Commands](03-cli-commands.md)
- 🛠️ Review [Available Tools](04-tools.md)
- 🔐 Understand [Permission System](05-permission-system.md)
- 💾 Learn [Memory System](06-memory-system.md)
- 🔌 Check [Plugin System](07-plugin-system.md)
