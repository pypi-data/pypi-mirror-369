from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Protocol, ContextManager

from .config import TargetConfig


class Logger(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def debug(self, message: str) -> None: ...


class Backend(Protocol):
    def execute(self, command: str) -> Optional[str]:
        ...


@dataclass
class SQLiteBackend:
    path: str
    logger: Logger

    def execute(self, command: str) -> Optional[str]:
        import sqlite3

        self.logger.debug(f"[sqlite] {command}")
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(command)
            try:
                rows = cur.fetchall()
                return _format_rows(rows, [d[0] for d in cur.description] if cur.description else None)
            except Exception:
                conn.commit()
                return None


@dataclass
class MySQLBackend:
    host: str
    port: int
    user: str
    password: str
    password_file: Optional[str]
    database: str
    logger: Logger

    def execute(self, command: str) -> Optional[str]:
        import os
        import pymysql
        import warnings
        password: str = self.password
        if (self.password_file or "").strip():
            try:
                with open(os.path.expanduser(str(self.password_file)), "r", encoding="utf-8") as f:
                    password = f.read().strip()
            except Exception:
                warnings.warn("Could not read password_file; falling back to inline password")

        self.logger.debug(f"[mysql] {command}")
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=password, database=self.database, autocommit=True)
        try:
            with conn.cursor() as cur:
                cur.execute(command)
                try:
                    rows = cur.fetchall()
                    headers = [d[0] for d in cur.description] if cur.description else None
                    return _format_rows(rows, headers)
                except Exception:
                    return None
        finally:
            conn.close()


@dataclass
class PostgresBackend:
    host: str
    port: int
    user: str
    password: str
    password_file: Optional[str]
    database: str
    sslmode: Optional[str]
    logger: Logger

    def execute(self, command: str) -> Optional[str]:
        import os
        import psycopg2
        import warnings
        password: str = self.password
        if (self.password_file or "").strip():
            try:
                with open(os.path.expanduser(str(self.password_file)), "r", encoding="utf-8") as f:
                    password = f.read().strip()
            except Exception:
                warnings.warn("Could not read password_file; falling back to inline password")

        self.logger.debug(f"[postgres] {command}")
        conn = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=password, dbname=self.database, sslmode=self.sslmode or "disable")
        try:
            with conn.cursor() as cur:
                cur.execute(command)
                try:
                    rows = cur.fetchall()
                    headers = [d[0] for d in cur.description] if cur.description else None
                    return _format_rows(rows, headers)
                except Exception:
                    conn.commit()
                    return None
        finally:
            conn.close()


@dataclass
class MongoBackend:
    uri: str
    database: str
    logger: Logger

    def execute(self, command: str) -> Optional[str]:
        from pymongo import MongoClient

        self.logger.debug(f"[mongo] {command}")
        client = MongoClient(self.uri)
        try:
            db = client[self.database]
            stmt = command.strip().rstrip(";")
            return _execute_sqlish_on_mongo(db, stmt)
        finally:
            client.close()


def create_backend(cfg: TargetConfig, logger: Logger) -> Backend:
    t = cfg.get("type", "sqlite")
    if t == "sqlite":
        return SQLiteBackend(path=str(cfg.get("sqlite_path", "./cnbdber.db")), logger=logger)
    if t == "mysql":
        return _create_mysql_backend(cfg, logger)
    if t == "postgres":
        return _create_postgres_backend(cfg, logger)
    if t == "mongodb":
        return MongoBackend(
            uri=str(cfg.get("mongo_uri", "mongodb://localhost:27017")),
            database=str(cfg.get("mongo_database", "test")),
            logger=logger,
        )
    raise ValueError(f"Unknown backend type: {t}")


def run_command(backend: Backend, command: str) -> Optional[str]:
    return backend.execute(command)


def _maybe_start_ssh_tunnel(cfg: TargetConfig, logger: Logger) -> Optional[tuple[str, int, Any]]:
    ssh_cfg = cfg.get("ssh")
    if not ssh_cfg or not ssh_cfg.get("enabled", False):
        return None
    try:
        from sshtunnel import SSHTunnelForwarder  # type: ignore
    except Exception:
        raise RuntimeError("SSH tunnel requested but sshtunnel is not installed. Install with `pip install sshtunnel`." )

    ssh_host = str(ssh_cfg.get("host", "127.0.0.1"))
    ssh_port = int(ssh_cfg.get("port", 22))
    ssh_user = str(ssh_cfg.get("user", ""))
    ssh_password = str(ssh_cfg.get("password", ""))
    ssh_password_file = str(ssh_cfg.get("password_file", ""))
    pkey_path = str(ssh_cfg.get("pkey_path", ""))
    pkey_password = str(ssh_cfg.get("pkey_password", ""))
    local_bind_host = str(ssh_cfg.get("local_bind_host", "127.0.0.1"))
    local_bind_port = int(ssh_cfg.get("local_bind_port", 0))
    remote_host = str(ssh_cfg.get("remote_host", cfg.get("host", "127.0.0.1")))
    remote_port = int(ssh_cfg.get("remote_port", cfg.get("port", 0)))

    # read password_file if provided
    if ssh_password_file.strip():
        import os
        try:
            with open(os.path.expanduser(ssh_password_file), "r", encoding="utf-8") as f:
                ssh_password = f.read().strip()
        except Exception:
            logger.error("Failed to read SSH password_file; falling back to inline password if any.")

    tunnel_kwargs: dict[str, Any] = {
        "ssh_address_or_host": (ssh_host, ssh_port),
        "ssh_username": ssh_user or None,
        "remote_bind_address": (remote_host, remote_port),
        "local_bind_address": (local_bind_host, local_bind_port),
    }
    if pkey_path:
        tunnel_kwargs["ssh_pkey"] = pkey_path
        if pkey_password:
            tunnel_kwargs["ssh_private_key_password"] = pkey_password
    elif ssh_password:
        tunnel_kwargs["ssh_password"] = ssh_password

    server = SSHTunnelForwarder(**tunnel_kwargs)
    server.start()
    bound_host, bound_port = server.local_bind_host, server.local_bind_port
    logger.info(f"SSH tunnel established {bound_host}:{bound_port} -> {remote_host}:{remote_port}")
    return bound_host, bound_port, server


def _create_mysql_backend(cfg: TargetConfig, logger: Logger) -> Backend:
    tunnel_info = _maybe_start_ssh_tunnel(cfg, logger)
    host = str(cfg.get("host", "127.0.0.1"))
    port = int(cfg.get("port", 3306))
    server = None
    if tunnel_info is not None:
        host, port, server = tunnel_info
    backend = MySQLBackend(
        host=host,
        port=port,
        user=str(cfg.get("user", "root")),
        password=str(cfg.get("password", "")),
        password_file=str(cfg.get("password_file", "")) or None,
        database=str(cfg.get("database", "test")),
        logger=logger,
    )
    if server is not None:
        # attach server to backend for lifecycle management via attribute
        setattr(backend, "_ssh_tunnel", server)
    return backend


def _create_postgres_backend(cfg: TargetConfig, logger: Logger) -> Backend:
    tunnel_info = _maybe_start_ssh_tunnel(cfg, logger)
    host = str(cfg.get("host", "127.0.0.1"))
    port = int(cfg.get("port", 5432))
    server = None
    if tunnel_info is not None:
        host, port, server = tunnel_info
    backend = PostgresBackend(
        host=host,
        port=port,
        user=str(cfg.get("user", "postgres")),
        password=str(cfg.get("password", "")),
        password_file=str(cfg.get("password_file", "")) or None,
        database=str(cfg.get("database", "postgres")),
        sslmode=str(cfg.get("sslmode", "disable")),
        logger=logger,
    )
    if server is not None:
        setattr(backend, "_ssh_tunnel", server)
    return backend


def _format_rows(rows: Iterable[Iterable[Any]], headers: Optional[list[str]] = None) -> str:
    data = list(rows)
    if not data:
        return ""
    lines: list[str] = []
    if headers:
        lines.append("\t".join(headers))
    for r in data:
        lines.append("\t".join(str(v) for v in r))
    return "\n".join(lines)


def _execute_sqlish_on_mongo(db: Any, stmt: str) -> Optional[str]:
    # Minimal SQL-ish support: SELECT ... FROM coll WHERE a=b; DELETE FROM ...; INSERT INTO ...; UPDATE ... SET ... WHERE a=b
    # This is intentionally basic and safe for quick admin tasks.
    tokens = stmt.split()
    if not tokens:
        return None
    op = tokens[0].upper()
    if op == "SELECT":
        # SELECT fields FROM collection WHERE field=value
        # Only supports * or comma-separated fields; WHERE only equality and single condition
        try:
            select_idx = 0
            from_idx = tokens.index("FROM")
            fields_raw = " ".join(tokens[select_idx + 1:from_idx])
            fields = None if fields_raw.strip() == "*" else [f.strip() for f in fields_raw.split(",")]
            coll = tokens[from_idx + 1]
            query = {}
            if "WHERE" in tokens:
                where_idx = tokens.index("WHERE")
                cond = " ".join(tokens[where_idx + 1:])
                key, val = _parse_eq(cond)
                query[key] = val
            projection = {f: 1 for f in fields} if fields else None
            cursor = db[coll].find(query, projection)
            docs = list(cursor)
            if not docs:
                return ""
            headers = sorted({k for d in docs for k in d.keys() if k != "_id"})
            lines = ["\t".join(headers)]
            for d in docs:
                lines.append("\t".join(str(d.get(h, "")) for h in headers))
            return "\n".join(lines)
        except Exception as exc:
            raise RuntimeError(f"Mongo SELECT parse/exec error: {exc}")
    if op == "DELETE":
        # DELETE FROM collection WHERE field=value
        try:
            from_idx = tokens.index("FROM")
            coll = tokens[from_idx + 1]
            query = {}
            if "WHERE" in tokens:
                where_idx = tokens.index("WHERE")
                cond = " ".join(tokens[where_idx + 1:])
                key, val = _parse_eq(cond)
                query[key] = val
            res = db[coll].delete_many(query)
            return str(res.deleted_count)
        except Exception as exc:
            raise RuntimeError(f"Mongo DELETE parse/exec error: {exc}")
    if op == "INSERT":
        # INSERT INTO collection (a,b) VALUES (1,2)
        try:
            into_idx = tokens.index("INTO")
            coll = tokens[into_idx + 1]
            cols_part = stmt[stmt.index("(") + 1: stmt.index(")")]
            vals_part = stmt[stmt.rindex("(") + 1: stmt.rindex(")")]
            cols = [c.strip() for c in cols_part.split(",")]
            vals = [_strip_quotes(v.strip()) for v in vals_part.split(",")]
            doc = dict(zip(cols, vals))
            db[coll].insert_one(doc)
            return "1"
        except Exception as exc:
            raise RuntimeError(f"Mongo INSERT parse/exec error: {exc}")
    if op == "UPDATE":
        # UPDATE collection SET a=1,b=2 WHERE c=3
        try:
            coll = tokens[1]
            set_idx = tokens.index("SET")
            where_idx = tokens.index("WHERE") if "WHERE" in tokens else None
            set_part = " ".join(tokens[set_idx + 1: where_idx]) if where_idx else " ".join(tokens[set_idx + 1:])
            updates = {}
            for pair in set_part.split(","):
                k, v = _parse_eq(pair)
                updates[k] = v
            query = {}
            if where_idx is not None:
                cond = " ".join(tokens[where_idx + 1:])
                k, v = _parse_eq(cond)
                query[k] = v
            res = db[coll].update_many(query, {"$set": updates})
            return str(res.modified_count)
        except Exception as exc:
            raise RuntimeError(f"Mongo UPDATE parse/exec error: {exc}")
    raise RuntimeError(f"Unsupported Mongo operation: {op}")


def _parse_eq(expr: str) -> tuple[str, Any]:
    if "=" not in expr:
        raise ValueError("Only equality conditions are supported")
    k, v = expr.split("=", 1)
    return k.strip(), _strip_quotes(v.strip())


def _strip_quotes(s: str) -> Any:
    if (len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'")):
        return s[1:-1]
    # try int/float
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        return s



def close_backend(backend: Backend) -> None:
    server = getattr(backend, "_ssh_tunnel", None)
    if server is not None:
        try:
            server.stop()
        except Exception:
            pass
        try:
            delattr(backend, "_ssh_tunnel")
        except Exception:
            pass


class _BackendContext(ContextManager[Backend]):
    def __init__(self, backend: Backend) -> None:
        self._backend = backend

    def __enter__(self) -> Backend:
        return self._backend

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Optional[bool]:
        close_backend(self._backend)
        return None


def create_backend_context(cfg: TargetConfig, logger: Logger) -> ContextManager[Backend]:
    return _BackendContext(create_backend(cfg, logger))

