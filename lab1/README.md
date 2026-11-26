# Лабораторная №1 · Архитектура CommandX

Проектирование серверного приложения и предметной области существующей SSH-панели. Стек: Django REST Framework, React/TypeScript и SQLite/PostgreSQL.

| Результат | Файл |
| --- | --- |
| Роли, 11 Use Cases, C4, словарь данных и 3НФ | [ARCHITECTURE.md](ARCHITECTURE.md) |
| C4 Container | [SVG](diagrams/c4-containers.svg) · [DOT](diagrams/c4-containers.dot) |
| ERD шести основных сущностей | [SVG](diagrams/erd.svg) · [DOT](diagrams/erd.dot) |
| Физическая схема с auth-инфраструктурой | [PostgreSQL SQL](database/schema.sql) |

Полный отчёт также находится в корневом [ARCHITECTURE.md](../ARCHITECTURE.md) по требованию задания. Ветка для сдачи — [lab1](https://github.com/bendyou/RSP/tree/lab1).

Диаграммы можно читать без установки зависимостей. Команды Graphviz и создания схемы в отдельной пустой базе приведены в разделе 6 отчёта. Данные и секреты исходного проекта не копируются. SQL не следует применять к рабочей БД.

## Проверка схемы

После создания отдельной учебной БД из SQL, из корня репозитория:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r lab1/requirements-validation.txt
.venv/bin/python tools/check_schema.py --database-url postgresql:///commandx_lab1
```

Проверка read-only: 12 таблиц с auth-инфраструктурой, 66 полей шести основных сущностей, 6 FK, ключи и индексы. [Машинный снимок моделей](database/model-snapshot.json) не содержит пользовательских записей.
