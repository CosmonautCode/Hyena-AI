"""Base service class for Hyena-AI service system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseService(ABC):
    """Base class for all Hyena-AI services."""
    
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check for service."""
        pass
    
    def __repr__(self) -> str:
        return f"<Service {self.name} v{self.version}>"


# Built-in services
class HealthService(BaseService):
    """System health service."""
    
    name = "health"
    version = "1.0.0"
    
    async def initialize(self) -> None:
        """Initialize health service."""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown health service."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check."""
        return {"status": "healthy", "service": "health"}
