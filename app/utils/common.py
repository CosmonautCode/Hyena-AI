"""Common utility functions for error handling and responses."""

from typing import Dict, Any, Optional


def create_error_response(error: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": error
    }
    if details:
        response["details"] = details
    return response


def create_success_response(message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Create standardized success response."""
    response = {
        "success": True,
        "message": message
    }
    if data:
        response["data"] = data
    return response


def safe_execute(func, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a function and return standardized response."""
    try:
        result = func(*args, **kwargs)
        if isinstance(result, dict) and "success" in result:
            return result
        return create_success_response("Operation completed", {"result": result})
    except Exception as e:
        return create_error_response(str(e))


def validate_file_path(path: str) -> bool:
    """Validate if a file path is safe."""
    import os
    # Basic safety checks
    if not path or not isinstance(path, str):
        return False
    
    # Prevent path traversal
    if ".." in path or path.startswith("/"):
        return False
    
    return True


def validate_command(command: str) -> bool:
    """Validate if a shell command is safe."""
    if not command or not isinstance(command, str):
        return False
    
    # Basic dangerous command patterns
    dangerous = ["rm -rf /", "format", "mkfs", "fdisk", "shutdown", "reboot"]
    command_lower = command.lower()
    
    for pattern in dangerous:
        if pattern in command_lower:
            return False
    
    return True
