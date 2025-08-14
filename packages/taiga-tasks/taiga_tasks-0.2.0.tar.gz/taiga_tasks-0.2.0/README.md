# Taiga Tasks CLI

A streamlined command-line interface for managing your Taiga tasks across all projects. This tool helps you stay on top of your assignments with an efficient, easy-to-use interface.

## ✨ Features

- 📋 View all your assigned tasks across multiple Taiga projects
- 🎨 Multiple output formats (table and simple views)
- 🔒 Secure credential management
- 🌐 Cross-platform compatibility (Windows, Linux, macOS)
- 🚀 Modern Python tooling with type hints and async support
- 📊 Rich text formatting for enhanced readability

## 🚀 Quick Start

### Installation

You can install Taiga Tasks CLI either via PyPI or from source.

#### Option 1: Install from PyPI (Recommended)

```bash
pip install taiga-tasks
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/codewithemd/taiga-tasks.git
cd taiga-tasks

# Install the package
pip install -e .
```

### Initial Setup

Before first use, configure your Taiga credentials:

```bash
# Configure with default Taiga host (https://support.abstract-technology.de)
taiga-tasks login

# Or specify a custom Taiga instance and username
taiga-tasks login --host https://your-taiga-instance.com --username your-username
```

Your credentials will be securely stored in `~/.taiga/config.json`.

## 📖 Usage Guide

### Available Commands

1. **Login and Configuration**

   ```bash
   taiga-tasks login [--host HOST] [--username USERNAME]
   ```

   - `--host`: Taiga host URL (default: <https://support.abstract-technology.de>)
   - `--username`: Your Taiga username (optional, will prompt if not provided)

2. **List Your Tasks**

   ```bash
   # Simple format (default)
   taiga-tasks [--output simple]

   # Table format with detailed view
   taiga-tasks --output table
   ```

   - `--output`: Choose output format (choices: `table`, `simple`, default: `simple`)

## 🛠️ Technical Details

### Project Structure

```t
taiga_tasks/
├── api/          # Taiga API client implementation
├── cli/          # CLI command handlers
├── config/       # Configuration management
├── display/      # Output formatting
└── main.py       # Application entry point
```

### Dependencies

- Python 3.7 or higher
- Core dependencies:
  - python-taiga (1.3.0) - Taiga API client
  - python-dotenv (1.1.1) - Environment management
  - rich (14.1.0) - Terminal formatting

### Development

To set up a development environment:

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

The project uses Ruff for linting and formatting with pre-configured settings in `pyproject.toml`.

## 🔒 Security

- Configuration stored in `~/.taiga/config.json`
- Secure file permissions:
  - Config directory: 700 (user-only access)
  - Config file: 600 (user-only access)
- Credentials are never logged or exposed

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📧 Contact

Author: Emad Rad
Email: <codewithemd@gmail.com>
Project Homepage: [https://github.com/codewithemd/taiga-tasks](https://github.com/codewithemd/taiga-tasks)
