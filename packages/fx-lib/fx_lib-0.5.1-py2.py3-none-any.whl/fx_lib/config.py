"""Configuration management for fx_lib.

This module provides centralized configuration handling for all fx_lib modules,
replacing hardcoded paths and global exit() calls with proper error handling.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union


__all__ = ["ConfigManager", "FxLibConfigError"]


class FxLibConfigError(Exception):
    """Raised when configuration is missing or invalid."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        """Initialize configuration error.
        
        Args:
            message: Error description
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        if cause:
            self.__cause__ = cause


class ConfigManager:
    """Centralized configuration management for fx_lib."""

    @staticmethod
    def find_config(filename: str) -> Optional[Path]:
        """Find configuration file in standard locations.
        
        Searches for configuration file in:
        1. Current working directory
        2. User's home directory
        
        Args:
            filename: Name of configuration file to find
            
        Returns:
            Path to configuration file if found, None otherwise
        """
        locations = [
            Path.cwd() / filename,
            Path.home() / filename
        ]
        
        for location in locations:
            if location.exists() and location.is_file():
                return location
        
        return None

    @staticmethod
    def load_yaml_config(config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load and parse YAML configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Dictionary containing parsed configuration
            
        Raises:
            FxLibConfigError: If file not found or invalid YAML
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FxLibConfigError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}
                return config
        except yaml.YAMLError as e:
            raise FxLibConfigError(f"Invalid YAML in {config_path}: {str(e)}", e)
        except (IOError, OSError) as e:
            raise FxLibConfigError(f"Unable to read {config_path}: {str(e)}", e)

    @classmethod
    def get_config(cls, filename: str, explicit_path: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration from file with automatic path resolution.
        
        Args:
            filename: Name of configuration file
            explicit_path: Optional explicit path to configuration file
            
        Returns:
            Dictionary containing parsed configuration
            
        Raises:
            FxLibConfigError: If configuration file not found or invalid
        """
        if explicit_path:
            config_path = Path(explicit_path)
        else:
            config_path = cls.find_config(filename)
            if config_path is None:
                raise FxLibConfigError(
                    f"Configuration file '{filename}' not found in current directory or home directory"
                )
        
        return cls.load_yaml_config(config_path)

    @classmethod
    def get_email_config(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Get email configuration with standard filename.
        
        Args:
            config_path: Optional explicit path to email config file
            
        Returns:
            Dictionary containing email configuration
            
        Raises:
            FxLibConfigError: If email configuration not found or invalid
        """
        config = cls.get_config(".email_config.yaml", config_path)
        
        if "zoho_email" not in config:
            raise FxLibConfigError(
                "Email configuration missing 'zoho_email' section in .email_config.yaml"
            )
        
        email_config = config["zoho_email"]
        required_fields = ["username", "password", "sender_title", "recipient"]
        
        missing_fields = [field for field in required_fields if field not in email_config]
        if missing_fields:
            raise FxLibConfigError(
                f"Email configuration missing required fields: {', '.join(missing_fields)}"
            )
        
        return email_config

    @classmethod
    def get_logging_config(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Get logging configuration with standard filename.
        
        Args:
            config_path: Optional explicit path to logging config file
            
        Returns:
            Dictionary containing logging configuration
            
        Raises:
            FxLibConfigError: If logging configuration not found or invalid
        """
        config = cls.get_config("logging.yaml", config_path)
        
        # If config contains a 'logging' section, return that section
        # Otherwise, assume the entire config is the logging configuration
        if "logging" in config:
            return config["logging"]
        return config

    @classmethod
    def get_config_with_fallback(cls, filename: str, fallback_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration with fallback to default if file not found.
        
        Args:
            filename: Name of configuration file
            fallback_config: Default configuration to use if file not found
            
        Returns:
            Dictionary containing configuration (loaded or fallback)
        """
        try:
            return cls.get_config(filename)
        except FxLibConfigError:
            return fallback_config