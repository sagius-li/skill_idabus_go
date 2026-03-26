from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    pass


def _load_dotenv(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Invalid .env line in {env_file}: {raw_line}")
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {name} must be an integer.") from exc


@dataclass(frozen=True)
class Settings:
    app_root: Path
    backend_root: Path
    web_root: Path
    idabus_root: Path
    openai_api_key: str
    openai_model: str
    chat_max_tool_rounds: int
    session_ttl_seconds: int


def load_settings() -> Settings:
    backend_root = Path(__file__).resolve().parent
    app_root = backend_root.parent
    web_root = app_root / "web"
    idabus_root = app_root / "idabus-go"
    _load_dotenv(backend_root / ".env")

    return Settings(
        app_root=app_root,
        backend_root=backend_root,
        web_root=web_root,
        idabus_root=idabus_root,
        openai_api_key=_require_env("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
        chat_max_tool_rounds=_get_int_env("CHAT_MAX_TOOL_ROUNDS", 8),
        session_ttl_seconds=_get_int_env("SESSION_TTL_SECONDS", 3600),
    )
