# Integrated Tools Reference

Complete guide to 40+ integrated tools.

## Tool Categories

Tools are organized by function:
- **File Operations** (8 tools)
- **Shell Operations** (4 tools)
- **Workspace Operations** (8 tools)
- **Search Tools** (6 tools)
- **Project Tools** (6 tools)
- **System Tools** (5 tools)

---

## File Operations

### `read_file`
Read file contents.

**Parameters:**
- `path` (str, required) - File path relative to workspace
- `lines` (tuple, optional) - (start_line, end_line) to read specific range

**Usage:**
```bash
/agentic "Read app/app.py"
/agentic "Show lines 10-20 of config.py"
```

**Permissions:** Safe (read)

### `write_file`
Write content to file.

**Parameters:**
- `path` (str, required) - File path
- `content` (str, required) - Content to write
- `mode` (str, optional) - 'w' (overwrite) or 'a' (append), default 'w'

**Usage:**
```bash
/agentic "Create a file named test.py with content: print('hello')"
```

**Permissions:** Dangerous (write) - requires approval

### `delete_file`
Delete a file.

**Parameters:**
- `path` (str, required) - File path

**Usage:**
```bash
/agentic "Delete the old_config.py file"
```

**Permissions:** Dangerous (delete) - requires approval

### `copy_file`
Copy file to new location.

**Parameters:**
- `source` (str, required) - Source path
- `destination` (str, required) - Destination path

**Usage:**
```bash
/agentic "Copy app.py to app_backup.py"
```

**Permissions:** Dangerous (write)

### `move_file`
Move/rename file.

**Parameters:**
- `source` (str, required) - Current path
- `destination` (str, required) - New path

**Usage:**
```bash
/agentic "Move config.py to app/config.py"
```

**Permissions:** Dangerous (write)

### `list_directory`
List directory contents.

**Parameters:**
- `path` (str, optional) - Directory path, default current
- `recursive` (bool, optional) - Include subdirectories
- `pattern` (str, optional) - Filter pattern (glob)

**Usage:**
```bash
/agentic "List all Python files in app/"
/agentic "Show directory tree"
```

**Permissions:** Safe (read)

### `search_directory`
Search for files matching pattern.

**Parameters:**
- `pattern` (str, required) - Glob pattern (*.py, *.md, etc.)
- `path` (str, optional) - Search path, default current
- `recursive` (bool, optional) - Include subdirectories

**Usage:**
```bash
/agentic "Find all test files"
```

**Permissions:** Safe (glob)

### `watch_file`
Watch file for changes (setup file watcher).

**Parameters:**
- `path` (str, required) - File path
- `callback` (callable, optional) - Function to call on change

**Usage:**
```python
# Used internally by watch system
```

**Permissions:** Safe (read)

---

## Shell Operations

### `execute_shell`
Execute shell command.

**Parameters:**
- `command` (str, required) - Shell command
- `timeout` (int, optional) - Command timeout in seconds
- `capture_output` (bool, optional) - Capture stdout/stderr

**Usage:**
```bash
/agentic "Run pytest tests"
/agentic "List files using ls command"
```

**Permissions:** Dangerous (shell_execute) - requires approval

### `process_manager`
Manage running processes.

**Parameters:**
- `action` (str, required) - 'list', 'kill', 'info'
- `process_id` (int, optional) - Process ID
- `name_pattern` (str, optional) - Process name pattern

**Usage:**
```bash
/agentic "List running Python processes"
/agentic "Kill process 1234"
```

**Permissions:** Dangerous (shell_execute)

### `run_script`
Run Python or shell script.

**Parameters:**
- `path` (str, required) - Script path
- `args` (list, optional) - Arguments
- `python` (bool, optional) - Run as Python script

**Usage:**
```bash
/agentic "Run setup.py"
```

**Permissions:** Dangerous (shell_execute)

### `get_environment`
Get environment variables.

**Parameters:**
- `name` (str, optional) - Specific variable name

**Usage:**
```bash
/agentic "Show environment variables"
```

**Permissions:** Safe (read)

---

## Workspace Operations

### `project_analyze`
Analyze project structure and statistics.

**Parameters:**
- `path` (str, optional) - Project path, default current
- `deep` (bool, optional) - Deep analysis

**Usage:**
```bash
/agentic "Analyze the workspace structure"
```

**Permissions:** Safe (read)

### `workspace_stats`
Show workspace statistics.

**Parameters:**
- `path` (str, optional) - Path to analyze

**Usage:**
```bash
/agentic "Show workspace statistics"
```

**Permissions:** Safe (read)

### `find_files_in_workspace`
Search files across workspace.

**Parameters:**
- `pattern` (str, required) - Search pattern
- `exclude` (list, optional) - Patterns to exclude

**Usage:**
```bash
/agentic "Find all TODO comments"
```

**Permissions:** Safe (glob)

### `get_git_status`
Get git repository status.

**Parameters:**
- `path` (str, optional) - Repository path

**Usage:**
```bash
/agentic "Show git status"
```

**Permissions:** Safe (read)

### `create_backup`
Create project backup.

**Parameters:**
- `path` (str, optional) - Path to backup
- `format` (str, optional) - 'zip', 'tar', default 'zip'

**Usage:**
```bash
/agentic "Backup the project"
```

**Permissions:** Dangerous (write)

### `restore_backup`
Restore from backup.

**Parameters:**
- `backup_path` (str, required) - Backup file path
- `target_path` (str, optional) - Restore destination

**Usage:**
```bash
/agentic "Restore from backup"
```

**Permissions:** Dangerous (write)

---

## Search Tools

### `grep_search`
Full-text search with regex support.

**Parameters:**
- `pattern` (str, required) - Search pattern (regex)
- `path` (str, optional) - Search path
- `case_sensitive` (bool, optional) - Case sensitivity

**Usage:**
```bash
/agentic "Find all imports of os module"
/agentic "Search for class definitions"
```

**Permissions:** Safe (read)

### `regex_search`
Advanced regex search across files.

**Parameters:**
- `regex` (str, required) - Regex pattern
- `extension` (str, optional) - File extension filter
- `path` (str, optional) - Search path

**Usage:**
```bash
/agentic "Find all function definitions"
```

**Permissions:** Safe (read)

### `semantic_search`
AI-powered semantic search (Phase 7).

**Parameters:**
- `query` (str, required) - Natural language query
- `path` (str, optional) - Search path
- `top_k` (int, optional) - Number of results

**Usage:**
```bash
/agentic "Find error handling code"
/agentic "Search for authentication logic"
```

**Permissions:** Safe (read)

### `code_search`
Search code by structure (functions, classes, etc.)

**Parameters:**
- `entity_type` (str, required) - 'function', 'class', 'import', etc.
- `name_pattern` (str, optional) - Name filter
- `path` (str, optional) - Search path

**Usage:**
```bash
/agentic "Find all async functions"
```

**Permissions:** Safe (read)

### `search_workspace`
Unified workspace search.

**Parameters:**
- `query` (str, required) - Search query
- `search_type` (str, optional) - 'semantic', 'keyword', 'regex'

**Usage:**
```bash
/agentic "Search workspace for database queries"
```

**Permissions:** Safe (read)

### `fuzzy_search`
Fuzzy file/content search.

**Parameters:**
- `query` (str, required) - Search query
- `fuzziness` (float, optional) - Fuzziness level (0-1)

**Usage:**
```bash
/agentic "Fuzzy find config files"
```

**Permissions:** Safe (read)

---

## Project Tools

### `analyze_code`
Analyze code quality and structure.

**Parameters:**
- `path` (str, required) - File or directory
- `analysis_type` (str, optional) - 'structure', 'quality', 'complexity'

**Usage:**
```bash
/agentic "Analyze app/app.py for quality"
```

**Permissions:** Safe (read)

### `generate_documentation`
Generate code documentation.

**Parameters:**
- `path` (str, required) - File or directory
- `format` (str, optional) - 'markdown', 'html', 'docstring'

**Usage:**
```bash
/agentic "Generate documentation for app/core/chat.py"
```

**Permissions:** Safe (read)

### `refactor_code`
Suggest code refactoring.

**Parameters:**
- `path` (str, required) - File path
- `strategy` (str, optional) - Refactoring strategy

**Usage:**
```bash
/agentic "Suggest refactoring for permission_system.py"
```

**Permissions:** Safe (read)

### `run_tests`
Execute test suite.

**Parameters:**
- `path` (str, optional) - Test path, default runs all
- `filter` (str, optional) - Test filter pattern

**Usage:**
```bash
/agentic "Run all tests"
/agentic "Run tests for permission system"
```

**Permissions:** Dangerous (shell_execute)

### `lint_code`
Run code linter.

**Parameters:**
- `path` (str, optional) - Path to lint
- `strict` (bool, optional) - Strict mode

**Usage:**
```bash
/agentic "Lint all Python files"
```

**Permissions:** Safe (read)

### `type_check`
Run type checker (mypy).

**Parameters:**
- `path` (str, optional) - Path to check

**Usage:**
```bash
/agentic "Check types in app/"
```

**Permissions:** Safe (read)

---

## System Tools

### `get_system_info`
Get system information.

**Usage:**
```bash
/agentic "Show system information"
```

**Permissions:** Safe (read)

### `check_dependencies`
Check project dependencies.

**Parameters:**
- `file` (str, optional) - Dependency file (pyproject.toml, requirements.txt)

**Usage:**
```bash
/agentic "Check project dependencies"
```

**Permissions:** Safe (read)

### `get_python_info`
Get Python environment info.

**Usage:**
```bash
/agentic "Show Python version and info"
```

**Permissions:** Safe (read)

### `benchmark_performance`
Run performance benchmarks.

**Parameters:**
- `test_name` (str, optional) - Specific benchmark

**Usage:**
```bash
/agentic "Run performance benchmarks"
```

**Permissions:** Dangerous (shell_execute)

### `memory_tools`
Interact with memory system.

**Parameters:**
- `action` (str, required) - 'get', 'search', 'clear', 'stats'
- `query` (str, optional) - Search query

**Usage:**
```bash
/agentic "Show memory statistics"
```

**Permissions:** Safe (read)

---

## Tool Management

### List All Tools
```bash
/tools list
/tools list --category file
/tools list --enabled-only
```

### Check Tool Info
```bash
/tools info read_file
/tools info execute_shell --verbose
```

### Test a Tool
```bash
/tools test read_file app/app.py
/tools test grep_search "class.*Agent"
```

### Enable/Disable Tools
```bash
/tools enable execute_shell
/tools disable execute_shell
```

### Manage Permissions
```bash
/tools permission execute_shell grant 1h
/tools permission write_file revoke
/tools permission read_file status
```

---

## Tool Usage Tips

1. **Safe Operations Approved Automatically**
   - read, glob, grep operations don't require approval
   - Shell, write, delete operations require permission

2. **Use Semantic Search**
   - For intelligent code search: `/agentic "Find authentication logic"`
   - More intuitive than regex for natural language queries

3. **Chain Tools with Agentic Loop**
   - Use `/agentic` to combine multiple tools automatically
   - System plans which tools to use in which order

4. **Stream Output**
   - Large results are streamed for responsive UX
   - Check memory for complete results with `/memory search`

5. **Permission Grants**
   - Grant temporary permissions: `/tools permission execute_shell grant 2h`
   - Automatic expiration for security

6. **Error Recovery**
   - Tools include retry logic for transient failures
   - See `/logs` for detailed error information

---

## Performance Considerations

| Tool | Speed | Memory | Notes |
|------|-------|--------|-------|
| read_file | Very Fast | Low | Linear with file size |
| grep_search | Fast | Low | Efficient streaming |
| semantic_search | Medium | Medium | Uses embeddings |
| execute_shell | Variable | Medium | Depends on command |
| project_analyze | Slow | High | Scans entire project |
| run_tests | Slow | High | Can take minutes |

---

## Examples

### Find and Analyze Code
```bash
/agentic "Find all error handling code and analyze its quality"
```

### Search and Refactor
```bash
/agentic "Find all TODO comments and suggest how to address them"
```

### Comprehensive Code Review
```bash
/agentic "Analyze app/core/chat.py for quality, suggest refactoring, and generate tests"
```

