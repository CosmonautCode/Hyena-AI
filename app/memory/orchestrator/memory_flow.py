"""Memory flow management for AutoMemoryOrchestrator."""

from typing import List, Dict, Optional
from pathlib import Path

from app.memory.store import ConversationStore
from app.memory.extractor import MemoryExtractor
from app.memory.retrieval import MemoryRetrieval


class MemoryFlowMixin:
    """Mixin for memory flow functionality."""
    
    def on_user_message(self, content: str, is_first_message: bool = False):
        """
        Called when user sends a message.
        
        Args:
            content: The message content
            is_first_message: Whether this is the first message in conversation
        """
        # Start new conversation file if this is the first message
        if is_first_message:
            filename = self.conversation_store.start_conversation(content)
            # Reset extraction counter for new conversation
            self.messages_since_extraction = 0
        
        # Append to conversation store
        self.conversation_store.append_message("user", content)
        self.messages_since_extraction += 1
        
        # Check if we should extract memories (Phase 2)
        self._maybe_extract_memories()
    
    def on_assistant_message(self, content: str):
        """
        Called when assistant responds.
        
        Args:
            content: The response content
        """
        # Append to conversation store
        self.conversation_store.append_message("assistant", content)
        self.messages_since_extraction += 1
        
        # Check if we should extract memories (Phase 2)
        self._maybe_extract_memories()
    
    def _maybe_extract_memories(self):
        """Check if we should run memory extraction."""
        if self.memory_extractor.should_extract(self.messages_since_extraction, self.extraction_interval):
            self._extract_memories()
            self.messages_since_extraction = 0
    
    def _extract_memories(self):
        """
        Extract insights from recent conversation using LLM.
        Phase 2 implementation.
        """
        # Get last messages for analysis
        recent_messages = [
            {"role": role, "content": content}
            for role, content in self.chat_system.history[-self.extraction_interval:]
        ]
        
        if len(recent_messages) < 2:
            return
        
        # Use MemoryExtractor to analyze
        extracted = self.memory_extractor.extract(recent_messages)
        
        if extracted and extracted.get("insights"):
            # Store extracted memories
            for insight in extracted["insights"]:
                memory = {
                    "insights": [insight.get("text", "")],
                    "topics": insight.get("topics", []),
                    "summary": insight.get("summary", ""),
                    "context": insight.get("context", ""),
                    "confidence": insight.get("confidence", 0.5)
                }
                self.memory_retrieval.add_memory(memory)
    
    def get_context_for_prompt(self, query: str) -> str:
        """Get relevant context for prompt injection."""
        return self.memory_retrieval.get_context_for_prompt(query)
    
    def force_save(self) -> Dict[str, Any]:
        """Force save current conversation."""
        try:
            if self.conversation_store.current_session:
                return self.conversation_store.save_session()
            else:
                return {"success": False, "error": "No active session"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def force_extraction(self) -> Dict[str, Any]:
        """Force memory extraction from current conversation."""
        try:
            original_count = self.messages_since_extraction
            self.messages_since_extraction = self.extraction_interval  # Force extraction
            self._extract_memories()
            self.messages_since_extraction = original_count  # Restore counter
            return {"success": True, "message": "Memory extraction completed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
