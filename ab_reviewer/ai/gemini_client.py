"""Gemini CLI integration for AB Code Reviewer."""

import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager

from ..utils.exceptions import AIReviewError
from ..utils.subprocess_utils import run_command, check_tool_available
from ..utils.git import GitManager


class GeminiClient:
    """Client for interacting with Gemini CLI."""

    def __init__(self, project_path: str = ".", dry_run: bool = False):
        """
        Initialize Gemini client with project path.

        Args:
            project_path: Path to the project
            dry_run: If True, skip actual Gemini CLI calls (for testing)
        """
        self.project_path = Path(project_path).resolve()
        self.git_manager = GitManager(self.project_path)
        self.logger = logging.getLogger(__name__)
        self.dry_run = dry_run
        self.max_retries = 3
        self.retry_delay = 1.0

    @contextmanager
    def _safe_temp_file(self, suffix: str = ".json", mode: str = "w+"):
        """Context manager for safe temporary file handling."""
        tf_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode=mode, delete=False, suffix=suffix, encoding="utf-8"
            ) as tf:
                tf_path = Path(tf.name)
                yield tf, tf_path
        finally:
            if tf_path and tf_path.exists():
                try:
                    tf_path.unlink()
                except Exception as e:
                    self.logger.exception("Failed to cleanup temp file %s", tf_path)

    def is_available(self) -> bool:
        """
        Check if Gemini CLI is available.

        Returns:
            True if Gemini CLI is available, False otherwise
        """
        return check_tool_available("gemini")

    def run_review(
        self, tool_results: Dict[str, Any], config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Run AI review using Gemini CLI with retry logic and safe temp file handling.

        Args:
            tool_results: Results from quality gate tools
            config: Configuration dictionary

        Returns:
            Tuple of (success, output)

        Raises:
            AIReviewError: If AI review fails
        """
        if self.dry_run:
            self.logger.info("Dry run mode: skipping Gemini CLI call")
            return True, "AI review skipped (dry run mode)"

        if not self.is_available():
            raise AIReviewError("Gemini CLI not found. Please install it first.")

        if not config.get("ai", {}).get("enabled", True):
            return True, "AI review disabled in configuration"

        # Prepare context
        context = self._prepare_context(tool_results, config)

        # Retry logic for robustness
        last_error = None
        for attempt in range(self.max_retries):
            try:
                with self._safe_temp_file(suffix=".json", mode="w+") as (tf, tf_path):
                    # Create structured payload for better parsing
                    payload = {
                        "prompt": "Please review this code and provide feedback:",
                        "context": context,
                        "project_path": str(self.project_path),
                        "format": "json",
                        "attempt": attempt + 1,
                    }
                    json.dump(payload, tf, indent=2)
                    tf.flush()

                    # Use secure command with input file
                    cmd = [
                        "gemini",
                        "review",
                        "--input",
                        str(tf_path),
                        "--format",
                        "json",
                    ]
                    success, output = run_command(
                        cmd, cwd=self.project_path, timeout=120
                    )

                    if not success:
                        raise AIReviewError(f"Gemini CLI failed: {output}")

                    # Try to parse JSON response, fallback to raw text
                    try:
                        parsed = json.loads(output)
                        return True, json.dumps(parsed, indent=2)
                    except json.JSONDecodeError:
                        # Fallback to raw text if not JSON
                        return True, output

            except Exception as e:
                last_error = e
                self.logger.warning("Attempt %d failed: %s", attempt + 1, str(e))

                if attempt < self.max_retries - 1:
                    self.logger.info("Retrying in %.1f seconds...", self.retry_delay)
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    break

        # All retries failed
        if isinstance(last_error, AIReviewError):
            raise last_error
        raise AIReviewError(
            f"Failed to run AI review after {self.max_retries} attempts: {str(last_error)}"
        ) from last_error

    def _prepare_context(
        self, tool_results: Dict[str, Any], config: Dict[str, Any]
    ) -> str:
        """
        Prepare context for AI review.

        Args:
            tool_results: Results from quality gate tools
            config: Configuration dictionary

        Returns:
            Formatted context string
        """
        context_parts = []

        # Project information
        context_parts.append("# Project Context")
        context_parts.append(f"Project Path: {self.project_path}")
        context_parts.append("")

        # Quality gate results
        context_parts.append("# Quality Gate Results")
        for tool_name, result in tool_results.items():
            status = "PASSED" if result.get("success") else "FAILED"
            context_parts.append(f"{tool_name.upper()}: {status}")

            if result.get("output"):
                # Limit output size
                output = result["output"]
                if len(output) > 500:
                    output = output[:500] + "..."
                context_parts.append(f"Output: {output}")
            context_parts.append("")

        # Git diff if enabled
        if config.get("ai", {}).get("context", {}).get("include_git_diff", True):
            try:
                git_diff = self.git_manager.get_git_diff()
                if git_diff:
                    context_parts.append("# Recent Changes (Git Diff)")
                    # Limit diff size
                    if len(git_diff) > 2000:
                        git_diff = git_diff[:2000] + "\n... (truncated)"
                    context_parts.append(git_diff)
                    context_parts.append("")
            except Exception:
                pass  # Ignore git diff failures

        # Test results if enabled
        if config.get("ai", {}).get("context", {}).get("include_test_results", True):
            test_output = tool_results.get("tests", {}).get("output", "")
            if test_output:
                context_parts.append("# Test Results")
                # Limit test output size
                if len(test_output) > 1000:
                    test_output = test_output[:1000] + "..."
                context_parts.append(test_output)
                context_parts.append("")

        # Review instructions
        context_parts.append("# Review Instructions")
        context_parts.append("Please provide a focused code review covering:")
        context_parts.append("- Architecture and design patterns")
        context_parts.append("- Code readability and maintainability")
        context_parts.append("- Potential edge cases or bugs")
        context_parts.append("- Performance considerations")
        context_parts.append("- Security implications")
        context_parts.append("")
        context_parts.append("Focus on high-value feedback since basic quality issues")
        context_parts.append("have already been caught by the automated tools.")

        return "\n".join(context_parts)

    def _get_git_diff(self) -> Optional[str]:
        """
        Get git diff of recent changes.

        Returns:
            Git diff string or None if no changes
        """
        try:
            return self.git_manager.get_git_diff()
        except Exception as e:
            self.logger.warning("Failed to get git diff: %s", str(e))
            return None

    def get_version(self) -> Optional[str]:
        """
        Get Gemini CLI version.

        Returns:
            Version string or None if not available
        """
        try:
            success, output = run_command(["gemini", "--version"], timeout=10)
            if success:
                return output.strip()
        except Exception as e:
            self.logger.warning("Failed to get Gemini CLI version: %s", e)
        return None

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the Gemini CLI.

        Returns:
            Dictionary with health status and details
        """
        health_status = {
            "available": False,
            "version": None,
            "error": None,
            "timestamp": None,
        }

        try:
            # Check if tool is available
            if not self.is_available():
                health_status["error"] = "Gemini CLI not found in PATH"
                return health_status

            # Get version
            version = self.get_version()
            health_status["version"] = version
            health_status["available"] = True

        except Exception as e:
            health_status["error"] = str(e)
            self.logger.exception("Health check failed")

        return health_status
