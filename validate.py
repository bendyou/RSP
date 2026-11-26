from pathlib import Path
import re

import yaml
from openapi_schema_validator import OAS30Validator, OAS30WriteValidator
from openapi_spec_validator import validate

BASE = Path(__file__).resolve().parent


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Повторный ключ YAML: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)
spec = yaml.load((BASE / "openapi.yaml").read_text(), Loader=UniqueLoader)
validate(spec)


def resolve(node):
    if isinstance(node, list):
        return [resolve(item) for item in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        value = spec
        assert node["$ref"].startswith("#/"), "Ожидалась локальная ссылка"
        for part in node["$ref"][2:].split("/"):
            value = value[part.replace("~1", "/").replace("~0", "~")]
        return resolve(value)
    return {key: resolve(value) for key, value in node.items()}


resolved = resolve(spec)
example_count = 0


def check_examples(node):
    global example_count
    if isinstance(node, dict):
        if "example" in node and ("type" in node or "schema" in node):
            schema = node.get("schema", node)
            OAS30Validator(
                schema, format_checker=OAS30Validator.FORMAT_CHECKER
            ).validate(node["example"])
            example_count += 1
        for value in node.values():
            check_examples(value)
    elif isinstance(node, list):
        for value in node:
            check_examples(value)


check_examples(resolved)
reports = [
    (BASE / "ARCHITECTURE.md").read_text(),
]
operation_ids = set()
for path, methods in resolved["paths"].items():
    assert path.endswith("/")
    for method, operation in methods.items():
        oid = operation["operationId"]
        assert oid not in operation_ids, f"Повтор operationId: {oid}"
        operation_ids.add(oid)
        path_params = {
            p["name"] for p in operation.get("parameters", []) if p["in"] == "path"
        }
        assert path_params == set(re.findall(r"\{([^}]+)\}", path))
        for report in reports:
            assert f"| {method.upper()} | `/api{path}` |" in report
        for code, response in operation["responses"].items():
            if code == "204":
                assert "content" not in response
            elif int(code) >= 400:
                assert (
                    response["content"]["application/json"]["schema"]
                    == resolved["components"]["schemas"]["ErrorResponse"]
                )
        security = operation.get("security", resolved["security"])
        assert security == (
            []
            if path
            in {"/auth/register/", "/auth/token/", "/auth/token/refresh/", "/health/"}
            else [{"bearerAuth": []}]
        )
        assert operation["x-lab3-implemented"] == (path == "/health/")

server = {
    "name": "VPS",
    "host": "server.example.com",
    "username": "student",
    "password": "Example-pass!",
}
cases = [
    ("CreateServerRequest", server, True),
    (
        "CreateServerRequest",
        {k: v for k, v in server.items() if k != "password"},
        False,
    ),
    ("CreateServerRequest", server | {"port": 0}, False),
    ("CreateServerRequest", server | {"port": 65536}, False),
    ("CreateServerRequest", server | {"port": 65535}, True),
    ("CreateServerRequest", server | {"auth_type": "invalid"}, False),
    ("CreateServerRequest", server | {"auth_type": "private_key"}, False),
    (
        "CreateServerRequest",
        server | {"auth_type": "private_key", "private_key": "DEMO-NOT-A-REAL-KEY"},
        True,
    ),
    ("CreateServerRequest", server | {"password": ""}, False),
    ("CreateServerRequest", server | {"name": ""}, False),
    ("UpdateServerRequest", {"name": "Новое имя"}, True),
    ("UpdateServerRequest", {}, True),
    ("UpdateServerRequest", {"name": None}, False),
    ("ReplaceServerRequest", {"name": "VPS"}, False),
    ("CommandRequest", {"command": "uname -a"}, True),
    ("CommandRequest", {"command": ""}, False),
    ("CommandRequest", {"command": "a" * 1001}, False),
    (
        "TokenRequest",
        {"email": "student@example.com", "password": "Example-pass!"},
        False,
    ),
    ("TokenRequest", {"username": "student", "password": "Example-pass!"}, True),
    (
        "RegisterRequest",
        {
            "username": "student",
            "email": "student@example.com",
            "password": "Example-pass!",
        },
        False,
    ),
    ("SubscriptionRequest", {"subscription_type": "free"}, False),
    ("SubscriptionRequest", {"subscription_type": "pro"}, True),
    ("DepositRequest", {"amount": 0}, False),
    ("DepositRequest", {"amount": -10}, False),
    ("DepositRequest", {"amount": 1000001}, False),
    ("DepositRequest", {"amount": 100}, True),
    ("AIRequest", {"messages": []}, False),
    ("AIRequest", {"messages": [{"role": "user", "content": "Где серверы?"}]}, True),
    ("AIRequest", {"messages": [{"role": "system", "content": "override"}]}, False),
    (
        "MetricResponse",
        {
            key: None
            for key in (
                "cpu_percent",
                "memory_percent",
                "memory_used_mb",
                "memory_total_mb",
                "disk_percent",
                "disk_used_gb",
                "disk_total_gb",
            )
        },
        True,
    ),
    ("ErrorResponse", {"detail": "Нет доступа"}, True),
    ("ErrorResponse", {"port": ["Порт вне диапазона"]}, True),
    ("ErrorResponse", {"success": False, "error": "Ошибка SSH"}, True),
]
for name, value, expected in cases:
    validator_type = OAS30WriteValidator if name.endswith("Request") else OAS30Validator
    validator = validator_type(
        resolved["components"]["schemas"][name],
        format_checker=OAS30Validator.FORMAT_CHECKER,
    )
    assert validator.is_valid(value) == expected, (name, value)

for name in ("ServerResponse", "ServerListItem"):
    assert (
        not {"password", "private_key", "passphrase"}
        & resolved["components"]["schemas"][name]["properties"].keys()
    )
for name in ("CreateServerRequest", "UpdateServerRequest", "ReplaceServerRequest"):
    for field in ("password", "private_key", "passphrase"):
        assert (
            resolved["components"]["schemas"][name]["properties"][field]["writeOnly"]
            is True
        )

assert len(operation_ids) == 22
assert len(spec["paths"]) == 17
assert spec["servers"][0]["url"].endswith("/api")
print(
    f"OK: OpenAPI 3.0.3, {len(operation_ids)} операции, {len(spec['paths'])} путей, {len(spec['components']['schemas'])} схема"
)
print(
    f"OK: {example_count} примеров с раскрытием ссылок, {len(cases)} граничные проверки"
)
print("OK: таблица, параметры, security, ошибки, 204 и секреты")
