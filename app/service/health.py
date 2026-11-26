from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class ServiceInfo:
    name: str
    version: str
    environment: str


class HealthService:
    def __init__(self, info: ServiceInfo) -> None:
        self._info = info
        self._started_at = monotonic()

    def get_status(self) -> dict[str, str | int]:
        return {
            "status": "pass",
            "app_name": self._info.name,
            "version": self._info.version,
            "environment": self._info.environment,
            "uptime_seconds": max(0, int(monotonic() - self._started_at)),
        }
