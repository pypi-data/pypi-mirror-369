"""Logging configuration for ML Assistant CLI."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    verbose: bool = False,
    log_file: Optional[str] = None
) -> None:
    """Setup logging configuration with Rich handler."""
    
    # Set log level
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create console for rich output
    console = Console(stderr=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=verbose,
                show_path=verbose,
            )
        ],
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("bentoml").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)