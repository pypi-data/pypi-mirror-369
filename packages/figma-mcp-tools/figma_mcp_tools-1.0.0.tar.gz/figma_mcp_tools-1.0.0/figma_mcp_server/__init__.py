"""
Figma MCP Server Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import FigmaMCPServer
from .cli import main

__all__ = ["FigmaMCPServer", "main"]
