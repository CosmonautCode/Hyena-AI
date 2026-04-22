from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger("hyena.agents.permission")


class PermissionMode(Enum):
    """Permission modes for AI operations."""
    ASK = "ask"          # Always prompt for operations
    AUTO = "auto"        # Auto-approve safe, ask for dangerous


@dataclass
class PermissionRequest:
    """A permission request from the AI."""
    operation_type: str  # "file_read", "file_write", "terminal", "shell"
    description: str
    details: Optional[Dict] = None
    callback: Optional[Callable] = None


SAFE_OPERATIONS = {
    "file_read",
    "file_glob",
    "file_grep",
    "list_directory"
}

DANGEROUS_OPERATIONS = {
    "file_write",
    "file_delete",
    "terminal",
    "shell_command",
    "file_append"
}


class PermissionSystem:
    """Permission management system with proper prompting."""
    
    def __init__(self):
        self.current_mode = PermissionMode.ASK
        self.permanent_approvals = set()
        self.permanent_denials = set()
        self.session_approvals = {}
        
    def set_mode(self, mode) -> None:
        """Set permission mode.
        
        Args:
            mode: "ask", "auto", or PermissionMode enum
            
        Raises:
            ValueError: If mode is invalid
        """
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
        """Check if an operation is permitted.
        
        Args:
            request: PermissionRequest to check
            
        Returns:
            bool: True if operation is permitted
        """
        # Check permanent denials
        request_key = self._get_request_key(request)
        if request_key in self.permanent_denials:
            logger.warning(f"Permanently denied: {request.description}")
            return False
        
        # Check permanent approvals
        if request_key in self.permanent_approvals:
            logger.info(f"Permanently approved: {request.description}")
            return True
        
        # Auto mode logic
        if self.current_mode == PermissionMode.AUTO:
            if request.operation_type in SAFE_OPERATIONS:
                logger.info(f"Auto-approved safe operation: {request.operation_type}")
                return True
            elif request.operation_type in DANGEROUS_OPERATIONS:
                logger.warning(f"Dangerous operation requires approval: {request.description}")
                return self._prompt_user(request)
            else:
                # Unknown operation - ask
                return self._prompt_user(request)
        
        # Ask mode - always prompt
        return self._prompt_user(request)
    
    def _prompt_user(self, request: PermissionRequest) -> bool:
        """Prompt user for permission.
        
        Args:
            request: Permission request
            
        Returns:
            bool: True if user approved
        """
        logger.warning(f"Requesting user permission for: {request.description}")
        
        # This should be integrated with TUI
        # For now, log and default to False for safety
        # The TUI will override this when integrated
        
        prompt = f"\n{'='*60}\n"
        prompt += f"Permission Required: {request.operation_type}\n"
        prompt += f"Description: {request.description}\n"
        if request.details:
            prompt += f"Details: {request.details}\n"
        prompt += f"{'='*60}\n"
        prompt += "Allow this operation? [Y]es [N]o [A]lways [D]eny: "
        
        try:
            response = input(prompt).lower().strip()
            
            request_key = self._get_request_key(request)
            
            if response in ['y', 'yes']:
                logger.info(f"User approved: {request.description}")
                return True
            elif response in ['a', 'always']:
                logger.info(f"User permanently approved: {request.description}")
                self.permanent_approvals.add(request_key)
                return True
            elif response in ['d', 'deny']:
                logger.info(f"User permanently denied: {request.description}")
                self.permanent_denials.add(request_key)
                return False
            else:
                # Default to deny for safety
                logger.warning(f"User declined: {request.description}")
                return False
        except EOFError:
            # Running in non-interactive mode
            logger.warning("Non-interactive mode: denying permission for safety")
            return False
    
    def _get_request_key(self, request: PermissionRequest) -> str:
        """Get a unique key for a permission request.
        
        Args:
            request: Permission request
            
        Returns:
            str: Unique key for the request
        """
        # Create hash of operation type + description for deduplication
        return f"{request.operation_type}:{request.description[:50]}"
    
    def reset_session(self) -> None:
        """Reset session approvals (but keep permanent ones)."""
        self.session_approvals.clear()
        logger.info("Session permissions reset")
    
    def reset_all(self) -> None:
        """Reset all permissions."""
        self.permanent_approvals.clear()
        self.permanent_denials.clear()
        self.session_approvals.clear()
        logger.info("All permissions reset")
