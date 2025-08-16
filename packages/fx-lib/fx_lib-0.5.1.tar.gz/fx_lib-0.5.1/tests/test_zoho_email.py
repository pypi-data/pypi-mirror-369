#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.zoho_email module."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fx_lib.zoho_email import Email
from fx_lib.config import FxLibConfigError


class TestZohoEmail(unittest.TestCase):
    """Tests for fx_lib.zoho_email module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "username": "test@example.com",
            "password": "testpass",
            "sender_title": "Test User",
            "recipient": "recipient@example.com"
        }

    def test_email_creation_with_config(self):
        """Test creating Email with configuration parameters."""
        email = Email(**self.test_config)
        self.assertEqual(email.username, "test@example.com")
        self.assertEqual(email.password, "testpass")
        self.assertEqual(email.sender_title, "Test User")
        self.assertEqual(email.recipient, "recipient@example.com")

    def test_email_from_config_file(self):
        """Test creating Email from configuration file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            config_data = {"zoho_email": self.test_config}
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            email = Email.from_config(config_path)
            self.assertEqual(email.username, "test@example.com")
            self.assertEqual(email.password, "testpass")
        finally:
            os.unlink(config_path)

    def test_email_from_config_missing_file_raises_error(self):
        """Test Email.from_config raises error for missing file."""
        with self.assertRaises(FxLibConfigError):
            Email.from_config("/nonexistent/path/config.yaml")

    @patch('smtplib.SMTP_SSL')
    def test_email_context_manager(self, mock_smtp):
        """Test Email as context manager."""
        # Mock SMTP client
        mock_client = MagicMock()
        mock_smtp.return_value = mock_client

        email = Email(**self.test_config)
        
        with email:
            # Should connect and login
            mock_smtp.assert_called_once_with('smtp.zoho.com', 465)
            mock_client.login.assert_called_once_with("test@example.com", "testpass")
        
        # Should quit after context
        mock_client.quit.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_email_send_message(self, mock_smtp):
        """Test sending email message."""
        # Mock SMTP client
        mock_client = MagicMock()
        mock_smtp.return_value = mock_client

        email = Email(**self.test_config)
        
        with email:
            email.send("Test Subject", "Test content")
            
            # Should call sendmail
            mock_client.sendmail.assert_called_once()
            args = mock_client.sendmail.call_args[0]
            self.assertEqual(args[0], "test@example.com")  # from
            self.assertEqual(args[1], ["recipient@example.com"])  # to

    def test_email_send_without_connection_raises_error(self):
        """Test sending email without connection raises error."""
        email = Email(**self.test_config)
        
        with self.assertRaises(RuntimeError) as cm:
            email.send("Test Subject", "Test content")
        
        self.assertIn("Not connected to SMTP server", str(cm.exception))

    @patch('smtplib.SMTP_SSL')
    def test_email_manual_connection(self, mock_smtp):
        """Test manual connection and disconnection."""
        mock_client = MagicMock()
        mock_smtp.return_value = mock_client

        email = Email(**self.test_config)
        
        # Manual connect and login
        email.connect()
        email.login()
        
        mock_smtp.assert_called_once_with('smtp.zoho.com', 465)
        mock_client.login.assert_called_once_with("test@example.com", "testpass")
        
        # Manual quit
        email.quit()
        mock_client.quit.assert_called_once()

    def test_backward_compatibility_read_config(self):
        """Test backward compatibility of read_config method."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            config_data = {"zoho_email": self.test_config}
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            email = Email.read_config(config_path)
            self.assertEqual(email.username, "test@example.com")
            self.assertIsInstance(email, Email)
        finally:
            os.unlink(config_path)


if __name__ == '__main__':
    unittest.main()
