"""Enhanced Tool execution orchestration for AB Code Reviewer."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ..utils.exceptions import ToolExecutionError, ToolNotFoundError
from ..utils.subprocess_utils import run_command, check_tool_available
from .quality_gate import QualityGateManager, GateStatus


class EnhancedToolRunner:
    """Enhanced orchestrator for quality gate tools with progressive enhancement."""

    def __init__(
        self, project_path: str = ".", config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize enhanced runner with project path and configuration.

        Args:
            project_path: Path to the project
            config: Configuration dictionary
        """
        self.project_path = Path(project_path).resolve()
        self.config = config or {}
        self.results = {}
        self.logger = logging.getLogger(__name__)
        self.quality_gate_manager = QualityGateManager(self.project_path, config)

    def run_quality_gates(
        self, gate_names: Optional[List[str]] = None, progressive: bool = True
    ) -> Dict[str, Any]:
        """
        Run quality gates with progressive enhancement.

        Args:
            gate_names: Optional list of specific gates to run
            progressive: If True, continue running gates even if some fail

        Returns:
            Dictionary with results from each tool
        """
        print("🔍 Running quality gates...")

        if progressive:
            # Use enhanced quality gate manager for progressive execution
            gate_results = self.quality_gate_manager.run_all_gates(gate_names)

            # Convert to legacy format for compatibility
            self.results = {}
            for gate_name, result in gate_results.items():
                self.results[gate_name] = {
                    "success": result.status == GateStatus.SUCCESS,
                    "output": result.output,
                    "error": result.error,
                    "duration": result.duration,
                    "status": result.status.value,
                    "enabled": True,
                }

            # Print summary
            summary = self.quality_gate_manager.get_summary()
            print(f"\n📊 Quality Gates Summary:")
            print(f"  ✅ Successful: {summary['successful']}/{summary['total_gates']}")
            print(f"  ❌ Failed: {summary['failed']}")
            print(f"  ⏭️  Skipped: {summary['skipped']}")
            print(f"  📈 Success Rate: {summary['success_rate']:.1f}%")

        else:
            # Use legacy sequential execution (all-or-nothing)
            self.results = self._run_legacy_quality_gates(gate_names)

        return self.results

    def _run_legacy_quality_gates(
        self, gate_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run quality gates in legacy mode (all-or-nothing)."""
        gates = [
            ("formatter", self._run_formatter),
            ("linter", self._run_linter),
            ("security", self._run_security),
            ("tests", self._run_tests),
        ]

        # Filter gates if specific ones requested
        if gate_names:
            gates = [(name, func) for name, func in gates if name in gate_names]

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

    def can_proceed_to_ai_review(self) -> bool:
        """Check if we can proceed to AI review based on quality gate results."""
        if hasattr(self, "quality_gate_manager"):
            summary = self.quality_gate_manager.get_summary()
            return summary["can_proceed_to_ai"]
        else:
            # Legacy mode: all tools must pass
            return self.all_tools_passed()

    def get_ai_context(self) -> Dict[str, Any]:
        """Get context for AI review from quality gate results."""
        if hasattr(self, "quality_gate_manager"):
            return self.quality_gate_manager.get_ai_context()
        else:
            # Legacy mode: return all results
            return {
                "available_results": {
                    name: {"output": result["output"]}
                    for name, result in self.results.items()
                    if result.get("success", False)
                },
                "failed_gates": [
                    {"name": name, "error": result.get("output", "Unknown error")}
                    for name, result in self.results.items()
                    if not result.get("success", False)
                ],
                "skipped_gates": [],
            }

    def get_failed_gates(self) -> List[str]:
        """Get list of failed quality gates."""
        return [
            name
            for name, result in self.results.items()
            if not result.get("success", False)
        ]

    def get_successful_gates(self) -> List[str]:
        """Get list of successful quality gates."""
        return [
            name
            for name, result in self.results.items()
            if result.get("success", False)
        ]

    def get_recovery_suggestions(self) -> List[Dict[str, str]]:
        """Get recovery suggestions for failed gates."""
        suggestions = []

        for gate_name, result in self.results.items():
            if not result.get("success", False):
                if gate_name == "formatter":
                    suggestions.append(
                        {
                            "gate": gate_name,
                            "suggestion": "Run 'black .' to fix formatting issues",
                            "command": "black .",
                            "priority": "high",
                        }
                    )
                elif gate_name == "linter":
                    suggestions.append(
                        {
                            "gate": gate_name,
                            "suggestion": "Review and fix pylint warnings",
                            "command": "pylint .",
                            "priority": "medium",
                        }
                    )
                elif gate_name == "security":
                    suggestions.append(
                        {
                            "gate": gate_name,
                            "suggestion": "Address security vulnerabilities found by bandit",
                            "command": "bandit -r .",
                            "priority": "high",
                        }
                    )
                elif gate_name == "tests":
                    suggestions.append(
                        {
                            "gate": gate_name,
                            "suggestion": "Fix failing tests",
                            "command": "pytest -v",
                            "priority": "medium",
                        }
                    )

        return suggestions

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
