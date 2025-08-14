"""CLI command handlers for Taiga Tasks."""

import argparse
import getpass

from ..config import settings


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Display Taiga tasks assigned to you.")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Configure Taiga credentials")
    login_parser.add_argument(
        "--host",
        default="https://support.abstract-technology.de",
        help="Taiga host URL (default: https://support.abstract-technology.de)",
    )
    login_parser.add_argument("--username", help="Your Taiga username")

    # Add output format as a top-level argument
    parser.add_argument(
        "--output",
        choices=["table", "simple"],
        default="simple",
        help="Output format: table or simple (default: simple)",
    )

    return parser.parse_args()


def handle_login(args):
    """Handle the login command."""
    username = args.username
    if not username:
        username = input("Enter your Taiga username: ")

    password = getpass.getpass("Enter your Taiga password: ")

    # Save the credentials
    settings.save_config(args.host, username, password)
    print(f"\nCredentials saved successfully to {settings.ConfigManager().config_file}")


def handle_list(args):
    """Handle the list command."""
    if not settings.is_configured():
        print("No credentials found. Please run 'taiga-tasks login' first.")
        return False
    return True
