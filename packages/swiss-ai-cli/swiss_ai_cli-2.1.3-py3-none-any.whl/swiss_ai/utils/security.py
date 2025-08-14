#!/usr/bin/env python3
"""
Security utilities for Swiss AI CLI
"""

import os
import re
import hashlib
import secrets
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation utilities"""
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",           # Dangerous file deletion
        r"sudo\s+",            # Privilege escalation
        r"su\s+",              # User switching
        r"chmod\s+777",        # Dangerous permissions
        r"wget\s+.*>\s*/",     # File overwrite via wget
        r"curl\s+.*>\s*/",     # File overwrite via curl
        r"\|\s*sh",            # Pipe to shell
        r"eval\s*\(",          # Code evaluation
        r"exec\s*\(",          # Code execution
        r"system\s*\(",        # System calls
        r"__import__",         # Dynamic imports
        r"getattr\s*\(",       # Dynamic attribute access
        r"setattr\s*\(",       # Dynamic attribute setting
        r"globals\s*\(",       # Global access
        r"locals\s*\(",        # Local scope access
        r"vars\s*\(",          # Variable access
        r"dir\s*\(",           # Directory listing of objects
    ]
    
    # Safe file extensions
    SAFE_EXTENSIONS = {
        '.txt', '.md', '.rst', '.json', '.yaml', '.yml', '.xml', '.csv',
        '.py', '.js', '.ts', '.html', '.css', '.scss', '.less',
        '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb',
        '.go', '.rs', '.kt', '.swift', '.dart', '.scala', '.clj',
        '.sql', '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore',
        '.log', '.cfg', '.conf', '.ini', '.toml', '.lock'
    }
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {
        '.exe', '.msi', '.scr', '.com', '.pif', '.bat', '.cmd',
        '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh', '.ps1',
        '.psm1', '.psd1', '.dll', '.so', '.dylib'
    }
    
    @classmethod
    def sanitize_file_path(cls, file_path: str) -> Optional[str]:
        """Sanitize and validate file path"""
        if not file_path:
            return None
        
        # Convert to Path object for safe handling
        try:
            path = Path(file_path).resolve()
        except (OSError, ValueError) as e:
            logger.warning(f"Invalid file path: {file_path} - {e}")
            return None
        
        # Check for directory traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            logger.warning(f"Potential directory traversal in path: {file_path}")
            return None
        
        # Check file extension
        if path.suffix.lower() in cls.DANGEROUS_EXTENSIONS:
            logger.warning(f"Dangerous file extension: {path.suffix}")
            return None
        
        # Ensure path is within reasonable bounds
        try:
            # Get absolute path to check if it's within allowed directories
            abs_path = path.absolute()
            
            # For now, allow paths under user home or current working directory
            home_dir = Path.home()
            cwd = Path.cwd()
            
            if not (str(abs_path).startswith(str(home_dir)) or 
                   str(abs_path).startswith(str(cwd))):
                logger.warning(f"Path outside allowed directories: {abs_path}")
                return None
            
        except Exception as e:
            logger.warning(f"Error validating path {file_path}: {e}")
            return None
        
        return str(path)
    
    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, str]:
        """Validate command for dangerous patterns"""
        if not command:
            return False, "Empty command"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check command length (prevent extremely long commands)
        if len(command) > 10000:
            return False, "Command too long"
        
        return True, "Command validated"
    
    @classmethod
    def sanitize_environment_variables(cls, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Sanitize environment variables"""
        sanitized = {}
        
        # Dangerous environment variables to filter
        dangerous_vars = {
            'LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES',
            'PYTHONPATH', 'PATH', 'SHELL', 'HOME', 'USER'
        }
        
        for key, value in env_vars.items():
            # Skip dangerous variables
            if key in dangerous_vars:
                logger.warning(f"Filtered dangerous environment variable: {key}")
                continue
            
            # Sanitize key and value
            if not isinstance(key, str) or not isinstance(value, str):
                continue
            
            # Remove dangerous characters
            key = re.sub(r'[;&|`$(){}[\]<>]', '', key)
            value = re.sub(r'[;&|`$(){}[\]<>]', '', value)
            
            if key and len(key) <= 100 and len(value) <= 1000:
                sanitized[key] = value
        
        return sanitized
    
    @classmethod
    def generate_session_token(cls) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def hash_sensitive_data(cls, data: str) -> str:
        """Hash sensitive data for logging/storage"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @classmethod
    def validate_input_size(cls, input_data: str, max_size: int = 100000) -> bool:
        """Validate input size to prevent DoS"""
        return len(input_data) <= max_size
    
    @classmethod
    def sanitize_user_input(cls, user_input: str) -> str:
        """Sanitize user input"""
        if not user_input:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', user_input)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized.strip())
        
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000] + "..."
        
        return sanitized
    
    @classmethod
    def validate_api_endpoint(cls, url: str) -> bool:
        """Validate API endpoint URL"""
        if not url:
            return False
        
        # Allow only HTTPS for API endpoints
        if not url.startswith('https://'):
            return False
        
        # Check for known safe domains
        safe_domains = [
            'api.openrouter.ai',
            'openrouter.ai',
            'api.openai.com',
            'openai.com'
        ]
        
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check if domain is in safe list or subdomain of safe domains
            for safe_domain in safe_domains:
                if domain == safe_domain or domain.endswith('.' + safe_domain):
                    return True
            
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return False
        
        return False
    
    @classmethod
    def create_secure_temp_file(cls, content: str, suffix: str = '.tmp') -> Optional[Path]:
        """Create a secure temporary file"""
        import tempfile
        
        try:
            # Ensure suffix is safe
            if suffix not in cls.SAFE_EXTENSIONS and suffix != '.tmp':
                suffix = '.tmp'
            
            # Create temporary file with restricted permissions
            fd, temp_path = tempfile.mkstemp(suffix=suffix, text=True)
            
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(content)
                
                # Set restrictive permissions (owner read/write only)
                os.chmod(temp_path, 0o600)
                
                return Path(temp_path)
                
            except Exception as e:
                # Clean up on error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise e
                
        except Exception as e:
            logger.error(f"Error creating secure temp file: {e}")
            return None