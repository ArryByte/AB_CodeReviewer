"""Tests for utility modules."""

import tempfile
from pathlib import Path
import pytest

from ab_reviewer.utils.exceptions import (
    ABReviewerError, ConfigurationError, ToolNotFoundError,
    ToolExecutionError, ProjectDetectionError, AIReviewError, ValidationError
)
from ab_reviewer.utils.validation import (
    validate_project_path, validate_python_version, validate_configuration,
    validate_tool_arguments, validate_file_path, validate_directory_path
)
from ab_reviewer.utils.cache import ToolCache
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


class TestValidation:
    """Test validation utilities."""

    def test_validate_project_path_valid(self):
        """Test valid project path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validate_project_path(Path(tmpdir))

    def test_validate_project_path_invalid(self):
        """Test invalid project path."""
        with pytest.raises(ValidationError):
            validate_project_path(Path("/nonexistent/path"))

    def test_validate_python_version(self):
        """Test Python version validation."""
        # Should not raise for current Python version
        validate_python_version((3, 0))
        
        # Should raise for future version
        with pytest.raises(ValidationError):
            validate_python_version((99, 0))

    def test_validate_configuration_valid(self):
        """Test valid configuration."""
        config = {
            "project": {"type": "python"},
            "tools": {
                "formatter": {"enabled": True},
                "linter": {"enabled": True},
                "security": {"enabled": True},
                "tests": {"enabled": True}
            },
            "ai": {"enabled": True}
        }
        validate_configuration(config)

    def test_validate_configuration_invalid(self):
        """Test invalid configuration."""
        # Missing required section
        with pytest.raises(ConfigurationError):
            validate_configuration({"project": {"type": "python"}})
        
        # Invalid project type
        with pytest.raises(ConfigurationError):
            validate_configuration({
                "project": {"type": "invalid"},
                "tools": {},
                "ai": {}
            })

    def test_validate_tool_arguments(self):
        """Test tool arguments validation."""
        validate_tool_arguments("test", ["--arg1", "value1"])
        
        with pytest.raises(ValidationError):
            validate_tool_arguments("test", "not a list")

    def test_validate_file_path(self):
        """Test file path validation."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            validate_file_path(Path(tmpfile.name))
        
        with pytest.raises(ValidationError):
            validate_file_path(Path("/nonexistent/file"))

    def test_validate_directory_path(self):
        """Test directory path validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validate_directory_path(Path(tmpdir))
        
        with pytest.raises(ValidationError):
            validate_directory_path(Path("/nonexistent/dir"))


class TestCache:
    """Test caching utilities."""

    def test_tool_cache_init(self):
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ToolCache(Path(tmpdir))
            assert cache.cache_dir == Path(tmpdir)
            assert cache.ttl_seconds == 3600

    def test_tool_cache_set_get(self):
        """Test cache set and get operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ToolCache(Path(tmpdir))
            
            # Set cache
            result = {"success": True, "output": "test output"}
            cache.set("test_tool", ["--arg"], Path(tmpdir), result)
            
            # Get cache
            cached_result = cache.get("test_tool", ["--arg"], Path(tmpdir))
            assert cached_result == result

    def test_tool_cache_miss(self):
        """Test cache miss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ToolCache(Path(tmpdir))
            
            cached_result = cache.get("nonexistent", [], Path(tmpdir))
            assert cached_result is None

    def test_tool_cache_clear(self):
        """Test cache clearing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ToolCache(Path(tmpdir))
            
            # Set cache
            cache.set("test", [], Path(tmpdir), {"success": True})
            
            # Clear cache
            cache.clear()
            
            # Should be empty
            result = cache.get("test", [], Path(tmpdir))
            assert result is None


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
