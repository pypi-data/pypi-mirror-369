"""
IntelliScript - World's First AI CLI Tool with LangExtract Integration
====================================================================

Transform natural language into executable commands with advanced data extraction,
analysis, and visualization capabilities.

Features:
- Command generation with multiple AI providers
- Structured data extraction using Google LangExtract
- Interactive visualizations and reporting
- Multi-step automated workflows
- Privacy-first local AI model support

Usage:
    from intelliscript import IntelliScript
    
    app = IntelliScript()
    result = app.process_query("find large files", provider="ollama")
    print(result)

Command Line:
    intelliscript "find large files"
    intelliscript extract "analyze logs" --visualize
    intelliscript report "system health" --format html

Author: IntelliScript Team
License: MIT
Version: 2.1.0
"""

__version__ = "2.1.0"
__author__ = "IntelliScript Team"
__email__ = "team@intelliscript.dev"
__license__ = "MIT"
__description__ = "World's first AI CLI tool with Google LangExtract integration"

# Main exports
from .core.intelliscript_main import IntelliScript

# Configuration exports  
from .core.config_manager import ConfigManager
from .core.error_handler import ErrorHandler

# CLI exports
from .cli.commands.extract_commands import ExtractCommands

__all__ = [
    # Core classes
    "IntelliScript",
    
    # Utility classes
    "ConfigManager",
    "ErrorHandler",
    
    # CLI classes
    "ExtractCommands",
    
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]

# Package-level configuration
import logging

# Set up package logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Version check warning
import sys
if sys.version_info < (3, 8):
    import warnings
    warnings.warn(
        "IntelliScript requires Python 3.8 or higher. "
        f"You are using Python {sys.version}",
        UserWarning,
        stacklevel=2
    )
