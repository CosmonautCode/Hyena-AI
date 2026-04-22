"""Base AutoMemoryOrchestrator class and core functionality."""

import json
import time
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from app.memory.store import ConversationStore
from app.memory.extractor import MemoryExtractor
from app.memory.retrieval import MemoryRetrieval
from .memory_flow import MemoryFlowMixin
from .stats import StatsMixin


class AutoMemoryOrchestrator(MemoryFlowMixin, StatsMixin):
    """
    Main orchestrator that ties together auto-save, memory extraction,
    and context retrieval. Provides seamless conversation persistence
    without requiring manual saves.
    """
    
    def __init__(self, llm, chat_system, base_path: str = ".hyena"):
        """
        Initialize the auto-memory orchestrator.
        
        Args:
            llm: The LLM instance for memory extraction
            chat_system: The ChatSystem instance for accessing history
            base_path: Base directory for memory storage
        """
        self.llm = llm
        self.chat_system = chat_system
        self.base_path = Path(base_path)
        
        # Initialize conversation store
        self.conversation_store = ConversationStore(str(self.base_path / "conversations"))
        
        # Initialize memory extractor and retrieval (Phase 2)
        self.memory_extractor = MemoryExtractor(llm)
        self.memory_retrieval = MemoryRetrieval(str(self.base_path / "memories"))
        
        # State tracking
        self.messages_since_extraction = 0
        self.extraction_interval = 5  # Extract memories every 5 messages
