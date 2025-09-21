"""Tests for Gemini client."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
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

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_is_available_true(self, mock_run):
        """Test Gemini CLI availability check - available."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gemini version 1.0.0"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            assert client.is_available() is True

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_is_available_false(self, mock_run):
        """Test Gemini CLI availability check - not available."""
        mock_run.side_effect = FileNotFoundError()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            assert client.is_available() is False

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_get_version(self, mock_run):
        """Test getting Gemini CLI version."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gemini version 1.0.0"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            version = client.get_version()
            assert version == "gemini version 1.0.0"

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_get_version_not_available(self, mock_run):
        """Test getting version when Gemini CLI not available."""
        mock_run.side_effect = FileNotFoundError()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            version = client.get_version()
            assert version is None

    def test_prepare_context(self):
        """Test context preparation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GeminiClient(tmpdir)
            
            tool_results = {
                "formatter": {"success": True, "output": "Format OK"},
                "linter": {"success": False, "output": "Lint errors"}
            }
            
            config = {
                "ai": {
                    "context": {
                        "include_git_diff": True,
                        "include_test_results": True,
                        "max_context_lines": 1000
                    }
                }
            }
            
            context = client._prepare_context(tool_results, config)
            
            assert "# Project Context" in context
            assert "FORMATTER: PASSED" in context
            assert "LINTER: FAILED" in context
            assert "# Review Instructions" in context

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_run_review_success(self, mock_run):
        """Test successful AI review."""
        # Mock is_available
        with patch.object(GeminiClient, 'is_available', return_value=True):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "AI review output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)
                
                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}
                
                success, output = client.run_review(tool_results, config)
                
                assert success is True
                assert "AI review output" in output

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_run_review_not_available(self, mock_run):
        """Test AI review when Gemini CLI not available."""
        with patch.object(GeminiClient, 'is_available', return_value=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)
                
                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}
                
                with pytest.raises(AIReviewError):
                    client.run_review(tool_results, config)

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_run_review_disabled(self, mock_run):
        """Test AI review when disabled in config."""
        with patch.object(GeminiClient, 'is_available', return_value=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)
                
                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": False}}
                
                success, output = client.run_review(tool_results, config)
                
                assert success is True
                assert "disabled" in output

    @patch('ab_reviewer.ai.gemini_client.subprocess.run')
    def test_run_review_timeout(self, mock_run):
        """Test AI review timeout."""
        with patch.object(GeminiClient, 'is_available', return_value=True):
            mock_run.side_effect = TimeoutError("Command timed out")
            
            with tempfile.TemporaryDirectory() as tmpdir:
                client = GeminiClient(tmpdir)
                
                tool_results = {"formatter": {"success": True}}
                config = {"ai": {"enabled": True}}
                
                with pytest.raises(AIReviewError):
                    client.run_review(tool_results, config)
