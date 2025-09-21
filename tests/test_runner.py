"""Tests for tool runner."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from ab_reviewer.core.runner import ToolRunner
from ab_reviewer.utils.exceptions import ToolExecutionError, ToolNotFoundError


class TestToolRunner:
    """Test cases for ToolRunner."""

    def test_init(self):
        """Test ToolRunner initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            assert runner.project_path == Path(tmpdir).resolve()
            assert runner.config == {}
            assert runner.results == {}

    def test_init_with_config(self):
        """Test ToolRunner initialization with config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"tools": {"formatter": {"enabled": False}}}
            runner = ToolRunner(tmpdir, config)
            assert runner.config == config

    def test_is_tool_enabled(self):
        """Test tool enabled check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "tools": {
                    "formatter": {"enabled": True},
                    "linter": {"enabled": False}
                }
            }
            runner = ToolRunner(tmpdir, config)
            
            assert runner._is_tool_enabled("formatter") is True
            assert runner._is_tool_enabled("linter") is False
            assert runner._is_tool_enabled("nonexistent") is True  # Default enabled

    @patch('ab_reviewer.core.runner.subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            success, output = runner._run_command("test", ["echo", "test"], [])
            
            assert success is True
            assert "Success output" in output

    @patch('ab_reviewer.core.runner.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test failed command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            success, output = runner._run_command("test", ["false"], [])
            
            assert success is False
            assert "Error output" in output

    @patch('ab_reviewer.core.runner.subprocess.run')
    def test_run_command_timeout(self, mock_run):
        """Test command timeout."""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            
            with pytest.raises(ToolExecutionError):
                runner._run_command("test", ["sleep", "10"], [])

    @patch('ab_reviewer.core.runner.subprocess.run')
    def test_run_command_not_found(self, mock_run):
        """Test command not found."""
        mock_run.side_effect = FileNotFoundError()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            
            with pytest.raises(ToolNotFoundError):
                runner._run_command("test", ["nonexistent"], [])

    def test_get_failed_tools(self):
        """Test getting failed tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            runner.results = {
                "formatter": {"success": True},
                "linter": {"success": False},
                "security": {"success": True},
                "tests": {"success": False}
            }
            
            failed = runner.get_failed_tools()
            assert "linter" in failed
            assert "tests" in failed
            assert "formatter" not in failed
            assert "security" not in failed

    def test_all_tools_passed(self):
        """Test checking if all tools passed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ToolRunner(tmpdir)
            
            # All passed
            runner.results = {
                "formatter": {"success": True},
                "linter": {"success": True}
            }
            assert runner.all_tools_passed() is True
            
            # Some failed
            runner.results = {
                "formatter": {"success": True},
                "linter": {"success": False}
            }
            assert runner.all_tools_passed() is False
