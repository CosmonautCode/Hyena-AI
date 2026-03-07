"""Skills management methods for ProjectMemory."""

from typing import Dict, Any, Optional
from pathlib import Path
import json


class SkillsMixin:
    """Mixin for skills management functionality."""
    
    def get_skills(self) -> Dict[str, Any]:
        """Get project skills configuration."""
        try:
            config = self._load_config_file('skills')
            return {
                "success": True,
                "skills": config or {}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_skill(self, skill_name: str, description: str, category: str = "general") -> Dict[str, Any]:
        """Add a skill to the project skills."""
        try:
            # Load current config
            current_config = self._load_config_file('skills') or {}
            
            # Add new skill
            if 'skills' not in current_config:
                current_config['skills'] = {}
            
            current_config['skills'][skill_name] = {
                "description": description,
                "category": category,
                "added_at": str(Path.cwd())
            }
            
            # Save updated config
            result = self._save_skills_config(current_config)
            
            return {
                "success": result["success"],
                "skill_name": skill_name,
                "description": description,
                "category": category,
                "path": result.get("path")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_skill(self, skill_name: str) -> Dict[str, Any]:
        """Remove a skill from the project skills."""
        try:
            # Load current config
            current_config = self._load_config_file('skills') or {}
            
            # Remove skill
            if 'skills' in current_config and skill_name in current_config['skills']:
                del current_config['skills'][skill_name]
                
                # Save updated config
                result = self._save_skills_config(current_config)
                
                return {
                    "success": result["success"],
                    "skill_name": skill_name,
                    "message": "Skill removed successfully"
                }
            else:
                return {"success": False, "error": f"Skill '{skill_name}' not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_skills_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Save skills configuration to file."""
        try:
            config_path = self._get_config_path('skills')
            if not config_path:
                # Create the file in .hyena directory
                self.hyena_dir.mkdir(exist_ok=True)
                config_path = self.hyena_dir / 'Skills.md'
            
            # Convert to markdown format
            content = self._format_skills_as_markdown(config)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"success": True, "path": str(config_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_skills_as_markdown(self, skills_config: Dict[str, Any]) -> str:
        """Format skills configuration as markdown."""
        content = []
        
        # Add title
        content.append("# Project Skills")
        content.append("")
        
        # Add skills section
        if 'skills' in skills_config and skills_config['skills']:
            content.append("## Available Skills")
            content.append("")
            
            for skill_name, skill_info in skills_config['skills'].items():
                content.append(f"### {skill_name}")
                content.append("")
                content.append(f"**Description:** {skill_info.get('description', 'No description')}")
                content.append(f"**Category:** {skill_info.get('category', 'general')}")
                if 'added_at' in skill_info:
                    content.append(f"**Added at:** {skill_info['added_at']}")
                content.append("")
        else:
            content.append("## Available Skills")
            content.append("")
            content.append("No skills defined yet.")
            content.append("")
        
        return '\n'.join(content)
