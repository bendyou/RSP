from django.conf import settings
from django.urls import path

from app.controller.health import HealthView
from app.service.health import HealthService

health_service = HealthService(settings.RUNTIME)
urlpatterns = [
    path("api/health/", HealthView.as_view(service=health_service), name="health")
]
