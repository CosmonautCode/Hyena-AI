"""Configuration module for Hyena-AI - Phase 0 compatible."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import json


@dataclass
class HyenaConfig:
    """Hyena-AI configuration dataclass."""
    
    # Model settings
    model_temperature: float = 0.7
    model_max_tokens: int = 1000
    model_name: str = "claude-3-5-sonnet-20241022"
    
    # Memory settings
    memory_extraction_interval: int = 5
    memory_compaction_threshold: int = 10000
    
    # Permission settings
    permission_mode: str = "ask"  # "auto", "ask", "manual"
    
    # Logging settings
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    
    # Feature flags
    enable_streaming: bool = True
    enable_memory_extraction: bool = True
    enable_tool_execution: bool = True
    
    # File settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB default
    
    # Additional settings
    workspace_path: Optional[str] = None
    debug_mode: bool = False
    config_path: Optional[str] = None
    
    @classmethod
    def get_config_path(cls) -> Path:
        """Get the configuration file path."""
        home = Path.home()
        hyena_dir = home / ".hyena"
        hyena_dir.mkdir(exist_ok=True)
        return hyena_dir / "config.json"
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> "HyenaConfig":
        """Load configuration from file."""
        if path is None:
            path = str(cls.get_config_path())
        
        config_file = Path(path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return cls.from_dict(data)
            except Exception:
                return cls()
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "model_temperature": self.model_temperature,
            "model_max_tokens": self.model_max_tokens,
            "model_name": self.model_name,
            "memory_extraction_interval": self.memory_extraction_interval,
            "memory_compaction_threshold": self.memory_compaction_threshold,
            "permission_mode": self.permission_mode,
            "log_level": self.log_level,
            "enable_streaming": self.enable_streaming,
            "enable_memory_extraction": self.enable_memory_extraction,
            "enable_tool_execution": self.enable_tool_execution,
            "max_file_size": self.max_file_size,
            "workspace_path": self.workspace_path,
            "debug_mode": self.debug_mode,
            "config_path": self.config_path,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HyenaConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Global config instance
_global_config: Optional[HyenaConfig] = None


def get_config() -> HyenaConfig:
    """Get the global configuration."""
    global _global_config
    if _global_config is None:
        _global_config = HyenaConfig()
    return _global_config


def update_config(**kwargs: Any) -> None:
    """Update the global configuration."""
    global _global_config
    if _global_config is None:
        _global_config = HyenaConfig()
    
    for key, value in kwargs.items():
        if hasattr(_global_config, key):
            setattr(_global_config, key, value)


def reload_config(path: Optional[str] = None) -> HyenaConfig:
    """Reload configuration from file."""
    global _global_config
    
    if path:
        config_path = Path(path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                _global_config = HyenaConfig.from_dict(data)
                return _global_config
    
    _global_config = HyenaConfig()
    return _global_config


# Preserve compatibility with app.config module
__all__ = ["HyenaConfig", "get_config", "update_config", "reload_config"]
