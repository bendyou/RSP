"""Информация о работоспособности процесса приложения."""

from time import monotonic

from app.config.settings import Settings


class HealthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._started_at = monotonic()

    def get_status(self) -> dict[str, str | int]:
        return {
            "status": "pass",
            "app_name": self._settings.app_name,
            "version": self._settings.app_version,
            "environment": self._settings.app_env,
            "uptime_seconds": max(0, int(monotonic() - self._started_at)),
        }
