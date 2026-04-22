"""Service registry and management system."""

from typing import Dict, Optional
from app.services.base import BaseService


class ServiceRegistry:
    """Registry for all services."""
    
    def __init__(self):
        self._services: Dict[str, BaseService] = {}
    
    def register(self, service: BaseService) -> None:
        """Register a service."""
        self._services[service.name] = service
    
    def get(self, name: str) -> Optional[BaseService]:
        """Get service by name."""
        return self._services.get(name)
    
    def list_all(self) -> list:
        """List all services."""
        return list(self._services.values())
    
    async def initialize_all(self) -> None:
        """Initialize all services."""
        for service in self._services.values():
            await service.initialize()
    
    async def shutdown_all(self) -> None:
        """Shutdown all services."""
        for service in self._services.values():
            await service.shutdown()
    
    async def health_check_all(self) -> Dict[str, dict]:
        """Get health status for all services."""
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = await service.health_check()
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        return {
            "total_services": len(self._services),
            "enabled": sum(1 for s in self._services.values() if s.enabled),
        }


# Global registry instance
_global_service_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """Get or create the global service registry."""
    global _global_service_registry
    if _global_service_registry is None:
        _global_service_registry = ServiceRegistry()
        # Register built-in services
        from app.services.base import HealthService
        _global_service_registry.register(HealthService())
    return _global_service_registry


def register_service(service: BaseService) -> None:
    """Register a service with the global registry."""
    get_service_registry().register(service)
