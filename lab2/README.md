# Лабораторная №2 · REST API CommandX

**22 операции · 17 путей · 31 схемы · OpenAPI 3.0.3**

Контракт продолжает архитектуру CommandX из №1 и сохраняет формат существующего Django/DRF API. Основной CRUD — собственные SSH-серверы. [Отчёт и контрольные вопросы](ARCHITECTURE.md) · [Спецификация](openapi.yaml) · [Результаты проверки](VALIDATION.md).

## Просмотр Swagger UI

Из корня репозитория:

```sh
python3 -m http.server 8082 --bind 127.0.0.1 --directory lab2
```

Откройте [http://127.0.0.1:8082/swagger.html](http://127.0.0.1:8082/swagger.html). Swagger UI включён локально вместе с лицензией, CDN не нужен. Отправка запросов отключена: учебный №3 содержит только health-check. HTTP-сервер здесь обслуживает файлы документации. Остановка — Ctrl+C.

## Проверка спецификации

Python 3.12–3.14, из корня:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r lab2/requirements-validation.txt
.venv/bin/python lab2/validate.py
```

Проверяются OpenAPI, ссылки, уникальность ключей YAML и operationId, примеры, таблицы маршрутов, ограничения запросов, ответы 204, write_only секреты и совпадение корневой копии. Установка требует интернета, последующая проверка локальная.

При изменении канонического `lab2/openapi.yaml` обновляйте копию `openapi.yaml` в корне и обе таблицы отчётов. Ветка для сдачи — [lab2](https://github.com/bendyou/RSP/tree/lab2). Корневые ARCHITECTURE.md и openapi.yaml соответствуют расположению из задания.
