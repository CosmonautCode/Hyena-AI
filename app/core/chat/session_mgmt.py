"""Session management methods for ChatSystem."""

from pathlib import Path


class SessionManagementMixin:
    """Mixin for session management functionality."""
    
    def save_conversation(self, filename):
        """Save conversation to file."""
        self.conversation_manager.save_conversation(filename)
    
    def load_conversation(self, filename):
        """Load conversation from file."""
        self.conversation_manager.load_conversation(filename)
    
    def export_conversation(self, filename):
        """Export conversation to text file."""
        self.conversation_manager.export_conversation(filename)
    
    def get_session_stats(self):
        """Get session statistics."""
        user_messages = len([h for h in self.history if h[0] == "user"])
        assistant_messages = len([h for h in self.history if h[0] == "assistant"])
        return {
            'total_messages': len(self.history),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'current_agent': self.agent_config[self.current_agent_index]['name'] if self.agent_config else 'None',
            'session_time': 'Active'
        }
