"""Base ProjectMemory class and initialization."""

from typing import Dict, Optional, Any
from pathlib import Path
import json
import os

from .config import ConfigMixin
from .memory_ops import MemoryOpsMixin
from .skills import SkillsMixin


class ProjectMemory(ConfigMixin, MemoryOpsMixin, SkillsMixin):
    """Manages project-level memory and configuration for Hyena CLI."""
    
    def __init__(self, workspace_manager):
        """Initialize the project memory manager."""
        self.workspace_manager = workspace_manager
        self.config_files = {
            'memories': 'Memories.md',
            'skills': 'Skills.md',
            'agents': 'agents.md'
        }
        self.hyena_dir = Path('.hyena')
        self.project_config = None
        self.skills_config = None
        self.agents_config = None
    
    def _get_config_path(self, config_type: str) -> Optional[Path]:
        """Get the path to a configuration file."""
        if config_type not in self.config_files:
            return None
        
        config_file = self.config_files[config_type]
        
        # Check in .hyena directory first
        hyena_config = self.hyena_dir / config_file
        if hyena_config.exists():
            return hyena_config
        
        # Fallback to workspace root
        workspace = self.workspace_manager.get_workspace()
        if workspace:
            workspace_path = Path(workspace)
            fallback_config = workspace_path / config_file
            if fallback_config.exists():
                return fallback_config
        
        return None
