"""Unit tests for tool registry system."""

import pytest
from app.tools.base import BaseTool, ToolMetadata
from app.tools.registry import ToolRegistry


class TestTool(BaseTool):
    """Test tool for unit tests."""
    
    def __init__(self, name="test_tool", category="test"):
        self.metadata = ToolMetadata(
            name=name,
            version="1.0.0",
            category=category,
            description="Test tool"
        )
    
    async def execute(self, **kwargs):
        return {"result": "success"}
    
    def validate(self, **kwargs):
        return True


class TestToolRegistry:
    """Tests for ToolRegistry."""
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = TestTool("test_tool")
        registry.register(tool)
        
        assert registry.get("test_tool") == tool
    
    def test_list_all_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()
        tool1 = TestTool("test_tool1")
        tool2 = TestTool("test_tool2")
        
        registry.register(tool1)
        registry.register(tool2)
        
        all_tools = registry.list_all()
        assert len(all_tools) == 2
    
    def test_get_by_category(self):
        """Test getting tools by category."""
        registry = ToolRegistry()
        tool = TestTool("test_tool", "test_cat")
        registry.register(tool)
        
        tools = registry.get_by_category("test_cat")
        assert len(tools) == 1
        assert tools[0].metadata.name == "test_tool"
    
    def test_search_tools(self):
        """Test searching tools."""
        registry = ToolRegistry()
        tool = TestTool("test_tool")
        registry.register(tool)
        
        results = registry.search("test")
        assert len(results) >= 1
        assert any(t.metadata.name == "test_tool" for t in results)
    
    def test_get_nonexistent_tool(self):
        """Test getting nonexistent tool."""
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None
    
    def test_tool_format_schema(self):
        """Test tool schema formatting."""
        tool = TestTool("my_tool")
        schema = tool.format_schema()
        
        assert schema["name"] == "my_tool"
        assert schema["category"] == "test"
        assert schema["version"] == "1.0.0"
    
    def test_registry_stats(self):
        """Test registry statistics."""
        registry = ToolRegistry()
        tool = TestTool("test_tool")
        registry.register(tool)
        
        stats = registry.get_stats()
        assert stats["total_tools"] == 1
        assert stats["enabled"] == 1


@pytest.mark.asyncio
async def test_execute_tool():
    """Test executing a tool."""
    tool = TestTool("test_tool")
    result = await tool.execute(test=True)
    
    assert result["result"] == "success"
