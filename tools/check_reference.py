import argparse
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from unittest.mock import patch

import yaml
from openapi_schema_validator import OAS30ReadValidator

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(
    description="Сверка контракта с изолированным исходным CommandX, без .env и внешних сервисов"
)
parser.add_argument("--source", type=Path, required=True)
args = parser.parse_args()
source = args.source.resolve()
manifest = json.loads((ROOT / "docs/source-manifest.json").read_text())
for name, expected in manifest["files"].items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == expected, (
        f"Исходник изменился после сверки: {name}"
    )

os.environ.pop("OPENAI_API_KEY", None)
sys.path.insert(0, str(source / "backend"))
import django
from django.conf import settings

settings.configure(
    SECRET_KEY="isolated-commandx-contract-check-key-2026",
    DEBUG=False,
    ALLOWED_HOSTS=["testserver"],
    ROOT_URLCONF="commandx.urls",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "api",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    MIDDLEWARE=[],
    TEMPLATES=[
        {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
    ],
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    USE_TZ=True,
    STATIC_URL="/static/",
    MEDIA_URL="/media/",
    PROJECT_ROOT=source,
    ENABLE_DEMO_PAYMENTS=False,
    SIMPLE_JWT={
        "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    },
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication"
        ],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
    },
)
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.urls import resolve
from rest_framework.test import APIClient

from api.models import Server

call_command("migrate", verbosity=0)
spec = yaml.safe_load((ROOT / "openapi.yaml").read_text())


def expand(node):
    if isinstance(node, list):
        return [expand(value) for value in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        target = spec
        for part in node["$ref"][2:].split("/"):
            target = target[part]
        return expand(target)
    return {key: expand(value) for key, value in node.items()}


resolved_spec = expand(spec)
route_count = 0
for path, methods in spec["paths"].items():
    if path == "/health/":
        continue
    match = resolve("/api" + re.sub(r"\{[^}]+\}", "1", path))
    for method in methods:
        if hasattr(match.func, "actions"):
            assert method in match.func.actions, (method, path)
        else:
            view_class = getattr(
                match.func, "cls", getattr(match.func, "view_class", None)
            )
            assert (
                view_class
                and method in view_class.http_method_names
                and hasattr(view_class, method)
            ), (method, path)
        route_count += 1

response_count = 0
covered = set()


def check(client, method, path, expected, body=None):
    global response_count
    actual_path = path.split("?")[0]
    contract_path = next(
        key
        for key in resolved_spec["paths"]
        if re.fullmatch("/api" + re.sub(r"\{[^}]+\}", r"\\d+", key), actual_path)
    )
    response = getattr(client, method)(path, body, format="json")
    assert response.status_code == expected, (
        method,
        path,
        response.status_code,
        response.data,
    )
    operation = resolved_spec["paths"][contract_path][method]
    contract = operation["responses"][str(expected)]
    if expected == 204:
        assert response.content == b""
    else:
        OAS30ReadValidator(
            contract["content"]["application/json"]["schema"],
            format_checker=OAS30ReadValidator.FORMAT_CHECKER,
        ).validate(response.data)
    response_count += 1
    covered.add((contract_path, method))
    return response


anonymous = APIClient()
client = APIClient()
registration = {
    "username": "student",
    "email": "student@example.com",
    "password": "Example-pass-2026!",
    "password_confirm": "Example-pass-2026!",
}
registered = check(anonymous, "post", "/api/auth/register/", 201, registration).data
check(anonymous, "post", "/api/auth/register/", 400, registration)
check(
    anonymous,
    "post",
    "/api/auth/token/",
    200,
    {"username": "student", "password": registration["password"]},
)
check(
    anonymous,
    "post",
    "/api/auth/token/",
    401,
    {"username": "student", "password": "wrong"},
)
check(
    anonymous,
    "post",
    "/api/auth/token/refresh/",
    200,
    {"refresh": registered["refresh"]},
)
check(anonymous, "get", "/api/auth/profile/", 401)
client.credentials(HTTP_AUTHORIZATION="Bearer " + registered["access"])
check(client, "get", "/api/auth/profile/", 200)
check(client, "patch", "/api/auth/profile/", 200, {"email": "changed@example.com"})
check(anonymous, "get", "/api/servers/", 401)
check(
    client,
    "post",
    "/api/servers/",
    400,
    {"name": "Demo", "host": "server.example.com", "username": "student"},
)
server_input = {
    "name": "Demo",
    "host": "server.example.com",
    "username": "student",
    "password": "Example-ssh-pass!",
}
check(client, "post", "/api/servers/", 400, server_input | {"port": 0})
server = check(client, "post", "/api/servers/", 201, server_input).data
server_id = server["id"]
assert not {"password", "private_key", "passphrase"} & server.keys()
check(client, "get", "/api/servers/", 200)
check(client, "get", f"/api/servers/{server_id}/", 200)
check(client, "patch", f"/api/servers/{server_id}/", 200, {"name": "Renamed"})
assert Server.objects.get(pk=server_id).password == server_input["password"]
check(client, "put", f"/api/servers/{server_id}/", 200, server_input)
with patch("api.views.exec_command", return_value=(1, "", "command failed")):
    result = check(
        client, "post", f"/api/servers/{server_id}/exec/", 200, {"command": "false"}
    )
    assert result.data["success"] is False
with patch("api.views.test_connection", return_value=(False, "Host key not trusted")):
    result = check(client, "post", f"/api/servers/{server_id}/test_connection/", 200)
    assert result.data["success"] is False
metric = {
    name: None
    for name in (
        "cpu_percent",
        "memory_percent",
        "memory_used_mb",
        "memory_total_mb",
        "disk_percent",
        "disk_used_gb",
        "disk_total_gb",
    )
}
metric["cpu_percent"] = 15.0
with patch("api.views.get_detailed_stats", return_value=metric):
    check(client, "get", f"/api/servers/{server_id}/detailed_stats/", 200)
check(client, "get", f"/api/servers/{server_id}/metrics_history/?hours=24", 200)
check(client, "get", f"/api/servers/{server_id}/metrics_history/?hours=0", 400)
check(client, "post", f"/api/servers/{server_id}/toggle_status/", 200)
check(client, "post", f"/api/servers/{server_id}/exec/", 403, {"command": "uname -a"})
check(client, "get", f"/api/servers/{server_id}/metrics_history/", 200)
check(client, "patch", f"/api/servers/{server_id}/", 200, {"is_active": True})

user_model = get_user_model()
other = user_model.objects.create_user(username="other", password="Example-pass-2026!")
other_client = APIClient()
other_client.force_authenticate(other)
check(other_client, "get", f"/api/servers/{server_id}/", 404)
check(other_client, "patch", f"/api/servers/{server_id}/", 404, {"name": "Forbidden"})
check(other_client, "delete", f"/api/servers/{server_id}/", 404)
check(client, "get", "/api/admin/users/", 403)
admin = user_model.objects.create_user(
    username="admin-check", password="Example-pass-2026!", is_staff=True
)
admin_client = APIClient()
admin_client.force_authenticate(admin)
check(admin_client, "get", "/api/admin/users/", 200)
check(admin_client, "get", f"/api/servers/{server_id}/", 404)

check(client, "post", "/api/payment/deposit/", 403, {"amount": 1000})
with override_settings(ENABLE_DEMO_PAYMENTS=True):
    check(client, "post", "/api/payment/deposit/", 400, {"amount": -1})
    check(client, "post", "/api/payment/deposit/", 200, {"amount": 1000})
check(
    client, "post", "/api/payment/buy-subscription/", 200, {"subscription_type": "pro"}
)
check(client, "get", "/api/payment/transactions/", 200)
check(
    client, "post", "/api/payment/buy-subscription/", 400, {"subscription_type": "plus"}
)
check(client, "post", "/api/ai/chat/", 400, {"messages": []})
check(
    client,
    "post",
    "/api/ai/chat/",
    503,
    {"messages": [{"role": "user", "content": "Где список серверов?"}]},
)
check(client, "delete", f"/api/servers/{server_id}/", 204)
assert len(covered) == route_count
print(
    f"OK: {len(manifest['files'])} SHA-256 исходников, {route_count} операция маршрутов, {response_count} ответов по контракту"
)
print(
    "OK: SQLite в памяти, без чтения .env, реальных SSH/AI/платежей и изменения исходного проекта"
)
