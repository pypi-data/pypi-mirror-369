"""Configuration manager for Taiga Tasks CLI."""

import json
from pathlib import Path


class ConfigManager:
    def __init__(self):
        """Initialize the config manager."""
        self.config_dir = Path.home() / ".taiga"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(mode=0o700, exist_ok=True)

    def save_credentials(self, host, username, password):
        """Save credentials to the config file."""
        config = {"host": host, "username": username, "password": password}

        # Create config file with restricted permissions (600)
        self.config_file.touch(mode=0o600, exist_ok=True)
        self.config_file.write_text(json.dumps(config, indent=2))

    def load_credentials(self):
        """Load credentials from the config file."""
        if not self.config_file.exists():
            raise ValueError(
                "No credentials found. Please run 'taiga-tasks login' first."
            )

        try:
            config = json.loads(self.config_file.read_text())
            required_keys = ["host", "username", "password"]

            if not all(key in config for key in required_keys):
                raise ValueError(
                    "Invalid config file. Please run 'taiga-tasks login' again."
                )

            return config
        except json.JSONDecodeError as err:
            raise ValueError(
                "Invalid config file format. Please run 'taiga-tasks login' again."
            ) from err  # noqa: F841

    def is_configured(self):
        """Check if credentials are configured."""
        return self.config_file.exists()
