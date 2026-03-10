#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path


class ConfigError(RuntimeError):
    pass


def default_env_path() -> Path:
    return Path(__file__).resolve().parents[1] / ".env"


def load_dotenv(env_file: Path) -> None:
    if not env_file.exists():
        raise ConfigError(f"Environment file not found: {env_file}")

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Invalid .env line: {raw_line}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ConfigError(f"Invalid .env line: {raw_line}")
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {name} must be an integer") from exc
