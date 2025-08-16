import os
import logging.config
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from .config import ConfigManager, FxLibConfigError


__all__ = ["setup_logging", "green", "blue", "yellow", "red", "blue_bar", "TColors"]

class TColors:
    """
    Terminal Colors
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


BAR = "="*80


def green(s):
    return "{}{}{}".format(TColors.OKGREEN, s, TColors.ENDC)


def blue(s):
    return "{}{}{}".format(TColors.OKBLUE, s, TColors.ENDC)


def yellow(s):
    return "{}{}{}".format(TColors.WARNING, s, TColors.ENDC)


def red(s):
    return "{}{}{}".format(TColors.RED, s, TColors.ENDC)


def blue_bar():
    return blue(BAR)


def setup_logging(default_path='logging.yaml', default_level=logging.DEBUG, env_key='LOG_CFG'):
    """Setup logging configuration from file or environment variable.
    
    Args:
        default_path: Default path to logging configuration file
        default_level: Default logging level if configuration fails
        env_key: Environment variable key for config file path override
    """
    # Check for environment variable override
    config_path = os.getenv(env_key)
    
    try:
        if config_path:
            # Use explicitly provided path
            config = ConfigManager.load_yaml_config(config_path)
        else:
            # Use ConfigManager to find logging config
            config = ConfigManager.get_logging_config()
        
        logging.config.dictConfig(config)
        
    except FxLibConfigError as e:
        print(f"Warning: Could not load logging configuration: {e}")
        print(f"Using default logging configuration with level {default_level}")
        logging.basicConfig(
            level=default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    except Exception as e:
        print(f"Error in logging configuration: {e}")
        print(f"Using default logging configuration with level {default_level}")
        logging.basicConfig(
            level=default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


class ZohoSMTPHandler(logging.Handler):
    """
    A handler class which sends an SMTP email for each logging event.
    """
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None, sender_title=None):
        """
        Initialize the handler.
        Initialize the instance with the from and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        A timeout in seconds can be specified for the SMTP connection (the
        default is one second).
        """
        logging.Handler.__init__(self)
        if isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, (list, tuple)):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        if sender_title is None:
            sender_title = fromaddr
        self.sender_title = sender_title

    def getSubject(self, record):
        """
        Determine the subject for the email.
        If you want to specify a subject line which is record-dependent,
        override this method.
        """
        return self.subject

    def emit(self, record):
        """
        Emit a record.
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            from email.message import EmailMessage
            import email.utils

            content = self.format(record)
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = Header(self.subject, 'utf-8')
            msg['From'] = formataddr((str(Header(self.sender_title, 'utf-8')), self.fromaddr))
            msg['To'] = ",".join(self.toaddrs)
            port = self.mailport
            if not port:
                port = 465  # Default SSL port for SMTP
            smtp = smtplib.SMTP_SSL(self.mailhost, port)
            smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg.as_string())
            smtp.quit()
        except Exception:
            self.handleError(record)


logging.handlers.ZohoSMTPHandler = ZohoSMTPHandler
