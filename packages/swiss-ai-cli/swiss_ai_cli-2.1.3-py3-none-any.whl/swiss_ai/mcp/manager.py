#!/usr/bin/env python3
"""
Secure MCP Server Management System for Swiss AI CLI
Handles lifecycle operations with security validation and health monitoring
"""

import os
import sys
import json
import time
import signal
import psutil
import shlex
import threading
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import re
import requests

# Rich for beautiful CLI output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
from rich import box
import sys

# Fix Windows console encoding issues
if sys.platform == "win32":
    console = Console(force_terminal=True, width=120)
else:
    console = Console()

logger = logging.getLogger(__name__)

class MCPServerStatus(Enum):
    """MCP Server status states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    auto_start: bool = False
    restart_on_failure: bool = True
    max_restarts: int = 3
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    startup_timeout: int = 30
    shutdown_timeout: int = 10
    security_level: str = "medium"  # low, medium, high
    allowed_capabilities: List[str] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class MCPServerInstance:
    """Runtime instance of an MCP server"""
    config: MCPServerConfig
    process: Optional[subprocess.Popen] = None
    status: MCPServerStatus = MCPServerStatus.STOPPED
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    health_status: str = "unknown"
    resource_usage: Dict[str, Any] = field(default_factory=dict)

class SecurityValidator:
    """Security validation for MCP server operations"""
    
    # Allowed commands (whitelist approach)
    ALLOWED_COMMANDS = {
        "python", "python3", "node", "npm", "npx", "docker", "java", "mvn",
        "cargo", "rustc", "go", "dotnet", "ruby", "php", "bash", "sh"
    }
    
    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf", r"sudo\s+", r"su\s+", r"chmod\s+777", 
        r"wget\s+", r"curl\s+.*>\s*/", r"\|\s*sh", r"eval\s*\(",
        r"exec\s*\(", r"system\s*\(", r"__import__"
    ]
    
    # Resource limits
    DEFAULT_LIMITS = {
        "max_memory_mb": 512,
        "max_cpu_percent": 50,
        "max_file_descriptors": 100,
        "max_processes": 5
    }
    
    @classmethod
    def validate_command(cls, command: str, args: List[str], security_level: str = "medium") -> Tuple[bool, str]:
        """Validate MCP server command for security"""
        
        # Extract base command
        base_cmd = os.path.basename(command)
        
        # Check if command is whitelisted
        if base_cmd not in cls.ALLOWED_COMMANDS:
            return False, f"Command '{base_cmd}' is not in the allowed list"
        
        # Check for dangerous patterns in command and args
        full_command = f"{command} {' '.join(args)}"
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, full_command, re.IGNORECASE):
                return False, f"Command contains dangerous pattern: {pattern}"
        
        # Security level specific checks
        if security_level == "high":
            # Additional strict checks for high security
            if any(arg.startswith("--") and "unsafe" in arg.lower() for arg in args):
                return False, "Unsafe flags detected in high security mode"
            
            # Check for network access (may be restricted)
            network_args = ["--network", "--port", "--bind", "--listen"]
            if any(any(net_arg in arg for net_arg in network_args) for arg in args):
                return False, "Network access restricted in high security mode"
        
        return True, "Command validated successfully"
    
    @classmethod
    def sanitize_environment(cls, env: Dict[str, str], security_level: str = "medium") -> Dict[str, str]:
        """Sanitize environment variables"""
        sanitized = {}
        
        # Dangerous environment variables to filter
        dangerous_vars = {
            "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
            "PYTHONPATH", "PATH"  # PATH needs careful handling
        }
        
        for key, value in env.items():
            if key in dangerous_vars and security_level in ["medium", "high"]:
                logger.warning(f"Filtered dangerous environment variable: {key}")
                continue
            
            # Sanitize values
            if not isinstance(value, str):
                value = str(value)
            
            # Remove potentially dangerous characters
            value = re.sub(r'[;&|`$(){}[\]<>]', '', value)
            
            sanitized[key] = value
        
        # Add safe defaults
        sanitized.setdefault("TERM", "xterm")
        sanitized.setdefault("HOME", str(Path.home()))
        
        return sanitized

class MCPManager:
    """Secure MCP server lifecycle management"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".swiss-ai"
        self.servers_dir = self.config_dir / "mcp_servers"
        self.logs_dir = self.config_dir / "logs"
        self.config_file = self.config_dir / "mcp_config.json"
        
        # Ensure directories exist
        self.servers_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Runtime state
        self.instances: Dict[str, MCPServerInstance] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        # Load configuration
        self.server_configs = self._load_server_configs()
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info(f"MCPManager initialized with {len(self.server_configs)} server configs")
    
    def _load_server_configs(self) -> Dict[str, MCPServerConfig]:
        """Load MCP server configurations"""
        configs = {}
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                for server_name, config_data in data.get('servers', {}).items():
                    configs[server_name] = MCPServerConfig.from_dict(config_data)
            else:
                # Do not auto-create defaults here; return empty configs (tests expect 0 initially)
                return {}
                
        except Exception as e:
            logger.error(f"Failed to load MCP server configs: {e}")
        
        return configs
    
    def _create_default_config(self):
        """Create default MCP server configuration"""
        default_config = {
            "version": "2.1.0",
            "servers": {
                "filesystem": {
                    "name": "filesystem",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.cwd())],
                    "auto_start": False,
                    "security_level": "medium",
                    "allowed_capabilities": ["read_files", "list_directory"],
                    "resource_limits": SecurityValidator.DEFAULT_LIMITS
                },
                "git": {
                    "name": "git", 
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-git", "--repository", str(Path.cwd())],
                    "auto_start": False,
                    "security_level": "medium",
                    "allowed_capabilities": ["read_repository", "get_status"],
                    "resource_limits": SecurityValidator.DEFAULT_LIMITS
                }
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            # Load into memory directly
            self.server_configs = {name: MCPServerConfig.from_dict(cfg) for name, cfg in default_config["servers"].items()}
            logger.info("Created default MCP server configuration")
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """Add a new MCP server configuration"""
        try:
            # Validate configuration
            is_valid, error_msg = SecurityValidator.validate_command(
                config.command, config.args, config.security_level
            )
            
            if not is_valid:
                logger.error(f"Security validation failed for {config.name}: {error_msg}")
                return False
            
            # Add to configs
            self.server_configs[config.name] = config
            
            # Save configuration
            self._save_server_configs()
            
            logger.info(f"Added MCP server configuration: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add server {config.name}: {e}")
            return False
    
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration"""
        try:
            # Stop server if running
            if server_name in self.instances:
                self.stop_server(server_name)
            
            # Remove from configs
            if server_name in self.server_configs:
                del self.server_configs[server_name]
                self._save_server_configs()
                
                logger.info(f"Removed MCP server configuration: {server_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove server {server_name}: {e}")
            return False
    
    def start_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        if server_name not in self.server_configs:
            logger.error(f"Server configuration not found: {server_name}")
            return False
        
        config = self.server_configs[server_name]
        
        # Check if already running
        if server_name in self.instances:
            instance = self.instances[server_name]
            if instance.status == MCPServerStatus.RUNNING:
                logger.warning(f"Server {server_name} is already running")
                return True
        
        try:
            # Security validation
            is_valid, error_msg = SecurityValidator.validate_command(
                config.command, config.args, config.security_level
            )
            
            if not is_valid:
                logger.error(f"Security validation failed: {error_msg}")
                return False
            
            # Prepare environment
            env = os.environ.copy()
            sanitized_env = SecurityValidator.sanitize_environment(
                config.env, config.security_level
            )
            env.update(sanitized_env)
            
            # Setup logging
            log_file = self.logs_dir / f"{server_name}.log"
            
            # Start process
            logger.info(f"Starting MCP server: {server_name}")
            
            with open(log_file, 'a') as log_f:
                process = subprocess.Popen(
                    [config.command] + config.args,
                    env=env,
                    cwd=config.working_dir,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
            
            # Create instance
            instance = MCPServerInstance(
                config=config,
                process=process,
                status=MCPServerStatus.STARTING,
                pid=process.pid,
                start_time=datetime.now()
            )
            
            self.instances[server_name] = instance
            
            # Wait for startup
            self._wait_for_startup(server_name)
            
            logger.info(f"MCP server {server_name} started with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            if server_name in self.instances:
                self.instances[server_name].status = MCPServerStatus.FAILED
                self.instances[server_name].last_error = str(e)
            return False
    
    def stop_server(self, server_name: str, force: bool = False) -> bool:
        """Stop an MCP server"""
        if server_name not in self.instances:
            logger.warning(f"Server {server_name} is not running")
            return True
        
        instance = self.instances[server_name]
        
        try:
            logger.info(f"Stopping MCP server: {server_name}")
            instance.status = MCPServerStatus.STOPPING
            
            if instance.process and instance.process.poll() is None:
                # Try graceful shutdown first
                if not force:
                    instance.process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        instance.process.wait(timeout=instance.config.shutdown_timeout)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Server {server_name} did not shutdown gracefully, forcing")
                        force = True
                
                # Force kill if necessary
                if force:
                    instance.process.kill()
                    instance.process.wait()
            
            instance.status = MCPServerStatus.STOPPED
            instance.process = None
            instance.pid = None
            
            logger.info(f"MCP server {server_name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop server {server_name}: {e}")
            instance.status = MCPServerStatus.FAILED
            instance.last_error = str(e)
            return False
    
    def restart_server(self, server_name: str) -> bool:
        """Restart an MCP server"""
        logger.info(f"Restarting MCP server: {server_name}")
        
        if server_name in self.instances:
            if not self.stop_server(server_name):
                return False
        
        return self.start_server(server_name)
    
    def get_server_status(self, server_name: str) -> MCPServerStatus:
        """Get the status of an MCP server"""
        if server_name not in self.instances:
            return MCPServerStatus.STOPPED
        
        return self.instances[server_name].status
    
    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all configured servers with their status"""
        servers = {}
        
        for server_name, config in self.server_configs.items():
            instance = self.instances.get(server_name)
            
            servers[server_name] = {
                "name": server_name,
                "status": instance.status.value if instance else "stopped",
                "pid": instance.pid if instance else None,
                "start_time": instance.start_time.isoformat() if instance and instance.start_time else None,
                "restart_count": instance.restart_count if instance else 0,
                "auto_start": config.auto_start,
                "health_status": instance.health_status if instance else "unknown",
                "last_error": instance.last_error if instance else None
            }
        
        return servers
    
    def start_all_auto_start_servers(self):
        """Start all servers marked for auto-start"""
        auto_start_servers = [
            name for name, config in self.server_configs.items() 
            if config.auto_start
        ]
        
        if not auto_start_servers:
            logger.info("No servers configured for auto-start")
            return
        
        logger.info(f"Starting auto-start servers: {', '.join(auto_start_servers)}")
        
        for server_name in auto_start_servers:
            self.start_server(server_name)
    
    def stop_all_servers(self):
        """Stop all running servers"""
        running_servers = [
            name for name, instance in self.instances.items()
            if instance.status == MCPServerStatus.RUNNING
        ]
        
        if not running_servers:
            logger.info("No servers currently running")
            return
        
        logger.info(f"Stopping all servers: {', '.join(running_servers)}")
        
        for server_name in running_servers:
            self.stop_server(server_name)
    
    def _wait_for_startup(self, server_name: str):
        """Wait for server to complete startup"""
        instance = self.instances[server_name]
        config = instance.config
        
        start_time = time.time()
        
        while time.time() - start_time < config.startup_timeout:
            if instance.process and instance.process.poll() is not None:
                # Process has terminated
                instance.status = MCPServerStatus.FAILED
                instance.last_error = f"Process terminated during startup (exit code: {instance.process.returncode})"
                return
            
            # Check health if URL is configured
            if config.health_check_url:
                try:
                    response = requests.get(config.health_check_url, timeout=5)
                    if response.status_code == 200:
                        instance.status = MCPServerStatus.RUNNING
                        instance.health_status = "healthy"
                        return
                except requests.RequestException:
                    pass  # Continue waiting
            else:
                # Simple process check
                time.sleep(1)
                if instance.process and instance.process.poll() is None:
                    # Process is still running, assume it's ready
                    instance.status = MCPServerStatus.RUNNING
                    return
        
        # Startup timeout
        instance.status = MCPServerStatus.FAILED
        instance.last_error = "Startup timeout exceeded"
    
    def _start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True,
            name="MCPMonitor"
        )
        self.monitoring_thread.start()
        logger.debug("MCP monitoring thread started")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.wait(10):  # Check every 10 seconds
            try:
                self._check_server_health()
                self._handle_failed_servers()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _check_server_health(self):
        """Check health of all running servers"""
        for server_name, instance in self.instances.items():
            if instance.status != MCPServerStatus.RUNNING:
                continue
            
            try:
                # Check if process is still alive
                if instance.process and instance.process.poll() is not None:
                    logger.warning(f"Server {server_name} process has terminated")
                    instance.status = MCPServerStatus.FAILED
                    instance.last_error = f"Process terminated (exit code: {instance.process.returncode})"
                    continue
                
                # Check resource usage
                if instance.pid:
                    try:
                        proc = psutil.Process(instance.pid)
                        instance.resource_usage = {
                            "memory_mb": proc.memory_info().rss / 1024 / 1024,
                            "cpu_percent": proc.cpu_percent(),
                            "num_fds": proc.num_fds() if hasattr(proc, 'num_fds') else 0
                        }
                        
                        # Check resource limits
                        limits = instance.config.resource_limits
                        if limits.get("max_memory_mb", 0) > 0:
                            if instance.resource_usage["memory_mb"] > limits["max_memory_mb"]:
                                logger.warning(f"Server {server_name} exceeding memory limit")
                        
                    except psutil.NoSuchProcess:
                        instance.status = MCPServerStatus.FAILED
                        instance.last_error = "Process no longer exists"
                
                # Health check via HTTP if configured
                config = instance.config
                if config.health_check_url:
                    now = datetime.now()
                    if (not instance.last_health_check or 
                        now - instance.last_health_check > timedelta(seconds=config.health_check_interval)):
                        
                        try:
                            response = requests.get(config.health_check_url, timeout=5)
                            if response.status_code == 200:
                                instance.health_status = "healthy"
                            else:
                                instance.health_status = "unhealthy"
                                logger.warning(f"Server {server_name} health check failed: {response.status_code}")
                        except requests.RequestException as e:
                            instance.health_status = "unhealthy"
                            logger.warning(f"Server {server_name} health check failed: {e}")
                        
                        instance.last_health_check = now
                
            except Exception as e:
                logger.error(f"Error checking health for {server_name}: {e}")
    
    def _handle_failed_servers(self):
        """Handle servers that have failed"""
        for server_name, instance in self.instances.items():
            if instance.status != MCPServerStatus.FAILED:
                continue
            
            config = instance.config
            
            # Check if should restart
            if (config.restart_on_failure and 
                instance.restart_count < config.max_restarts):
                
                logger.info(f"Attempting to restart failed server: {server_name}")
                instance.restart_count += 1
                
                # Wait a bit before restarting
                time.sleep(5)
                
                if self.start_server(server_name):
                    logger.info(f"Successfully restarted server {server_name}")
                else:
                    logger.error(f"Failed to restart server {server_name}")
    
    def _save_server_configs(self):
        """Save server configurations to file"""
        try:
            config_data = {
                "version": "2.1.0",
                "servers": {
                    name: config.to_dict() 
                    for name, config in self.server_configs.items()
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save server configs: {e}")
    
    def display_server_status(self):
        """Display server status using Rich console"""
        servers = self.list_servers()
        
        table = Table(title="MCP Server Status", box=box.ROUNDED)
        table.add_column("Server", style="cyan")
        table.add_column("Status", style="green") 
        table.add_column("PID", style="blue")
        table.add_column("Uptime", style="yellow")
        table.add_column("Health", style="magenta")
        table.add_column("Restarts", style="red")
        
        for server_name, info in servers.items():
            # Status with color
            status = info["status"]
            if status == "running":
                status_display = f"[green]{status}[/green]"
            elif status == "failed":
                status_display = f"[red]{status}[/red]"
            elif status == "starting":
                status_display = f"[yellow]{status}[/yellow]"
            else:
                status_display = f"[dim]{status}[/dim]"
            
            # Calculate uptime
            uptime = "N/A"
            if info["start_time"]:
                start_time = datetime.fromisoformat(info["start_time"])
                uptime_delta = datetime.now() - start_time
                uptime = str(uptime_delta).split('.')[0]  # Remove microseconds
            
            table.add_row(
                server_name,
                status_display,
                str(info["pid"]) if info["pid"] else "N/A",
                uptime,
                info["health_status"],
                str(info["restart_count"])
            )
        
        console.print(table)
    
    def shutdown(self):
        """Shutdown MCP manager and all servers"""
        logger.info("Shutting down MCP Manager")
        
        # Stop monitoring
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Stop all servers
        self.stop_all_servers()
        
        logger.info("MCP Manager shutdown complete")

# Convenience function for global access
_global_mcp_manager: Optional[MCPManager] = None

def get_mcp_manager() -> MCPManager:
    """Get the global MCP manager instance"""
    global _global_mcp_manager
    if _global_mcp_manager is None:
        _global_mcp_manager = MCPManager()
    return _global_mcp_manager