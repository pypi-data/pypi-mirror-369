from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Optional, TypedDict


DEFAULT_CONFIG_PATH: str = "./.configs/cnbdber.config"


class SshConfig(TypedDict, total=False):
    enabled: bool
    host: str
    port: int
    user: str
    password: str
    password_file: str
    pkey_path: str
    pkey_password: str
    local_bind_host: str
    local_bind_port: int
    remote_host: str
    remote_port: int


class TargetConfig(TypedDict, total=False):
    type: Literal["sqlite", "mysql", "postgres", "mongodb"]
    # sqlite
    sqlite_path: str
    # mysql
    host: str
    port: int
    user: str
    password: str
    password_file: str
    database: str
    # postgres
    sslmode: str
    # optional SSH tunnel for MySQL/Postgres
    ssh: SshConfig
    # mongodb
    mongo_uri: str
    mongo_database: str


@dataclass(frozen=True)
class AppConfig:
    logger_config_path: str
    logger: dict
    target: TargetConfig


def _default_config_dict() -> Dict[str, Any]:
    return {
        "logger_config_path": "./.configs/cnblogger.config",
        "logger": {
            "mode": "both",
            "file_dir": "./.logs",
            "file_same_day_mode": "append"
        },
        "target": {
            "type": "sqlite",
            "sqlite_path": "./cnbdber.db"
        }
    }


def _ensure_parent_dir(path: str) -> None:
    parent = Path(path).expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


def load_config(path: Optional[str] = None) -> AppConfig:
    cfg_path = path or os.getenv("CNBDBER_CONFIG") or DEFAULT_CONFIG_PATH
    cfg_path_resolved = str(Path(cfg_path).expanduser())
    data: Dict[str, Any] = {}
    if os.path.isfile(cfg_path_resolved):
        try:
            with open(cfg_path_resolved, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    data = raw
        except Exception:
            data = {}
    else:
        data = _default_config_dict()
        try:
            _ensure_parent_dir(cfg_path_resolved)
            with open(cfg_path_resolved, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            # If we cannot write, proceed with the in-memory defaults
            pass

    logger_config_path = str(data.get("logger_config_path", "./.configs/cnblogger.config"))
    logger_cfg = data.get("logger", {"mode": "both", "file_dir": "./.logs", "file_same_day_mode": "append"})  # type: ignore[assignment]
    target: TargetConfig = data.get("target", {"type": "sqlite", "sqlite_path": "./cnbdber.db"})  # type: ignore[assignment]
    return AppConfig(logger_config_path=logger_config_path, logger=logger_cfg, target=target)


