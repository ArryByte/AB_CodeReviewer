"""Project type detection for AB Code Reviewer."""

from pathlib import Path
from typing import Dict, Any

from ..utils.exceptions import ProjectDetectionError


class ProjectDetector:
    """Detects project type and configuration."""

    def __init__(self, project_path: str = "."):
        """
        Initialize detector with project path.

        Args:
            project_path: Path to the project directory

        Raises:
            ProjectDetectionError: If project path is invalid
        """
        self.project_path = Path(project_path).resolve()

        # Validate project path
        if not self.project_path.exists():
            raise ProjectDetectionError(
                f"Project path does not exist: {self.project_path}"
            )
        if not self.project_path.is_dir():
            raise ProjectDetectionError(
                f"Project path is not a directory: {self.project_path}"
            )

    def detect_project_type(self) -> str:
        """
        Detect the project type based on files present.

        Returns:
            Project type string ("python", "java", "go", "unknown")

        Raises:
            ProjectDetectionError: If detection fails
        """
        try:
            if self._is_python_project():
                return "python"
            elif self._is_java_project():
                return "java"
            elif self._is_go_project():
                return "go"
            else:
                return "unknown"

        except Exception as e:
            raise ProjectDetectionError(f"Failed to detect project type: {str(e)}")

    def _is_python_project(self) -> bool:
        """Check if this is a Python project."""
        python_indicators = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
        ]

        # Check for indicators in root directory
        for indicator in python_indicators:
            if (self.project_path / indicator).exists():
                return True

        # Check for indicators in subdirectories (up to 2 levels deep)
        for indicator in python_indicators:
            if list(self.project_path.glob(f"*/{indicator}")) or list(
                self.project_path.glob(f"*/*/{indicator}")
            ):
                return True

        # Check for Python files in root
        python_files = list(self.project_path.glob("*.py"))
        if python_files:
            return True

        # Check for Python files in subdirectories (up to 2 levels deep)
        python_files = list(self.project_path.glob("**/*.py"))
        if python_files:
            return True

        return False

    def _is_java_project(self) -> bool:
        """Check if this is a Java project."""
        java_indicators = [
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
        ]

        for indicator in java_indicators:
            if (self.project_path / indicator).exists():
                return True

        # Check for Java files
        java_files = list(self.project_path.glob("**/*.java"))
        if java_files:
            return True

        return False

    def _is_go_project(self) -> bool:
        """Check if this is a Go project."""
        go_indicators = [
            "go.mod",
            "Gopkg.toml",
        ]

        for indicator in go_indicators:
            if (self.project_path / indicator).exists():
                return True

        # Check for Go files
        go_files = list(self.project_path.glob("**/*.go"))
        if go_files:
            return True

        return False

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get comprehensive project information.

        Returns:
            Dictionary with project information

        Raises:
            ProjectDetectionError: If project info cannot be gathered
        """
        try:
            project_type = self.detect_project_type()

            info = {
                "type": project_type,
                "path": str(self.project_path),
                "is_git_repo": self._is_git_repository(),
            }

            if project_type == "python":
                info.update(self._get_python_info())
            elif project_type == "java":
                info.update(self._get_java_info())
            elif project_type == "go":
                info.update(self._get_go_info())

            return info

        except Exception as e:
            raise ProjectDetectionError(f"Failed to get project info: {str(e)}")

    def _is_git_repository(self) -> bool:
        """Check if this is a git repository."""
        return (self.project_path / ".git").exists()

    def _get_python_info(self) -> Dict[str, Any]:
        """Get Python-specific project information."""
        info = {}

        # Check for virtual environment
        venv_paths = [
            self.project_path / "venv",
            self.project_path / ".venv",
            self.project_path / "env",
        ]

        for venv_path in venv_paths:
            if venv_path.exists():
                info["virtual_env"] = str(venv_path)
                break

        # Check for Python version files
        if (self.project_path / ".python-version").exists():
            info["python_version_file"] = True

        # Check for Python files count
        python_files = list(self.project_path.glob("**/*.py"))
        info["python_file_count"] = len(python_files)

        return info

    def _get_java_info(self) -> Dict[str, Any]:
        """Get Java-specific project information."""
        info = {}

        # Check for build files
        if (self.project_path / "pom.xml").exists():
            info["build_system"] = "maven"
        elif (self.project_path / "build.gradle").exists() or (
            self.project_path / "build.gradle.kts"
        ).exists():
            info["build_system"] = "gradle"

        # Check for Java files count
        java_files = list(self.project_path.glob("**/*.java"))
        info["java_file_count"] = len(java_files)

        return info

    def _get_go_info(self) -> Dict[str, Any]:
        """Get Go-specific project information."""
        info = {}

        # Check for Go modules
        if (self.project_path / "go.mod").exists():
            info["go_modules"] = True

        # Check for Go files count
        go_files = list(self.project_path.glob("**/*.go"))
        info["go_file_count"] = len(go_files)

        return info
