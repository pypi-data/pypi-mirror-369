# cnblogger

Configurable, typed Python logger that can write to CLI, file, HTTP API, and databases. Controlled by a simple JSON config file `cnblogger.config`.

- Repository: https://github.com/AznIronMan/cnblogger

## Installation

```bash
pip install cnblogger                 # base (no optional deps)
pip install "cnblogger[colors]"      # CLI colors via colorama
pip install "cnblogger[api]"         # HTTP API sink via requests
pip install "cnblogger[sqlite]"      # SQLite (built-in stdlib, extras not required)
pip install "cnblogger[mysql]"       # MySQL via PyMySQL
pip install "cnblogger[postgres]"    # PostgreSQL via psycopg2-binary
pip install "cnblogger[mongo]"       # MongoDB via pymongo
pip install "cnblogger[all]"         # everything
```

## Usage

```python
from cnblogger import CNBLogger

logger = CNBLogger()  # auto-loads ./cnblogger.config if present
logger.info("App started")
logger.error("Something went wrong")
```

### Configuration
If `cnblogger.config` does not exist, it will be created automatically with defaults on first use. You can also copy from `cnblogger.config.example`.

Create or edit a `cnblogger.config` JSON file in your project root (or set `CNBLOGGER_CONFIG` env var to a path). Example with databases:

```json
{
  "mode": "all",
  "delimiter": "|",
  "file_dir": "./.logs",
  "file_same_day_mode": "append",
  "api_url": "https://log.example.com/ingest",
  "api_verify": true,
  "api_timeout_seconds": 3.0,
  "api_headers": {"Authorization": "Bearer <token>"},
  "db_sqlite_path": "./.logs/logs.db",
  "db_sqlite_table": "logs",
  "db_mysql": {"host": "localhost", "port": 3306, "user": "root", "password": "", "database": "logs", "table": "logs"},
  "db_postgres": {"host": "localhost", "port": 5432, "user": "postgres", "password": "", "database": "logs", "table": "logs", "sslmode": "prefer"},
  "db_mongo_uri": "mongodb://localhost:27017",
  "db_mongo_database": "logs",
  "db_mongo_collection": "entries",
  "colors": {"INFO": "cyan", "CRITICAL": "red", "ERROR": "bright_yellow", "WARN": "yellow", "DEBUG": "blue"},
  "timestamp_utc": false
}
```

- mode: `cli` | `file` | `api` | `both` (cli+file) | `all` (cli+file+api). Default: `cli`.
- file names: `yyyymmdd.log` (append by default on same day). If `file_same_day_mode` is `new`, files are `yyyymmdd_HHMMSS.log`.
- CLI format: `[yyyy.mm.dd hh:mm:ss.mmm] [LEVEL] message` (LEVEL colored, colors configurable).
- File/API/DB format stored consistently as `ts|LEVEL|message` or in columns.
- API verify: Set `api_verify` to `true`/`false` or a CA bundle path. Protocol is inferred from `api_url`.
- Databases:
  - SQLite: set `db_sqlite_path` and optional `db_sqlite_table`.
  - MySQL: set `db_mysql` object with connection details and `table`.
  - Postgres: set `db_postgres` object; optional `sslmode`.
  - MongoDB: set `db_mongo_uri`, `db_mongo_database`, `db_mongo_collection`.

### Types
The package is typed (`py.typed`). All public APIs include type hints.

### License
MIT - See the [LICENSE](LICENSE) file.