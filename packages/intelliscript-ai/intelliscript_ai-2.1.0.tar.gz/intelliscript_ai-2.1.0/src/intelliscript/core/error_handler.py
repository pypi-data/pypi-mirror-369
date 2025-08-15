"""
Error Handler - Simplified for PyPI Build
"""

import sys
from typing import Optional, Dict, Any

class ErrorHandler:
    """
    Error handler for IntelliScript
    Simplified version for package testing
    """
    
    def __init__(self):
        """Initialize error handler"""
        self.error_count = 0
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle and format error messages
        """
        self.error_count += 1
        
        error_msg = str(error)
        if context:
            error_msg += f" (Context: {context})"
        
        return f"IntelliScript Error: {error_msg}"
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"ERROR: {message}", file=sys.stderr)
