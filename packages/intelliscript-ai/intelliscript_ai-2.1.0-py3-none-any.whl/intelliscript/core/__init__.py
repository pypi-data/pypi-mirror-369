"""
IntelliScript Core Module
========================

Core functionality for IntelliScript including:
- Main application class
- Configuration management  
- Provider abstractions
- Error handling
"""

from .intelliscript_main import IntelliScript
from .config_manager import ConfigManager
from .error_handler import ErrorHandler

__all__ = [
    'IntelliScript',
    'ConfigManager', 
    'ErrorHandler'
]
