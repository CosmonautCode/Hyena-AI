"""Base tool class for Hyena-AI tool system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolMetadata:
    """Metadata for a tool."""
    name: str
    version: str = "1.0.0"
    category: str = "general"  # "file", "code", "git", "web", "ai", etc.
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)  # JSON Schema
    returns: Dict[str, Any] = field(default_factory=dict)     # JSON Schema
    permissions: List[str] = field(default_factory=list)
    enabled: bool = True
    cost_estimate: Optional[Dict[str, float]] = None  # {"tokens": 100, "latency_ms": 50}


class BaseTool(ABC):
    """Base class for all Hyena-AI tools."""
    
    metadata: ToolMetadata
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool."""
        pass
    
    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """Validate input parameters."""
        pass
    
    def format_schema(self) -> Dict[str, Any]:
        """Return tool schema for introspection."""
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "parameters": self.metadata.parameters,
            "returns": self.metadata.returns,
            "version": self.metadata.version,
            "category": self.metadata.category,
            "enabled": self.metadata.enabled,
        }
    
    def __repr__(self) -> str:
        return f"<Tool {self.metadata.name} v{self.metadata.version}>"


# Example built-in tool
class EchoTool(BaseTool):
    """Simple echo tool for testing."""
    
    metadata = ToolMetadata(
        name="echo",
        version="1.0.0",
        category="system",
        description="Echo tool - returns input as output",
        parameters={"message": {"type": "string", "description": "Message to echo"}},
        returns={"message": {"type": "string", "description": "Echoed message"}},
    )
    
    async def execute(self, message: str = "", **kwargs: Any) -> Dict[str, Any]:
        """Echo the input."""
        return {"message": message}
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate echo tool."""
        return "message" in kwargs or len(kwargs) == 0
