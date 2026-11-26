import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP_NAME = os.getenv("APP_NAME", "CommandX")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
if not 1 <= HTTP_PORT <= 65535:
    raise ValueError("HTTP_PORT должен быть от 1 до 65535")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("Укажите DJANGO_SECRET_KEY в .env")

DEBUG = APP_ENV == "development"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
ROOT_URLCONF = "app.controller"
INSTALLED_APPS = ["rest_framework"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "UNAUTHENTICATED_USER": None,
}
