# CLI Commands Reference

Complete guide to all 60+ available commands.

## Command Format

All commands follow this format:
```
/command [subcommand] [options] [arguments]
```

Type `/help` to see all commands, or `/help <command>` for specific help.

---

## Agent Commands (`/agent`)

Manage and control AI agents.

### `/agent init <name>`
Initialize a new agent.
```bash
/agent init researcher
/agent init code_analyzer --template default
```
**Options:**
- `--template` - Agent template (default, tool_expert, code_expert)
- `--description` - Agent description
- `--system_prompt` - Custom system prompt

### `/agent list`
List all available agents.
```bash
/agent list
/agent list --verbose  # Show full details
```

### `/agent load <name>`
Load an agent for the current session.
```bash
/agent load researcher
```

### `/agent unload`
Unload current agent.
```bash
/agent unload
```

### `/agent run <task>`
Execute a task with the loaded agent.
```bash
/agent run "Analyze the project structure"
/agent run "Find all TODO comments"
```

### `/agent edit <name> [property] [value]`
Edit agent properties.
```bash
/agent edit researcher name data_analyst
/agent edit researcher description "Analyzes datasets"
```

### `/agent delete <name>`
Delete an agent.
```bash
/agent delete old_agent
```

### `/agent clone <source> <target>`
Clone an existing agent.
```bash
/agent clone researcher senior_researcher
```

### `/agent export <name> [path]`
Export agent configuration.
```bash
/agent export researcher ./researcher_config.json
```

### `/agent import <path>`
Import agent from file.
```bash
/agent import ./researcher_config.json
```

---

## Tool Commands (`/tools`)

Manage and inspect available tools.

### `/tools list`
List all available tools.
```bash
/tools list
/tools list --category file   # Filter by category
/tools list --enabled-only    # Only show enabled tools
```

### `/tools info <tool_name>`
Get detailed information about a tool.
```bash
/tools info read_file
/tools info execute_shell
```

### `/tools test <tool_name> [args]`
Test a tool with sample arguments.
```bash
/tools test read_file app/app.py
/tools test search_directory *.py
```

### `/tools enable <tool_name>`
Enable a tool (allow its use).
```bash
/tools enable execute_shell
```

### `/tools disable <tool_name>`
Disable a tool (prevent its use).
```bash
/tools disable execute_shell
```

### `/tools permission <tool_name> [action] [duration]`
Manage tool permissions.
```bash
/tools permission execute_shell grant 1h   # Grant for 1 hour
/tools permission write_file revoke         # Revoke permission
/tools permission read_file status          # Check status
```

---

## Memory Commands (`/memory`)

Access and manage the memory system.

### `/memory list [limit]`
List memory entries.
```bash
/memory list              # Last 20 entries
/memory list 50           # Last 50 entries
/memory list --agent researcher  # Agent-specific
```

### `/memory search <query>`
Search memory with keyword or semantic search.
```bash
/memory search "Python implementation"
/memory search --semantic "database design"
/memory search --regex "^(class|def)"
```

### `/memory clear [type]`
Clear memory entries.
```bash
/memory clear               # Clear all
/memory clear session       # Current session only
/memory clear --older-than 7d  # Older than 7 days
```

### `/memory export [agent_name] [format] [path]`
Export memory to file.
```bash
/memory export researcher json ./memory.json
/memory export --all markdown ./full_memory.md
```

### `/memory import <path>`
Import memory from file.
```bash
/memory import ./memory.json
```

### `/memory stats`
Show memory statistics.
```bash
/memory stats
```

### `/memory compact`
Optimize memory (compaction and indexing).
```bash
/memory compact
```

### `/memory hierarchy`
Show memory hierarchy and structure.
```bash
/memory hierarchy
```

---

## Code Commands (`/code`)

AI-powered code analysis and manipulation.

### `/code analyze [file_or_pattern]`
Analyze code structure and quality.
```bash
/code analyze app/app.py
/code analyze app/**/*.py     # Multiple files
```

### `/code explain [file_or_pattern]`
Generate explanation of code.
```bash
/code explain app/agents/permission_system.py
```

### `/code suggest [query]`
Get code suggestions for a query.
```bash
/code suggest "async error handling patterns"
```

### `/code refactor [file_or_pattern]`
Suggest refactoring improvements.
```bash
/code refactor app/llm/engine.py
```

### `/code test [file_or_pattern]`
Suggest test cases.
```bash
/code test app/agents/permission_system.py
```

### `/code document [file_or_pattern]`
Generate documentation.
```bash
/code document app/core/chat.py
```

---

## Workspace Commands (`/workspace`)

Manage workspace and project operations.

### `/workspace info`
Show current workspace information.
```bash
/workspace info
```

### `/workspace tree [depth]`
Show directory tree.
```bash
/workspace tree
/workspace tree 3       # Up to 3 levels deep
```

### `/workspace search <pattern>`
Search files in workspace.
```bash
/workspace search *.py
/workspace search --regex "class.*Agent"
```

### `/workspace stats`
Show workspace statistics.
```bash
/workspace stats
```

### `/workspace rename <old_path> <new_path>`
Rename file/directory.
```bash
/workspace rename old_name.py new_name.py
```

---

## Session Commands (`/session`)

Manage current session.

### `/session info`
Show session information.
```bash
/session info
```

### `/session history [limit]`
Show command history.
```bash
/session history         # Last 20 commands
/session history 50      # Last 50 commands
```

### `/session clear`
Clear current session.
```bash
/session clear
```

### `/session save [filename]`
Save session state.
```bash
/session save my_session.json
```

### `/session load <filename>`
Load saved session.
```bash
/session load my_session.json
```

---

## Configuration Commands (`/config`)

Manage system configuration.

### `/config show [key]`
Show configuration.
```bash
/config show                    # All config
/config show model_name         # Specific key
```

### `/config set <key> <value>`
Update configuration.
```bash
/config set temperature 0.5
/config set max_tokens 1024
/config set permission_mode auto
```

### `/config reset [key]`
Reset to defaults.
```bash
/config reset               # All config
/config reset temperature   # Specific key
```

### `/config permissions`
Show permission status.
```bash
/config permissions
```

### `/config flags`
Show feature flags.
```bash
/config flags
```

---

## System Commands

### `/help [command]`
Show help.
```bash
/help                  # All commands
/help agent           # Command-specific
/help agent init      # Subcommand-specific
```

### `/version`
Show version information.
```bash
/version
```

### `/debug [mode]`
Enable debug mode.
```bash
/debug              # Toggle debug
/debug on           # Enable
/debug off          # Disable
```

### `/logs [limit] [filter]`
Show system logs.
```bash
/logs                      # Last 20 log entries
/logs 50 error            # Last 50 errors
/logs --today             # Today's logs
```

### `/benchmark [test]`
Run performance benchmarks.
```bash
/benchmark
/benchmark llm_inference
/benchmark tools
```

### `/profile [duration_seconds]`
Profile system performance.
```bash
/profile          # 10 second profile
/profile 30       # 30 second profile
```

### `/report [type]`
Generate reports.
```bash
/report system
/report permissions     # Permission audit report
/report performance
```

---

## Agentic Loop Commands

### `/agentic <task>`
Execute an agentic planning-execution cycle.
```bash
/agentic "What Python files are in the workspace?"
/agentic "Analyze app/agents/permission_system.py and suggest improvements"
/agentic "Delete all .pyc files and __pycache__ directories"
```

The agentic loop:
1. Parses the task
2. Plans tool execution
3. Checks permissions
4. Executes tools
5. Verifies results
6. Returns response and updates memory

---

## Examples

### Complete Workflow Example

```bash
# 1. Initialize researcher agent
/agent init researcher --description "Analyzes code and documents"

# 2. Load the agent
/agent load researcher

# 3. List available tools
/tools list

# 4. Run agentic task
/agentic "Find all Python files and analyze their structure"

# 5. Search memory for results
/memory search "Python files"

# 6. View stats
/memory stats

# 7. Export session
/memory export researcher json ./session_results.json
```

### Code Analysis Workflow

```bash
# 1. Analyze specific file
/code analyze app/core/chat.py

# 2. Get explanation
/code explain app/core/chat.py

# 3. Suggest improvements
/code refactor app/core/chat.py

# 4. Generate tests
/code test app/core/chat.py

# 5. Create documentation
/code document app/core/chat.py
```

### Permission Management

```bash
# 1. Check current permissions
/config permissions

# 2. Grant tool permission for 1 hour
/tools permission execute_shell grant 1h

# 3. Run shell command
/agentic "List all Python files"

# 4. View audit log
/config permissions --log

# 5. Revoke permission
/tools permission execute_shell revoke
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/agent init/list/load` | Agent management |
| `/tools list/info/test` | Tool inspection |
| `/memory search/export` | Memory access |
| `/code analyze/explain` | Code analysis |
| `/workspace info/tree` | Project navigation |
| `/session info/history` | Session management |
| `/config show/set` | Configuration |
| `/help` | Command help |
| `/agentic` | AI planning/execution |

---

## Tips & Tricks

1. **Use Tab Completion**: Most shells support tab completion for commands
2. **Chain Commands**: Use `/agentic` to combine multiple operations
3. **Save Sessions**: Use `/session save` to preserve important work
4. **Export for Sharing**: Use `/memory export --all markdown` for reports
5. **Permission Grants**: Use time-limited grants for temporary access
6. **Debug Mode**: Enable `/debug` to see detailed execution flow
7. **Search Memory**: Use `/memory search --semantic` for AI-assisted search

