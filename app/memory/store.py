"""Automatic conversation persistence - no manual save needed."""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional


class ConversationStore:
    """Automatically saves every conversation, no manual save required."""
    
    def __init__(self, base_path: str = ".hyena/conversations"):
        self.auto_path = Path(base_path) / "auto"
        self.named_path = Path(base_path) / "named"
        self.auto_path.mkdir(parents=True, exist_ok=True)
        self.named_path.mkdir(parents=True, exist_ok=True)
        self.current_auto_file: Optional[Path] = None
    
    def _slugify(self, text: str) -> str:
        """Convert text to filesystem-safe slug."""
        # Remove non-alphanumeric, replace spaces with dashes
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:40]  # Limit length
    
    def start_conversation(self, first_message: str) -> str:
        """Called when first user message arrives."""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        slug = self._slugify(first_message[:40])
        filename = f"{timestamp}-{slug}.json"
        self.current_auto_file = self.auto_path / filename
        
        # Initialize conversation file with first message
        data = {
            "started_at": time.time(),
            "filename": filename,
            "messages": [{
                "role": "user",
                "content": first_message,
                "timestamp": time.time()
            }]
        }
        self._atomic_save(data)
        return filename
    
    def append_message(self, role: str, content: str):
        """Auto-save every message as it happens."""
        if not self.current_auto_file:
            return
        
        data = self._load_current()
        if data is None:
            return
            
        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self._atomic_save(data)
    
    def _load_current(self) -> Optional[Dict]:
        """Load current conversation data."""
        if not self.current_auto_file or not self.current_auto_file.exists():
            return None
        try:
            return json.loads(self.current_auto_file.read_text(encoding='utf-8'))
        except Exception:
            return None
    
    def _atomic_save(self, data: Dict):
        """Atomically save data to file."""
        if not self.current_auto_file:
            return
        
        try:
            # Write to temp file then rename for atomicity
            temp_file = self.current_auto_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            temp_file.replace(self.current_auto_file)
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def list_conversations(self, limit: int = 50) -> List[Dict]:
        """List recent conversations with summaries."""
        conversations = []
        
        # Get all json files sorted by modification time (newest first)
        all_files = sorted(
            self.auto_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for file in all_files[:limit]:
            try:
                data = json.loads(file.read_text(encoding='utf-8'))
                messages = data.get("messages", [])
                
                # Get preview from first user message
                preview = ""
                for msg in messages:
                    if msg.get("role") == "user":
                        preview = msg.get("content", "")[:60]
                        break
                
                # Format date from filename
                date_str = file.stem[:10]  # YYYY-MM-DD
                time_str = file.stem[11:15]  # HHMM
                formatted_date = f"{date_str} {time_str[:2]}:{time_str[2:]}"
                
                conversations.append({
                    "filename": file.name,
                    "date": formatted_date,
                    "preview": preview + "..." if len(preview) >= 60 else preview,
                    "message_count": len(messages),
                    "path": str(file)
                })
            except Exception:
                continue
        
        return conversations
    
    def load_conversation(self, filename: str) -> List[Tuple[str, str]]:
        """Load a conversation into history format."""
        # Try auto path first, then named path
        for path in [self.auto_path, self.named_path]:
            file = path / filename
            if file.exists():
                try:
                    data = json.loads(file.read_text(encoding='utf-8'))
                    return [(m["role"], m["content"]) for m in data.get("messages", [])]
                except Exception as e:
                    raise FileNotFoundError(f"Error loading {filename}: {e}")
        
        raise FileNotFoundError(f"Conversation {filename} not found")
    
    def delete_conversation(self, filename: str) -> bool:
        """Delete a conversation file."""
        for path in [self.auto_path, self.named_path]:
            file = path / filename
            if file.exists():
                try:
                    file.unlink()
                    # If we're deleting the current conversation, reset it
                    if self.current_auto_file and self.current_auto_file.name == filename:
                        self.current_auto_file = None
                    return True
                except Exception:
                    return False
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored conversations."""
        try:
            # Count total conversations
            auto_files = list(self.auto_path.glob("*.json"))
            named_files = list(self.named_path.glob("*.json"))
            total_conversations = len(auto_files) + len(named_files)
            
            # Get current session info
            current_session = None
            if self.current_auto_file:
                current_session = self.current_auto_file.name
            
            return {
                "total_conversations": total_conversations,
                "auto_saved": len(auto_files),
                "named_saved": len(named_files),
                "current_session": current_session,
                "has_active_session": self.current_auto_file is not None
            }
        except Exception:
            return {
                "total_conversations": 0,
                "auto_saved": 0,
                "named_saved": 0,
                "current_session": None,
                "has_active_session": False
            }
    
    def save_named(self, name: str, history: List[Tuple[str, str]], agent_name: str = ""):
        """User explicitly names and saves current conversation."""
        # Sanitize name
        safe_name = self._slugify(name)
        file = self.named_path / f"{safe_name}.json"
        
        data = {
            "name": name,
            "saved_at": time.time(),
            "agent": agent_name,
            "messages": [{"role": r, "content": c} for r, c in history]
        }
        
        try:
            file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            return True
        except Exception:
            return False
