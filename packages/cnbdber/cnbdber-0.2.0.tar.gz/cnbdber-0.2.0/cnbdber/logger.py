from __future__ import annotations

import os
from typing import Optional
import json

try:
    from cnblogger import CNBLogger  # type: ignore
except Exception:  # dev workspace fallback where top-level 'cnblogger' is a namespace dir
    from cnblogger.cnblogger import CNBLogger  # type: ignore
from pathlib import Path


_LOGGER: Optional[CNBLogger] = None


def get_logger(config_path: Optional[str], inline_config: Optional[dict] = None) -> CNBLogger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    # Allow override via env var per cnblogger behavior [[memory:6119777]]
    if config_path and not os.getenv("CNBLOGGER_CONFIG"):
        try:
            parent = Path(config_path).expanduser().resolve().parent
            parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        # If inline config is provided (from cnbdber.config), make sure it is written to file
        if inline_config:
            try:
                # Merge/override defaults focusing on mode and file_dir
                existing = {}
                if os.path.isfile(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            existing = json.load(f) or {}
                    except Exception:
                        existing = {}
                merged = {**existing, **inline_config}
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(merged, f, indent=2)
            except Exception:
                pass
        _LOGGER = CNBLogger(config_path)
    else:
        _LOGGER = CNBLogger()
    return _LOGGER


