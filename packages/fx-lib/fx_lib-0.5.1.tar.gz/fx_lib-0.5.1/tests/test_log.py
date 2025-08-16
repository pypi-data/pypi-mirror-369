#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.log module."""

import unittest
import tempfile
import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from fx_lib.log import (
    setup_logging, green, blue, yellow, red, blue_bar, 
    TColors, ZohoSMTPHandler
)


class TestColorUtilities(unittest.TestCase):
    """Test cases for terminal color utilities."""

    def test_tcolors_constants(self):
        """Test TColors class has expected constants."""
        self.assertTrue(hasattr(TColors, 'HEADER'))
        self.assertTrue(hasattr(TColors, 'OKBLUE'))
        self.assertTrue(hasattr(TColors, 'OKGREEN'))
        self.assertTrue(hasattr(TColors, 'WARNING'))
        self.assertTrue(hasattr(TColors, 'RED'))
        self.assertTrue(hasattr(TColors, 'FAIL'))
        self.assertTrue(hasattr(TColors, 'ENDC'))
        self.assertTrue(hasattr(TColors, 'BOLD'))
        self.assertTrue(hasattr(TColors, 'UNDERLINE'))

    def test_green_function(self):
        """Test green color function."""
        result = green("test")
        self.assertIn("test", result)
        self.assertTrue(result.startswith(TColors.OKGREEN))
        self.assertTrue(result.endswith(TColors.ENDC))

    def test_blue_function(self):
        """Test blue color function."""
        result = blue("test")
        self.assertIn("test", result)
        self.assertTrue(result.startswith(TColors.OKBLUE))
        self.assertTrue(result.endswith(TColors.ENDC))

    def test_yellow_function(self):
        """Test yellow color function."""
        result = yellow("test")
        self.assertIn("test", result)
        self.assertTrue(result.startswith(TColors.WARNING))
        self.assertTrue(result.endswith(TColors.ENDC))

    def test_red_function(self):
        """Test red color function."""
        result = red("test")
        self.assertIn("test", result)
        self.assertTrue(result.startswith(TColors.RED))
        self.assertTrue(result.endswith(TColors.ENDC))

    def test_blue_bar_function(self):
        """Test blue_bar function."""
        result = blue_bar()
        self.assertIn("=" * 80, result)
        self.assertTrue(result.startswith(TColors.OKBLUE))
        self.assertTrue(result.endswith(TColors.ENDC))


class TestSetupLogging(unittest.TestCase):
    """Test cases for setup_logging function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.valid_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "default"
                }
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["console"]
            }
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('fx_lib.log.ConfigManager.get_logging_config')
    @patch('logging.config.dictConfig')
    def test_setup_logging_success(self, mock_dict_config, mock_get_config):
        """Test successful logging setup."""
        mock_get_config.return_value = self.valid_config
        
        setup_logging()
        
        mock_get_config.assert_called_once()
        mock_dict_config.assert_called_once_with(self.valid_config)

    @patch('fx_lib.log.ConfigManager.load_yaml_config')
    @patch('logging.config.dictConfig')
    def test_setup_logging_with_env_var(self, mock_dict_config, mock_load_config):
        """Test logging setup with environment variable."""
        mock_load_config.return_value = self.valid_config
        
        with patch.dict(os.environ, {'LOG_CFG': '/custom/path/logging.yaml'}):
            setup_logging()
        
        mock_load_config.assert_called_once_with('/custom/path/logging.yaml')
        mock_dict_config.assert_called_once_with(self.valid_config)

    @patch('fx_lib.log.ConfigManager.get_logging_config')
    @patch('logging.basicConfig')
    @patch('builtins.print')
    def test_setup_logging_config_not_found(self, mock_print, mock_basic_config, mock_get_config):
        """Test logging setup when config file not found."""
        from fx_lib.config import FxLibConfigError
        mock_get_config.side_effect = FxLibConfigError("Config not found")
        
        setup_logging()
        
        mock_basic_config.assert_called_once()
        mock_print.assert_called()

    @patch('fx_lib.log.ConfigManager.get_logging_config')
    @patch('logging.config.dictConfig')
    @patch('logging.basicConfig')
    @patch('builtins.print')
    def test_setup_logging_invalid_config(self, mock_print, mock_basic_config, mock_dict_config, mock_get_config):
        """Test logging setup with invalid configuration."""
        mock_get_config.return_value = self.valid_config
        mock_dict_config.side_effect = ValueError("Invalid config")
        
        setup_logging()
        
        mock_dict_config.assert_called_once_with(self.valid_config)
        mock_basic_config.assert_called_once()
        mock_print.assert_called()

    @patch('fx_lib.log.ConfigManager.get_logging_config')
    @patch('logging.basicConfig')
    def test_setup_logging_with_custom_level(self, mock_basic_config, mock_get_config):
        """Test logging setup with custom default level."""
        from fx_lib.config import FxLibConfigError
        mock_get_config.side_effect = FxLibConfigError("Config not found")
        
        setup_logging(default_level=logging.INFO)
        
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs['level'], logging.INFO)


class TestZohoSMTPHandler(unittest.TestCase):
    """Test cases for ZohoSMTPHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler_config = {
            'mailhost': 'smtp.zoho.com',
            'fromaddr': 'sender@example.com',
            'toaddrs': ['recipient@example.com'],
            'subject': 'Test Log Message',
            'credentials': ('username', 'password'),
            'sender_title': 'Test Sender'
        }

    def test_handler_initialization_single_recipient(self):
        """Test handler initialization with single recipient."""
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs='single@example.com',
            subject=self.handler_config['subject'],
            credentials=self.handler_config['credentials']
        )
        
        self.assertEqual(handler.mailhost, 'smtp.zoho.com')
        self.assertEqual(handler.fromaddr, 'sender@example.com')
        self.assertEqual(handler.toaddrs, ['single@example.com'])
        self.assertEqual(handler.subject, 'Test Log Message')
        self.assertEqual(handler.username, 'username')
        self.assertEqual(handler.password, 'password')

    def test_handler_initialization_multiple_recipients(self):
        """Test handler initialization with multiple recipients."""
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=['one@example.com', 'two@example.com'],
            subject=self.handler_config['subject']
        )
        
        self.assertEqual(handler.toaddrs, ['one@example.com', 'two@example.com'])

    def test_handler_initialization_with_port(self):
        """Test handler initialization with mailhost and port."""
        handler = ZohoSMTPHandler(
            mailhost=('smtp.zoho.com', 465),
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=self.handler_config['toaddrs'],
            subject=self.handler_config['subject']
        )
        
        self.assertEqual(handler.mailhost, 'smtp.zoho.com')
        self.assertEqual(handler.mailport, 465)

    def test_get_subject_default(self):
        """Test getSubject returns configured subject."""
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=self.handler_config['toaddrs'],
            subject='Test Subject'
        )
        
        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='', lineno=0,
            msg='Test message', args=(), exc_info=None
        )
        
        subject = handler.getSubject(record)
        self.assertEqual(subject, 'Test Subject')

    @patch('smtplib.SMTP_SSL')
    def test_emit_success(self, mock_smtp_ssl):
        """Test successful email emission."""
        # Mock SMTP client
        mock_client = MagicMock()
        mock_smtp_ssl.return_value = mock_client
        
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=self.handler_config['toaddrs'],
            subject=self.handler_config['subject'],
            credentials=self.handler_config['credentials']
        )
        
        # Create log record
        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='test.py', lineno=42,
            msg='Test error message', args=(), exc_info=None
        )
        
        # Emit the record
        handler.emit(record)
        
        # Verify SMTP operations
        mock_smtp_ssl.assert_called_once_with('smtp.zoho.com', 465)
        mock_client.login.assert_called_once_with('username', 'password')
        mock_client.sendmail.assert_called_once()
        mock_client.quit.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_emit_with_sender_title(self, mock_smtp_ssl):
        """Test email emission with custom sender title."""
        mock_client = MagicMock()
        mock_smtp_ssl.return_value = mock_client
        
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=self.handler_config['toaddrs'],
            subject=self.handler_config['subject'],
            credentials=self.handler_config['credentials'],
            sender_title='Custom Sender'
        )
        
        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='test.py', lineno=42,
            msg='Test error message', args=(), exc_info=None
        )
        
        handler.emit(record)
        
        # Check that sendmail was called with proper parameters
        mock_client.sendmail.assert_called_once()
        args = mock_client.sendmail.call_args[0]
        self.assertEqual(args[0], 'sender@example.com')  # from
        self.assertEqual(args[1], ['recipient@example.com'])  # to
        # Message content should contain headers and base64 content
        message_content = args[2]
        self.assertIn('Subject:', message_content)
        self.assertIn('From: Custom Sender <sender@example.com>', message_content)
        self.assertIn('To: recipient@example.com', message_content)

    @patch('smtplib.SMTP_SSL')
    def test_emit_exception_handling(self, mock_smtp_ssl):
        """Test emit handles exceptions gracefully."""
        # Mock SMTP to raise exception
        mock_smtp_ssl.side_effect = Exception("SMTP Error")
        
        handler = ZohoSMTPHandler(
            mailhost=self.handler_config['mailhost'],
            fromaddr=self.handler_config['fromaddr'],
            toaddrs=self.handler_config['toaddrs'],
            subject=self.handler_config['subject']
        )
        
        # Mock handleError to verify it's called
        handler.handleError = MagicMock()
        
        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='test.py', lineno=42,
            msg='Test error message', args=(), exc_info=None
        )
        
        # Should not raise exception
        handler.emit(record)
        
        # Should call handleError
        handler.handleError.assert_called_once_with(record)


if __name__ == '__main__':
    unittest.main()