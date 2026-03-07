"""Main chat system with modern terminal TUI."""

import asyncio
from pathlib import Path
from typing import Optional

from app.ui.tui import TUI
from app.core.commands import CommandManager
from app.workspace.tools import AITools
from app.workspace.manager import WorkspaceManager
from app.llm.engine import load_instances
from app.agents.permission_system import PermissionSystem
from app.agents.loop import AgenticLoop
from app.agents.tools import ToolManager
from app.memory.session import UnifiedSessionManager
from app.memory.compactor import ContextCompactor
from app.memory.project import ProjectMemory
from app.memory.orchestrator import AutoMemoryOrchestrator
from .chat_loop import ChatLoopMixin


class ChatSystem(ChatLoopMixin):
    """Main chat system with modern terminal interface."""
    
    def __init__(self):
        """Initialize the chat system."""
        self.history = []
        self.llm = None
        self.system_prompt = None
        self.current_agent_index = 0
        self.running = True
        
        # Load agent configurations
        self.agent_config = self._load_agent_config()
        
        # Initialize new TUI
        history_file = Path.home() / '.hyena' / 'history.txt'
        self.tui = TUI(history_file=history_file)
        
        # Initialize managers (kept for backend functionality)
        self.command_manager = CommandManager(self)
        self.workspace_manager = WorkspaceManager(self)
        self.ai_tools = AITools(self.workspace_manager)
        
        # Initialize advanced backend systems
        self.permission_system = PermissionSystem()
        self.agentic_loop = None
        self.tool_manager = ToolManager(self.workspace_manager, self.permission_system)
        self.session_manager = UnifiedSessionManager()
        self.context_compactor = ContextCompactor()
        self.project_memory = ProjectMemory(self.workspace_manager)
        
        # Initialize processing lock for rapid input protection (Phase 3)
        self._processing_lock = asyncio.Lock()
        # Note: llm will be set after load_agents(), so we init auto_memory there too
        self.auto_memory = None
        
        # Load workspace config
        self.workspace_manager._load_workspace_config()
        
        # Commands list for reference
        self.commands = [
            '/help', '/?', '/agents', '/switch', '/clear', '/save', '/load', '/export',
            '/stats', '/reset', '/exit', '/quit', '/workspace', '/permissions', '/status',
            '/tools', '/session', '/compact', '/memory', '/agentic'
        ]

    def _load_agent_config(self):
        """Load agent configuration from JSON file."""
        import json
        agents_file = Path(__file__).parent.parent / 'data' / 'agents.json'
        try:
            with open(agents_file, 'r') as f:
                data = json.load(f)
                return data.get('agents', [])
        except Exception:
            # Fallback to default agent if file not found
            return [{
                'name': 'Default Agent',
                'specialty': 'General purpose AI assistant',
                'system_prompt': 'You are a helpful AI assistant.'
            }]

    def process_command(self, user_input: str) -> bool:
        """Process a command and return whether to continue."""
        result = self.command_manager.process_command(user_input)
        # Commands display their own output, no need for success feedback
        return result

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

    def save_conversation(self, filename):
        """Save conversation to file."""
        return self.session_manager.save_conversation(filename, self)

    def load_conversation(self, filename):
        """Load conversation from file."""
        return self.session_manager.load_conversation(filename, self)

    def export_conversation(self, filename):
        """Export conversation to text file."""
        return self.session_manager.export_conversation(filename, self)

    def get_session_stats(self):
        """Get session statistics."""
        user_messages = len([h for h in self.history if h[0] == "user"])
        assistant_messages = len([h for h in self.history if h[0] == "assistant"])
        return {
            'total_messages': len(self.history),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'current_agent': self.agent_config[self.current_agent_index]['name'] if self.agent_config else 'None',
            'session_time': 'Active'
        }

    def get_workspace(self):
        """Get current workspace directory."""
        return self.workspace_manager.get_workspace()
    
    def set_workspace(self, workspace_dir):
        """Set workspace directory."""
        return self.workspace_manager.set_workspace(workspace_dir)
