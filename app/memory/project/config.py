"""Configuration loading methods for ProjectMemory."""

from typing import Dict, Optional, Any
from pathlib import Path
import json


class ConfigMixin:
    """Mixin for configuration loading functionality."""
    
    def load_project_memory(self) -> Dict[str, Any]:
        """Load project memory from configuration files."""
        self.project_config = self._load_config_file('memories')
        self.skills_config = self._load_config_file('skills')
        self.agents_config = self._load_config_file('agents')
        
        return {
            'memories': self.project_config,
            'skills': self.skills_config,
            'agents': self.agents_config
        }
    
    def reload_configs(self) -> Dict[str, Any]:
        """Reload all project configurations from disk."""
        return self.load_project_memory()
    
    def clear_memory(self) -> bool:
        """Clear project memory configuration."""
        try:
            self.project_config = None
            self.skills_config = None
            self.agents_config = None
            return True
        except Exception:
            return False
    
    def _load_config_file(self, config_type: str) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        config_path = self._get_config_path(config_type)
        if not config_path:
            return None
        
        if config_path.suffix == '.md':
            return self._parse_markdown_config(config_path)
        elif config_path.suffix == '.json':
            return self._parse_json_config(config_path)
        
        return None
    
    def _parse_markdown_config(self, config_path: Path) -> Dict[str, Any]:
        """Parse configuration from markdown file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {
            "coding_standards": [],
            "architecture_notes": "",
            "project_rules": [],
            "raw_content": content
        }
        
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.startswith('# '):
                if current_section and section_content:
                    config[current_section] = '\n'.join(section_content)
                current_section = line[2:].lower().replace(' ', '_')
                section_content = []
            elif line.startswith('## '):
                if current_section and section_content:
                    config[current_section] = '\n'.join(section_content)
                current_section = line[3:].lower().replace(' ', '_')
                section_content = []
            elif line.startswith('- '):
                # List items
                item = line[2:].strip()
                if current_section == 'coding_standards':
                    config['coding_standards'].append(item)
                elif current_section == 'project_rules':
                    config['project_rules'].append(item)
            elif line and current_section:
                # Regular content
                section_content.append(line)
        
        # Add final section
        if current_section and section_content:
            config[current_section] = '\n'.join(section_content)
        
        return config
    
    def _parse_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Parse configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
