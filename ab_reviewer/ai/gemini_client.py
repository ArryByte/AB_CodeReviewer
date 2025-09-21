"""Gemini CLI integration for AB Code Reviewer."""

import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from ..utils.exceptions import AIReviewError, ToolNotFoundError, ToolExecutionError
from ..utils.subprocess_utils import run_command, check_tool_available
from ..utils.git import GitManager


class GeminiClient:
    """Client for interacting with Gemini CLI."""

    def __init__(self, project_path: str = "."):
        """
        Initialize Gemini client with project path.
        
        Args:
            project_path: Path to the project
        """
        self.project_path = Path(project_path).resolve()
        self.git_manager = GitManager(self.project_path)

    def is_available(self) -> bool:
        """
        Check if Gemini CLI is available.
        
        Returns:
            True if Gemini CLI is available, False otherwise
        """
        return check_tool_available("gemini")

    def run_review(
        self,
        tool_results: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Run AI review using Gemini CLI.
        
        Args:
            tool_results: Results from quality gate tools
            config: Configuration dictionary
            
        Returns:
            Tuple of (success, output)
            
        Raises:
            AIReviewError: If AI review fails
        """
        if not self.is_available():
            raise AIReviewError("Gemini CLI not found. Please install it first.")
        
        if not config.get("ai", {}).get("enabled", True):
            return True, "AI review disabled in configuration"
        
        try:
            # Prepare context
            context = self._prepare_context(tool_results, config)
            
            # Create temporary file with context
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(context)
                context_file = f.name
            
            try:
                # Run Gemini CLI
                cmd = [
                    "gemini",
                    "review",
                    "--context", context_file,
                    "--project", str(self.project_path)
                ]
                
                success, output = run_command(cmd, cwd=self.project_path, timeout=300)
                
                if success:
                    return True, output
                else:
                    raise AIReviewError(f"Gemini CLI error: {output}")
                    
            finally:
                # Clean up temporary file
                Path(context_file).unlink(missing_ok=True)
        
        except Exception as e:
            if isinstance(e, AIReviewError):
                raise
            raise AIReviewError(f"Failed to run AI review: {str(e)}")

    def _prepare_context(
        self,
        tool_results: Dict[str, Any],
        config: Dict[str, Any]
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
                output = result['output']
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
            self.logger.warning(f"Failed to get git diff: {str(e)}")
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
        except Exception:
            pass
        return None
