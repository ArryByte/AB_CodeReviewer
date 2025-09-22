"""Python-specific tool integrations for AB Code Reviewer."""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

from ..utils.exceptions import ToolNotFoundError, ToolExecutionError, ValidationError
from ..utils.subprocess_utils import run_command, check_tool_available


class PythonTools:
    """Manages Python-specific code quality tools."""

    def __init__(self, project_path: str = "."):
        """
        Initialize with project path.

        Args:
            project_path: Path to the project

        Raises:
            ValidationError: If project path is invalid
        """
        self.project_path = Path(project_path).resolve()

        # Validate project path
        if not self.project_path.exists():
            raise ValidationError(f"Project path does not exist: {self.project_path}")
        if not self.project_path.is_dir():
            raise ValidationError(
                f"Project path is not a directory: {self.project_path}"
            )

    def install_tools(self) -> bool:
        """
        Install required Python tools if not present.

        Returns:
            True if installation successful, False otherwise

        Raises:
            ToolExecutionError: If installation fails
        """
        tools = ["black", "pylint", "bandit", "pytest", "pytest-cov"]
        missing_tools = []

        for tool in tools:
            if not check_tool_available(tool):
                missing_tools.append(tool)

        if not missing_tools:
            return True

        print(f"📦 Installing missing tools: {', '.join(missing_tools)}")

        # Install tools using pip
        cmd = [sys.executable, "-m", "pip", "install"] + missing_tools
        success, output = run_command(cmd, timeout=120)

        if success:
            print("✅ Tools installed successfully")
            return True
        else:
            print(f"❌ Failed to install tools: {output}")
            raise ToolExecutionError(f"Failed to install tools: {output}")

    def get_tool_versions(self) -> Dict[str, str]:
        """Get versions of installed tools."""
        tools = ["black", "pylint", "bandit", "pytest"]
        versions = {}

        for tool in tools:
            try:
                result = subprocess.run(
                    [tool, "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    versions[tool] = result.stdout.strip()
                else:
                    versions[tool] = "Not installed"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                versions[tool] = "Not installed"

        return versions

    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate that the Python environment is ready.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")

        # Check if we're in a virtual environment (recommended)
        if not self._is_virtual_environment():
            issues.append("Not in a virtual environment (recommended)")

        # Check for required tools
        missing_tools = []
        tools = ["black", "pylint", "bandit", "pytest"]
        for tool in tools:
            if not check_tool_available(tool):
                missing_tools.append(tool)

        if missing_tools:
            issues.append(f"Missing tools: {', '.join(missing_tools)}")

        return len(issues) == 0, issues

    def _is_virtual_environment(self) -> bool:
        """Check if we're running in a virtual environment."""
        return (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
            or os.environ.get("VIRTUAL_ENV") is not None
        )

    def setup_project(self) -> bool:
        """
        Set up project-specific configurations.

        Returns:
            True if setup successful, False otherwise

        Raises:
            ToolExecutionError: If setup fails
        """
        try:
            # Create .ab-reviewer.yaml if it doesn't exist
            config_file = self.project_path / ".ab-reviewer.yaml"
            if not config_file.exists():
                self._create_default_config(config_file)

            # Create .gitignore entries if needed
            self._update_gitignore()

            return True
        except Exception as e:
            error_msg = f"Error setting up project: {str(e)}"
            print(f"❌ {error_msg}")
            raise ToolExecutionError(error_msg)

    def _create_default_config(self, config_file: Path) -> None:
        """
        Create a default .ab-reviewer.yaml file.

        Args:
            config_file: Path to the configuration file
        """
        default_config = """# AB Code Reviewer Configuration
# Override only what you need to change from defaults

tools:
  linter:
    args: ["--max-line-length=88", "--output-format=text", "--score=no"]
  security:
    args: ["-r", ".", "-f", "json", "-ll"]
  tests:
    args: ["--cov", "--cov-report=term-missing", "-v"]

ai:
  enabled: true
  context:
    include_git_diff: true
    include_test_results: true
    max_context_lines: 1000
"""
        config_file.write_text(default_config, encoding="utf-8")
        print(f"📝 Created default config: {config_file}")

    def _update_gitignore(self) -> None:
        """Update .gitignore with AB Reviewer specific entries."""
        gitignore_file = self.project_path / ".gitignore"
        entries_to_add = [
            "# AB Code Reviewer",
            "review_report.md",
        ]

        try:
            if gitignore_file.exists():
                content = gitignore_file.read_text(encoding="utf-8")
                for entry in entries_to_add:
                    if entry not in content:
                        content += f"\n{entry}"
                gitignore_file.write_text(content, encoding="utf-8")
            else:
                gitignore_file.write_text("\n".join(entries_to_add), encoding="utf-8")
        except Exception as e:
            pass  # Ignore gitignore update failures
