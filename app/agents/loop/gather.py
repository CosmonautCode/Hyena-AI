"""Context gathering methods for AgenticLoop."""

from typing import Dict, List, Any
import time


class GatherMixin:
    """Mixin for context gathering functionality."""
    
    def _gather_context(self, user_input: str, conversation_history: List) -> Dict[str, Any]:
        """Gather context for the request."""
        return {
            "user_input": user_input,
            "conversation_history": conversation_history[-5:],  # Last 5 messages
            "workspace": self.workspace_manager.get_workspace(),
            "available_tools": list(self.tool_registry.keys()),
            "timestamp": time.time()
        }
