#!/usr/bin/env python3
"""
Swiss AI CLI - Professional AI Command Line Interface
A powerful, extensible CLI for AI-powered development workflows
"""

__version__ = "2.1.3"
__author__ = "Swiss AI CLI Team"
__email__ = "contact@swiss-ai.dev"
__description__ = "Professional AI Command Line Interface with intelligent routing and MCP integration"

from .config.manager import ConfigManager
from .models.selector import ModelSelector
from .mcp.manager import MCPManager
from .routing.router import IntelligentRouter
from .cli import SwissAICLI

# Public API
__all__ = [
    "ConfigManager",
    "ModelSelector", 
    "MCPManager",
    "IntelligentRouter",
    "SwissAICLI",
    "__version__"
]

# Package-level configuration
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, log_dir=None):
    """Setup logging for Swiss AI CLI"""
    if log_dir is None:
        log_dir = Path.home() / ".swiss-ai" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "swiss-ai.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Initialize default logging
setup_logging()