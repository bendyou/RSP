import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from app.config.settings import DEV_SECRET, load_settings


class SettingsTests(TestCase):
    def settings(self, values):
        return load_settings(
            env_file=Path("/nonexistent-commandx-test-env"), environ=values
        )

    def test_defaults_work_without_env_file(self):
        settings = self.settings({})
        self.assertEqual(settings.app_name, "CommandX")
        self.assertEqual(settings.http_port, 8000)
        self.assertTrue(settings.debug)

    def test_process_values_override_file_without_mutating_environment(self):
        before = dict(os.environ)
        with TemporaryDirectory() as folder:
            path = Path(folder) / ".env"
            path.write_text("APP_NAME=From-file\nHTTP_PORT=8001\n")
            settings = load_settings(path, environ={"HTTP_PORT": "8123"})
        self.assertEqual(settings.app_name, "From-file")
        self.assertEqual(settings.http_port, 8123)
        self.assertEqual(dict(os.environ), before)

    def test_invalid_ports_are_rejected(self):
        for port in ("0", "65536", "abc", ""):
            with self.subTest(port=port), self.assertRaises(ValueError):
                self.settings({"HTTP_PORT": port})

    def test_invalid_values_are_rejected(self):
        for name, value in [
            ("APP_NAME", " "),
            ("APP_ENV", "other"),
            ("DEBUG", "yes"),
            ("ALLOWED_HOSTS", ", ,"),
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.settings({name: value})

    def test_production_requires_secret_and_debug_off(self):
        for values in (
            {"APP_ENV": "production"},
            {"DEBUG": "false"},
            {"APP_ENV": "production", "DEBUG": "true", "DJANGO_SECRET_KEY": "x" * 40},
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.settings(values)
        self.assertFalse(
            self.settings(
                {"APP_ENV": "production", "DJANGO_SECRET_KEY": "x" * 40}
            ).debug
        )

    def test_secrets_are_not_in_repr(self):
        self.assertNotIn(DEV_SECRET, repr(self.settings({})))
        self.assertNotIn("sqlite://", repr(self.settings({})))
