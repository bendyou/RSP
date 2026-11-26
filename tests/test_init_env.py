from pathlib import Path
from secrets import token_urlsafe
import stat
from tempfile import TemporaryDirectory
from unittest import TestCase

from dotenv import dotenv_values

from tools.init_env import initialize_env


class InitEnvTests(TestCase):
    def test_creates_private_local_env_with_generated_secret(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text(
                "APP_NAME=CommandX\nDJANGO_SECRET_KEY=\n"
            )
            self.assertTrue(initialize_env(root))
            values = dotenv_values(root / ".env")
            self.assertEqual(values["APP_NAME"], "CommandX")
            self.assertGreaterEqual(len(values["DJANGO_SECRET_KEY"]), 32)
            self.assertEqual(stat.S_IMODE((root / ".env").stat().st_mode), 0o600)

    def test_existing_local_env_is_never_overwritten(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text("DJANGO_SECRET_KEY=\n")
            original = f"APP_NAME=Existing\nDJANGO_SECRET_KEY={token_urlsafe(48)}\n"
            (root / ".env").write_text(original)
            self.assertFalse(initialize_env(root))
            self.assertEqual((root / ".env").read_text(), original)

    def test_adds_missing_secret_preserving_existing_parameters(self):
        for line in ("", "DJANGO_SECRET_KEY=\n", 'DJANGO_SECRET_KEY=""\n'):
            with self.subTest(line=line), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / ".env").write_text("APP_NAME=Existing\nHTTP_PORT=8123\n" + line)
                self.assertTrue(initialize_env(root))
                values = dotenv_values(root / ".env")
                self.assertEqual(values["APP_NAME"], "Existing")
                self.assertEqual(values["HTTP_PORT"], "8123")
                self.assertGreaterEqual(len(values["DJANGO_SECRET_KEY"]), 32)

    def test_two_projects_get_different_secrets(self):
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            roots = [Path(first), Path(second)]
            for root in roots:
                (root / ".env.example").write_text("DJANGO_SECRET_KEY=\n")
                initialize_env(root)
            self.assertNotEqual(
                dotenv_values(roots[0] / ".env")["DJANGO_SECRET_KEY"],
                dotenv_values(roots[1] / ".env")["DJANGO_SECRET_KEY"],
            )
