from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.service.health import HealthService


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pass"])
    app_name = serializers.CharField()
    version = serializers.CharField()
    environment = serializers.CharField()
    uptime_seconds = serializers.IntegerField(min_value=0)


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    service: HealthService | None = None

    def get(self, request):
        if self.service is None:
            raise RuntimeError(
                "HealthService должен быть передан при сборке приложения"
            )
        payload = HealthResponseSerializer(data=self.service.get_status())
        payload.is_valid(raise_exception=True)
        return Response(payload.validated_data)
