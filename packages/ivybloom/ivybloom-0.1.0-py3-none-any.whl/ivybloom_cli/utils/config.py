"""
Configuration management for IvyBloom CLI
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import appdirs

class Config:
    """Configuration manager for IvyBloom CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.app_name = "ivybloom"
        self.app_author = "IvyBiosciences"
        
        # Determine config file location
        if config_file:
            self.config_path = Path(config_file)
        else:
            config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"
        
        # Default configuration
        self.defaults = {
            "api_url": "https://catharsis-jpg--ivyai-orchestrator-fastapi-app.modal.run/api/v1",
            "timeout": 30,
            "output_format": "json",
            "theme": "light",
            "show_welcome": True,
            "debug": False
        }
        
        # Load existing config
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                merged = self.defaults.copy()
                merged.update(config)
                return merged
            except (json.JSONDecodeError, IOError):
                pass
        
        return self.defaults.copy()
    
    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        self.save()
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.save()
    
    def show_config(self) -> Dict[str, Any]:
        """Return current configuration"""
        return self.config.copy()
    
    def get_auth_token_path(self) -> Path:
        """Get path for storing authentication token"""
        config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
        return config_dir / "auth_token"
    
    def get_api_key_path(self) -> Path:
        """Get path for storing API key"""
        config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
        return config_dir / "api_key"