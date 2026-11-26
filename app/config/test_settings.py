from pathlib import Path
from secrets import token_urlsafe

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
from app.config.settings import load_settings

SECRET_KEY = token_urlsafe(48)
RUNTIME = load_settings(
    environ={"APP_ENV": "test", "DJANGO_SECRET_KEY": SECRET_KEY},
    env_file=Path("/nonexistent-commandx-test-env"),
)
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
