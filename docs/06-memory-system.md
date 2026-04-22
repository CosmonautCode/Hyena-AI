# Memory System

Advanced multi-level memory architecture with semantic search and auto-persistence.

## Overview

The memory system is intelligent context management that:
- **Auto-extracts insights** - Every 5 messages automatically analyzed
- **Multi-session support** - Maintains separate memory for each agent/session
- **Semantic search** - AI-powered search with vector embeddings
- **Hybrid retrieval** - Combines keyword matching with semantic understanding
- **Persistence** - Automatic saving across sessions
- **Compression** - Context optimization to fit token limits

---

## Memory Hierarchy

```
┌─────────────────────────────────────────────┐
│        Session Memory Manager               │
│     (Unified Interface)                     │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌──────────┐
│Session │ │Project │ │Semantic  │
│Memory  │ │Memory  │ │Search    │
│        │ │        │ │Engine    │
└────────┘ └────────┘ └──────────┘
    │         │         │
    ├─────────┼─────────┤
    │         │         │
    ▼         ▼         ▼
┌─────────────────────────────────┐
│    Persistent Data Store        │
│   (~/.hyena/memory/)            │
└─────────────────────────────────┘
```

### 1. Session Memory
Short-term context for current session.
- Agent interactions and responses
- Current task context
- Recently accessed files
- Temporary notes

### 2. Project Memory
Long-term workspace-specific memory.
- Project structure and organization
- Common patterns discovered
- File locations and purposes
- Domain-specific insights

### 3. Semantic Search Index
Vector embeddings for intelligent search.
- Indexed content with embeddings
- Fast similarity matching
- Natural language query support
- Relevance scoring

---

## How Memory Works

### Automatic Extraction

Every 5 messages, the system:
```
Messages: [msg1, msg2, msg3, msg4, msg5]
    │
    ▼
Extract Insights
    ├─ Key findings
    ├─ Completed tasks
    ├─ Discovered patterns
    └─ Important decisions
    │
    ▼
Index & Store
    ├─ Add to session memory
    ├─ Add to project memory
    ├─ Create semantic embeddings
    └─ Persist to disk
    │
    ▼
Auto Clean-up
    ├─ Compress old entries
    ├─ Remove duplicates
    └─ Update indices
```

### Search Pipeline

```
User Query: "Find authentication code"
    │
    ├─ Parse Query
    │   ├─ Keywords: "authentication", "code"
    │   └─ Intent: Find implementation
    │
    ├─ Search Memory
    │   ├─ Keyword Search (fast)
    │   │   └─ Match files/entries with keywords
    │   │
    │   └─ Semantic Search (accurate)
    │       └─ Find semantically similar content
    │
    ├─ Combine Results
    │   ├─ Score by relevance
    │   ├─ Rerank by similarity
    │   └─ Filter by confidence
    │
    ▼
Return Results
    ├─ Top 10 most relevant
    ├─ With context snippets
    └─ Ranked by score
```

---

## Using Memory

### Search Memory

```bash
# Keyword search
/memory search "authentication"

# Semantic search (AI-powered)
/memory search --semantic "user login implementation"

# Regex search
/memory search --regex "def.*auth.*\("

# Search in specific agent
/memory search "pattern" --agent researcher

# Show top N results
/memory search "query" --limit 50
```

### List Memory Entries

```bash
# Show last 20 entries
/memory list

# Show last N entries
/memory list 100

# Show entries from specific time
/memory list --since 1h
/memory list --since 7d

# Show by agent
/memory list --agent researcher
```

### Clear Memory

```bash
# Clear current session only
/memory clear session

# Clear all memory
/memory clear --all

# Clear older entries
/memory clear --older-than 30d

# Clear specific agent
/memory clear --agent old_agent
```

### Export Memory

```bash
# Export as JSON
/memory export researcher json ./memory.json

# Export as Markdown
/memory export researcher markdown ./memory.md

# Export all agents
/memory export --all markdown ./full_memory.md

# Export last N entries
/memory export researcher json ./recent.json --limit 100
```

### Import Memory

```bash
# Import from file
/memory import ./memory.json

# Merge with existing
/memory import ./memory.json --merge
```

### Statistics

```bash
# Show memory statistics
/memory stats

# Show detailed breakdown
/memory stats --detailed

# Show by agent
/memory stats --by-agent
```

### Maintenance

```bash
# Compact memory (optimize)
/memory compact

# Rebuild indices
/memory compact --rebuild

# Verify integrity
/memory compact --verify

# Show memory hierarchy
/memory hierarchy
```

---

## Memory Configuration

### Auto-Extraction Settings

```json
{
  "memory": {
    "auto_extraction_interval": 5,     // Extract every N messages
    "max_extraction_length": 500,      // Max tokens per extraction
    "extraction_model": "default",     // Which model to use
    "store_raw_interactions": true,    // Keep original messages
    "store_agent_states": true         // Track agent state changes
  }
}
```

### Semantic Search Settings

```json
{
  "memory": {
    "semantic_search": {
      "enabled": true,
      "model": "all-MiniLM-L6-v2",     // Embedding model
      "embedding_cache_size": "1GB",
      "similarity_threshold": 0.6,     // Min confidence
      "top_k": 10                       // Default results
    }
  }
}
```

### Storage Settings

```json
{
  "memory": {
    "storage": {
      "path": "~/.hyena/memory",
      "max_size": "10GB",              // Max total size
      "retention_days": 90,            // Auto-delete old
      "compression": true,             // Compress on disk
      "backup_on_shutdown": true
    }
  }
}
```

---

## Memory Structure

### Session Memory Entry

```json
{
  "id": "msg_abc123",
  "timestamp": "2024-04-22T10:30:45Z",
  "agent": "researcher",
  "user_query": "Find authentication code",
  "extracted_insights": [
    "Found LoginService in auth/login.py",
    "Uses JWT tokens with 24h expiry",
    "Implements RBAC for permissions"
  ],
  "files_accessed": ["auth/login.py", "auth/jwt.py"],
  "memory_tags": ["authentication", "security", "implementation"],
  "relevance_score": 0.95
}
```

### Project Memory Entry

```json
{
  "id": "proj_auth_patterns",
  "timestamp": "2024-04-22T08:00:00Z",
  "category": "pattern",
  "title": "Authentication Pattern",
  "description": "JWT-based auth with RBAC",
  "files": ["auth/login.py", "auth/jwt.py", "auth/rbac.py"],
  "pattern_details": {
    "type": "authentication",
    "mechanism": "JWT tokens",
    "expiry": "24 hours",
    "permissions": "Role-based"
  }
}
```

---

## Advanced Memory Features

### Semantic Similarity Matching

Find related content using AI:

```bash
# Find code similar to a pattern
/memory search --semantic "permission checking code"

# Find related documentation
/memory search --semantic "how to add new permission"

# Find similar error handling
/memory search --semantic "error recovery strategy"
```

### Memory Compaction

Optimize memory structure and performance:

```bash
# Simple compaction
/memory compact

# Full rebuild (slower, more thorough)
/memory compact --rebuild

# Analyze memory usage before/after
/memory compact --analyze
```

### Hybrid Search

Combine semantic and keyword search for best results:

```bash
# Default: uses both keyword and semantic
/memory search "authentication"

# Force keyword only (faster)
/memory search "authentication" --method keyword

# Force semantic only (more accurate)
/memory search "authentication" --method semantic

# Custom weights
/memory search "authentication" --keyword-weight 0.4 --semantic-weight 0.6
```

---

## Use Cases

### Use Case 1: Code Review Session

```bash
# 1. Load project code
/agentic "Analyze app/core/chat.py"

# 2. Memory auto-extracts insights
# Check what was found
/memory list

# 3. Search for related patterns
/memory search --semantic "async error handling"

# 4. Find similar implementations
/memory search "chat system architecture"

# 5. Export findings
/memory export researcher markdown ./code_review.md
```

### Use Case 2: Cross-Session Knowledge Transfer

```bash
# Session 1: Researcher discovers pattern
/agent load researcher
/agentic "Analyze permission system"
/memory stats  # Auto-saved

# Session 2: Another agent reuses knowledge
/agent load code_expert
/memory search "permission patterns"  # Finds previous analysis
/agentic "Apply permission pattern to new code"
```

### Use Case 3: Long-Term Context Building

```bash
# Day 1: Initial project analysis
/agentic "Understand the project structure"

# Day 2: Continue work (memory contains previous insights)
/memory list  # Shows previous findings
/memory search "main entry points"  # Finds from Day 1

# Day 30: Quick onboarding
/memory hierarchy  # Shows complete project understanding
/memory export --all markdown ./project_overview.md
```

---

## Performance Considerations

### Memory Size Management

| Action | Impact | Recommendation |
|--------|--------|-----------------|
| Search | Linear with memory size | Compact regularly |
| Insert | O(log n) with indexing | Continuous indexing |
| Query | Fast with embeddings | Keep indices updated |
| Export | Linear with size | Large exports may take time |

### Optimization Tips

1. **Regular Compaction**
   ```bash
   # Weekly maintenance
   /memory compact
   ```

2. **Archive Old Memory**
   ```bash
   # Archive aged-out memory
   /memory export --older-than 90d json ./archive.json
   /memory clear --older-than 90d
   ```

3. **Use Targeted Search**
   ```bash
   # Faster than search all
   /memory search "query" --limit 20
   ```

4. **Monitor Statistics**
   ```bash
   # Check memory health
   /memory stats --detailed
   ```

---

## Troubleshooting Memory Issues

### Memory Growing Too Large

```bash
# Check size
/memory stats

# Archive and clear old
/memory export --older-than 60d json ./archive.json
/memory clear --older-than 60d

# Compact
/memory compact
```

### Search Results Not Relevant

```bash
# Try different search method
/memory search "query" --method semantic

# Check memory content
/memory list --limit 50

# Rebuild indices
/memory compact --rebuild
```

### Memory Not Persisting

```bash
# Check configuration
/config show memory

# Verify permissions
ls -la ~/.hyena/memory/

# Manually save
/memory export researcher json ~/.hyena/backup.json
```

### Slow Search Performance

```bash
# Compact memory
/memory compact --rebuild

# Check memory size
/memory stats

# Reduce search scope
/memory search "query" --agent specific_agent
```

---

## Memory API (For Developers)

### Access Memory Programmatically

```python
from app.memory import UnifiedSessionManager

memory = UnifiedSessionManager()

# Search memory
results = memory.search(
    query="authentication code",
    search_type="semantic",
    top_k=10
)

# List entries
entries = memory.list_entries(
    agent="researcher",
    limit=20
)

# Get statistics
stats = memory.get_stats()
```

### Extract Insights

```python
from app.memory.extractor import InsightExtractor

extractor = InsightExtractor()

# Extract from conversation
insights = extractor.extract(
    messages=conversation_history,
    max_insights=5
)

# Store automatically
for insight in insights:
    memory.store(insight)
```

### Semantic Search API

```python
from app.memory.retrieval import SemanticSearchEngine

search_engine = SemanticSearchEngine()

# Find similar content
results = search_engine.find_similar(
    query="user authentication implementation",
    top_k=10,
    threshold=0.6
)

# Get embeddings
embedding = search_engine.embed("search query")
```

---

## Summary

| Feature | Capability |
|---------|-----------|
| **Auto-Extraction** | Every 5 messages |
| **Search Types** | Keyword, semantic, regex |
| **Storage** | Persistent ~/.hyena/memory |
| **Sessions** | Per-agent isolation |
| **Compaction** | Automatic optimization |
| **Export** | JSON, Markdown formats |
| **Retention** | Configurable (default 90 days) |
| **Performance** | Sub-second searches on typical workloads |

The memory system is fundamental to Hyena-AI's ability to maintain context,learn from interactions, and provide relevant assistance over time.

