# Troubleshooting Guide

Solutions to common issues and error messages.

## Getting Help

Before troubleshooting, check:
1. `/help` - General command help
2. `/logs` - Recent system logs
3. `/debug` - Enable debug mode for detailed output
4. This guide - Common issues and solutions

---

## Installation Issues

### Python Version Mismatch

**Error**: `Python 3.10+ required, found 3.9.x`

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.12
# Ubuntu/Debian:
sudo apt-get install python3.12

# macOS:
brew install python@3.12

# Windows:
# Download from python.org or use Windows Store

# Use specific version
python3.12 -m venv .venv
```

### Dependencies Installation Fails

**Error**: `pip install failed: Command failed with exit code`

**Solution**:
```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Clear cache
pip cache purge

# Install with verbose output
pip install -v -e .

# Try with no-cache
pip install --no-cache-dir -r requirements.txt

# Check for broken dependencies
pip check
```

### llama-cpp-python Installation Issues

**Error**: `Building llama-cpp-python failed`

**Solution**:
```bash
# Install build tools
# Ubuntu/Debian:
sudo apt-get install build-essential python3-dev

# macOS:
brew install cmake

# Windows:
# Install Visual C++ Build Tools

# Then retry
pip install llama-cpp-python

# Alternative: Use pre-built wheel
pip install llama-cpp-python --only-binary :all:
```

---

## Model Loading Issues

### Model File Not Found

**Error**: `Model file not found at app/models/Qwen3.5-9B.Q8_0.gguf`

**Solution**:
```bash
# Check models directory
ls -la app/models/

# Download model
mkdir -p app/models
cd app/models
wget https://huggingface.co/Qwen/...  # Full URL

# Or use huggingface-hub
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir app/models

# Update config with correct path
/config set model_path /path/to/model.gguf
```

### Model File Corrupted

**Error**: `Failed to load model: Invalid GGUF format`

**Solution**:
```bash
# Check file integrity
sha256sum app/models/Qwen3.5-9B.Q8_0.gguf

# Re-download model
rm app/models/Qwen3.5-9B.Q8_0.gguf
# Download again from Hugging Face

# Verify GGUF format
python -c "
import llama_cpp
model = llama_cpp.Llama('app/models/Qwen3.5-9B.Q8_0.gguf', n_gpu_layers=0)
print('Model loaded successfully')
"
```

### Insufficient VRAM

**Error**: `CUDA out of memory` or `GPU memory exceeded`

**Solution**:
```bash
# Use CPU inference instead of GPU
# In config.json:
{
  "gpu_layers": 0  // Use CPU only
}

# Or use fewer GPU layers
{
  "gpu_layers": 10  // Use some, not all
}

# Reduce tokens
/config set max_tokens 512

# Check available memory
nvidia-smi  # For GPU
free -h     # For system RAM
```

---

## Runtime Issues

### Out of Memory During Operation

**Error**: `MemoryError` or system freezes

**Solution**:
```bash
# Check memory usage
free -h
vmstat 1 5

# Reduce max tokens
/config set max_tokens 1024

# Reduce cache size
/config set cache_size 2GB

# Close other applications

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Response Time

**Error**: Commands taking >10 seconds to respond

**Solution**:
```bash
# Enable debug to see bottleneck
/debug on
/your_command

# Check logs
/logs

# Profile performance
/profile 30

# Optimize settings
/config set temperature 0.5  // Lower = faster
/config set max_tokens 1024  // Reduce length

# Check system resources
top     # Show processes
free -h # Show memory
```

### Commands Timeout

**Error**: `Command timeout: execution took >30s`

**Solution**:
```bash
# Increase timeout in config
{
  "command_timeout_seconds": 60
}

# Check what's taking time
/logs --filter timeout

# Break into smaller operations
# Instead of: /agentic "analyze entire project"
# Use: /agentic "analyze app/core/chat.py"
```

---

## Permission Issues

### Permission Denied

**Error**: `Operation denied: <operation> requires permission`

**Solution**:
```bash
# Check permission mode
/config show permission_mode

# Grant permission temporarily
/tools permission execute_shell grant 1h

# Or set to auto mode
/config set permission_mode auto

# Check permission status
/config permissions

# View audit log
/logs --filter permission
```

### Permission Grant Expired

**Error**: `Permission expired for <operation>`

**Solution**:
```bash
# Check grant expiration
/tools permission write_file status

# Grant again for longer duration
/tools permission write_file grant 1d

# Or grant permanently
/tools permission write_file grant  # No duration = permanent

# Check all active grants
/config permissions --active-grants
```

### Can't Revoke Permission

**Error**: `Failed to revoke permission`

**Solution**:
```bash
# Verify permission exists
/tools permission execute_shell status

# Try force revoke
/tools permission execute_shell revoke --force

# Check audit log for issues
/logs --filter permission

# Restart service
sudo systemctl restart hyena-ai  # Or just restart app
```

---

## Memory Issues

### Memory Size Growing Too Large

**Error**: `Memory database size exceeds 10GB`

**Solution**:
```bash
# Check current size
/memory stats

# Archive old entries
/memory export --older-than 60d json archive.json

# Clear old entries
/memory clear --older-than 60d

# Compact memory
/memory compact

# Rebuild indices
/memory compact --rebuild
```

### Search Results Not Relevant

**Error**: Semantic search returns irrelevant results

**Solution**:
```bash
# Try different search method
/memory search "query" --method keyword  # Try keyword first

# Rebuild search indices
/memory compact --rebuild

# Check memory content
/memory list --limit 50

# Verify semantic settings
/config show memory.semantic_search
```

### Memory Not Saving

**Error**: Memory entries disappear between sessions

**Solution**:
```bash
# Check memory path
/config show memory.storage.path

# Verify directory exists and is writable
ls -la ~/.hyena/memory/
chmod 750 ~/.hyena/memory/

# Check permissions
/config permissions --resource memory

# Manually save
/memory export researcher json backup.json
```

---

## Agent Issues

### Agent Won't Load

**Error**: `Failed to load agent: <agent_name>`

**Solution**:
```bash
# List available agents
/agent list

# Check if agent exists
ls -la ~/.hyena/agents/

# Try initializing agent
/agent init test_agent

# Check agent configuration
cat ~/.hyena/agents/<agent_name>/config.json

# Verify formatting is valid JSON
python -m json.tool ~/.hyena/agents/<agent_name>/config.json
```

### Agent Commands Failing

**Error**: `/agentic` returns errors

**Solution**:
```bash
# Enable debug mode
/debug on

# Run agentic with simple task
/agentic "say hello"

# Check logs
/logs

# Verify tools are available
/tools list

# Check permissions
/config permissions
```

---

## CLI Issues

### Command Not Recognized

**Error**: `/command: command not found`

**Solution**:
```bash
# Show all available commands
/help

# Check command syntax
/help <command>

# Verify command is typed correctly
# Note: Commands are case-sensitive
/Agent init  # Wrong
/agent init  # Correct

# Check for typos
/agentic    # Correct
/agentic    # Wrong (extra character)
```

### Incomplete Output

**Error**: Response cuts off or incomplete

**Solution**:
```bash
# Check if streaming is working
/config show performance.stream_buffer_size

# View full output in memory
/memory search <query>

# Export results
/memory export researcher json results.json

# Increase buffer size
/config set stream_buffer_size 8192
```

---

## File Operation Issues

### Can't Read File

**Error**: `Failed to read file: Permission denied`

**Solution**:
```bash
# Check file permissions
ls -la /path/to/file

# Make readable
chmod 644 /path/to/file

# Check workspace path
/workspace info

# Try with full path
/agentic "Read /full/path/to/file"
```

### Can't Write File

**Error**: `Failed to write file: Permission denied`

**Solution**:
```bash
# Check directory permissions
ls -la /path/to/directory

# Grant write permission
chmod 755 /path/to/directory

# Verify permission grant
/tools permission write_file status

# Grant permission if needed
/tools permission write_file grant 1h
```

### File Not Found in Search

**Error**: `Can't find file with pattern`

**Solution**:
```bash
# List workspace
/workspace tree

# Try exact path
/agentic "Read app/app.py"

# Check file exists
ls app/app.py

# Try glob pattern
/agentic "Find *.py files"

# Search relative to workspace
/workspace search "*.py"
```

---

## Shell/Execute Issues

### Shell Command Fails

**Error**: `Command execution failed`

**Solution**:
```bash
# Check command syntax
/agentic "Run: python --version"

# Test command manually
python --version

# Check environment
/agentic "show environment variables"

# Find executable
which python

# Update PATH if needed
export PATH=/usr/local/bin:$PATH
```

### Process Management Issues

**Error**: `Can't kill process` or `Process not found`

**Solution**:
```bash
# List processes
/agentic "list all python processes"

# Or manually
ps aux | grep python

# Get exact PID
pidof python

# Kill process
kill -9 <PID>

# Check if killed
ps -p <PID>
```

---

## Logging Issues

### No Logs Generated

**Error**: `/logs` returns empty

**Solution**:
```bash
# Check log file
tail -f /var/log/hyena-ai/app.log

# Verify logging is enabled
/config show logging

# Enable debug logging
/debug on

# Check log directory exists
ls -la /var/log/hyena-ai/

# Create if missing
mkdir -p /var/log/hyena-ai
chmod 750 /var/log/hyena-ai
```

### Logs Are Too Verbose

**Error**: Logs contain too much information

**Solution**:
```bash
# Change log level
/config set logging.level WARNING

# Or disable debug
/debug off

# Filter logs when viewing
/logs --filter error

# Or by time range
/logs --since 1h

# Rotate logs
logrotate /etc/logrotate.d/hyena-ai
```

---

## Network Issues

### Can't Connect to External Services

**Error**: `Network error: Connection refused`

**Solution**:
```bash
# Check network connectivity
ping 8.8.8.8

# Or
curl https://www.google.com

# Check firewall
sudo ufw status

# Check proxy settings
env | grep -i proxy

# Verify service is running
systemctl status hyena-ai
```

---

## Performance Debugging

### Check System Resources

```bash
# Memory usage
free -h
vmstat 1 5

# CPU usage
top
ps aux --sort=%cpu | head

# Disk usage
df -h
du -sh ~/.hyena/

# Network
netstat -tulpn
ss -an
```

### Profile Application

```bash
# Run profiler
/profile 30

# View results
/logs --filter profile
```

---

## Clean Reinstall

If all else fails, perform a clean reinstall:

```bash
# Backup current state
tar -czf hyena-ai-backup.tar.gz ~/.hyena

# Remove old installation
rm -rf /opt/hyena-ai
rm -rf ~/.hyena

# Reinstall
git clone <repo-url> /opt/hyena-ai
cd /opt/hyena-ai
uv sync

# Download model
mkdir -p app/models
# Download model file

# Reconfigure
mkdir -p ~/.hyena
# Create new config.json

# Test
python -m app.app
```

---

## Getting More Help

If you're still stuck:
1. Check [Development Guide](11-development.md)
2. Review [Architecture](01-overview.md)
3. Check [CLI Commands](03-cli-commands.md)
4. View [Testing Guide](12-testing.md)
5. Open an issue on GitHub with:
   - Error message
   - Command that triggered error
   - Log output (`/logs`)
   - System info (`/agentic "show system info"`)

