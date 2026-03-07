"""Session statistics and utilities."""

from typing import Dict, Any
import time
from .base import SessionManager


class StatsMixin(SessionManager):
    """Mixin for session statistics functionality."""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session."""
        if self.current_session_data is None:
            return {}
        
        history = self.current_session_data.get("history", [])
        user_messages = [m for m in history if m["role"] == "user"]
        assistant_messages = [m for m in history if m["role"] == "assistant"]
        
        return {
            "session_id": self.current_session_id,
            "total_messages": len(history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_duration": time.time() - self.current_session_data["created_at"],
            "context_usage": self.current_session_data.get("context_usage", 0),
            "session_cost": self.current_session_data.get("session_cost", 0.0)
        }
