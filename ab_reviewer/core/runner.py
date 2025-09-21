"""Tool execution orchestrator for AB Code Reviewer."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ..utils.exceptions import ToolExecutionError, ToolNotFoundError
from ..utils.subprocess_utils import run_command, check_tool_available


class ToolRunner:
    """Orchestrates execution of quality gate tools."""

    def __init__(self, project_path: str = ".", config: Optional[Dict[str, Any]] = None):
        """
        Initialize runner with project path and configuration.
        
        Args:
            project_path: Path to the project
            config: Configuration dictionary
        """
        self.project_path = Path(project_path).resolve()
        self.config = config or {}
        self.results = {}
        self.logger = logging.getLogger(__name__)

    def run_quality_gates(self) -> Dict[str, Any]:
        """
        Run all quality gates in sequence.
        
        Returns:
            Dictionary with tool results
        """
        print("🔍 Running quality gates...")
        
        gates = [
            ("formatter", self._run_formatter),
            ("linter", self._run_linter),
            ("security", self._run_security),
            ("tests", self._run_tests),
        ]
        
        for gate_name, gate_func in gates:
            if not self._is_tool_enabled(gate_name):
                print(f"⏭️  Skipping {gate_name} (disabled)")
                continue
                
            print(f"🔧 Running {gate_name}...")
            try:
                success, output = gate_func()
                
                self.results[gate_name] = {
                    "success": success,
                    "output": output,
                    "enabled": True,
                }
                
                if not success:
                    print(f"❌ {gate_name} failed")
                    return self.results
                else:
                    print(f"✅ {gate_name} passed")
            
            except Exception as e:
                print(f"❌ {gate_name} failed: {str(e)}")
                self.results[gate_name] = {
                    "success": False,
                    "output": f"Error: {str(e)}",
                    "enabled": True,
                }
                return self.results
        
        return self.results
    

    def _is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled in configuration."""
        return self.config.get("tools", {}).get(tool_name, {}).get("enabled", True)

    def _run_formatter(self) -> Tuple[bool, str]:
        """Run code formatter (black)."""
        tool_config = self.config.get("tools", {}).get("formatter", {})
        args = tool_config.get("args", ["--check", "--diff"])
        
        cmd = ["black"] + args + [str(self.project_path)]
        return run_command(cmd, cwd=self.project_path)

    def _run_linter(self) -> Tuple[bool, str]:
        """Run code linter (pylint)."""
        tool_config = self.config.get("tools", {}).get("linter", {})
        args = tool_config.get("args", ["--output-format=text", "--score=no"])
        
        # Find Python files to lint
        python_files = list(self.project_path.glob("**/*.py"))
        if not python_files:
            return True, "No Python files found to lint"
        
        cmd = ["pylint"] + args + [str(f) for f in python_files]
        return run_command(cmd, cwd=self.project_path)

    def _run_security(self) -> Tuple[bool, str]:
        """Run security scanner (bandit)."""
        tool_config = self.config.get("tools", {}).get("security", {})
        args = tool_config.get("args", ["-r", ".", "-f", "json"])
        
        cmd = ["bandit"] + args
        return run_command(cmd, cwd=self.project_path)

    def _run_tests(self) -> Tuple[bool, str]:
        """Run test suite (pytest)."""
        tool_config = self.config.get("tools", {}).get("tests", {})
        args = tool_config.get("args", ["--cov", "--cov-report=term-missing", "-v"])
        
        cmd = ["pytest"] + args
        return run_command(cmd, cwd=self.project_path)


    def get_failed_tools(self) -> List[str]:
        """Get list of tools that failed."""
        return [
            tool_name
            for tool_name, result in self.results.items()
            if not result.get("success", False)
        ]

    def all_tools_passed(self) -> bool:
        """Check if all enabled tools passed."""
        return not self.get_failed_tools()
