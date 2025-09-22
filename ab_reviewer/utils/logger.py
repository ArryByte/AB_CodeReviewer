"""Centralized logging utilities for AB Code Reviewer."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "ab_reviewer",
    level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    project_name: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logger for AB Code Reviewer.

    Args:
        name: Logger name
        level: Logging level
        log_dir: Directory to store logs
        project_name: Name of the project being reviewed

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Format for console
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler if log directory is provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create project-specific log file if project name provided
        if project_name:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file = log_dir / f"{project_name}_{timestamp}.log"
        else:
            log_file = log_dir / "ab-reviewer.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # More detailed format for file
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "ab_reviewer") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)


def create_project_log_dir(base_dir: Path, project_name: str) -> Path:
    """
    Create project-specific log directory.

    Args:
        base_dir: Base logging directory
        project_name: Name of the project

    Returns:
        Path to project log directory
    """
    project_log_dir = base_dir / "project_reviews" / project_name
    project_log_dir.mkdir(parents=True, exist_ok=True)
    return project_log_dir
