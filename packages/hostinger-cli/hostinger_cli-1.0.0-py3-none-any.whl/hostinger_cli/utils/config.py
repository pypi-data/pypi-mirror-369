"""
Configuration management for Hostinger CLI
"""

import json
import os
from pathlib import Path
from typing import Optional


class ConfigManager:
    """Manages configuration for the Hostinger CLI"""
    
    def __init__(self, config_file: str = "~/.hostinger-cli.json"):
        self.config_file = Path(config_file).expanduser()
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        # Create directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Set file permissions to be readable only by owner
        os.chmod(self.config_file, 0o600)
    
    def get_api_key(self) -> Optional[str]:
        """Get the stored API key"""
        return self.config.get('api_key')
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key"""
        self.config['api_key'] = api_key
        self._save_config()
    
    def remove_api_key(self) -> None:
        """Remove the stored API key"""
        if 'api_key' in self.config:
            del self.config['api_key']
            self._save_config()
    
    def get_setting(self, key: str, default=None):
        """Get a setting value"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value) -> None:
        """Set a setting value"""
        self.config[key] = value
        self._save_config()
