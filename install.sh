#!/bin/bash
# Installation script for AB Code Reviewer

set -e

echo "🚀 Installing AB Code Reviewer..."

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install package in development mode
echo "📥 Installing AB Code Reviewer..."
pip install -e .

# Install development dependencies
echo "📥 Installing development dependencies..."
pip install -e ".[dev]"

echo "✅ Installation completed!"
echo ""
echo "To use AB Code Reviewer:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run: ab-reviewer --help"
echo ""
echo "To set up a project:"
echo "1. Navigate to your Python project"
echo "2. Run: ab-reviewer --setup"
echo "3. Run: ab-reviewer"
