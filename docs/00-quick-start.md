# Quick Start Guide

Get up and running with Hyena-AI in minutes.

## Prerequisites

- **Python**: 3.10, 3.11, or 3.12
- **UV Package Manager**: For dependency management (recommended)
- **8GB RAM+**: For local LLM inference
- **Model File**: Qwen 3.5-9B quantized (∼7-8GB VRAM)

## Installation

### 1. Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd Hyena-AI

# Create virtual environment with UV
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv sync
```

### 2. Download LLM Model

Download the Qwen 3.5-9B quantized model:

```bash
# Create models directory
mkdir -p app/models

# Download from Hugging Face (or use alternative)
# Visit: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
# Download: Qwen3.5-9B.Q8_0.gguf to app/models/
```

Or use a compatible alternative GGUF model.

### 3. Run Hyena-AI

```bash
# Option 1: Direct Python
python -m app.app

# Option 2: Windows Batch
./run_app.bat

# Option 3: UV
uv run python -m app.app
```

## First Commands

Once the app starts, try these commands:

```bash
# Get help
/help

# List available agents
/agent list

# Initialize a new agent
/agent init my_first_agent

# List available tools
/tools list

# Check permissions
/config permissions

# View memory stats
/memory stats

# Run agentic loop
/agentic "What files are in my workspace?"
```

## Example Workflow

```
1. /agent init researcher         # Create an agent
2. /agent load researcher          # Load the agent
3. /tools list                      # See what tools available
4. /agentic "Search for Python files"  # Execute agentic task
5. /memory search Python           # Search memory for results
6. /memory export researcher       # Export session memory
```

## Configuration

Hyena-AI stores configuration in `~/.hyena/config.json`:

```json
{
  "model_name": "Qwen3.5-9B",
  "model_path": "app/models/Qwen3.5-9B.Q8_0.gguf",
  "temperature": 0.7,
  "max_tokens": 2048,
  "permission_mode": "ask",
  "memory_extraction_interval": 5
}
```

Modify as needed for your use case. Permission modes:
- `auto` - Auto-approve safe operations
- `ask` - Prompt user for each permission
- `manual` - Require explicit permission grant

## Common Issues

### Model File Not Found

**Error**: `Model file not found at app/models/Qwen3.5-9B.Q8_0.gguf`

**Solution**: Download the GGUF model from Hugging Face or update path in config.

### Out of Memory

**Error**: `CUDA out of memory` or system freezes

**Solution**: 
- Use smaller model (e.g., 7B instead of 13B)
- Reduce `max_tokens` in config
- Close other applications

### Permission Denied

**Error**: Tool execution blocked by permission system

**Solution**: 
- Check `/config permissions` status
- Set `permission_mode: auto` for safe operations
- Grant temporary permissions with `/tool permission <tool> grant`

## Next Steps

- 📖 Read [Architecture Overview](01-overview.md)
- 🛠️ Explore [CLI Commands Reference](03-cli-commands.md)
- 🔧 Review [Tools Available](04-tools.md)
- 🔐 Understand [Permission System](05-permission-system.md)
- 🚀 See [Deployment Guide](10-deployment.md)

## FAQ

**Q: Can I use a different LLM?**
A: Yes! Any GGUF-quantized model works. Update config and use `/config set model_path <path>`.

**Q: How do I integrate with external APIs?**
A: Use the plugin system in `app/plugins/` to create custom tool integrations.

**Q: Is this suitable for production?**
A: Yes! See [Deployment Guide](10-deployment.md) for enterprise setup.

**Q: What's the permission system for?**
A: Safety. All tool operations go through RBAC gates with audit logging. See [Permission System](05-permission-system.md).

## Getting Help

- Read the full [Documentation Index](README.md)
- Check [Troubleshooting Guide](13-troubleshooting.md)
- View [API Reference](14-api-reference.md)
- Explore [Development Guide](11-development.md) if contributing
