#!/usr/bin/env python3
"""
Helper utilities for Swiss AI CLI
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import requests

def setup_logging(level: str = "INFO", log_dir: Optional[Path] = None) -> None:
    """Setup logging configuration"""
    if log_dir is None:
        log_dir = Path.home() / ".swiss-ai" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "swiss-ai.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def validate_api_key(api_key: str) -> bool:
    """Validate OpenRouter API key format"""
    if not api_key:
        return False
    
    # OpenRouter API keys typically start with 'sk-or-' 
    if api_key.startswith('sk-or-') and len(api_key) > 20:
        return True
    
    # Also accept generic OpenAI-style keys for compatibility
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    
    return False

def sanitize_input(user_input: str, max_length: int = 10000) -> str:
    """Sanitize user input for safety"""
    if not user_input:
        return ""
    
    # Truncate if too long
    if len(user_input) > max_length:
        user_input = user_input[:max_length] + "..."
    
    # Remove potentially dangerous control characters
    user_input = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', user_input)
    
    # Normalize whitespace
    user_input = re.sub(r'\s+', ' ', user_input.strip())
    
    return user_input

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        'disk_free_gb': round(psutil.disk_usage('/').free / (1024**3), 2) if os.name != 'nt' else round(psutil.disk_usage('C:').free / (1024**3), 2)
    }

def check_internet_connection() -> bool:
    """Check if internet connection is available"""
    try:
        response = requests.get('https://api.openrouter.ai/api/v1/models', timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if necessary"""
    path.mkdir(parents=True, exist_ok=True)

def get_config_dir() -> Path:
    """Get the standard config directory"""
    return Path.home() / ".swiss-ai"

def get_cache_dir() -> Path:
    """Get the standard cache directory"""
    if os.name == 'nt':  # Windows
        cache_dir = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'swiss-ai' / 'cache'
    else:  # Unix-like
        cache_dir = Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache')) / 'swiss-ai'
    
    ensure_directory(cache_dir)
    return cache_dir

def get_data_dir() -> Path:
    """Get the standard data directory"""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'swiss-ai' / 'data'
    else:  # Unix-like
        data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'swiss-ai'
    
    ensure_directory(data_dir)
    return data_dir