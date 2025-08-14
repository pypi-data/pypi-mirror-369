from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Union, Optional
import re

from .types import LogLevel, Sink, FormatTimestamp

_VALID_TABLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class CLISink(Sink):
    format_timestamp: FormatTimestamp
    level_to_color: Dict[str, str]

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        color = self.level_to_color.get(level.value)
        # Colorize only the level token; defer import to avoid cycle
        try:
            from .colors import colorize

            level_text = colorize(level.value, color) if color else level.value
        except Exception:
            level_text = level.value
        out = f"[{ts}] [{level_text}] {message}"
        print(out)


@dataclass
class FileSink(Sink):
    format_timestamp: FormatTimestamp
    delimiter: str
    logs_dir: Path
    same_day_mode: str  # "append" | "new"

    def __post_init__(self) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _filename_for(self, when_epoch_s: float) -> Path:
        dt = datetime.fromtimestamp(when_epoch_s)
        day = dt.strftime("%Y%m%d")
        if self.same_day_mode == "append":
            return self.logs_dir / f"{day}.log"
        # new file per call/time on same day
        suffix = dt.strftime("%H%M%S")
        return self.logs_dir / f"{day}_{suffix}.log"

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        line = f"{ts}{self.delimiter}{level.value}{self.delimiter}{message}\n"
        fp = self._filename_for(when_epoch_s)
        try:
            with open(fp, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            # Avoid crashing the caller on FS issues
            pass


@dataclass
class APISink(Sink):
    format_timestamp: FormatTimestamp
    delimiter: str
    url: str
    verify: Union[bool, str]
    timeout_seconds: float
    headers: Dict[str, str]

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        payload = f"{ts}{self.delimiter}{level.value}{self.delimiter}{message}"
        try:
            import requests  # type: ignore

            req_headers = {"Content-Type": "text/plain; charset=utf-8", **(self.headers or {})}
            requests.post(
                self.url,
                data=payload.encode("utf-8"),
                headers=req_headers,
                verify=self.verify,
                timeout=self.timeout_seconds,
            )
        except Exception:
            # Swallow network errors and missing dependency to avoid crashing the app using the logger
            pass


@dataclass
class SQLiteSink(Sink):
    format_timestamp: FormatTimestamp
    path: str
    table: str

    def _ensure_table(self, cursor) -> None:
        if not _VALID_TABLE.match(self.table):
            raise ValueError("Invalid SQLite table name")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        try:
            import sqlite3
            # Ensure parent directory exists
            parent = Path(self.path).parent
            if str(parent):
                parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.path)
            try:
                cur = conn.cursor()
                self._ensure_table(cur)
                cur.execute(
                    f"INSERT INTO {self.table} (ts, level, message) VALUES (?, ?, ?)",
                    (ts, level.value, message),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass


@dataclass
class MySQLSink(Sink):
    format_timestamp: FormatTimestamp
    host: str
    port: int
    user: str
    password: str
    database: str
    table: str

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        try:
            if not _VALID_TABLE.match(self.table):
                raise ValueError("Invalid MySQL table name")
            import pymysql  # type: ignore

            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                autocommit=True,
            )
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        CREATE TABLE IF NOT EXISTS {self.table} (
                            id BIGINT PRIMARY KEY AUTO_INCREMENT,
                            ts VARCHAR(32) NOT NULL,
                            level VARCHAR(16) NOT NULL,
                            message TEXT NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                        """
                    )
                    cur.execute(
                        f"INSERT INTO {self.table} (ts, level, message) VALUES (%s, %s, %s)",
                        (ts, level.value, message),
                    )
            finally:
                conn.close()
        except Exception:
            pass


@dataclass
class PostgresSink(Sink):
    format_timestamp: FormatTimestamp
    host: str
    port: int
    user: str
    password: str
    database: str
    table: str
    sslmode: Optional[str] = None

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        try:
            if not _VALID_TABLE.match(self.table):
                raise ValueError("Invalid Postgres table name")
            import psycopg2  # type: ignore

            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                sslmode=self.sslmode or "prefer",
            )
            try:
                cur = conn.cursor()
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table} (
                        id BIGSERIAL PRIMARY KEY,
                        ts VARCHAR(32) NOT NULL,
                        level VARCHAR(16) NOT NULL,
                        message TEXT NOT NULL
                    )
                    """
                )
                cur.execute(
                    f"INSERT INTO {self.table} (ts, level, message) VALUES (%s, %s, %s)",
                    (ts, level.value, message),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass


@dataclass
class MongoSink(Sink):
    format_timestamp: FormatTimestamp
    uri: str
    database: str
    collection: str

    def write(self, level: LogLevel, message: str, when_epoch_s: float) -> None:
        ts = self.format_timestamp(when_epoch_s)
        try:
            from pymongo import MongoClient  # type: ignore

            client = MongoClient(self.uri, serverSelectionTimeoutMS=1000)
            try:
                db = client[self.database]
                db[self.collection].insert_one({
                    "ts": ts,
                    "level": level.value,
                    "message": message,
                })
            finally:
                client.close()
        except Exception:
            pass
