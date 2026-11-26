# Проверка лабораторной №3

Каркас Django REST Framework для CommandX: конфигурация .env, слои controller/service/repository, WSGI/ASGI и GET /api/health/. Модели, JWT и CRUD в этот этап не входят.

На Python 3.14 прошли Django system check и 12 тестов: публичность health, JSON, запрет записи, отсутствие будущего CRUD, подмена сервиса, монотонный uptime, приоритет окружения и валидация настроек. Проверен реальный loopback HTTP 200 без обращения к БД и внешним сервисам. [Команды](../README.md).

Для №3 отдельная методичка в исходном каталоге не найдена; проверены сохранённые требования прежнего README. [Контекст источника](PROJECT_CONTEXT.md).

В этой ветке находятся только файлы №3. [№1](https://github.com/bendyou/RSP/tree/lab1) и [№2](https://github.com/bendyou/RSP/tree/lab2) размещены отдельно. Лабораторная №4 не выполнялась. Перед её выполнением нужно прочитать [AGENTS.md](../AGENTS.md) и получить реальное задание.
