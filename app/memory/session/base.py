"""Session persistence and state management."""

from typing import Dict, List, Optional, Any
import json
import time
from pathlib import Path


class SessionManager:
    """Manages session persistence and state."""
    
    def __init__(self, workspace_dir: str = ".hyena/sessions"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id = None
        self.current_session_data = None
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session."""
        if session_id is None:
            session_id = self._generate_session_id()
        
        session_file = self.workspace_dir / f"{session_id}.json"
        
        # Check if session already exists
        if session_file.exists():
            # Generate new ID if collision
            session_id = self._generate_session_id()
            session_file = self.workspace_dir / f"{session_id}.json"
        
        session_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "last_updated": time.time(),
            "history": [],
            "workspace": "",
            "current_agent": 0,
            "context_usage": 0,
            "session_cost": 0.0,
            "metadata": {}
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.current_session_id = session_id
        self.current_session_data = session_data
        
        return session_id
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load an existing session."""
        session_file = self.workspace_dir / f"{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        self.current_session_id = session_id
        self.current_session_data = session_data
        
        return session_data
    
    def save_session(self, session_data: Optional[Dict] = None) -> bool:
        """Save current session state."""
        if self.current_session_id is None:
            return False
        
        if session_data is None:
            session_data = self.current_session_data
        
        if session_data is None:
            return False
        
        session_data["last_updated"] = time.time()
        
        session_file = self.workspace_dir / f"{self.current_session_id}.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def update_session(self, updates: Dict[str, Any]) -> None:
        """Update current session with new data."""
        if self.current_session_data is None:
            return
        
        self.current_session_data.update(updates)
        self.save_session()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the current session."""
        if self.current_session_data is None:
            return
        
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.current_session_data["history"].append(message)
        self.save_session()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history."""
        if self.current_session_data is None:
            return []
        
        history = self.current_session_data.get("history", [])
        if limit:
            return history[-limit:]
        return history
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        sessions = []
        
        for session_file in self.workspace_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "session_id": session_data["session_id"],
                    "created_at": session_data["created_at"],
                    "last_updated": session_data["last_updated"],
                    "message_count": len(session_data.get("history", [])),
                    "workspace": session_data.get("workspace", "")
                })
            except Exception:
                continue
        
        # Sort by last updated
        sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_file = self.workspace_dir / f"{session_id}.json"
        
        try:
            session_file.unlink()
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.current_session_data = None
            return True
        except Exception:
            return False
    
    def fork_session(self, parent_session_id: str, new_session_id: Optional[str] = None) -> str:
        """Fork an existing session."""
        parent_data = self.load_session(parent_session_id)
        
        # Create new session with parent's data
        new_session_id = self.create_session(new_session_id)
        
        # Copy parent data but reset timestamps
        parent_data["session_id"] = new_session_id
        parent_data["created_at"] = time.time()
        parent_data["last_updated"] = time.time()
        parent_data["metadata"] = {
            **parent_data.get("metadata", {}),
            "forked_from": parent_session_id
        }
        
        self.current_session_data = parent_data
        self.save_session()
        
        return new_session_id
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = str(int(time.time()))
        random_data = str(time.time_ns())[-6:]
        return f"session_{timestamp}_{random_data}"
