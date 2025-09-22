"""Tests for project detector."""

import tempfile
from pathlib import Path
import pytest

from ab_reviewer.core.detector import ProjectDetector


class TestProjectDetector:
    """Test cases for ProjectDetector."""

    def test_detect_python_project_with_pyproject_toml(self):
        """Test detection of Python project with pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml
            (Path(tmpdir) / "pyproject.toml").write_text("[build-system]")

            detector = ProjectDetector(tmpdir)
            assert detector.detect_project_type() == "python"

    def test_detect_python_project_with_setup_py(self):
        """Test detection of Python project with setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create setup.py
            (Path(tmpdir) / "setup.py").write_text("from setuptools import setup")

            detector = ProjectDetector(tmpdir)
            assert detector.detect_project_type() == "python"

    def test_detect_python_project_with_requirements_txt(self):
        """Test detection of Python project with requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            (Path(tmpdir) / "requirements.txt").write_text("click>=8.0.0")

            detector = ProjectDetector(tmpdir)
            assert detector.detect_project_type() == "python"

    def test_detect_python_project_with_py_files(self):
        """Test detection of Python project with .py files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file
            (Path(tmpdir) / "main.py").write_text("print('hello')")

            detector = ProjectDetector(tmpdir)
            assert detector.detect_project_type() == "python"

    def test_detect_unknown_project(self):
        """Test detection of unknown project type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create non-Python file
            (Path(tmpdir) / "README.md").write_text("# Project")

            detector = ProjectDetector(tmpdir)
            assert detector.detect_project_type() == "unknown"

    def test_is_git_repository(self):
        """Test git repository detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git directory
            (Path(tmpdir) / ".git").mkdir()

            detector = ProjectDetector(tmpdir)
            assert detector._is_git_repository() is True

    def test_is_not_git_repository(self):
        """Test non-git repository detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ProjectDetector(tmpdir)
            assert detector._is_git_repository() is False

    def test_get_project_info(self):
        """Test getting comprehensive project information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python project files
            (Path(tmpdir) / "pyproject.toml").write_text("[build-system]")
            (Path(tmpdir) / ".git").mkdir()

            detector = ProjectDetector(tmpdir)
            info = detector.get_project_info()

            assert info["type"] == "python"
            assert info["path"] == str(Path(tmpdir).resolve())
            assert info["is_git_repo"] is True
