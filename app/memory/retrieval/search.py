"""Search functionality for MemoryRetrieval."""

from typing import List, Dict, Tuple


class SearchMixin:
    """Mixin for memory search functionality."""
    
    def calculate_relevance(self, query: str, memory: Dict) -> float:
        """
        Calculate relevance score between query and memory.
        Simple keyword matching - can be enhanced with embeddings.
        
        Args:
            query: Current user message or context
            memory: Structured memory dict
            
        Returns:
            Relevance score 0-1
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        if not query_words:
            return 0.0
        
        score = 0.0
        
        # Check topics
        for topic in memory.get("topics", []):
            if topic.lower() in query_lower:
                score += 0.3
        
        # Check insights
        for insight in memory.get("insights", []):
            insight_words = set(insight.lower().split())
            overlap = len(query_words & insight_words)
            if overlap > 0:
                score += 0.2 * (overlap / len(insight_words))
        
        # Check summary
        summary = memory.get("summary", "")
        summary_words = set(summary.lower().split())
        overlap = len(query_words & summary_words)
        if overlap > 0:
            score += 0.1 * (overlap / len(summary_words))
        
        # Boost score for recent memories
        extracted_at = memory.get("extracted_at", 0)
        days_old = (time.time() - extracted_at) / (24 * 3600)
        if days_old < 7:
            score *= 1.2  # 20% boost for memories less than a week old
        elif days_old < 30:
            score *= 1.1  # 10% boost for memories less than a month old
        
        return min(score, 1.0)
    
    def search_memories(self, query: str, limit: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for relevant memories based on query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of (memory, score) tuples
        """
        memories = self.load_structured_memories()
        
        # Calculate relevance scores
        scored_memories = []
        for memory in memories:
            score = self.calculate_relevance(query, memory)
            if score > 0.1:  # Only include memories with meaningful relevance
                scored_memories.append((memory, score))
        
        # Sort by relevance score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return scored_memories[:limit]
    
    def get_context_for_prompt(self, query: str, max_memories: int = 3) -> str:
        """
        Get formatted context string for prompt injection.
        
        Args:
            query: Current user message
            max_memories: Maximum memories to include
            
        Returns:
            Formatted context string
        """
        relevant_memories = self.search_memories(query, max_memories)
        
        if not relevant_memories:
            return ""
        
        context_parts = []
        context_parts.append("Relevant project context:")
        context_parts.append("")
        
        for i, (memory, score) in enumerate(relevant_memories, 1):
            context_parts.append(f"Memory {i} (relevance: {score:.2f}):")
            
            # Add summary if available
            if memory.get("summary"):
                context_parts.append(f"  {memory['summary']}")
            
            # Add key insights
            insights = memory.get("insights", [])
            if insights:
                context_parts.append("  Key insights:")
                for insight in insights[:3]:  # Limit to top 3 insights
                    context_parts.append(f"    - {insight}")
            
            # Add topics
            topics = memory.get("topics", [])
            if topics:
                context_parts.append(f"  Topics: {', '.join(topics)}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
