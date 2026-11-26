# CommandX · Лабораторные №1–№2

**Разработка серверных приложений — архитектура и REST API**

SSH-панель на Django REST Framework и React/TypeScript. Эта ветка продолжает №1 и содержит контракт №2, согласованный с реальным CommandX.

[Архитектура](ARCHITECTURE.md) · [OpenAPI](openapi.yaml) · [Отчёт №2](lab2/ARCHITECTURE.md) · [Проверки](docs/REVIEW.md)

| № | Результат | Ветка |
| --- | --- | --- |
| 1 | [C4, ERD, 6 сущностей и PostgreSQL DDL](lab1/README.md) | [lab1](https://github.com/bendyou/RSP/tree/lab1) |
| 2 | [22 операции, 17 путей, 31 схема и Swagger UI](lab2/README.md) | [lab2](https://github.com/bendyou/RSP/tree/lab2) |

## Swagger UI

```sh
python3 -m http.server 8082 --bind 127.0.0.1 --directory lab2
```

Откройте [http://127.0.0.1:8082/swagger.html](http://127.0.0.1:8082/swagger.html). Документация полностью локальная, отправка запросов отключена. API-сервер в этой ветке не реализован; маршруты описывают исходный CommandX и будущий health-check №3.

## Проверка

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r lab2/requirements-validation.txt
.venv/bin/python lab2/validate.py
.venv/bin/python tools/check_docs.py
```

OpenAPI 3.0.3, примеры, 33 граничных случая, таблицы и копии проверяются автоматически. [Снимки и результаты](lab2/VALIDATION.md). Схема БД проверяется отдельно по [инструкции №1](lab1/README.md).

`lab2` включает №1–№2, `main` собирает завершённые этапы. Каркас №3 будет в следующей ветке; №4 не выполнялась. Следующий агент должен прочитать [AGENTS.md](AGENTS.md).
