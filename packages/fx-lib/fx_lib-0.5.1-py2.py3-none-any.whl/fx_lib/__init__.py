# -*- coding: utf-8 -*-

"""fx-lib: Frank Xu's personal Python utility library.

A lightweight collection of helper modules providing common functionality for:
- Logging with YAML configuration and Zoho SMTP support
- Email sending via Zoho SMTP with configuration management
- Extended datetime classes with formatting and arithmetic operations
- Enhanced string and list classes with utility methods
- Mathematical and functional utilities
- Centralized configuration management

Key Features:
- Test-driven development with comprehensive test coverage
- Proper error handling without global exit() calls
- Dependency injection and configuration management
- Backward compatibility for existing APIs
"""

__author__ = """Frank Xu"""
__email__ = 'frank@frankxu.me'
__version__ = '0.5.1'

# Core utilities
from .math import modable
from .func import range1, enumerate1, p, convert_size, chunks

# Extended data types
from .str_ext import StrExt, S
from .list_ext import ListExt
from .datetime_ext import Date, Datetime

# Configuration and error handling
from .config import ConfigManager, FxLibConfigError

# Logging utilities
from .log import setup_logging, green, blue, yellow, red, blue_bar, TColors, ZohoSMTPHandler

# Email functionality
from .zoho_email import Email

__all__ = [
    # Math utilities
    'modable',
    
    # Functional utilities
    'range1', 'enumerate1', 'p', 'convert_size', 'chunks',
    
    # Extended data types
    'StrExt', 'S', 'ListExt', 'Date', 'Datetime',
    
    # Configuration management
    'ConfigManager', 'FxLibConfigError',
    
    # Logging utilities
    'setup_logging', 'green', 'blue', 'yellow', 'red', 'blue_bar', 
    'TColors', 'ZohoSMTPHandler',
    
    # Email functionality
    'Email',
]
