"""Project analysis utilities for AB Code Reviewer."""

import json
from pathlib import Path
from typing import Dict, Any


class ProjectAnalyzer:
    """Analyzes project structure and dependencies."""

    def __init__(self, project_path: Path):
        """
        Initialize project analyzer.

        Args:
            project_path: Path to the project
        """
        self.project_path = project_path.resolve()

    def analyze_structure(self) -> Dict[str, Any]:
        """
        Analyze project structure.

        Returns:
            Dictionary with project analysis results
        """
        analysis = {
            "project_path": str(self.project_path),
            "project_name": self.project_path.name,
            "analysis_timestamp": self._get_timestamp(),
            "file_structure": self._analyze_file_structure(),
            "python_files": self._find_python_files(),
            "dependencies": self._analyze_dependencies(),
            "project_indicators": self._find_project_indicators(),
            "git_info": self._analyze_git_info(),
            "estimated_complexity": self._estimate_complexity(),
        }

        return analysis

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze file structure."""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "directory_structure": [],
        }

        for item in self.project_path.rglob("*"):
            if item.is_file():
                structure["total_files"] += 1
                ext = item.suffix.lower()
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
            elif item.is_dir():
                structure["total_directories"] += 1

        # Get top-level directory structure
        for item in sorted(self.project_path.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                structure["directory_structure"].append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "files": (
                            len(list(item.rglob("*.py")))
                            if item.name in ["app", "src", "backend", "frontend"]
                            else 0
                        ),
                    }
                )
            elif item.is_file() and not item.name.startswith("."):
                structure["directory_structure"].append(
                    {"name": item.name, "type": "file", "size": item.stat().st_size}
                )

        return structure

    def _find_python_files(self) -> Dict[str, Any]:
        """Find and analyze Python files."""
        python_files = list(self.project_path.rglob("*.py"))

        analysis = {
            "total_python_files": len(python_files),
            "files_by_directory": {},
            "largest_files": [],
            "recent_files": [],
        }

        # Group by directory
        for py_file in python_files:
            rel_path = py_file.relative_to(self.project_path)
            dir_name = str(rel_path.parent) if rel_path.parent != Path(".") else "root"

            if dir_name not in analysis["files_by_directory"]:
                analysis["files_by_directory"][dir_name] = []

            file_info = {
                "name": py_file.name,
                "path": str(rel_path),
                "size": py_file.stat().st_size,
                "modified": py_file.stat().st_mtime,
            }
            analysis["files_by_directory"][dir_name].append(file_info)

        # Find largest files
        largest_files = sorted(
            python_files, key=lambda f: f.stat().st_size, reverse=True
        )[:10]
        for py_file in largest_files:
            analysis["largest_files"].append(
                {
                    "path": str(py_file.relative_to(self.project_path)),
                    "size": py_file.stat().st_size,
                    "lines": self._count_lines(py_file),
                }
            )

        return analysis

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return len(f.readlines())
        except Exception:
            return 0

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            "requirements_files": [],
            "detected_tools": [],
            "python_version": None,
        }

        # Look for requirements files
        req_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "poetry.lock",
        ]

        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                dependencies["requirements_files"].append(
                    {
                        "name": req_file,
                        "path": str(req_path),
                        "size": req_path.stat().st_size,
                    }
                )

        # Detect common tools
        common_tools = [
            "black",
            "pylint",
            "flake8",
            "mypy",
            "bandit",
            "pytest",
            "coverage",
        ]
        for tool in common_tools:
            # This is a simple check - in real implementation, you'd check if tools are installed
            dependencies["detected_tools"].append(
                {"name": tool, "likely_used": self._check_tool_usage(tool)}
            )

        return dependencies

    def _check_tool_usage(self, tool: str) -> bool:
        """Check if a tool is likely used in the project."""
        # Check for tool-specific files
        tool_files = {
            "black": [".black", "pyproject.toml"],
            "pylint": [".pylintrc", "pylint.cfg"],
            "flake8": [".flake8", "setup.cfg"],
            "mypy": ["mypy.ini", ".mypy.ini"],
            "pytest": ["pytest.ini", "conftest.py"],
            "coverage": [".coveragerc", "coverage.ini"],
        }

        if tool in tool_files:
            for file_name in tool_files[tool]:
                if (self.project_path / file_name).exists():
                    return True

        return False

    def _find_project_indicators(self) -> Dict[str, Any]:
        """Find project type indicators."""
        indicators = {
            "python_indicators": [],
            "framework_indicators": [],
            "build_tools": [],
            "deployment_files": [],
        }

        # Python indicators
        python_indicators = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "MANIFEST.in",
        ]

        for indicator in python_indicators:
            if (self.project_path / indicator).exists():
                indicators["python_indicators"].append(indicator)

        # Framework indicators
        framework_files = {
            "django": ["manage.py", "settings.py"],
            "flask": ["app.py", "application.py"],
            "fastapi": ["main.py", "app.py"],
            "streamlit": ["app.py", "main.py"],
        }

        for framework, files in framework_files.items():
            for file_name in files:
                if list(self.project_path.rglob(file_name)):
                    indicators["framework_indicators"].append(framework)
                    break

        # Build tools
        build_tools = ["Makefile", "docker-compose.yml", "Dockerfile", "Jenkinsfile"]
        for tool in build_tools:
            if (self.project_path / tool).exists():
                indicators["build_tools"].append(tool)

        return indicators

    def _analyze_git_info(self) -> Dict[str, Any]:
        """Analyze git repository information."""
        git_info = {
            "is_git_repo": (self.project_path / ".git").exists(),
            "gitignore_exists": (self.project_path / ".gitignore").exists(),
            "git_attributes_exists": (self.project_path / ".gitattributes").exists(),
        }

        if git_info["is_git_repo"]:
            # Try to get git information
            try:
                import subprocess

                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_info["current_branch"] = result.stdout.strip()
            except Exception:
                pass

        return git_info

    def _estimate_complexity(self) -> Dict[str, Any]:
        """Estimate project complexity."""
        python_files = list(self.project_path.rglob("*.py"))
        total_lines = sum(self._count_lines(f) for f in python_files)

        complexity = {
            "total_python_files": len(python_files),
            "total_lines_of_code": total_lines,
            "average_file_size": total_lines / len(python_files) if python_files else 0,
            "complexity_level": "low",
        }

        # Determine complexity level
        if total_lines > 10000:
            complexity["complexity_level"] = "high"
        elif total_lines > 1000:
            complexity["complexity_level"] = "medium"

        return complexity

    def save_analysis(self, output_dir: Path) -> Path:
        """
        Save analysis results to file.

        Args:
            output_dir: Directory to save analysis

        Returns:
            Path to saved analysis file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        analysis = self.analyze_structure()
        analysis_file = output_dir / "project_analysis.json"

        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)

        return analysis_file
