"""
Serena CLI

A powerful CLI tool for quickly enabling and configuring Serena coding agent tools in specified projects.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .mcp_server import SerenaCLIMCPServer
from .serena_manager import SerenaManager
from .project_detector import ProjectDetector
from .config_manager import ConfigManager

__all__ = [
    "SerenaCLIMCPServer",
    "SerenaManager",
    "ProjectDetector",
    "ConfigManager",
]
