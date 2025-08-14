from __future__ import annotations

from typing import Optional

from .config import AppConfig, load_config
from .logger import get_logger
from .core import create_backend, run_command, create_backend_context, close_backend

__all__ = [
    "AppConfig",
    "load_config",
    "get_logger",
    "cnbdber",
    "create_backend",
    "run_command",
    "create_backend_context",
    "close_backend",
]


def cnbdber(command: str, config_path: Optional[str] = None) -> Optional[str]:
    """Execute a SQL-like command using cnbdber configuration.

    Parameters
    ----------
    command: str
        The SQL-like command to execute against the configured target.
    config_path: Optional[str]
        Optional path to `cnbdber.config` (JSON). If not provided, uses
        the `CNBDBER_CONFIG` environment variable or the default path.

    Returns
    -------
    Optional[str]
        The formatted result string if the command returns rows; otherwise None.
    """
    app_cfg = load_config(config_path)
    logger = get_logger(app_cfg.logger_config_path, inline_config=app_cfg.logger)
    with create_backend_context(app_cfg.target, logger) as backend:
        return run_command(backend, command)


