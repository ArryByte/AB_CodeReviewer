"""Quality gate types and configurations."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Callable


class GateStatus(Enum):
    """Quality gate execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class QualityGateResult:
    """Result of a quality gate execution."""

    tool_name: str
    status: GateStatus
    output: str = ""
    error: str = ""
    duration: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QualityGateConfig:
    """Configuration for a quality gate."""

    name: str
    command: list
    timeout: int = 300
    required: bool = True
    auto_install: bool = True
    install_command: list = None
    check_available: bool = True
    success_criteria: Callable[[str], bool] = None
