"""Custom exceptions for Hyena-AI system."""

from typing import Optional, Dict, Any


class HyenaException(Exception):
    """Base exception for Hyena-AI system."""
    
    def __init__(self, message: str, code: str = "HYENA_ERROR", details: Optional[Dict[str, Any]] = None):
        """Initialize Hyena exception.
        
        Args:
            message: Error message
            code: Error code for identification
            details: Additional details about the error
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ToolExecutionError(HyenaException):
    """Raised when tool execution fails."""
    
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize tool execution error.
        
        Args:
            tool_name: Name of the tool that failed
            message: Error message
            details: Additional details
        """
        full_message = f"Tool '{tool_name}' failed: {message}"
        super().__init__(
            full_message,
            code="TOOL_EXECUTION_ERROR",
            details={**(details or {}), "tool_name": tool_name}
        )
        self.tool_name = tool_name


class PermissionDeniedError(HyenaException):
    """Raised when user denies permission."""
    
    def __init__(self, operation: str, reason: str = "User denied"):
        """Initialize permission denied error.
        
        Args:
            operation: Operation that was denied
            reason: Reason for denial
        """
        super().__init__(
            f"Permission denied for operation: {operation}",
            code="PERMISSION_DENIED",
            details={"operation": operation, "reason": reason}
        )
        self.operation = operation


class LLMError(HyenaException):
    """Raised when LLM operations fail."""
    
    def __init__(self, message: str, model: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize LLM error.
        
        Args:
            message: Error message
            model: Model name (if applicable)
            details: Additional details
        """
        super().__init__(
            message,
            code="LLM_ERROR",
            details={**(details or {}), "model": model}
        )
        self.model = model


class MemoryError(HyenaException):
    """Raised when memory operations fail."""
    
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize memory error.
        
        Args:
            operation: Memory operation that failed
            message: Error message
            details: Additional details
        """
        super().__init__(
            f"Memory operation '{operation}' failed: {message}",
            code="MEMORY_ERROR",
            details={**(details or {}), "operation": operation}
        )
        self.operation = operation


class WorkspaceError(HyenaException):
    """Raised when workspace operations fail."""
    
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize workspace error.
        
        Args:
            operation: Workspace operation that failed
            message: Error message
            details: Additional details
        """
        super().__init__(
            f"Workspace operation '{operation}' failed: {message}",
            code="WORKSPACE_ERROR",
            details={**(details or {}), "operation": operation}
        )
        self.operation = operation


class ConfigurationError(HyenaException):
    """Raised when configuration is invalid."""
    
    def __init__(self, setting: str, reason: str, details: Optional[Dict[str, Any]] = None):
        """Initialize configuration error.
        
        Args:
            setting: Configuration setting that's invalid
            reason: Reason it's invalid
            details: Additional details
        """
        super().__init__(
            f"Invalid configuration for '{setting}': {reason}",
            code="CONFIGURATION_ERROR",
            details={**(details or {}), "setting": setting}
        )
        self.setting = setting


class AgenticLoopError(HyenaException):
    """Raised when agentic loop fails."""
    
    def __init__(self, phase: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize agentic loop error.
        
        Args:
            phase: Phase that failed (gather, plan, execute, verify)
            message: Error message
            details: Additional details
        """
        super().__init__(
            f"Agentic loop failed at '{phase}' phase: {message}",
            code="AGENTIC_LOOP_ERROR",
            details={**(details or {}), "phase": phase}
        )
        self.phase = phase


class RetryableError(HyenaException):
    """Base exception for errors that can be retried."""
    
    def __init__(self, message: str, code: str = "RETRYABLE_ERROR", retry_count: int = 0, details: Optional[Dict[str, Any]] = None):
        """Initialize retryable error.
        
        Args:
            message: Error message
            code: Error code
            retry_count: Number of retries attempted
            details: Additional details
        """
        super().__init__(
            message,
            code=code,
            details={**(details or {}), "retry_count": retry_count, "retryable": True}
        )
        self.retry_count = retry_count


class TimeoutError(RetryableError):
    """Raised when operation times out."""
    
    def __init__(self, operation: str, timeout_seconds: float):
        """Initialize timeout error.
        
        Args:
            operation: Operation that timed out
            timeout_seconds: Timeout duration
        """
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            code="TIMEOUT_ERROR",
            details={"operation": operation, "timeout_seconds": timeout_seconds}
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds
