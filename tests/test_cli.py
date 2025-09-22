"""Tests for CLI interface."""

import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

from ab_reviewer.cli import main, load_configuration, merge_configs


class TestCLI:
    """Test cases for CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AB Code Reviewer" in result.output

    def test_merge_configs(self):
        """Test configuration merging."""
        default = {
            "tools": {"linter": {"enabled": True, "args": ["--max-line-length=88"]}}
        }

        override = {"tools": {"linter": {"args": ["--max-line-length=100"]}}}

        merged = merge_configs(default, override)

        assert merged["tools"]["linter"]["enabled"] is True
        assert merged["tools"]["linter"]["args"] == ["--max-line-length=100"]

    def test_load_configuration_with_defaults(self):
        """Test loading default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_configuration(None, Path(tmpdir))

            assert "project" in config
            assert "tools" in config
            assert "ai" in config
            assert config["project"]["type"] == "python"

    def test_load_configuration_with_custom_file(self):
        """Test loading custom configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create custom config
            config_file = Path(tmpdir) / "custom.yaml"
            config_file.write_text(
                """
project:
  type: python
tools:
  linter:
    enabled: false
"""
            )

            config = load_configuration(config_file, Path(tmpdir))

            assert config["tools"]["linter"]["enabled"] is False
