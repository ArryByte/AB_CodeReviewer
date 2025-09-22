"""Tests for Gemini client."""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from ab_reviewer.ai.gemini_client import GeminiClient
from ab_reviewer.utils.exceptions import AIReviewError


class TestGeminiClient:
    """Test cases for GeminiClient."""

    def test_init(self):
        """Test GeminiClient initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            assert client.project_path == Path(tmpdir).resolve()
            assert client.dry_run is False

    def test_init_dry_run(self):
        """Test GeminiClient initialization with dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir, dry_run=True)
            assert client.project_path == Path(tmpdir).resolve()
            assert client.dry_run is True

    @patch("ab_reviewer.ai.gemini_client.check_tool_available")
    def test_is_available_true(self, mock_check):
        """Test Gemini CLI availability check - available."""
        mock_check.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            assert client.is_available() is True

    @patch("ab_reviewer.ai.gemini_client.check_tool_available")
    def test_is_available_false(self, mock_check):
        """Test Gemini CLI availability check - not available."""
        mock_check.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            assert client.is_available() is False

    @patch("ab_reviewer.ai.gemini_client.run_command")
    def test_get_version(self, mock_run):
        """Test getting Gemini CLI version."""
        mock_run.return_value = (True, "gemini version 1.0.0")

        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            version = client.get_version()
            assert version == "gemini version 1.0.0"

    @patch("ab_reviewer.ai.gemini_client.run_command")
    def test_get_version_not_available(self, mock_run):
        """Test getting version when Gemini CLI not available."""
        from ab_reviewer.utils.exceptions import ToolNotFoundError

        mock_run.side_effect = ToolNotFoundError("Tool not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            version = client.get_version()
            assert version is None

    def test_run_review_dry_run(self):
        """Test AI review in dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir, dry_run=True)
            tool_results = {"formatter": {"success": True}}
            config = {"ai": {"enabled": True}}

            success, output = client.run_review(tool_results, config)
            assert success is True
            assert "dry run mode" in output

    def test_prepare_context(self):
        """Test context preparation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)

            tool_results = {
                "formatter": {"success": True, "output": "Format OK"},
                "linter": {"success": False, "output": "Lint errors"},
            }

            config = {
                "ai": {
                    "context": {
                        "include_git_diff": True,
                        "include_test_results": True,
                        "max_context_lines": 1000,
                    }
                }
            }

            context = client._prepare_context(tool_results, config)

            assert "# Project Context" in context
            assert "FORMATTER: PASSED" in context
            assert "LINTER: FAILED" in context
            assert "# Review Instructions" in context

    @patch("ab_reviewer.ai.gemini_client.run_command")
    def test_run_review_success(self, mock_run):
        """Test successful AI review."""
        # Mock is_available
        with patch.object(GeminiClient, "is_available", return_value=True):
            mock_run.return_value = (True, "AI review output")

            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)

                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}

                success, output = client.run_review(tool_results, config)

                assert success is True
                assert "AI review output" in output

    def test_run_review_not_available(self):
        """Test AI review when Gemini CLI not available."""
        with patch.object(GeminiClient, "is_available", return_value=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)

                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}

                with pytest.raises(AIReviewError):
                    client.run_review(tool_results, config)

    def test_run_review_disabled(self):
        """Test AI review when disabled in config."""
        with patch.object(GeminiClient, "is_available", return_value=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)

                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": False}}

                success, output = client.run_review(tool_results, config)

                assert success is True
                assert "disabled" in output

    @patch("ab_reviewer.ai.gemini_client.run_command")
    def test_run_review_timeout(self, mock_run):
        """Test AI review timeout."""
        with patch.object(GeminiClient, "is_available", return_value=True):
            from ab_reviewer.utils.exceptions import ToolExecutionError

            mock_run.side_effect = ToolExecutionError("Command timed out")

            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)

                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}

                with pytest.raises(AIReviewError):
                    client.run_review(tool_results, config)
