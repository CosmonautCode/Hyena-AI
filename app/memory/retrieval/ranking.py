"""Ranking and filtering methods for MemoryRetrieval."""

from typing import List, Dict, Tuple
import time


class RankingMixin:
    """Mixin for memory ranking and filtering functionality."""
    
    def get_memories_by_recency(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memories sorted by recency
        """
        memories = self.load_structured_memories()
        
        # Sort by extraction time (newest first)
        memories.sort(key=lambda m: m.get("extracted_at", 0), reverse=True)
        
        return memories[:limit]
    
    def get_memories_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Get memories related to a specific topic.
        
        Args:
            topic: Topic to search for
            limit: Maximum number of memories to return
            
        Returns:
            List of memories related to the topic
        """
        memories = self.load_structured_memories()
        
        # Filter by topic
        topic_memories = []
        for memory in memories:
            topics = memory.get("topics", [])
            if any(topic.lower() in t.lower() for t in topics):
                topic_memories.append(memory)
        
        # Sort by relevance (most recent first)
        topic_memories.sort(key=lambda m: m.get("extracted_at", 0), reverse=True)
        
        return topic_memories[:limit]
    
    def get_memory_statistics(self) -> Dict:
        """
        Get statistics about stored memories.
        
        Returns:
            Dictionary with memory statistics
        """
        memories = self.load_structured_memories()
        
        if not memories:
            return {
                "total_memories": 0,
                "unique_topics": 0,
                "oldest_memory": None,
                "newest_memory": None,
                "average_age_days": 0
            }
        
        # Calculate statistics
        current_time = time.time()
        extraction_times = [m.get("extracted_at", current_time) for m in memories]
        
        oldest_time = min(extraction_times)
        newest_time = max(extraction_times)
        
        # Collect all topics
        all_topics = set()
        for memory in memories:
            all_topics.update(memory.get("topics", []))
        
        # Calculate average age
        ages = [(current_time - et) / (24 * 3600) for et in extraction_times]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            "total_memories": len(memories),
            "unique_topics": len(all_topics),
            "oldest_memory": time.strftime("%Y-%m-%d", time.localtime(oldest_time)),
            "newest_memory": time.strftime("%Y-%m-%d", time.localtime(newest_time)),
            "average_age_days": round(avg_age, 1),
            "topics": list(all_topics)
        }
    
    def cleanup_old_memories(self, days_threshold: int = 90) -> Dict:
        """
        Remove memories older than the specified threshold.
        
        Args:
            days_threshold: Age in days beyond which memories are removed
            
        Returns:
            Dictionary with cleanup results
        """
        memories = self.load_structured_memories()
        current_time = time.time()
        threshold_seconds = days_threshold * 24 * 3600
        
        # Filter out old memories
        recent_memories = []
        removed_count = 0
        
        for memory in memories:
            extracted_at = memory.get("extracted_at", current_time)
            if current_time - extracted_at <= threshold_seconds:
                recent_memories.append(memory)
            else:
                removed_count += 1
        
        # Save filtered memories
        self.save_structured_memories(recent_memories)
        
        return {
            "success": True,
            "removed_count": removed_count,
            "remaining_count": len(recent_memories),
            "days_threshold": days_threshold
        }
