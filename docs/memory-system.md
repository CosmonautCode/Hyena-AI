# Memory System Documentation

## Overview

The memory system provides **persistent memory** without manual saves. It automatically extracts insights, stores conversations, and injects relevant context into AI responses.

## Architecture

```
Memory System
├── ConversationStore     # Auto-save conversations
├── MemoryExtractor       # AI-powered insight extraction  
├── MemoryRetrieval       # Smart context retrieval
├── AutoMemoryOrchestrator # Main coordination
├── ProjectMemory         # Project-specific memory
└── ContextCompactor      # Conversation management
```

## Components

### 1. ConversationStore (`app/memory/store.py`)
**Purpose**: Automatic conversation persistence
**Key Features**:
- Auto-save every message without manual commands
- Timestamped file naming with content slugs
- Atomic writes to prevent data corruption
- Dual storage: auto-conversations + named conversations

**File Structure**:
```
.hyena/conversations/
├── auto/                    # Auto-saved conversations
│   └── 2024-03-07-120000-discuss-python.json
└── named/                   # Manually named conversations
    └── project-planning.json
```

**Key Methods**:
```python
def start_conversation(self, first_message: str) -> str:
    """Initialize new conversation file."""

def append_message(self, role: str, content: str):
    """Auto-save message to current conversation."""
```

### 2. MemoryExtractor (`app/memory/extractor.py`)
**Purpose**: AI-powered insight extraction from conversations
**Key Features**:
- Extracts key facts, decisions, patterns every 5 messages
- Uses LLM for intelligent analysis
- Structured JSON output for easy retrieval
- Configurable extraction intervals

**Extraction Process**:
```python
def extract_memories(self, conversation_segment: List[Dict]) -> Dict:
    """
    Extract structured memories from conversation.
    
    Returns:
    {
        "insights": ["User prefers Python over JavaScript"],
        "decisions": ["Chose to use FastAPI for the backend"],
        "patterns": ["Always writes tests before implementation"],
        "topics": ["api-design", "database", "authentication"],
        "importance": "high"
    }
    """
```

**Extraction Prompt**:
The system uses a carefully crafted prompt to extract:
1. **Insights**: Key facts and information
2. **Decisions**: Choices made during conversation
3. **Patterns**: Coding patterns and approaches
4. **Topics**: Themes and subjects discussed
5. **Importance**: High/medium/low priority

### 3. MemoryRetrieval (`app/memory/retrieval/`)
**Purpose**: Smart context retrieval and injection
**Key Features**:
- Semantic search for relevant memories
- Ranking algorithm for importance
- Context injection into system prompts
- Topic-based memory organization

**Search Process**:
```python
def get_relevant_memories(self, current_context: str, limit: int = 5) -> List[Dict]:
    """Retrieve most relevant memories for current context."""
    
    # 1. Semantic search through stored memories
    candidates = self._search_memories(current_context)
    
    # 2. Rank by relevance and recency
    ranked = self._rank_memories(candidates, current_context)
    
    # 3. Return top memories
    return ranked[:limit]
```

**Ranking Algorithm**:
- **Semantic similarity** to current context
- **Recency** - newer memories weighted higher
- **Importance** - high/medium/low priority
- **Usage frequency** - frequently accessed memories

### 4. AutoMemoryOrchestrator (`app/memory/orchestrator/`)
**Purpose**: Main coordination hub for memory operations
**Key Features**:
- Coordinates all memory components
- Manages extraction timing and intervals
- Provides unified memory interface
- Tracks memory statistics

**Workflow**:
```python
def on_user_message(self, content: str):
    """Called when user sends a message."""
    # 1. Auto-save conversation
    self.conversation_store.append_message("user", content)
    
    # 2. Check if extraction needed
    self.messages_since_extraction += 1
    if self.messages_since_extraction >= self.extraction_interval:
        self._trigger_extraction()
    
    # 3. Update statistics
    self._update_stats()
```

### 5. ProjectMemory (`app/memory/project/`)
**Purpose**: Project-specific memory and configuration
**Key Features**:
- Project-level configuration files
- Skills and capabilities tracking
- Agent customization per project
- Workspace-aware memory

**Configuration Files**:
```
.hyena/
├── Memories.md          # Project knowledge base
├── Skills.md            # Learned capabilities
└── agents.md            # Custom agent configurations
```

**Memory Loading**:
```python
def load_project_memory(self) -> Dict[str, Any]:
    """Load all project-specific memory files."""
    
    memories = self._load_config_file('memories')
    skills = self._load_config_file('skills')
    agents = self._load_config_file('agents')
    
    return {
        'project_knowledge': memories,
        'learned_skills': skills,
        'custom_agents': agents
    }
```

### 6. ContextCompactor (`app/memory/compactor.py`)
**Purpose**: Conversation history management and summarization
**Key Features**:
- Automatic conversation compaction
- Token count estimation
- Intelligent summarization
- Tool output truncation

**Compaction Strategy**:
```python
def compact_history(self, history: List[Dict]) -> List[Dict]:
    """Compact conversation history to fit context limits."""
    
    # 1. Keep recent messages (last 10)
    recent_messages = history[-10:]
    
    # 2. Summarize older messages
    old_messages = history[:-10]
    if old_messages:
        summary = self._summarize_messages(old_messages)
        
        # 3. Insert summary as compacted message
        compacted = {
            "role": "system",
            "content": f"[COMPACTED] {summary}",
            "metadata": {
                "compacted": True,
                "original_count": len(old_messages)
            }
        }
        
        return [compacted] + recent_messages
    
    return history
```

## Memory Flow

### Complete Memory Lifecycle
```
1. User Message
   ↓
2. ConversationStore.append_message() (Auto-save)
   ↓
3. Check extraction interval (every 5 messages)
   ↓
4. MemoryExtractor.extract_memories() (AI analysis)
   ↓
5. MemoryRetrieval.save_structured_memories() (Storage)
   ↓
6. Next User Input
   ↓
7. MemoryRetrieval.get_relevant_memories() (Context search)
   ↓
8. Inject memories into system prompt
   ↓
9. Enhanced AI Response
```

### Storage Structure
```
.hyena/
├── conversations/
│   ├── auto/           # Timestamped auto-conversations
│   └── named/          # Manually named conversations
├── memories/
│   ├── structured.json # Extracted insights database
│   └── topics/         # Topic-specific memory files
└── project/
    ├── Memories.md     # Project knowledge
    ├── Skills.md       # Learned capabilities
    └── agents.md       # Custom agents
```

## Configuration

### Memory Settings
```python
# In AutoMemoryOrchestrator
self.extraction_interval = 5  # Extract every 5 messages
self.max_memories = 100       # Maximum stored memories
self.context_limit = 8192     # Context token limit
```

### Extraction Customization
```python
# Custom extraction prompt
custom_prompt = """
Extract the following from this conversation:
1. Technical decisions made
2. Code patterns used
3. Important facts about the project
4. User preferences and requirements

Format as JSON with insights, decisions, patterns, topics, importance.
"""
```

## API Reference

### ConversationStore
```python
class ConversationStore:
    def start_conversation(self, first_message: str) -> str
    def append_message(self, role: str, content: str)
    def list_conversations(self) -> List[Dict]
    def load_conversation(self, filename: str) -> List[Dict]
```

### MemoryExtractor
```python
class MemoryExtractor:
    def extract_memories(self, conversation: List[Dict]) -> Dict
    def should_extract(self, messages_count: int) -> bool
```

### MemoryRetrieval
```python
class MemoryRetrieval:
    def get_relevant_memories(self, context: str, limit: int) -> List[Dict]
    def save_structured_memories(self, memories: List[Dict])
    def search_memories(self, query: str) -> List[Dict]
```

### AutoMemoryOrchestrator
```python
class AutoMemoryOrchestrator:
    def on_user_message(self, content: str)
    def on_assistant_message(self, content: str)
    def get_stats(self) -> Dict[str, Any]
    def get_relevant_context(self, user_input: str) -> str
```

## Usage Examples

### Basic Memory Usage
```python
# Initialize memory system
memory_orchestrator = AutoMemoryOrchestrator(llm, chat_system)

# Process user message (auto-saves and extracts)
memory_orchestrator.on_user_message("I'm building a FastAPI app")

# Get relevant context for new message
context = memory_orchestrator.get_relevant_context("Should I use SQLAlchemy?")

# Get memory statistics
stats = memory_orchestrator.get_stats()
print(f"Extracted {stats['insights']} insights from {stats['conversations']} conversations")
```

### Project Memory Usage
```python
# Initialize project memory
project_memory = ProjectMemory(workspace_manager)

# Load project configuration
project_config = project_memory.load_project_memory()

# Access project knowledge
project_knowledge = project_config['project_knowledge']
print(f"Project: {project_knowledge.get('project_name', 'Unknown')}")
```

## Performance Considerations

### Memory Efficiency
- **Lazy Loading**: Memories loaded only when needed
- **Indexed Search**: Fast semantic search capabilities
- **Automatic Cleanup**: Old memories pruned automatically

### Storage Optimization
- **Compressed Storage**: JSON format with efficient encoding
- **Incremental Updates**: Only save changes, not full history
- **Backup Strategy**: Automatic backups before modifications

## Troubleshooting

### Common Issues

**Memory Not Extracting**
```python
# Check extraction interval
if memory_orchestrator.messages_since_extraction < 5:
    print("Need more messages for extraction")
```

**Context Not Loading**
```python
# Check if memories exist
if not memory_retrieval.load_structured_memories():
    print("No structured memories found")
```

**Project Memory Not Loading**
```python
# Check configuration files
if not project_memory._get_config_path('memories'):
    print("No Memories.md file found")
```

### Debug Information
```python
# Enable debug mode
memory_orchestrator.debug = True

# Get detailed statistics
stats = memory_orchestrator.get_stats()
print(f"Memory system stats: {stats}")
```

## Future Enhancements

### Planned Features
- **Vector Database**: For faster semantic search
- **Memory Sharing**: Between projects and sessions
- **Memory Analytics**: Usage patterns and insights
- **Web Interface**: For memory management

### Extension Points
- **Custom Extractors**: For domain-specific extraction
- **Alternative Storage**: Database backends
- **Advanced Ranking**: Machine learning-based ranking

The memory system transforms Hyena-3 from a simple chatbot into a **context-aware AI assistant** that learns, remembers, and adapts to user needs and project contexts automatically.
