"""Unit tests for configuration system."""

import pytest
import json
import tempfile
from pathlib import Path
from app.config import HyenaConfig, get_config, update_config, reload_config


class TestHyenaConfig:
    """Test HyenaConfig dataclass."""
    
    def test_default_config_creation(self):
        """Test creating config with default values."""
        config = HyenaConfig()
        
        assert config.model_temperature == 0.7
        assert config.model_max_tokens == 1000
        assert config.memory_extraction_interval == 5
        assert config.permission_mode == "ask"
        assert config.enable_streaming is True
    
    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = HyenaConfig(
            model_temperature=0.5,
            memory_extraction_interval=10,
            permission_mode="auto"
        )
        
        assert config.model_temperature == 0.5
        assert config.memory_extraction_interval == 10
        assert config.permission_mode == "auto"
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = HyenaConfig(model_temperature=0.8)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["model_temperature"] == 0.8
        assert "enable_streaming" in config_dict
    
    def test_config_load_default_when_file_missing(self):
        """Test load returns default config when file doesn't exist."""
        config = HyenaConfig.load()
        
        assert config is not None
        assert config.model_temperature == 0.7
    
    def test_config_save_and_load(self, tmp_path):
        """Test saving and loading config file."""
        # Create config with custom values
        config = HyenaConfig(
            model_temperature=0.5,
            memory_extraction_interval=10
        )
        
        # Save to temp file
        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config.to_dict(), f)
        
        # Load from file
        with open(config_file, 'r') as f:
            data = json.load(f)
            loaded_config = HyenaConfig(**data)
        
        assert loaded_config.model_temperature == 0.5
        assert loaded_config.memory_extraction_interval == 10
    
    def test_config_get_path(self):
        """Test getting configuration file path."""
        path = HyenaConfig.get_config_path()
        assert isinstance(path, Path)
        assert ".hyena" in str(path)
    
    def test_config_fields_validation(self):
        """Test config field validation."""
        config = HyenaConfig(
            model_temperature=0.9,
            max_file_size=5 * 1024 * 1024
        )
        
        assert config.model_temperature == 0.9
        assert config.max_file_size == 5 * 1024 * 1024
        # Default values should still be present
        assert config.enable_memory_extraction is True
    
    def test_permission_mode_values(self):
        """Test valid permission modes."""
        config1 = HyenaConfig(permission_mode="ask")
        config2 = HyenaConfig(permission_mode="auto")
        
        assert config1.permission_mode == "ask"
        assert config2.permission_mode == "auto"
    
    def test_log_level_values(self):
        """Test valid log level values."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = HyenaConfig(log_level=level)
            assert config.log_level == level
    
    def test_feature_flags(self):
        """Test feature flags can be individually toggled."""
        config = HyenaConfig()
        
        assert config.enable_streaming is True
        assert config.enable_memory_extraction is True
        assert config.enable_tool_execution is True
        
        # Can disable features
        config.enable_memory_extraction = False
        assert config.enable_memory_extraction is False


class TestConfigGlobals:
    """Test global config functions."""
    
    def test_get_config_returns_instance(self):
        """Test get_config returns HyenaConfig instance."""
        config = get_config()
        assert isinstance(config, HyenaConfig)
    
    def test_get_config_caches_instance(self):
        """Test get_config caches the instance."""
        config1 = get_config()
        config2 = get_config()
        # Both should refer to same instance (memory address same)
        assert config1 is config2
    
    def test_config_attributes_accessible(self):
        """Test all config attributes are accessible."""
        config = get_config()
        
        # Should not raise AttributeError
        _ = config.model_temperature
        _ = config.memory_extraction_interval
        _ = config.permission_mode
        _ = config.log_level
        _ = config.enable_streaming
