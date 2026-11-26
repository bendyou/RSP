# Проверка лабораторной №2

Контракт CommandX: 22 операции, 17 путей и 31 схема OpenAPI 3.0.3. Проверены 92 примера с раскрытием ссылок, 33 граничных случая, права, отсутствие SSH-секретов в ответах и 204 без тела. Swagger UI показывает все операции без ошибок JavaScript. [Подробности](../VALIDATION.md).

При сверке 26 ноября 2026 года 21 операция найдена в исходных URL, 40 ответов прошли схемы контракта. Использовалась SQLite в памяти, SSH подменялся; рабочий .env и внешние сервисы не использовались. [Контрольные суммы 22 файлов](source-manifest.json).

Повторение сверки после установки зависимостей контракта, с собственным путём:

```sh
COMMANDX_SOURCE=/path/to/pic_project
.venv/bin/python -m pip install -r "$COMMANDX_SOURCE/backend/requirements.txt"
.venv/bin/python tools/check_reference.py --source "$COMMANDX_SOURCE"
```

В этой ветке только файлы №2. [Архитектура №1](https://github.com/bendyou/RSP/blob/lab1/ARCHITECTURE.md) и [каркас №3](https://github.com/bendyou/RSP/tree/lab3) находятся отдельно. №4 не выполнялась.
