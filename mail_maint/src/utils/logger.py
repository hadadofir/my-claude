"""Logging setup for Mail Maint"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


_logger: Optional[logging.Logger] = None


def setup_logger(
    name: str = "mail_maint",
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up and configure the application logger.

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_size_mb: Maximum log file size in MB before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """
    global _logger

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get the configured logger instance.

    Args:
        name: Optional child logger name

    Returns:
        Logger instance
    """
    global _logger

    if _logger is None:
        _logger = setup_logger()

    if name:
        return _logger.getChild(name)

    return _logger
