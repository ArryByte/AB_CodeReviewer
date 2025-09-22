"""Enhanced Quality Gate Management System."""

import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..utils.exceptions import ToolExecutionError
from ..utils.subprocess_utils import run_command, check_tool_available
from .gate_types import QualityGateConfig, QualityGateResult, GateStatus
from .config_loader import ConfigLoader


class QualityGateManager:
    """Manages quality gate execution with progressive enhancement."""

    def __init__(
        self,
        project_path: Path,
        config: Optional[Dict] = None,
        config_path: Optional[Path] = None,
    ):
        """
        Initialize quality gate manager.

        Args:
            project_path: Path to the project
            config: Optional configuration overrides (legacy support)
            config_path: Path to configuration file
        """
        self.project_path = project_path
        self.config = config or {}
        self.config_loader = ConfigLoader(config_path)
        self.results: Dict[str, QualityGateResult] = {}

        # Load quality gates from configuration
        self.gates = self.config_loader.get_quality_gate_configs()

    def check_tool_availability(self, gate_config: QualityGateConfig) -> bool:
        """Check if a tool is available."""
        if not gate_config.check_available:
            return True

        tool_name = gate_config.command[0]
        return check_tool_available(tool_name)

    def install_tool(self, gate_config: QualityGateConfig) -> bool:
        """Install a tool if auto_install is enabled."""
        if not gate_config.auto_install or not gate_config.install_command:
            return False

        try:
            success, output = run_command(
                gate_config.install_command,
                cwd=str(self.project_path),
                timeout=300,
                tool_name=f"Install {gate_config.name}",
            )
            return success
        except Exception:
            return False

    def run_single_gate(
        self, gate_name: str, gate_config: QualityGateConfig
    ) -> QualityGateResult:
        """Run a single quality gate."""
        start_time = time.time()

        # Check tool availability
        if not self.check_tool_availability(gate_config):
            if gate_config.auto_install:
                if not self.install_tool(gate_config):
                    return QualityGateResult(
                        tool_name=gate_name,
                        status=GateStatus.SKIPPED,
                        error=f"Failed to install {gate_name}",
                        duration=time.time() - start_time,
                    )
            else:
                return QualityGateResult(
                    tool_name=gate_name,
                    status=GateStatus.SKIPPED,
                    error=f"Tool {gate_name} not available and auto_install disabled",
                    duration=time.time() - start_time,
                )

        # Run the quality gate
        try:
            success, output = run_command(
                gate_config.command, cwd=self.project_path, timeout=gate_config.timeout
            )

            # Determine success based on criteria
            if gate_config.success_criteria:
                try:
                    is_success = gate_config.success_criteria(output)
                except Exception:
                    # If criteria evaluation fails, fall back to command success
                    is_success = success
            else:
                is_success = success

            status = GateStatus.SUCCESS if is_success else GateStatus.FAILED

            return QualityGateResult(
                tool_name=gate_name,
                status=status,
                output=output,
                duration=time.time() - start_time,
                metadata={"command": gate_config.command},
            )

        except ToolExecutionError as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower():
                status = GateStatus.TIMEOUT
            else:
                status = GateStatus.FAILED

            return QualityGateResult(
                tool_name=gate_name,
                status=status,
                error=error_msg,
                duration=time.time() - start_time,
            )
        except Exception as e:
            return QualityGateResult(
                tool_name=gate_name,
                status=GateStatus.FAILED,
                error=f"Unexpected error: {str(e)}",
                duration=time.time() - start_time,
            )

    def run_all_gates(
        self, gate_names: Optional[List[str]] = None
    ) -> Dict[str, QualityGateResult]:
        """
        Run all quality gates with progressive enhancement.

        Args:
            gate_names: Optional list of specific gates to run

        Returns:
            Dictionary of gate results
        """
        gates_to_run = gate_names or list(self.gates.keys())
        self.results = {}

        for gate_name in gates_to_run:
            if gate_name not in self.gates:
                continue

            gate_config = self.gates[gate_name]
            print(f"🔧 Running {gate_name}...")

            result = self.run_single_gate(gate_name, gate_config)
            self.results[gate_name] = result

            # Print status
            if result.status == GateStatus.SUCCESS:
                print(f"✅ {gate_name} passed")
            elif result.status == GateStatus.FAILED:
                print(f"❌ {gate_name} failed")
            elif result.status == GateStatus.SKIPPED:
                print(f"⏭️  {gate_name} skipped: {result.error}")
            elif result.status == GateStatus.TIMEOUT:
                print(f"⏰ {gate_name} timed out")

        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of quality gate results."""
        total = len(self.results)
        successful = sum(
            1 for r in self.results.values() if r.status == GateStatus.SUCCESS
        )
        failed = sum(1 for r in self.results.values() if r.status == GateStatus.FAILED)
        skipped = sum(
            1 for r in self.results.values() if r.status == GateStatus.SKIPPED
        )

        return {
            "total_gates": total,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "can_proceed_to_ai": successful > 0,  # Can proceed if any gate succeeded
            "results": {
                name: {
                    "status": result.status.value,
                    "duration": result.duration,
                    "error": result.error,
                }
                for name, result in self.results.items()
            },
        }

    def get_ai_context(self) -> Dict[str, Any]:
        """Get context for AI review from successful gates."""
        context = {"available_results": {}, "failed_gates": [], "skipped_gates": []}

        for name, result in self.results.items():
            if result.status == GateStatus.SUCCESS:
                context["available_results"][name] = {
                    "output": result.output,
                    "duration": result.duration,
                }
            elif result.status == GateStatus.FAILED:
                context["failed_gates"].append(
                    {"name": name, "error": result.error, "output": result.output}
                )
            elif result.status == GateStatus.SKIPPED:
                context["skipped_gates"].append({"name": name, "reason": result.error})

        return context
