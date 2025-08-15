"""
Configuration Manager - Simplified for PyPI Build
"""

import os
from typing import Optional, Dict, Any

class ConfigManager:
    """
    Configuration manager for IntelliScript
    Simplified version for package testing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path
        self.config = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration"""
        self.config = {
            'default_provider': 'openai',
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-3.5-turbo'
            },
            'history': {
                'max_entries': 10
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
