"""Configuration settings for the Taiga Tasks CLI."""

from .manager import ConfigManager


def load_config():
    """Load configuration from config file."""
    config_manager = ConfigManager()
    return config_manager.load_credentials()


def save_config(host, username, password):
    """Save configuration to config file."""
    config_manager = ConfigManager()
    config_manager.save_credentials(host, username, password)


def is_configured():
    """Check if the application is configured."""
    config_manager = ConfigManager()
    return config_manager.is_configured()
