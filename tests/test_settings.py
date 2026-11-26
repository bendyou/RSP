import os
from pathlib import Path
from secrets import token_urlsafe
from tempfile import TemporaryDirectory
from unittest import TestCase

from app.config.settings import load_settings


class SettingsTests(TestCase):
    secret = token_urlsafe(48)

    def settings(self, values):
        return load_settings(
            env_file=Path("/nonexistent-commandx-test-env"),
            environ={"DJANGO_SECRET_KEY": self.secret, **values},
        )

    def test_nonsecret_defaults_with_secret_from_environment(self):
        settings = self.settings({})
        self.assertEqual(settings.app_name, "CommandX")
        self.assertEqual(settings.http_port, 8000)
        self.assertTrue(settings.debug)

    def test_process_values_override_file_without_mutating_environment(self):
        before = dict(os.environ)
        with TemporaryDirectory() as folder:
            path = Path(folder) / ".env"
            path.write_text("APP_NAME=From-file\nHTTP_PORT=8001\n")
            settings = load_settings(
                path, environ={"HTTP_PORT": "8123", "DJANGO_SECRET_KEY": self.secret}
            )
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

    def test_secret_is_required_in_every_environment(self):
        for values in ({}, {"APP_ENV": "production"}, {"DEBUG": "false"}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                load_settings(
                    env_file=Path("/nonexistent-commandx-test-env"), environ=values
                )

    def test_production_requires_debug_off(self):
        with self.assertRaises(ValueError):
            self.settings({"APP_ENV": "production", "DEBUG": "true"})
        self.assertFalse(self.settings({"APP_ENV": "production"}).debug)

    def test_secrets_are_not_in_repr(self):
        self.assertNotIn(self.secret, repr(self.settings({})))
        self.assertNotIn("sqlite://", repr(self.settings({})))

    def test_blank_or_short_secret_is_rejected(self):
        for secret in ("", " " * 32, "x" * 31):
            with self.subTest(length=len(secret)), self.assertRaises(ValueError):
                self.settings({"DJANGO_SECRET_KEY": secret})
