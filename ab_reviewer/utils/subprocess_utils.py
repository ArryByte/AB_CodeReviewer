"""Subprocess utilities for AB Code Reviewer."""

import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Optional

from .exceptions import ToolExecutionError, ToolNotFoundError


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    timeout: int = 300,
    capture_output: bool = True
) -> Tuple[bool, str]:
    """
    Run a command and return success status and output.
    
    Args:
        cmd: Command to execute
        cwd: Working directory
        timeout: Timeout in seconds
        capture_output: Whether to capture output
        
    Returns:
        Tuple of (success, output)
        
    Raises:
        ToolExecutionError: If command execution fails
        ToolNotFoundError: If command not found
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        output = ""
        if capture_output:
            output = result.stdout + result.stderr
        
        success = result.returncode == 0
        return success, output
        
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out: {' '.join(cmd)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)
    except FileNotFoundError:
        tool_name = cmd[0] if cmd else "unknown"
        error_msg = f"Tool not found: {tool_name}. Please install it first."
        logger.error(error_msg)
        raise ToolNotFoundError(error_msg)
    except Exception as e:
        error_msg = f"Error running command: {str(e)}"
        logger.error(error_msg)
        raise ToolExecutionError(error_msg)


def check_tool_available(tool_name: str, timeout: int = 10) -> bool:
    """
    Check if a tool is available.
    
    Args:
        tool_name: Name of the tool to check
        timeout: Timeout in seconds
        
    Returns:
        True if tool is available, False otherwise
    """
    try:
        result = subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            timeout=timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
