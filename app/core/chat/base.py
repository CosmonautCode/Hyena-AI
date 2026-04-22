"""Base ChatSystem class and initialization."""

import asyncio
from pathlib import Path
from typing import Optional
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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

from .agent_mgmt import AgentManagementMixin
from .conversation import ConversationMixin
from .session_mgmt import SessionManagementMixin
from .workspace_ops import WorkspaceOperationsMixin


class ChatSystem(AgentManagementMixin, ConversationMixin, SessionManagementMixin, WorkspaceOperationsMixin):
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
        
        agents_file = Path(__file__).parent.parent.parent / 'data' / 'agents.json'
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
