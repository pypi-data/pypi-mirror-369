# -*- coding: utf-8 -*-

"""Main module for fx-lib compatibility.

This module provides backward compatibility imports and serves as an alternative
entry point for the fx-lib package. All functionality is available through
the main package __init__.py as well.
"""

# Import everything from the main package for backward compatibility
from . import *

# Convenience functions for common workflows
def quick_email_setup():
    """Quick setup example for email functionality.
    
    Returns:
        str: Example configuration content for .email_config.yaml
    """
    return """
# .email_config.yaml
zoho_email:
  username: your_email@domain.com
  password: your_app_password
  sender_title: Your Name
  recipient: recipient@domain.com
"""

def quick_logging_setup():
    """Quick setup example for logging configuration.
    
    Returns:
        str: Example configuration content for logging.yaml
    """
    return """
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: default
    stream: ext://sys.stdout
  file:
    class: logging.FileHandler
    level: INFO
    formatter: detailed
    filename: app.log
    mode: a
root:
  level: DEBUG
  handlers: [console, file]
"""

def demo_usage():
    """Demonstrate common fx-lib usage patterns.
    
    This function shows examples of how to use the main features of fx-lib.
    """
    print(blue("=== fx-lib Demo ==="))
    
    # String extensions
    s = StrExt("  hello world  ")
    print(f"String: '{s}' - Empty: {s.is_empty()}, Blank: {s.is_blank()}")
    
    # List extensions  
    lst = ListExt([1, 2, 3, 4, 5])
    print(f"List: {lst.join(' -> ')}")
    
    # Date operations
    today = Date.today()
    tomorrow = today.tomorrow()
    print(f"Today: {today.to_yyyy_mm_dd()}, Tomorrow: {tomorrow.to_yyyy_mm_dd()}")
    
    # Math utilities
    print(f"Is 10 divisible by 5? {modable(10, 5)}")
    print(f"Is 10 divisible by 3? {modable(10, 3)}")
    
    # Functional utilities
    print(f"1-indexed range(5): {list(range1(5))}")
    print(f"Convert 1024 bytes: {convert_size(1024)}")
    
    print(green("Demo completed successfully!"))


if __name__ == "__main__":
    demo_usage()
