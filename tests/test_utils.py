"""Tests for utility modules."""

import tempfile
from pathlib import Path
import pytest

from ab_reviewer.utils.exceptions import (
    ABReviewerError,
    ConfigurationError,
    ToolNotFoundError,
    ToolExecutionError,
    ProjectDetectionError,
    AIReviewError,
    ValidationError,
)
from ab_reviewer.utils.git import GitManager


class TestExceptions:
    """Test custom exceptions."""

    def test_ab_reviewer_error(self):
        """Test base exception."""
        with pytest.raises(ABReviewerError):
            raise ABReviewerError("Test error")

    def test_configuration_error(self):
        """Test configuration error."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")

    def test_tool_not_found_error(self):
        """Test tool not found error."""
        with pytest.raises(ToolNotFoundError):
            raise ToolNotFoundError("Tool not found")

    def test_tool_execution_error(self):
        """Test tool execution error."""
        with pytest.raises(ToolExecutionError):
            raise ToolExecutionError("Tool execution failed")

    def test_project_detection_error(self):
        """Test project detection error."""
        with pytest.raises(ProjectDetectionError):
            raise ProjectDetectionError("Project detection failed")

    def test_ai_review_error(self):
        """Test AI review error."""
        with pytest.raises(AIReviewError):
            raise AIReviewError("AI review failed")

    def test_validation_error(self):
        """Test validation error."""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")


class TestSubprocessUtils:
    """Test subprocess utilities."""

    def test_run_command_success(self):
        """Test successful command execution."""
        from ab_reviewer.utils.subprocess_utils import run_command

        success, output = run_command(["echo", "test"], timeout=10)
        assert success is True
        assert "test" in output

    def test_run_command_failure(self):
        """Test failed command execution."""
        from ab_reviewer.utils.subprocess_utils import run_command

        success, output = run_command(["false"], timeout=10)
        assert success is False
        # false command doesn't produce output, just returns non-zero exit code

    def test_run_command_not_found(self):
        """Test command not found."""
        from ab_reviewer.utils.subprocess_utils import run_command
        from ab_reviewer.utils.exceptions import ToolNotFoundError

        with pytest.raises(ToolNotFoundError):
            run_command(["nonexistent_command"], timeout=10)


class TestGitManager:
    """Test git utilities."""

    def test_git_manager_init(self):
        """Test GitManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(Path(tmpdir))
            assert git_manager.project_path == Path(tmpdir)

    def test_is_git_repository_false(self):
        """Test non-git repository detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(Path(tmpdir))
            assert git_manager.is_git_repository() is False

    def test_is_git_repository_true(self):
        """Test git repository detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git directory
            (Path(tmpdir) / ".git").mkdir()

            git_manager = GitManager(Path(tmpdir))
            assert git_manager.is_git_repository() is True

    def test_get_branch_info_non_git(self):
        """Test branch info for non-git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(Path(tmpdir))
            branch_info = git_manager.get_branch_info()
            assert branch_info == {}

    def test_get_file_status_non_git(self):
        """Test file status for non-git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(Path(tmpdir))
            status = git_manager.get_file_status()
            assert status == {}
