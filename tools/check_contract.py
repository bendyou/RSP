import os
from pathlib import Path
import re
import sys

import yaml
from openapi_schema_validator import OAS30ReadValidator
from openapi_spec_validator import validate

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


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
spec = yaml.load((ROOT / "openapi.yaml").read_text(), Loader=UniqueLoader)
validate(spec)
ids = set()
implemented = set()
operation_count = 0
for path, item in spec["paths"].items():
    for method, operation in item.items():
        if method not in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
        }:
            continue
        oid = operation["operationId"]
        assert oid not in ids, oid
        ids.add(oid)
        parameters = item.get("parameters", []) + operation.get("parameters", [])
        assert set(re.findall(r"\{([^}]+)\}", path)) == {
            parameter["name"]
            for parameter in parameters
            if parameter.get("in") == "path"
        }
        if operation["x-lab3-implemented"]:
            assert method == "get"
            assert operation["security"] == []
            implemented.add(path)
        operation_count += 1
assert implemented == {"/api/v1/health", "/health", "/api/health/"}
assert operation_count == 24

os.environ["DJANGO_SETTINGS_MODULE"] = "app.config.test_settings"
import django

django.setup()
from django.db import connection
from django.test import Client


def no_database(*args, **kwargs):
    raise AssertionError("Health-check не должен обращаться к БД")


client = Client()
schema = spec["components"]["schemas"]["HealthResponse"]
with connection.execute_wrapper(no_database):
    for path in sorted(implemented):
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["Content-Type"] == "application/json"
        assert "Location" not in response.headers
        OAS30ReadValidator(schema).validate(response.json())
print(
    f"OK: OpenAPI 3.0.3, {operation_count} операции, 21 контрактная и 3 реализованных"
)
print(
    "OK: /api/v1/health, /health, /api/health/ — 200 JSON по схеме, без БД и перенаправления"
)
