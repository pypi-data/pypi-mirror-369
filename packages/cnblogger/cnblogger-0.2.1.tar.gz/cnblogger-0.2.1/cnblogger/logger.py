from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import CNBConfig
from .types import FormatTimestamp, LogLevel, Sink
from .sinks import APISink, CLISink, FileSink, SQLiteSink, MySQLSink, PostgresSink, MongoSink


DEFAULT_COLORS: Dict[str, str] = {
    "INFO": "cyan",
    "CRITICAL": "red",
    "ERROR": "bright_yellow",
    "WARN": "yellow",
    "DEBUG": "blue",
}


def _format_timestamp_factory(use_utc: bool) -> FormatTimestamp:
    def _fmt(epoch_s: float) -> str:
        dt = datetime.fromtimestamp(epoch_s, tz=timezone.utc if use_utc else None)
        # yyyy.mm.dd hh:mm:ss.mmm
        return dt.strftime("%Y.%m.%d %H:%M:%S.") + f"{int(dt.microsecond/1000):03d}"

    return _fmt


@dataclass
class CNBLogger:
    config: CNBConfig
    sinks: List[Sink]
    format_timestamp: FormatTimestamp

    def __init__(self, config_path: Optional[str] = None) -> None:
        cfg = CNBConfig.load(config_path)
        fmt_ts = _format_timestamp_factory(cfg.timestamp_utc)
        level_to_color = {**DEFAULT_COLORS, **(cfg.colors or {})}

        sinks: List[Sink] = []
        if cfg.mode in ("cli", "both", "all"):
            sinks.append(CLISink(format_timestamp=fmt_ts, level_to_color=level_to_color))
        if cfg.mode in ("file", "both", "all"):
            sinks.append(
                FileSink(
                    format_timestamp=fmt_ts,
                    delimiter=cfg.delimiter,
                    logs_dir=Path(cfg.file_dir),
                    same_day_mode=cfg.file_same_day_mode,
                )
            )
        if cfg.mode in ("api", "all") and cfg.api_url:
            sinks.append(
                APISink(
                    format_timestamp=fmt_ts,
                    delimiter=cfg.delimiter,
                    url=str(cfg.api_url),
                    verify=cfg.api_verify,
                    timeout_seconds=cfg.api_timeout_seconds,
                    headers=cfg.api_headers,
                )
            )
        # Databases (opt-in via config presence)
        if cfg.db_sqlite_path:
            sinks.append(
                SQLiteSink(
                    format_timestamp=fmt_ts,
                    path=cfg.db_sqlite_path,
                    table=cfg.db_sqlite_table,
                )
            )
        if cfg.db_mysql:
            m = cfg.db_mysql
            host = str(m.get("host", "localhost"))
            port = int(m.get("port", 3306))
            user = str(m.get("user", "root"))
            password = str(m.get("password", ""))
            database = str(m.get("database", "logs"))
            table = str(m.get("table", "logs"))
            sinks.append(
                MySQLSink(
                    format_timestamp=fmt_ts,
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    table=table,
                )
            )
        if cfg.db_postgres:
            p = cfg.db_postgres
            host = str(p.get("host", "localhost"))
            port = int(p.get("port", 5432))
            user = str(p.get("user", "postgres"))
            password = str(p.get("password", ""))
            database = str(p.get("database", "logs"))
            table = str(p.get("table", "logs"))
            sslmode = p.get("sslmode")
            sinks.append(
                PostgresSink(
                    format_timestamp=fmt_ts,
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    table=table,
                    sslmode=sslmode,  # type: ignore[arg-type]
                )
            )
        if cfg.db_mongo_uri and cfg.db_mongo_database and cfg.db_mongo_collection:
            sinks.append(
                MongoSink(
                    format_timestamp=fmt_ts,
                    uri=cfg.db_mongo_uri,
                    database=cfg.db_mongo_database,
                    collection=cfg.db_mongo_collection,
                )
            )

        self.config = cfg
        self.sinks = sinks
        self.format_timestamp = fmt_ts

    def _log(self, level: LogLevel, message: str) -> None:
        now = time.time()
        for sink in self.sinks:
            sink.write(level, message, now)

    def info(self, message: str) -> None:
        self._log(LogLevel.INFO, message)

    def critical(self, message: str) -> None:
        self._log(LogLevel.CRITICAL, message)

    def error(self, message: str) -> None:
        self._log(LogLevel.ERROR, message)

    def warn(self, message: str) -> None:
        self._log(LogLevel.WARN, message)

    def debug(self, message: str) -> None:
        self._log(LogLevel.DEBUG, message)
