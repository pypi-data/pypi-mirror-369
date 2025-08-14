#!/usr/bin/env python3
"""
Enhanced Configuration Manager for Swiss AI CLI
Supports YAML-based configuration with schema validation and backward compatibility
"""

import os
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging
from dotenv import load_dotenv

# Rich for beautiful error messages
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
import sys

# Fix Windows console encoding issues
if sys.platform == "win32":
    console = Console(force_terminal=True, width=120)
else:
    console = Console()

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    def __init__(self, message: str, suggestion: Optional[str] = None, path: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        self.path = path
        super().__init__(message)

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: str = "openrouter"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 30
    use_cases: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfig':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class ProfileConfig:
    """Configuration for a user profile"""
    name: str
    description: str = ""
    default_model: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    enabled_features: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class SwissAIConfig:
    """Main Swiss AI CLI configuration"""
    version: str = "2.1.0"
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    profiles: Dict[str, ProfileConfig] = field(default_factory=dict)
    active_profile: str = "default"
    global_settings: Dict[str, Any] = field(default_factory=dict)
    mcp_servers: Dict[str, Any] = field(default_factory=dict)
    routing_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Ensure default profile exists
        if "default" not in self.profiles:
            self.profiles["default"] = ProfileConfig(
                name="default",
                description="Default Swiss AI CLI profile"
            )
        
        # Set default global settings
        if not self.global_settings:
            self.global_settings = {
                "theme": "auto",
                "logging_level": "INFO", 
                "auto_save": True,
                "backup_configs": True,
                "check_updates": True
            }

class ConfigManager:
    """Enhanced configuration manager with YAML support and validation"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".swiss-ai"
        self.config_file = self.config_dir / "config.yaml"
        self.backup_dir = self.config_dir / "backups"
        self.legacy_config_file = self.config_dir / "config.json"  # For migration
        self.env_file = self.config_dir / ".env"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self._config: Optional[SwissAIConfig] = None
        self._watchers: List[callable] = []
        
        logger.info(f"ConfigManager initialized with config_dir: {self.config_dir}")
        # Load environment variables from ~/.swiss-ai/.env and local .env if present
        try:
            if self.env_file.exists():
                load_dotenv(dotenv_path=self.env_file, override=False)
            # Load project .env without overriding already-set vars
            load_dotenv(override=False)
        except Exception as e:
            logger.debug(f"ENV load skipped: {e}")
    
    def load_config(self, create_if_missing: bool = True) -> SwissAIConfig:
        """Load configuration from YAML file"""
        try:
            # Check for legacy JSON config and migrate
            if self.legacy_config_file.exists() and not self.config_file.exists():
                self._migrate_legacy_config()
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Convert model configs
                if 'models' in config_data:
                    for model_name, model_data in config_data['models'].items():
                        if isinstance(model_data, dict):
                            config_data['models'][model_name] = ModelConfig.from_dict(model_data)
                
                # Convert profile configs
                if 'profiles' in config_data:
                    for profile_name, profile_data in config_data['profiles'].items():
                        if isinstance(profile_data, dict):
                            config_data['profiles'][profile_name] = ProfileConfig(**profile_data)
                
                self._config = SwissAIConfig(**config_data)
                logger.info("Configuration loaded successfully")
                
            elif create_if_missing:
                self._config = SwissAIConfig()
                self.save_config()
                logger.info("Created new default configuration")
            else:
                raise ConfigurationError(
                    "Configuration file not found",
                    suggestion="Run 'swiss-ai init' to create a new configuration"
                )
                
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in configuration file: {e}",
                suggestion="Check your YAML syntax or restore from backup",
                path=str(self.config_file)
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                suggestion="Check file permissions and syntax",
                path=str(self.config_file)
            )
        
        return self._config
    
    def save_config(self, backup: bool = True) -> None:
        """Save configuration to YAML file"""
        if self._config is None:
            raise ConfigurationError("No configuration to save")
        
        try:
            # Create backup if requested
            if backup and self.config_file.exists():
                self._create_backup()
            
            # Convert config to dict for serialization
            config_dict = asdict(self._config)
            
            # Convert ModelConfig objects to dicts
            if 'models' in config_dict:
                for model_name, model_config in config_dict['models'].items():
                    if isinstance(model_config, ModelConfig):
                        config_dict['models'][model_name] = model_config.to_dict()
            
            # Save to YAML
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, 
                         default_flow_style=False, 
                         indent=2, 
                         allow_unicode=True,
                         sort_keys=False)
            
            logger.info("Configuration saved successfully")
            
            # Notify watchers
            for watcher in self._watchers:
                try:
                    watcher(self._config)
                except Exception as e:
                    logger.warning(f"Configuration watcher failed: {e}")
                    
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration: {e}",
                suggestion="Check file permissions and disk space",
                path=str(self.config_file)
            )
    
    def get_config(self) -> SwissAIConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with partial updates"""
        config = self.get_config()
        
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
        
        self.save_config()
    
    def add_model(self, model_config: ModelConfig) -> None:
        """Add a new model configuration"""
        config = self.get_config()
        config.models[model_config.name] = model_config
        self.save_config()
        logger.info(f"Added model configuration: {model_config.name}")
    
    def remove_model(self, model_name: str) -> None:
        """Remove a model configuration"""
        config = self.get_config()
        if model_name in config.models:
            del config.models[model_name]
            self.save_config()
            logger.info(f"Removed model configuration: {model_name}")
        else:
            raise ConfigurationError(f"Model '{model_name}' not found in configuration")
    
    def add_profile(self, profile_config: ProfileConfig) -> None:
        """Add a new user profile"""
        config = self.get_config()
        config.profiles[profile_config.name] = profile_config
        self.save_config()
        logger.info(f"Added profile: {profile_config.name}")
    
    def set_active_profile(self, profile_name: str) -> None:
        """Set the active user profile"""
        config = self.get_config()
        if profile_name not in config.profiles:
            raise ConfigurationError(f"Profile '{profile_name}' not found")
        
        config.active_profile = profile_name
        self.save_config()
        logger.info(f"Switched to profile: {profile_name}")
    
    def get_active_profile(self) -> ProfileConfig:
        """Get the currently active profile"""
        config = self.get_config()
        return config.profiles[config.active_profile]
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        config = self.get_config()
        
        # Validate models (only warn when no provider key is available at all)
        any_provider_key = any(
            os.getenv(k) for k in (
                'OPENROUTER_API_KEY','GOOGLE_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY','XAI_API_KEY'
            )
        )
        for model_name, model_config in config.models.items():
            if not model_config.api_key and not any_provider_key:
                issues.append(f"Model '{model_name}' has no API key configured and no provider key found in environment")
            
            if model_config.temperature < 0 or model_config.temperature > 2:
                issues.append(f"Model '{model_name}' has invalid temperature: {model_config.temperature}")
        
        # Validate active profile
        if config.active_profile not in config.profiles:
            issues.append(f"Active profile '{config.active_profile}' does not exist")
        
        return issues
    
    def _migrate_legacy_config(self) -> None:
        """Migrate from legacy JSON configuration"""
        logger.info("Migrating legacy JSON configuration")
        
        try:
            with open(self.legacy_config_file, 'r') as f:
                legacy_data = json.load(f)
            
            # Convert to new format
            new_config = SwissAIConfig()
            
            # Migrate models (simplified)
            if 'api_key' in legacy_data:
                new_config.models['default'] = ModelConfig(
                    name="qwen/qwen3-coder:free",
                    api_key=legacy_data['api_key'],
                    temperature=legacy_data.get('temperature', 0.1),
                    max_tokens=legacy_data.get('max_tokens', 4096)
                )
            
            self._config = new_config
            self.save_config()
            
            # Backup legacy file
            backup_path = self.backup_dir / f"legacy_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.legacy_config_file.rename(backup_path)
            
            logger.info("Legacy configuration migrated successfully")
            
        except Exception as e:
            logger.error(f"Failed to migrate legacy configuration: {e}")
            raise ConfigurationError(f"Migration failed: {e}")
    
    def _create_backup(self) -> None:
        """Create a backup of the current configuration"""
        backup_name = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        backup_path = self.backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(self.config_file, backup_path)
            logger.debug(f"Created configuration backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    def add_watcher(self, callback: callable) -> None:
        """Add a configuration change watcher"""
        self._watchers.append(callback)
    
    def remove_watcher(self, callback: callable) -> None:
        """Remove a configuration change watcher"""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    def reset_config(self) -> None:
        """Reset configuration to defaults"""
        self._config = SwissAIConfig()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def export_config(self, export_path: Path, format: str = "yaml") -> None:
        """Export configuration to a file"""
        config = self.get_config()
        
        if format.lower() == "json":
            with open(export_path, 'w') as f:
                json.dump(asdict(config), f, indent=2, default=str)
        else:  # YAML
            with open(export_path, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration exported to: {export_path}")
    
    def display_config(self) -> None:
        """Display current configuration using Rich"""
        config = self.get_config()
        
        # Main config table
        table = Table(title="Swiss AI CLI Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Version", config.version)
        table.add_row("Active Profile", config.active_profile)
        table.add_row("Models Count", str(len(config.models)))
        table.add_row("Profiles Count", str(len(config.profiles)))
        
        console.print(table)
        
        # Models table
        if config.models:
            models_table = Table(title="Configured Models", box=box.ROUNDED)
            models_table.add_column("Name", style="cyan")
            models_table.add_column("Provider", style="yellow")
            models_table.add_column("Enabled", style="green")
            models_table.add_column("Priority", style="blue")
            
            for model_name, model_config in config.models.items():
                models_table.add_row(
                    model_name,
                    model_config.provider,
                    "✓" if model_config.enabled else "✗",
                    str(model_config.priority)
                )
            
            console.print(models_table)

# Convenience function for global access
_global_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager