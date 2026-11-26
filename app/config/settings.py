from collections.abc import Mapping
from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import dotenv_values

PROJECT_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    http_host: str
    http_port: int
    debug: bool
    allowed_hosts: tuple[str, ...]
    secret_key: str = field(repr=False)
    database_url: str = field(repr=False)


def load_settings(
    env_file: Path | None = None, environ: Mapping[str, str] | None = None
) -> Settings:
    file_values = dotenv_values(
        env_file if env_file is not None else PROJECT_DIR / ".env", interpolate=False
    )
    values = {key: value for key, value in file_values.items() if value is not None}
    values.update(os.environ if environ is None else environ)

    def value(name: str, default: str) -> str:
        result = values.get(name, default).strip()
        if not result:
            raise ValueError(f"{name} не может быть пустым")
        return result

    app_name = value("APP_NAME", "CommandX")
    app_version = value("APP_VERSION", "1.0.0")
    app_env = value("APP_ENV", "development")
    if app_env not in {"development", "test", "production"}:
        raise ValueError("APP_ENV: development, test или production")
    http_host = value("HTTP_HOST", "127.0.0.1")
    try:
        http_port = int(value("HTTP_PORT", "8000"))
    except ValueError as exc:
        raise ValueError("HTTP_PORT должен быть целым числом") from exc
    if not 1 <= http_port <= 65535:
        raise ValueError("HTTP_PORT должен быть в диапазоне 1–65535")
    raw_debug = value("DEBUG", "false" if app_env == "production" else "true").lower()
    if raw_debug not in {"true", "false"}:
        raise ValueError("DEBUG: true или false")
    debug = raw_debug == "true"
    allowed_hosts = tuple(
        host.strip()
        for host in value("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
        if host.strip()
    )
    if not allowed_hosts:
        raise ValueError("ALLOWED_HOSTS должен содержать хотя бы один hostname")
    secret_key = value("DJANGO_SECRET_KEY", "")
    if len(secret_key) < 32:
        raise ValueError(
            "DJANGO_SECRET_KEY должен содержать собственный секрет длиной от 32 символов"
        )
    if app_env == "production" and debug:
        raise ValueError("В production DEBUG должен быть false")

    return Settings(
        app_name,
        app_version,
        app_env,
        http_host,
        http_port,
        debug,
        allowed_hosts,
        secret_key,
        value("DATABASE_URL", "sqlite:///:memory:"),
    )
