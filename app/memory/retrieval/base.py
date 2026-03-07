"""Base MemoryRetrieval class and core functionality."""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .search import SearchMixin
from .ranking import RankingMixin


class MemoryRetrieval(SearchMixin, RankingMixin):
    """
    Retrieves relevant memories based on current context and injects
    them into system prompts for enhanced AI responses.
    """
    
    def __init__(self, memory_store_path: str = ".hyena/memories"):
        """
        Initialize memory retrieval.
        
        Args:
            memory_store_path: Path to memory storage directory
        """
        self.memory_path = Path(memory_store_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.structured_file = self.memory_path / "structured.json"
    
    def load_structured_memories(self) -> List[Dict]:
        """Load all structured memories from disk."""
        if self.structured_file.exists():
            try:
                return json.loads(self.structured_file.read_text(encoding='utf-8'))
            except Exception:
                return []
        return []
    
    def save_structured_memories(self, memories: List[Dict]):
        """Save structured memories to disk."""
        try:
            self.memory_path.mkdir(parents=True, exist_ok=True)
            self.structured_file.write_text(
                json.dumps(memories, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    def add_memory(self, memory: Dict):
        """
        Add a new structured memory.
        
        Args:
            memory: Extracted memory dict with insights, topics, etc.
        """
        memories = self.load_structured_memories()
        
        # Add timestamp if not present
        if "extracted_at" not in memory:
            memory["extracted_at"] = time.time()
        
        # Add to list
        memories.append(memory)
        
        # Keep only recent memories (last 100)
        if len(memories) > 100:
            # Sort by extraction time and keep newest
            memories.sort(key=lambda m: m.get("extracted_at", 0), reverse=True)
            memories = memories[:100]
        
        self.save_structured_memories(memories)
