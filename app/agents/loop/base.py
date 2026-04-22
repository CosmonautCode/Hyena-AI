"""Base AgenticLoop class and core functionality."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import time

from .gather import GatherMixin
from .plan import PlanMixin
from .execute import ExecuteMixin
from .verify import VerifyMixin
from .history import HistoryMixin


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class AgenticLoop(GatherMixin, PlanMixin, ExecuteMixin, VerifyMixin, HistoryMixin):
    """Implements Gather → Plan → Act → Verify loop for AI operations."""
    
    def __init__(self, llm, workspace_manager, permission_system, tui=None):
        """Initialize the agentic loop."""
        self.llm = llm
        self.workspace_manager = workspace_manager
        self.permission_system = permission_system
        self.tui = tui  # TUI for displaying tool calls (Phase 3)
        self.current_context = []
        self.tool_registry = {}
        self.execution_history = []
        self.active = False
        self.current_plan = None
    
    def activate(self):
        """Activate the agentic loop."""
        self.active = True
        return True
    
    def deactivate(self):
        """Deactivate the agentic loop."""
        self.active = False
        return True
    
    def register_tool(self, name: str, func: callable, description: str, parameters: Dict[str, str]):
        """Register a tool with the agentic loop."""
        self.tool_registry[name] = {
            "func": func,
            "description": description,
            "parameters": parameters
        }
    
    def process_request(self, user_input: str, conversation_history: List) -> Dict[str, Any]:
        """Process a user request through the agentic loop."""
        if not self.active:
            return {"success": False, "error": "Agentic loop not active"}
        
        try:
            # Step 1: Gather - Analyze the request and context
            context = self._gather_context(user_input, conversation_history)
            
            # Step 2: Plan - Create an execution plan
            plan = self._create_plan(context)
            self.current_plan = plan
            
            # Step 3: Act - Execute the plan
            results = self._execute_plan(plan)
            
            # Step 4: Verify - Validate results
            verification = self._verify_results(results, context)
            
            return {
                "success": True,
                "plan": plan,
                "results": results,
                "verification": verification,
                "context": context
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
