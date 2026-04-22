"""Conversation operations for SessionManager."""

from typing import Optional
from datetime import datetime
from .base import SessionManager


class ConversationMixin(SessionManager):
    """Mixin for conversation operations."""
    
    def save_conversation(self, filename: str, chat_system) -> bool:
        """Save conversation to file (consolidated from ConversationManager)."""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "agent": chat_system.agent_config[chat_system.current_agent_index]["name"],
                "history": chat_system.history
            }
            
            with open(filename, 'w') as f:
                import json
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_conversation(self, filename: str, chat_system) -> bool:
        """Load conversation from file (consolidated from ConversationManager)."""
        try:
            with open(filename, 'r') as f:
                import json
                data = json.load(f)
            
            chat_system.history = data.get("history", [])
            
            # Find and set the agent
            agent_name = data.get("agent", "")
            for i, agent in enumerate(chat_system.agent_config):
                if agent["name"] == agent_name:
                    chat_system.choose_agent(i)
                    break
            return True
        except Exception:
            return False
    
    def export_conversation(self, filename: str, chat_system) -> bool:
        """Export conversation to readable text format (consolidated from ConversationManager)."""
        try:
            with open(filename, 'w') as f:
                f.write(f"Conversation Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Agent: {chat_system.agent_config[chat_system.current_agent_index]['name']}\n")
                f.write("=" * 50 + "\n\n")
                
                for role, content in chat_system.history:
                    if role == "user":
                        f.write(f"You: {content}\n\n")
                    else:
                        f.write(f"{chat_system.agent_config[chat_system.current_agent_index]['name']}: {content}\n\n")
            return True
        except Exception:
            return False
