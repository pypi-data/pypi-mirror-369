import smtplib
import logging
from typing import Optional
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from .config import ConfigManager, FxLibConfigError

log = logging

__all__ = ["Email"]


@dataclass
class Email:
    """Email client for sending emails via Zoho SMTP."""
    
    username: str
    password: str
    sender_title: str
    recipient: str
    smtp_host: str = 'smtp.zoho.com'
    smtp_port: int = 465
    client: Optional[smtplib.SMTP_SSL] = None

    def __post_init__(self):
        """Initialize SMTP client after dataclass initialization."""
        self.client = None  # Will be created in __enter__ or login()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()

    def connect(self):
        """Create SMTP connection."""
        if self.client is None:
            log.debug(f"Connecting to {self.smtp_host}:{self.smtp_port}")
            self.client = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

    def login(self):
        """Login to SMTP server."""
        if self.client is None:
            self.connect()
        log.debug("Logging in to Zoho server")
        self.client.login(self.username, self.password)

    def quit(self):
        """Close SMTP connection."""
        if self.client:
            log.debug("Closing Zoho email connection")
            self.client.quit()
            self.client = None

    def send(self, title: str, content: str):
        """Send email message.
        
        Args:
            title: Email subject
            content: Email body content
            
        Raises:
            RuntimeError: If not connected to SMTP server
        """
        if self.client is None:
            raise RuntimeError("Not connected to SMTP server. Use as context manager or call login() first.")
            
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = formataddr((str(Header(self.sender_title, 'utf-8')), self.username))
        msg['To'] = self.recipient
        self.client.sendmail(self.username, [self.recipient], msg.as_string())

    @classmethod
    def from_config(cls, config_path: Optional[str] = None):
        """Create Email instance from configuration file.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Email instance configured from file
            
        Raises:
            FxLibConfigError: If configuration file not found or invalid
        """
        try:
            config = ConfigManager.get_email_config(config_path)
            return cls(**config)
        except FxLibConfigError:
            raise

    # Backward compatibility
    @staticmethod
    def read_config(path: Optional[str] = None):
        """Deprecated: Use from_config() instead.
        
        Args:
            path: Optional path to configuration file
            
        Returns:
            Email instance configured from file
            
        Raises:
            FxLibConfigError: If configuration file not found or invalid
        """
        return Email.from_config(path)


