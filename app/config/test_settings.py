from pathlib import Path

from app.config.base_settings import (
    ASGI_APPLICATION,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    MIDDLEWARE,
    REST_FRAMEWORK,
    ROOT_URLCONF,
    TIME_ZONE,
    USE_TZ,
    WSGI_APPLICATION,
)
from app.config.settings import DEV_SECRET, load_settings

RUNTIME = load_settings(
    environ={"APP_ENV": "test"}, env_file=Path("/nonexistent-commandx-test-env")
)
SECRET_KEY = DEV_SECRET
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
