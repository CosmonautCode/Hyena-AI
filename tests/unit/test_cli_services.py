"""Unit tests for service registry system."""

import pytest
from app.services.base import BaseService
from app.services.registry import ServiceRegistry


class TestService(BaseService):
    """Test service for unit tests."""
    
    name = "test_service"
    version = "1.0.0"
    
    def __init__(self):
        self.initialized = False
        self.shutdown_flag = False
    
    async def initialize(self):
        self.initialized = True
    
    async def shutdown(self):
        self.shutdown_flag = True
    
    async def health_check(self):
        return {"status": "healthy", "service": "test_service"}


class TestServiceRegistry:
    """Tests for ServiceRegistry."""
    
    def test_register_service(self):
        """Test registering a service."""
        registry = ServiceRegistry()
        service = TestService()
        registry.register(service)
        
        assert registry.get("test_service") == service
    
    def test_list_all_services(self):
        """Test listing all services."""
        registry = ServiceRegistry()
        service1 = TestService()
        service2 = TestService()
        service2.name = "test_service2"
        
        registry.register(service1)
        registry.register(service2)
        
        all_services = registry.list_all()
        assert len(all_services) == 2
    
    def test_get_nonexistent_service(self):
        """Test getting nonexistent service."""
        registry = ServiceRegistry()
        assert registry.get("nonexistent") is None
    
    def test_registry_stats(self):
        """Test registry statistics."""
        registry = ServiceRegistry()
        service = TestService()
        registry.register(service)
        
        stats = registry.get_stats()
        assert stats["total_services"] == 1
        assert stats["enabled"] == 1


@pytest.mark.asyncio
async def test_initialize_all_services():
    """Test initializing all services."""
    registry = ServiceRegistry()
    service = TestService()
    registry.register(service)
    
    await registry.initialize_all()
    
    assert service.initialized


@pytest.mark.asyncio
async def test_shutdown_all_services():
    """Test shutting down all services."""
    registry = ServiceRegistry()
    service = TestService()
    registry.register(service)
    
    await registry.shutdown_all()
    
    assert service.shutdown_flag


@pytest.mark.asyncio
async def test_health_check_all():
    """Test health check for all services."""
    registry = ServiceRegistry()
    service = TestService()
    registry.register(service)
    
    results = await registry.health_check_all()
    
    assert "test_service" in results
    assert results["test_service"]["status"] == "healthy"
