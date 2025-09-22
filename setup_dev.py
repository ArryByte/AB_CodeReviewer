#!/usr/bin/env python3
"""
Development setup script for AB Code Reviewer.
This script ensures all dependencies are installed and the environment is ready.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+"
        )
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install all dependencies."""
    print("📦 Installing dependencies...")

    # Install core dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing core dependencies",
    ):
        return False

    # Install dev dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
        "Installing dev dependencies",
    ):
        return False

    # Install package in development mode
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        "Installing package in development mode",
    ):
        return False

    return True


def verify_installation():
    """Verify that the installation is working."""
    print("🔍 Verifying installation...")

    # Check if we can import the package
    try:
        import ab_reviewer

        print("✅ Package import successful")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

    # Check if CLI is available
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ab_reviewer", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✅ CLI is available")
        else:
            print(f"❌ CLI test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

    return True


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    if not run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v"], "Running test suite"
    ):
        return False
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up AB Code Reviewer development environment...")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)

    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)

    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)

    print("=" * 60)
    print("🎉 Setup completed successfully!")
    print("You can now run:")
    print("  python3 -m ab_reviewer --help")
    print("  python3 -m pytest tests/ -v")
    print("  python3 -m ab_reviewer --project-path . --progressive")


if __name__ == "__main__":
    main()
