"""Точка входа HTTP-сервиса панели управления."""

from fastapi import FastAPI
import uvicorn

from app.config.settings import Settings, load_settings
from app.controller.health import create_health_router
from app.service.health import HealthService


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(create_health_router(HealthService(settings)))
    return app


app = create_app()


if __name__ == "__main__":
    settings = load_settings()
    uvicorn.run(app, host=settings.http_host, port=settings.http_port)
