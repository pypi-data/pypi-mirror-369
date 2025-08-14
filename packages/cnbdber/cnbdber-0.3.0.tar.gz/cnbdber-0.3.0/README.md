CNBDBer

Universal DB runner for SQL-like commands across SQLite, MySQL, PostgreSQL, and MongoDB.

Install

- From PyPI (Python 3.9+):
```bash
pip install cnbdber
# optional extras
pip install 'cnbdber[mysql]'
pip install 'cnbdber[postgres]'
pip install 'cnbdber[mongo]'
pip install 'cnbdber[ssh]'  # for SSH tunnel support
```
- From source (development):
```bash
pip install -e .
```

Config

- App config: `./.configs/cnbdber.config` (auto-created on first run)
- Logger config: `./.configs/cnblogger.config` (auto-created if missing)
- Logs: `./.logs/`

You can override the app config via `CNBDBER_CONFIG=/abs/path/to/cnbdber.config`.
The logger path is read from `cnbdber.config` and passed directly to `CNBLogger`.

See `.config-examples/` in this repo for ready-to-copy examples:

- `sqlite-cnbdber.config`
- `mysql-cnbdber.config`
- `postgres-cnbdber.config`
- `mongo-cnbdber.config`
- `mysql-direct.config`
- `mysql-ssh-same-creds.config`
- `mysql-ssh-different-creds.config`
- `postgres-direct.config`
- `postgres-ssh-same-creds.config`
- `postgres-ssh-different-creds.config`

Usage

Run a one-off command:
```bash
cnbdber -c "SELECT * FROM users LIMIT 5;"
```
Run from a file:
```bash
cnbdber --file ./query.sql
```
Specify a config explicitly:
```bash
cnbdber --config ./my-config.json -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL 30 DAY;"
```

- Library usage (import in Python)

Quick one-liner function:

```python
from cnbdber import cnbdber

# Use default/auto-created config
result = cnbdber("SELECT 1;")
print(result or "")

# Or pass a custom config path
result = cnbdber("SELECT * FROM users LIMIT 5;", "./my-config.json")
print(result or "")
```

Or use the config loader and backend helpers for finer control:

```python
from typing import Optional
from cnbdber import load_config, get_logger
from cnbdber.core import create_backend, run_command, create_backend_context

cfg = load_config()  # or load_config("./my-config.json")
logger = get_logger(cfg.logger_config_path, inline_config=cfg.logger)

with create_backend_context(cfg.target, logger) as backend:
  # DDL/DML: returns None on success
  ddl_result: Optional[str] = run_command(backend, "CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, name TEXT);")

  insert_result: Optional[str] = run_command(backend, "INSERT INTO items(name) VALUES ('alpha');")

  # SELECT: returns tab-separated text (with header when available)
  select_result: Optional[str] = run_command(backend, "SELECT id, name FROM items ORDER BY id;")
  print(select_result or "")
```

To target MySQL/PostgreSQL/MongoDB, set `cfg.target` via `cnbdber.config` (see examples below) or construct a dict at runtime and pass it to `create_backend`.

- SQL backends (SQLite/MySQL/PostgreSQL): raw SQL is executed as-is.
- MongoDB: a minimal SQL-to-Mongo translation is supported for simple `SELECT/INSERT/UPDATE/DELETE` with equality-only `WHERE` clauses.

Example cnbdber.config

```json
{
  "logger_config_path": "./.configs/cnblogger.config",
  "target": {
    "type": "sqlite",
    "sqlite_path": "./example.db"
  }
}
```

Switch to MySQL:
```json
{
  "logger_config_path": "./.configs/cnblogger.config",
  "target": {
    "type": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",          
    "password_file": "",      
    "database": "test"
  }
}
```

SSH tunnel (optional) for MySQL/PostgreSQL:
```json
{
  "logger_config_path": "./.configs/cnblogger.config",
  "target": {
    "type": "postgres",
    "host": "db.internal",
    "port": 5432,
    "user": "postgres",
    "password": "",
    "password_file": "~/.secrets/db.pass",
    "database": "app",
    "sslmode": "require",
    "ssh": {
      "enabled": true,
      "host": "bastion.example.com",
      "port": 22,
      "user": "ec2-user",
      "pkey_path": "~/.ssh/id_rsa",
      "pkey_password": "",
      "local_bind_host": "127.0.0.1",
      "local_bind_port": 0,
      "remote_host": "db.internal",
      "remote_port": 5432
    }
  }
}
```

Notes:
- When `password_file` is provided, it will be read and used instead of `password`.
- Using SSH requires extra `cnbdber[ssh]`.
- Always prefer the context manager (`create_backend_context`) to ensure SSH tunnels (if any) are cleaned up automatically.

License

MIT


