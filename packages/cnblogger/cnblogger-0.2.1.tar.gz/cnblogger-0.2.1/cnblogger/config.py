from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, Union

from .types import ColorsConfig, ConfigDict, Mode


DEFAULT_CONFIG_FILENAME = "cnblogger.config"


def _default_config_dict() -> ConfigDict:
	return {
		"mode": "cli",
		"delimiter": "|",
		"file_dir": "./.logs",
		"file_same_day_mode": "append",
		"api_url": None,
		"api_verify": True,
		"api_timeout_seconds": 3.0,
		"api_headers": {},
		# databases (all disabled by default)
		"db_sqlite_path": None,
		"db_sqlite_table": "logs",
		"db_mysql": {},
		"db_postgres": {},
		"db_mongo_uri": None,
		"db_mongo_database": None,
		"db_mongo_collection": None,
		"colors": {
			"INFO": "cyan",
			"CRITICAL": "red",
			"ERROR": "bright_yellow",
			"WARN": "yellow",
			"DEBUG": "blue",
		},
		"timestamp_utc": False,
	}


@dataclass(frozen=True)
class CNBConfig:
	mode: Mode
	delimiter: str
	file_dir: str
	file_same_day_mode: str
	api_url: Optional[str]
	api_verify: Union[bool, str]
	api_timeout_seconds: float
	api_headers: Dict[str, str]
	# databases
	db_sqlite_path: Optional[str]
	db_sqlite_table: str
	db_mysql: Dict[str, object]
	db_postgres: Dict[str, object]
	db_mongo_uri: Optional[str]
	db_mongo_database: Optional[str]
	db_mongo_collection: Optional[str]
	colors: ColorsConfig
	timestamp_utc: bool

	@staticmethod
	def load(path: Optional[str] = None) -> "CNBConfig":
		cfg_path = path or os.getenv("CNBLOGGER_CONFIG") or DEFAULT_CONFIG_FILENAME
		data: ConfigDict = {}
		if os.path.isfile(cfg_path):
			try:
				with open(cfg_path, "r", encoding="utf-8") as f:
					raw = json.load(f)
					if isinstance(raw, dict):
						data = raw  # type: ignore[assignment]
			except Exception:
				# On any config error, proceed with defaults
				data = {}
		else:
			# Create a default config file for convenience
			default_cfg = _default_config_dict()
			try:
				with open(cfg_path, "w", encoding="utf-8") as f:
					json.dump(default_cfg, f, indent=2)
				data = default_cfg
			except Exception:
				data = _default_config_dict()

		mode: Mode = data.get("mode", "cli")  # type: ignore[assignment]
		delimiter = data.get("delimiter", "|")
		file_dir = data.get("file_dir", "./.logs")
		file_same_day_mode = data.get("file_same_day_mode", "append")
		api_url = data.get("api_url")
		# Prefer api_verify, but accept legacy api_ssl_verify
		api_verify_val = data.get("api_verify")
		if api_verify_val is None and "api_ssl_verify" in data:
			api_verify_val = data.get("api_ssl_verify")
		if api_verify_val is None:
			api_verify_val = True
		api_verify = api_verify_val  # type: ignore[assignment]
		api_timeout_seconds = float(data.get("api_timeout_seconds", 3.0))
		api_headers: Dict[str, str] = data.get("api_headers", {})  # type: ignore[assignment]
		# dbs
		db_sqlite_path = data.get("db_sqlite_path")
		db_sqlite_table = data.get("db_sqlite_table", "logs")
		db_mysql = data.get("db_mysql", {})  # type: ignore[assignment]
		db_postgres = data.get("db_postgres", {})  # type: ignore[assignment]
		db_mongo_uri = data.get("db_mongo_uri")
		db_mongo_database = data.get("db_mongo_database")
		db_mongo_collection = data.get("db_mongo_collection")
		colors = data.get("colors", {})  # type: ignore[assignment]
		timestamp_utc = bool(data.get("timestamp_utc", False))
		return CNBConfig(
			mode=mode,
			delimiter=delimiter,
			file_dir=file_dir,
			file_same_day_mode=file_same_day_mode,
			api_url=api_url,
			api_verify=api_verify,  # type: ignore[arg-type]
			api_timeout_seconds=api_timeout_seconds,
			api_headers=api_headers,
			# dbs
			db_sqlite_path=db_sqlite_path,
			db_sqlite_table=str(db_sqlite_table),
			db_mysql=db_mysql,
			db_postgres=db_postgres,
			db_mongo_uri=db_mongo_uri,
			db_mongo_database=db_mongo_database,
			db_mongo_collection=db_mongo_collection,
			colors=colors,
			timestamp_utc=timestamp_utc,
		)
