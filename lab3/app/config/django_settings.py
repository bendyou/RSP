import dj_database_url

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

RUNTIME = load_settings()
SECRET_KEY = RUNTIME.secret_key
DEBUG = RUNTIME.debug
ALLOWED_HOSTS = list(RUNTIME.allowed_hosts)
DATABASES = {"default": dj_database_url.parse(RUNTIME.database_url, conn_max_age=0)}
