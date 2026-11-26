from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.service import get_health


@api_view(["GET"])
def health(request):
    return Response(get_health(settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV))


urlpatterns = [path("api/v1/health", health)]
