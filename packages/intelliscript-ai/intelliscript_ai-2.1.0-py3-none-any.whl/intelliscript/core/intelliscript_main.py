"""
IntelliScript Main Application Class - Simplified for PyPI Build
"""

import os
import sys
from typing import Optional, Dict, Any

class IntelliScript:
    """
    Main IntelliScript application class
    Simplified version for PyPI package testing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize IntelliScript"""
        self.config_path = config_path
        self.providers = {}
        self.default_provider = "openai"
    
    def process_query(self, query: str, provider: Optional[str] = None) -> str:
        """
        Process a natural language query and return a command
        Simplified implementation for package testing
        """
        if not query:
            return "Error: Empty query provided"
        
        # Simplified response for testing
        return f"echo 'Processed query: {query}'"
    
    def get_version(self) -> str:
        """Get IntelliScript version"""
        return "2.1.0"
