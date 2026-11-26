import argparse
import json
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(
    description="Проверка отдельной учебной PostgreSQL после применения database/schema.sql"
)
parser.add_argument("--database-url", required=True)
args = parser.parse_args()
models = json.loads((ROOT / "database/model-snapshot.json").read_text())
field_count = 0
foreign_keys = 0
with psycopg2.connect(args.database_url) as connection:
    connection.set_session(readonly=True)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
        )
        assert cursor.fetchone()[0] == 12, "Ожидалась пустая учебная схема из 12 таблиц"
        for model in models:
            cursor.execute(
                """
                SELECT a.attname, format_type(a.atttypid, a.atttypmod), NOT a.attnotnull
                FROM pg_attribute a
                JOIN pg_class t ON t.oid=a.attrelid
                JOIN pg_namespace n ON n.oid=t.relnamespace
                WHERE n.nspname='public' AND t.relname=%s AND a.attnum>0 AND NOT a.attisdropped
                ORDER BY a.attnum
            """,
                (model["table"],),
            )
            rows = cursor.fetchall()
            expected = [
                (
                    field["column"],
                    field["type"]
                    .replace("varchar", "character varying")
                    .replace(", ", ","),
                    field["null"],
                )
                for field in model["fields"]
            ]
            assert rows == expected, (model["table"], rows, expected)
            cursor.execute(
                """
                SELECT c.contype, pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_class t ON t.oid=c.conrelid
                JOIN pg_namespace n ON n.oid=t.relnamespace
                WHERE n.nspname='public' AND t.relname=%s
            """,
                (model["table"],),
            )
            constraints = cursor.fetchall()
            assert sum(kind == "p" for kind, _ in constraints) == 1
            for field in model["fields"]:
                if field["target"]:
                    assert any(
                        kind == "f"
                        and f"FOREIGN KEY ({field['column']}) REFERENCES {field['target']}(id)"
                        in definition
                        for kind, definition in constraints
                    )
                    foreign_keys += 1
                if field["unique"] and not field["pk"]:
                    assert any(
                        kind == "u" and f"UNIQUE ({field['column']})" == definition
                        for kind, definition in constraints
                    )
            field_count += len(rows)
        cursor.execute(
            "SELECT indexdef FROM pg_indexes WHERE schemaname='public' AND tablename='api_servermetric'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        for fields in (
            "(server_id, created_at DESC)",
            "(allocated_server_id, created_at DESC)",
        ):
            assert any(fields in definition for definition in indexes), fields
print(
    f"OK: 12 таблиц; {len(models)} основных сущностей, {field_count} полей, {foreign_keys} FK; типы, NULL, PK, UNIQUE и индексы"
)
print("OK: проверка read-only, без изменения данных")
