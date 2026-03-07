"""Planning methods for AgenticLoop."""

from typing import Dict, List, Any


class PlanMixin:
    """Mixin for planning functionality."""
    
    def _create_plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an execution plan."""
        user_input = context["user_input"]
        
        # Simple planning logic - can be enhanced with AI
        plan = []
        
        # Check if file operations are needed
        if any(keyword in user_input.lower() for keyword in ["read", "write", "file", "save", "load"]):
            plan.append({
                "tool": "file_operations",
                "action": "analyze_file_request",
                "description": "Analyze file operation request"
            })
        
        # Check if shell commands are needed
        if any(keyword in user_input.lower() for keyword in ["run", "execute", "command", "shell"]):
            plan.append({
                "tool": "shell_operations",
                "action": "analyze_shell_request",
                "description": "Analyze shell command request"
            })
        
        # Default action if no specific patterns found
        if not plan:
            plan.append({
                "tool": "general_analysis",
                "action": "analyze_request",
                "description": "General request analysis"
            })
        
        return plan
