"""Memory operation methods for ProjectMemory."""

from typing import Dict, Any, Optional
from pathlib import Path
import json


class MemoryOpsMixin:
    """Mixin for memory operations functionality."""
    
    def save_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save memory data to file."""
        try:
            config_path = self._get_config_path('memories')
            if not config_path:
                # Create the file in .hyena directory
                self.hyena_dir.mkdir(exist_ok=True)
                config_path = self.hyena_dir / 'Memories.md'
            
            # Convert to markdown format
            content = self._format_memory_as_markdown(memory_data)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"success": True, "path": str(config_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_memory_entry(self, key: str, value: str, category: str = "general") -> Dict[str, Any]:
        """Add a memory entry."""
        try:
            # Load current config
            current_config = self._load_config_file('memories') or {}
            
            # Add new entry
            if category not in current_config:
                current_config[category] = []
            
            if isinstance(current_config[category], list):
                current_config[category].append(f"{key}: {value}")
            else:
                # Convert to list if it's a string
                current_config[category] = [str(current_config[category]), f"{key}: {value}"]
            
            # Save updated config
            result = self.save_memory(current_config)
            
            return {
                "success": result["success"],
                "key": key,
                "value": value,
                "category": category,
                "path": result.get("path")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_memory_entries(self, category: str = None) -> Dict[str, Any]:
        """Get memory entries by category."""
        try:
            config = self._load_config_file('memories') or {}
            
            if category:
                return {
                    "success": True,
                    "category": category,
                    "entries": config.get(category, [])
                }
            else:
                return {
                    "success": True,
                    "config": config
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_memory_as_markdown(self, memory_data: Dict[str, Any]) -> str:
        """Format memory data as markdown."""
        content = []
        
        # Add title
        content.append("# Project Memory")
        content.append("")
        
        # Add each section
        for key, value in memory_data.items():
            if isinstance(value, list):
                content.append(f"## {key.title()}")
                content.append("")
                for item in value:
                    content.append(f"- {item}")
                content.append("")
            elif isinstance(value, str):
                content.append(f"## {key.title()}")
                content.append("")
                content.append(value)
                content.append("")
            elif isinstance(value, dict):
                content.append(f"## {key.title()}")
                content.append("")
                for sub_key, sub_value in value.items():
                    content.append(f"**{sub_key.title()}:** {sub_value}")
                    content.append("")
                content.append("")
        
        return '\n'.join(content)
