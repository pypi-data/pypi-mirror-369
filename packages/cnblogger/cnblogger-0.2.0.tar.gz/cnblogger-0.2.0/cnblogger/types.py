from __future__ import annotations

from enum import Enum
from typing import Callable, Dict, Literal, Protocol, TypedDict, Union, Optional


class LogLevel(str, Enum):
    INFO = "INFO"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARN = "WARN"
    DEBUG = "DEBUG"


Mode = Literal["cli", "file", "api", "both", "all"]


class ColorsConfig(TypedDict, total=False):
    INFO: str
    CRITICAL: str
    ERROR: str
    WARN: str
    DEBUG: str


class MySQLConfig(TypedDict, total=False):
    host: str
    port: int
    user: str
    password: str
    database: str
    table: str


class PostgresConfig(TypedDict, total=False):
    host: str
    port: int
    user: str
    password: str
    database: str
    table: str
    sslmode: str


class ConfigDict(TypedDict, total=False):
    mode: Mode
    delimiter: str
    file_dir: str
    file_same_day_mode: Literal["append", "new"]
    api_url: str
    api_verify: Union[bool, str]
    api_ssl_verify: Union[bool, str]
    api_timeout_seconds: float
    api_headers: Dict[str, str]
    colors: ColorsConfig
    timestamp_utc: bool
    # Databases
    db_sqlite_path: str
    db_sqlite_table: str
    db_mysql: MySQLConfig
    db_postgres: PostgresConfig
    db_mongo_uri: str
    db_mongo_database: str
    db_mongo_collection: str


class Sink(Protocol):
    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None: ...


FormatTimestamp = Callable[[float], str]
