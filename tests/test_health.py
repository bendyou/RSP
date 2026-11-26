from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from app.controller.health import HealthView
from app.service.health import HealthService, ServiceInfo


class HealthTests(SimpleTestCase):
    def test_public_health_without_database(self):
        self.assertEqual(reverse("health"), "/api/v1/health")
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        payload = response.json()
        self.assertEqual(
            set(payload),
            {"status", "app_name", "version", "environment", "uptime_seconds"},
        )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["app_name"], "CommandX")
        self.assertIsInstance(payload["uptime_seconds"], int)
        self.assertGreaterEqual(payload["uptime_seconds"], 0)

    def test_aliases_return_json_without_authentication_or_redirect(self):
        for path in ("/api/v1/health", "/health", "/api/health/"):
            with self.subTest(path=path):
                response = self.client.get(
                    path, HTTP_AUTHORIZATION="Bearer invalid-demo-token"
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["Content-Type"], "application/json")
                self.assertNotIn("Location", response.headers)

    def test_write_is_not_allowed(self):
        self.assertEqual(
            self.client.post(
                reverse("health"), {}, content_type="application/json"
            ).status_code,
            405,
        )

    def test_future_routes_are_not_implemented(self):
        self.assertEqual(self.client.get("/api/servers/").status_code, 404)

    def test_service_uses_monotonic_time(self):
        with patch("app.service.health.monotonic", side_effect=[100.5, 104.9]):
            service = HealthService(ServiceInfo("CommandX", "1.0.0", "test"))
            self.assertEqual(service.get_status()["uptime_seconds"], 4)

    def test_head_has_no_body(self):
        response = self.client.head("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_health_does_not_expose_configuration_secrets(self):
        from django.conf import settings

        response = self.client.get("/api/v1/health")
        self.assertNotIn(settings.SECRET_KEY, response.content.decode())
        self.assertNotIn("database_url", response.json())

    def test_controller_accepts_explicit_service(self):
        from rest_framework.test import APIRequestFactory
        from unittest.mock import Mock

        service = Mock()
        service.get_status.return_value = {
            "status": "pass",
            "app_name": "Injected",
            "version": "1",
            "environment": "test",
            "uptime_seconds": 7,
        }
        response = HealthView.as_view(service=service)(
            APIRequestFactory().get("/api/health/")
        )
        self.assertEqual(response.data["app_name"], "Injected")
        service.get_status.assert_called_once_with()
