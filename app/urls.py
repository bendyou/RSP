from django.conf import settings
from django.urls import path

from app.controller.health import HealthView
from app.service.health import HealthService, ServiceInfo

health_service = HealthService(
    ServiceInfo(
        settings.RUNTIME.app_name,
        settings.RUNTIME.app_version,
        settings.RUNTIME.app_env,
    )
)
health_view = HealthView.as_view(service=health_service)
urlpatterns = [
    path("api/v1/health", health_view, name="health"),
    path("health", health_view, name="health-short"),
    path("api/health/", health_view, name="health-legacy"),
]
