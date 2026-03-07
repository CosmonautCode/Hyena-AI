"""Agent management methods for ChatSystem."""

from pathlib import Path
from app.llm.engine import load_instances
from app.memory.orchestrator import AutoMemoryOrchestrator
from app.agents.loop import AgenticLoop


class AgentManagementMixin:
    """Mixin for agent management functionality."""
    
    def load_agents(self):
        """Load the AI agents and initialize systems."""
        # Load the LLM
        try:
            instances = load_instances(num_instances=1)
            if instances:
                self.llm = instances[0]
        except Exception as e:
            self.tui.show_error(f"Failed to load LLM: {e}")
            return
        
        # Initialize auto-memory system now that LLM is available
        if self.llm:
            self.auto_memory = AutoMemoryOrchestrator(self.llm, self)
        
        # Initialize agentic loop now that LLM is available (with TUI for tool panels)
        if self.llm:
            self.agentic_loop = AgenticLoop(self.llm, self.workspace_manager, self.permission_system, self.tui)
        
        # Register tools with agentic loop
        if self.tool_manager and self.agentic_loop:
            tools = self.tool_manager.get_all_tools()
            for tool_name, tool_info in tools.items():
                self.agentic_loop.register_tool(
                    tool_name,
                    tool_info["func"],
                    tool_info["description"],
                    tool_info["parameters"]
                )
        
        # Load project memory
        self.project_memory.load_project_memory()
    
    def choose_agent(self, index=None):
        """Choose an agent by index."""
        if index is not None:
            if 0 <= index < len(self.agent_config):
                self.current_agent_index = index
            else:
                return False
        
        # Use the single LLM instance with different system prompts
        self.system_prompt = self.agent_config[self.current_agent_index]["system_prompt"]
        return True
