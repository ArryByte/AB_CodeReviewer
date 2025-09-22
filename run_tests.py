#!/usr/bin/env python3
"""Test runner for AB Code Reviewer."""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage."""
    print("🧪 Running AB Code Reviewer tests...")

    # Check if pytest is available
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest not found. Installing...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest",
                "pytest-cov",
                "pytest-mock",
            ],
            check=True,
        )

    # Run tests with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=ab_reviewer",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
    ]

    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def run_linting():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")

    # Black formatting check
    print("  Checking code formatting (black)...")
    try:
        subprocess.run(
            [sys.executable, "-m", "black", "--check", "ab_reviewer/", "tests/"],
            check=True,
            capture_output=True,
        )
        print("  ✅ Code formatting is correct")
    except subprocess.CalledProcessError:
        print("  ❌ Code formatting issues found. Run: black ab_reviewer/ tests/")
        return False

    # Pylint
    print("  Running pylint...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pylint", "ab_reviewer/"],
            check=True,
            capture_output=True,
        )
        print("  ✅ Pylint passed")
    except subprocess.CalledProcessError:
        print("  ⚠️  Pylint found issues (non-blocking)")

    # Bandit security check
    print("  Running security check (bandit)...")
    try:
        subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "ab_reviewer/"],
            check=True,
            capture_output=True,
        )
        print("  ✅ Security check passed")
    except subprocess.CalledProcessError:
        print("  ⚠️  Security issues found (non-blocking)")

    return True


def main():
    """Main test runner."""
    print("🚀 AB Code Reviewer - Test Suite")
    print("=" * 50)

    # Change to project root
    project_root = Path(__file__).parent
    import os

    os.chdir(project_root)

    # Run linting first
    if not run_linting():
        print("❌ Code quality checks failed")
        sys.exit(1)

    print()

    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)

    print()
    print("🎉 All checks passed! The code is ready for production.")


if __name__ == "__main__":
    main()
