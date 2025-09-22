"""Tests for tool runner."""

import tempfile
from pathlib import Path

from ab_reviewer.core.enhanced_runner import EnhancedToolRunner


class TestEnhancedToolRunner:
    """Test cases for EnhancedToolRunner."""

    def test_init(self):
        """Test EnhancedToolRunner initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = EnhancedToolRunner(tmpdir)
            assert runner.project_path == Path(tmpdir).resolve()
            assert runner.config == {}
            assert runner.results == {}
            assert hasattr(runner, "quality_gate_manager")

    def test_init_with_config(self):
        """Test EnhancedToolRunner initialization with config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"tools": {"formatter": {"enabled": False}}}
            runner = EnhancedToolRunner(tmpdir, config)
            assert runner.config == config

    def test_can_proceed_to_ai_review_all_passed(self):
        """Test AI review can proceed when all tools pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = EnhancedToolRunner(tmpdir)
            # Mock results with all tools passing
            runner.results = {
                "formatter": {"success": True, "output": "All good"},
                "linter": {"success": True, "output": "All good"},
            }
            # Remove quality_gate_manager to force legacy mode
            delattr(runner, "quality_gate_manager")
            # In legacy mode, all tools must pass
            assert runner.can_proceed_to_ai_review() is True

    def test_can_proceed_to_ai_review_some_failed(self):
        """Test AI review cannot proceed when some tools fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = EnhancedToolRunner(tmpdir)
            # Mock results with some tools failing
            runner.results = {
                "formatter": {"success": True, "output": "All good"},
                "linter": {"success": False, "output": "Failed"},
            }
            # Remove quality_gate_manager to force legacy mode
            delattr(runner, "quality_gate_manager")
            # In legacy mode, all tools must pass
            assert runner.can_proceed_to_ai_review() is False

    def test_get_recovery_suggestions(self):
        """Test getting recovery suggestions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = EnhancedToolRunner(tmpdir)
            # Mock results with failed tools
            runner.results = {
                "formatter": {"success": False, "output": "Formatting issues found"},
                "linter": {"success": True, "output": "All good"},
            }
            suggestions = runner.get_recovery_suggestions()
            assert len(suggestions) == 1
            assert suggestions[0]["gate"] == "formatter"
            assert "black" in suggestions[0]["command"]
