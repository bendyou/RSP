"""HTTP-адаптер для проверки состояния приложения."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.service.health import HealthService


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    uptime_seconds: int = Field(ge=0)


def create_health_router(service: HealthService) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/health", response_model=HealthResponse, tags=["service"])
    def health() -> HealthResponse:
        return HealthResponse(**service.get_status())

    return router
