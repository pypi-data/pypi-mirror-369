from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config import load_config
from .logger import get_logger
from .core import create_backend, run_command


def _read_stdin_if_piped() -> Optional[str]:
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        return data if data.strip() else None
    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cnbdber", description="CNBDBer universal DB runner")
    p.add_argument("-c", "--command", help="SQL-like command to execute")
    p.add_argument("-f", "--file", help="Path to a file containing the command")
    p.add_argument("--config", help="Path to cnbdber.config (JSON)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    app_cfg = load_config(args.config)
    logger = get_logger(app_cfg.logger_config_path, inline_config=app_cfg.logger)

    cmd = args.command
    if not cmd and args.file:
        cmd = Path(args.file).read_text(encoding="utf-8")
    if not cmd:
        cmd = _read_stdin_if_piped()
    if not cmd:
        parser.error("No command provided. Use -c, --file, or pipe via stdin.")
        return 2

    backend = create_backend(app_cfg.target, logger)
    try:
        result = run_command(backend, cmd)
        if result is not None:
            print(result)
        return 0
    except Exception as exc:
        logger.error(f"Execution failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


