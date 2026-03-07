from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


class PermissionMode(Enum):
    """Simplified permission modes for AI operations."""
    ASK = "ask"          # Prompt for dangerous operations
    AUTO = "auto"        # Auto-accept safe operations, ask for dangerous ones


@dataclass
class PermissionRequest:
    """A permission request from the AI."""
    operation_type: str  # "file_read", "file_write", "terminal"
    description: str
    details: Optional[Dict] = None
    callback: Optional[Callable] = None


class PermissionSystem:
    """Simplified permission management."""
    
    def __init__(self):
        self.current_mode = PermissionMode.ASK
        
    def set_mode(self, mode: str) -> None:
        """Set permission mode."""
        if isinstance(mode, str):
            mode = mode.lower()
            if mode == "ask":
                self.current_mode = PermissionMode.ASK
            elif mode == "auto":
                self.current_mode = PermissionMode.AUTO
            else:
                raise ValueError(f"Invalid permission mode: {mode}")
        elif isinstance(mode, PermissionMode):
            self.current_mode = mode
        else:
            raise ValueError("Mode must be string or PermissionMode enum")
    
    def check_permission(self, request: PermissionRequest) -> bool:
        """Check if an operation is permitted based on current mode."""
        # Auto mode - allow file operations, ask for terminal
        if self.current_mode == PermissionMode.AUTO:
            if request.operation_type in ["file_read", "file_write"]:
                return True
            elif request.operation_type == "terminal":
                return self._prompt_user(request)
        
        # Ask mode - prompt for everything
        return self._prompt_user(request)
    
    def _prompt_user(self, request: PermissionRequest) -> bool:
        """Prompt user for permission (placeholder for UI integration)."""
        # This will be integrated with the UI system
        # For now, return True as default
        return True
