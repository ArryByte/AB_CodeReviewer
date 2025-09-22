"""Subprocess utilities for AB Code Reviewer."""

import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import shutil

from .exceptions import ToolExecutionError, ToolNotFoundError

logger = logging.getLogger(__name__)


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    timeout: int = 300,
    capture_output: bool = True,
) -> Tuple[bool, str]:
    """
    Run a command and return (success, output).

    - cmd: list of arguments (no shell=True)
    - returns: (True, combined_output) on returncode==0, else (False, combined_output)
    - raises ToolNotFoundError if binary is missing
    - raises ToolExecutionError for abnormal termination with non-zero exit if you prefer exceptions
    """
    if not cmd:
        raise ValueError("cmd must be a non-empty list")

    if shutil.which(cmd[0]) is None:
        raise ToolNotFoundError(f"Tool not found: {cmd[0]}")

    try:
        logger.debug("Running command: %s (cwd=%s)", " ".join(cmd), cwd)
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        output = ""
        if capture_output:
            output = (result.stdout or "") + (result.stderr or "")

        success = result.returncode == 0
        if not success:
            # Optionally raise an exception instead of returning False
            logger.debug("Command failed (code=%s): %s", result.returncode, output)
            return False, output

        return True, output

    except subprocess.TimeoutExpired as e:
        msg = f"Command timeout after {timeout}s: {' '.join(cmd)}"
        logger.exception(msg)
        raise ToolExecutionError(msg) from e
    except FileNotFoundError as e:
        msg = f"Command not found: {cmd[0]}"
        logger.exception(msg)
        raise ToolNotFoundError(msg) from e
    except Exception as e:
        msg = f"Unexpected error running command: {' '.join(cmd)}"
        logger.exception(msg)
        raise ToolExecutionError(msg) from e


def check_tool_available(tool_name: str, timeout: int = 5) -> bool:
    """
    Check tool availability using shutil.which and a lightweight '--version' call.
    """
    if shutil.which(tool_name) is None:
        return False
    try:
        result = subprocess.run(
            [tool_name, "--version"], capture_output=True, timeout=timeout, text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
