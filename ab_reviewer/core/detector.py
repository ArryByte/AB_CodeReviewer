"""Project type detection for AB Code Reviewer."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from ..utils.exceptions import ProjectDetectionError
from ..utils.validation import validate_project_path


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
        self.logger = logging.getLogger(__name__)
        
        # Validate project path
        try:
            validate_project_path(self.project_path)
        except Exception as e:
            raise ProjectDetectionError(f"Invalid project path: {str(e)}")

    def detect_project_type(self) -> str:
        """
        Detect the project type based on files present.
        
        Returns:
            Project type string ("python", "java", "go", "unknown")
            
        Raises:
            ProjectDetectionError: If detection fails
        """
        try:
            self.logger.debug(f"Detecting project type in: {self.project_path}")
            
            if self._is_python_project():
                self.logger.info("Detected Python project")
                return "python"
            elif self._is_java_project():
                self.logger.info("Detected Java project")
                return "java"
            elif self._is_go_project():
                self.logger.info("Detected Go project")
                return "go"
            else:
                self.logger.warning("Unknown project type")
                return "unknown"
        
        except Exception as e:
            error_msg = f"Failed to detect project type: {str(e)}"
            self.logger.error(error_msg)
            raise ProjectDetectionError(error_msg)

    def _is_python_project(self) -> bool:
        """Check if this is a Python project."""
        python_indicators = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
        ]
        
        for indicator in python_indicators:
            if (self.project_path / indicator).exists():
                self.logger.debug(f"Found Python indicator: {indicator}")
                return True
        
        # Check for Python files in root
        python_files = list(self.project_path.glob("*.py"))
        if python_files:
            self.logger.debug(f"Found {len(python_files)} Python files in root")
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
                self.logger.debug(f"Found Java indicator: {indicator}")
                return True
        
        # Check for Java files
        java_files = list(self.project_path.glob("**/*.java"))
        if java_files:
            self.logger.debug(f"Found {len(java_files)} Java files")
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
                self.logger.debug(f"Found Go indicator: {indicator}")
                return True
        
        # Check for Go files
        go_files = list(self.project_path.glob("**/*.go"))
        if go_files:
            self.logger.debug(f"Found {len(go_files)} Go files")
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
                
            self.logger.debug(f"Project info: {info}")
            return info
        
        except Exception as e:
            error_msg = f"Failed to get project info: {str(e)}"
            self.logger.error(error_msg)
            raise ProjectDetectionError(error_msg)

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
                self.logger.debug(f"Found virtual environment: {venv_path}")
                break
        
        # Check for Python version files
        if (self.project_path / ".python-version").exists():
            info["python_version_file"] = True
            self.logger.debug("Found .python-version file")
        
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
        elif (self.project_path / "build.gradle").exists() or (self.project_path / "build.gradle.kts").exists():
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
