"""Configuration management system for Hyena-AI."""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HyenaConfig:
    """Main configuration for Hyena-AI system."""
    
    # LLM Settings
    model_temperature: float = 0.7
    model_max_tokens: int = 1000
    model_context_size: int = 8192
    
    # Memory Settings
    memory_extraction_interval: int = 5
    memory_max_results: int = 5
    memory_compact_at_size: int = 10000
    
    # Tool Settings
    max_file_size: int = 2 * 1024 * 1024  # 2MB
    max_command_timeout: int = 30
    command_output_limit: int = 10000
    
    # Permission Settings
    permission_mode: str = "ask"
    auto_approve_safe_operations: bool = True
    
    # Workspace Settings
    default_workspace: Optional[str] = None
    
    # Logging Settings
    log_level: str = "INFO"
    log_dir: Optional[str] = None
    
    # Feature Flags
    enable_streaming: bool = True
    enable_memory_extraction: bool = True
    enable_tool_execution: bool = True
    enable_context_injection: bool = True
    
    # Performance Settings
    debug_mode: bool = False
    performance_tracking: bool = True
    
    @staticmethod
    def get_config_path() -> Path:
        """Get the configuration file path.
        
        Returns:
            Path: Path to config.json
        """
        return Path.home() / ".hyena" / "config.json"
    
    @staticmethod
    def load() -> 'HyenaConfig':
        """Load configuration from file.
        
        Returns:
            HyenaConfig: Loaded configuration or default if file doesn't exist
        """
        config_path = HyenaConfig.get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                
                # Filter to only known fields
                known_fields = {f.name for f in HyenaConfig.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in known_fields}
                
                config = HyenaConfig(**filtered_data)
                logger.info(f"Configuration loaded from {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                return HyenaConfig()
        
        logger.info("No config file found. Using default configuration.")
        return HyenaConfig()
    
    def save(self) -> bool:
        """Save configuration to file.
        
        Returns:
            bool: True if save successful
        """
        config_path = HyenaConfig.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
            logger.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.
        
        Returns:
            Dict: Configuration as dictionary
        """
        return asdict(self)
    
    @staticmethod
    def create_default_config_file() -> bool:
        """Create a default configuration file with documentation.
        
        Returns:
            bool: True if successful
        """
        config_path = HyenaConfig.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = HyenaConfig()
        return config.save()


# Global configuration instance
_config_instance: Optional[HyenaConfig] = None


def get_config() -> HyenaConfig:
    """Get the global configuration instance.
    
    Returns:
        HyenaConfig: Global configuration
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = HyenaConfig.load()
    return _config_instance


def reload_config() -> HyenaConfig:
    """Reload configuration from file.
    
    Returns:
        HyenaConfig: Reloaded configuration
    """
    global _config_instance
    _config_instance = HyenaConfig.load()
    return _config_instance


def update_config(**kwargs) -> bool:
    """Update configuration with given values.
    
    Args:
        **kwargs: Configuration fields to update
        
    Returns:
        bool: True if update successful
    """
    config = get_config()
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
            logger.info(f"Updated config: {key} = {value}")
        else:
            logger.warning(f"Unknown config field: {key}")
    
    return config.save()
