"""Tool registry and management system."""

from typing import Dict, List, Optional
from app.tools.base import BaseTool


class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        name = tool.metadata.name
        category = tool.metadata.category
        
        self._tools[name] = tool
        
        # Track by category
        if category not in self._categories:
            self._categories[category] = []
        
        if name not in self._categories[category]:
            self._categories[category].append(name)
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get tool by name."""
        return self._tools.get(name)
    
    def list_all(self) -> List[BaseTool]:
        """List all tools."""
        return list(self._tools.values())
    
    def get_by_category(self, category: str) -> List[BaseTool]:
        """Get tools by category."""
        if category not in self._categories:
            return []
        
        return [
            self._tools[name] 
            for name in self._categories[category]
            if name in self._tools
        ]
    
    def search(self, query: str) -> List[BaseTool]:
        """Search tools by name or description."""
        query = query.lower()
        results = []
        
        for tool in self._tools.values():
            if (query in tool.metadata.name or
                query in tool.metadata.description.lower()):
                results.append(tool)
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        return {
            "total_tools": len(self._tools),
            "categories": len(self._categories),
            "enabled": sum(1 for t in self._tools.values() if t.metadata.enabled),
        }


# Global registry instance
_global_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create the global tool registry."""
    global _global_tool_registry
    if _global_tool_registry is None:
        _global_tool_registry = ToolRegistry()
        # Register built-in tools
        from app.tools.base import EchoTool
        _global_tool_registry.register(EchoTool())
    return _global_tool_registry


def register_tool(tool: BaseTool) -> None:
    """Register a tool with the global registry."""
    get_tool_registry().register(tool)
