from typing import Dict, List, Optional, Any
import json
import time
from pathlib import Path


class ContextCompactor:
    """Manages context compaction and summarization."""
    
    def __init__(self, max_tokens: int = 8192, compression_ratio: float = 0.7):
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self.compaction_history = []
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple approximation: ~4 characters per token
        return len(text) // 4
    
    def needs_compaction(self, history: List[tuple]) -> bool:
        """Check if context needs compaction."""
        total_tokens = 0
        for role, content in history:
            if content:
                total_tokens += self.estimate_tokens(content)
        return total_tokens > (self.max_tokens * self.compression_ratio)
    
    def compact_history(self, history: List[tuple], llm=None) -> List[tuple]:
        """Compact conversation history."""
        if not self.needs_compaction(history):
            return history
        
        # Strategy 1: Keep recent messages, summarize old ones
        recent_messages = history[-10:]  # Keep last 10 messages
        old_messages = history[:-10]
        
        if old_messages:
            summary = self._summarize_messages(old_messages, llm)
            compacted_message = {
                "role": "system",
                "content": f"[COMPACTED] {summary}",
                "timestamp": time.time(),
                "metadata": {
                    "compacted": True,
                    "original_count": len(old_messages),
                    "compacted_at": time.time()
                }
            }
            
            new_history = [compacted_message] + recent_messages
            
            # Record compaction
            self.compaction_history.append({
                "timestamp": time.time(),
                "original_count": len(history),
                "new_count": len(new_history),
                "compression_ratio": len(new_history) / len(history)
            })
            
            return new_history
        
        return history
    
    def _summarize_messages(self, messages: List[Dict], llm=None) -> str:
        """Summarize a list of messages."""
        if not llm:
            # Simple summarization without LLM
            return self._simple_summary(messages)
        
        try:
            # Create summary prompt
            summary_text = self._create_summary_text(messages)
            prompt = f"Summarize this conversation in 2-3 sentences:\n\n{summary_text}"
            
            response = llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            return response["choices"][0]["message"]["content"].strip()
        
        except Exception:
            # Fallback to simple summary
            return self._simple_summary(messages)
    
    def _simple_summary(self, messages: List[Dict]) -> str:
        """Simple summarization without LLM."""
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        # Extract key topics from user messages
        topics = []
        for msg in user_messages[:5]:  # First 5 user messages
            content = msg["content"]
            # Simple keyword extraction
            if "file" in content.lower():
                topics.append("file operations")
            if "code" in content.lower():
                topics.append("code discussion")
            if "error" in content.lower():
                topics.append("error troubleshooting")
        
        summary = f"Conversation covered {len(user_messages)} user interactions and {len(assistant_messages)} AI responses"
        if topics:
            summary += f", discussing: {', '.join(set(topics))}"
        
        return summary
    
    def _create_summary_text(self, messages: List[Dict]) -> str:
        """Create text for summarization."""
        summary_lines = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            # Truncate very long messages
            if len(content) > 200:
                content = content[:200] + "..."
            summary_lines.append(f"{role.upper()}: {content}")
        
        return "\n".join(summary_lines)
    
    def compact_tool_outputs(self, history: List[Dict]) -> List[Dict]:
        """Compact large tool outputs in history."""
        compacted_history = []
        
        for msg in history:
            if msg.get("metadata", {}).get("tool_output"):
                # Check if content is too large
                content = msg["content"]
                if len(content) > 2000:
                    # Truncate tool outputs
                    truncated = content[:1000] + "\n\n[... OUTPUT TRUNCATED ...]\n\n" + content[-500:]
                    compacted_msg = msg.copy()
                    compacted_msg["content"] = truncated
                    compacted_msg["metadata"]["truncated"] = True
                    compacted_history.append(compacted_msg)
                else:
                    compacted_history.append(msg)
            else:
                compacted_history.append(msg)
        
        return compacted_history
    
    def get_compaction_stats(self) -> Dict[str, Any]:
        """Get statistics about compaction history."""
        if not self.compaction_history:
            return {"total_compactions": 0}
        
        total_compactions = len(self.compaction_history)
        avg_compression = sum(c["compression_ratio"] for c in self.compaction_history) / total_compactions
        
        return {
            "total_compactions": total_compactions,
            "average_compression_ratio": avg_compression,
            "last_compaction": self.compaction_history[-1]["timestamp"] if self.compaction_history else None
        }
