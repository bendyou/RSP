"""Настройки приложения из окружения и локального .env."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    http_host: str
    http_port: int


def load_settings(env_file: Path | None = None) -> Settings:
    """Считать .env; переменные процесса имеют приоритет над файлом."""
    load_dotenv(env_file or PROJECT_DIR / ".env", override=False)

    app_name = os.getenv("APP_NAME", "Интеллектуальная панель управления серверами").strip()
    app_version = os.getenv("APP_VERSION", "1.0.0").strip()
    app_env = os.getenv("APP_ENV", "development").strip()
    http_host = os.getenv("HTTP_HOST", "127.0.0.1").strip()
    raw_port = os.getenv("HTTP_PORT", "8080")

    if not all((app_name, app_version, app_env, http_host)):
        raise ValueError("APP_NAME, APP_VERSION, APP_ENV и HTTP_HOST не могут быть пустыми")
    try:
        http_port = int(raw_port)
    except ValueError as exc:
        raise ValueError("HTTP_PORT должен быть целым числом") from exc
    if not 1 <= http_port <= 65535:
        raise ValueError("HTTP_PORT должен быть в диапазоне 1–65535")

    return Settings(app_name, app_version, app_env, http_host, http_port)
