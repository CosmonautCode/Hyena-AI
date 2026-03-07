"""Statistics and monitoring for AutoMemoryOrchestrator."""

from typing import Dict, Any
import time


class StatsMixin:
    """Mixin for statistics and monitoring functionality."""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the memory system."""
        try:
            # Get conversation stats
            conv_stats = self.conversation_store.get_stats()
            
            # Get memory stats
            mem_stats = {}
            if hasattr(self, 'memory_retrieval') and self.memory_retrieval:
                mem_stats = self.memory_retrieval.get_memory_statistics()
            
            # Get current session info
            current_session = None
            if hasattr(self.conversation_store, 'current_auto_file') and self.conversation_store.current_auto_file:
                current_session = self.conversation_store.current_auto_file.name
            
            return {
                "conversations": conv_stats,
                "memories": mem_stats,
                "current_session": current_session,
                "messages_since_extraction": getattr(self, 'messages_since_extraction', 0),
                "extraction_interval": getattr(self, 'extraction_interval', 5),
                "auto_active": True
            }
        except Exception as e:
            return {"error": str(e), "auto_active": False}
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation summaries."""
        try:
            return self.conversation_store.list_sessions(limit=limit)
        except Exception as e:
            return []
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get recent memories."""
        try:
            return self.memory_retrieval.get_memories_by_recency(limit)
        except Exception as e:
            return []
