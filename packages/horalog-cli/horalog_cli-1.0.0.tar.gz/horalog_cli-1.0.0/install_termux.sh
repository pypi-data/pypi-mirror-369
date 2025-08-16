#!/bin/bash
# HoraLog_CLI Termux Installation Script

echo "HoraLog_CLI - Termux Installation"
echo "=================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Installing Python..."
    pkg install python -y
else
    echo "Python is already installed."
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Installing pip..."
    pkg install python-pip -y
else
    echo "pip is already installed."
fi

# Install pyyaml
echo "Installing pyyaml..."
pip install pyyaml

# Install HoraLog_CLI in development mode
echo "Installing HoraLog_CLI..."
pip install -e .

echo ""
echo "Installation completed!"
echo ""
echo "Usage:"
echo "  horalog-cli              # Start journal mode"
echo "  horalog-cli --review     # Start review mode"
echo "  horalog-cli --help       # Show help"
echo ""
echo "Or run directly with:"
echo "  python -m horalog_cli.main"
