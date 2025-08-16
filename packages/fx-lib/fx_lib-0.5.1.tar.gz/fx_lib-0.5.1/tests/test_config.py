#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.config module."""

import unittest
import tempfile
import os
from pathlib import Path
from fx_lib.config import ConfigManager, FxLibConfigError


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_content = """
email:
  username: test@example.com
  password: testpass
  sender_title: Test User
  recipient: recipient@example.com

logging:
  version: 1
  formatters:
    default:
      format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      level: DEBUG
      formatter: default
  root:
    level: DEBUG
    handlers: [console]
"""

    def test_find_config_in_current_directory(self):
        """Test find_config finds file in current directory."""
        # Create config file in test directory
        config_file = Path(self.test_dir) / "test_config.yaml"
        config_file.write_text(self.test_config_content)
        
        # Change to test directory and search
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            found_path = ConfigManager.find_config("test_config.yaml")
            self.assertIsNotNone(found_path)
            self.assertEqual(found_path.name, "test_config.yaml")
            self.assertTrue(found_path.exists())
        finally:
            os.chdir(old_cwd)

    def test_find_config_in_home_directory(self):
        """Test find_config finds file in home directory."""
        # Create config file in home directory
        home_config = Path.home() / "test_fx_config.yaml"
        
        # Clean up any existing file first
        if home_config.exists():
            home_config.unlink()
            
        try:
            home_config.write_text(self.test_config_content)
            
            found_path = ConfigManager.find_config("test_fx_config.yaml")
            self.assertIsNotNone(found_path)
            self.assertEqual(found_path, home_config)
        finally:
            # Clean up
            if home_config.exists():
                home_config.unlink()

    def test_find_config_returns_none_when_not_found(self):
        """Test find_config returns None when file doesn't exist."""
        found_path = ConfigManager.find_config("nonexistent_config.yaml")
        self.assertIsNone(found_path)

    def test_find_config_prefers_current_directory(self):
        """Test find_config prefers current directory over home."""
        # Create config in both locations
        current_config = Path(self.test_dir) / "priority_test.yaml"
        home_config = Path.home() / "priority_test.yaml"
        
        current_config.write_text("current: true")
        
        # Clean up home file first if it exists
        if home_config.exists():
            home_config.unlink()
            
        try:
            home_config.write_text("home: true")
            
            old_cwd = os.getcwd()
            try:
                os.chdir(self.test_dir)
                found_path = ConfigManager.find_config("priority_test.yaml")
                self.assertEqual(found_path, current_config)
            finally:
                os.chdir(old_cwd)
        finally:
            # Clean up
            if home_config.exists():
                home_config.unlink()

    def test_load_yaml_config_success(self):
        """Test load_yaml_config successfully loads valid YAML."""
        config_file = Path(self.test_dir) / "valid_config.yaml"
        config_file.write_text(self.test_config_content)
        
        config = ConfigManager.load_yaml_config(config_file)
        self.assertIsInstance(config, dict)
        self.assertIn("email", config)
        self.assertIn("logging", config)
        self.assertEqual(config["email"]["username"], "test@example.com")

    def test_load_yaml_config_file_not_found(self):
        """Test load_yaml_config raises FxLibConfigError for missing file."""
        nonexistent_file = Path(self.test_dir) / "missing.yaml"
        
        with self.assertRaises(FxLibConfigError) as cm:
            ConfigManager.load_yaml_config(nonexistent_file)
        
        self.assertIn("Configuration file not found", str(cm.exception))

    def test_load_yaml_config_invalid_yaml(self):
        """Test load_yaml_config raises FxLibConfigError for invalid YAML."""
        config_file = Path(self.test_dir) / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [unclosed")
        
        with self.assertRaises(FxLibConfigError) as cm:
            ConfigManager.load_yaml_config(config_file)
        
        self.assertIn("Invalid YAML", str(cm.exception))

    def test_get_config_with_custom_path(self):
        """Test get_config with explicitly provided path."""
        config_file = Path(self.test_dir) / "custom_config.yaml"
        config_file.write_text(self.test_config_content)
        
        config = ConfigManager.get_config("custom_config.yaml", str(config_file))
        self.assertIsInstance(config, dict)
        self.assertEqual(config["email"]["username"], "test@example.com")

    def test_get_config_searches_standard_locations(self):
        """Test get_config searches standard locations when no path provided."""
        # Create config in current directory
        config_file = Path(self.test_dir) / "search_test.yaml"
        config_file.write_text(self.test_config_content)
        
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            config = ConfigManager.get_config("search_test.yaml")
            self.assertIsInstance(config, dict)
            self.assertEqual(config["email"]["username"], "test@example.com")
        finally:
            os.chdir(old_cwd)

    def test_get_config_raises_error_when_not_found(self):
        """Test get_config raises FxLibConfigError when file not found."""
        with self.assertRaises(FxLibConfigError) as cm:
            ConfigManager.get_config("definitely_missing.yaml")
        
        self.assertIn("Configuration file 'definitely_missing.yaml' not found", str(cm.exception))

    def test_get_email_config(self):
        """Test get_email_config convenience method."""
        config_file = Path(self.test_dir) / ".email_config.yaml"
        email_config = {
            "zoho_email": {
                "username": "test@example.com",
                "password": "testpass",
                "sender_title": "Test User",
                "recipient": "recipient@example.com"
            }
        }
        
        import yaml
        config_file.write_text(yaml.dump(email_config))
        
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            config = ConfigManager.get_email_config()
            self.assertEqual(config["username"], "test@example.com")
            self.assertEqual(config["password"], "testpass")
        finally:
            os.chdir(old_cwd)

    def test_get_logging_config(self):
        """Test get_logging_config convenience method."""
        config_file = Path(self.test_dir) / "logging.yaml"
        config_file.write_text(self.test_config_content)
        
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            config = ConfigManager.get_logging_config()
            self.assertIn("version", config)
            self.assertEqual(config["version"], 1)
        finally:
            os.chdir(old_cwd)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)


class TestFxLibConfigError(unittest.TestCase):
    """Test cases for FxLibConfigError exception."""

    def test_config_error_is_exception(self):
        """Test FxLibConfigError inherits from Exception."""
        error = FxLibConfigError("test message")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "test message")

    def test_config_error_with_cause(self):
        """Test FxLibConfigError can wrap other exceptions."""
        original_error = ValueError("original error")
        config_error = FxLibConfigError("config error", original_error)
        
        self.assertEqual(str(config_error), "config error")
        self.assertEqual(config_error.__cause__, original_error)


if __name__ == '__main__':
    unittest.main()