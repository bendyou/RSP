# Лабораторная №3 · Каркас Django REST Framework

**CommandX · Python · Django 5.2 · DRF**

Цель — подготовить слои backend, конфигурацию из `.env` и работающий health-check для проекта из лабораторных №1–№2. Стек совпадает с исходным `pic_project`. Реализован только `GET /api/health/`; SSH, JWT, CRUD, модели и миграции в этой работе ещё не добавлены.

## Соответствие этапу

| Требование | Результат |
| --- | --- |
| Инициализация backend | Django/DRF, закреплённые прямые зависимости, manage.py, WSGI/ASGI |
| Слои | controller → service; repository подготовлен для следующих заданий |
| Конфигурация | .env, приоритет окружения процесса, валидация порта и значений |
| Health-check | 200 JSON без JWT, БД и внешних сервисов |
| Git | .env и окружения исключены; ветка lab3 |

## Запуск

Python 3.12–3.14, команды из корня репозитория:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r lab3/requirements.txt
test -f lab3/.env || cp lab3/.env.example lab3/.env
.venv/bin/python lab3/main.py
```

`main.py` берёт host/port из конфигурации. По умолчанию: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/). Остановка — Ctrl+C. Альтернативный запуск с явным адресом:

```sh
.venv/bin/python lab3/manage.py runserver 127.0.0.1:8000
```

Миграции не требуются: собственных моделей нет, health не открывает соединение с БД. `DATABASE_URL` по умолчанию указывает SQLite в памяти. Зависимость PostgreSQL подготовлена для дальнейших работ, но не означает проверку готовности PostgreSQL.

## Проверка

```sh
curl -i http://127.0.0.1:8000/api/health/
.venv/bin/python lab3/manage.py check
.venv/bin/python lab3/manage.py test tests --settings=app.config.test_settings
```

Ожидается HTTP 200, `Content-Type: application/json`:

```json
{"status":"pass","app_name":"CommandX","version":"1.0.0","environment":"development","uptime_seconds":0}
```

Uptime отсчитывается с создания сервиса монотонными часами и растёт. Ответ не содержит секретов. Тесты запрещают доступ к БД на уровне SimpleTestCase, проверяют публичность маршрута, метод 405, отсутствие будущего CRUD, подмену сервиса, конфигурацию и секреты.

Swagger UI смотрите отдельно по инструкции [№2](../lab2/README.md); `/docs` FastAPI здесь отсутствует. Наличие остальных маршрутов в OpenAPI не означает их реализации в каркасе.

## Конфигурация

| Переменная | По умолчанию / правило |
| --- | --- |
| APP_NAME / APP_VERSION | CommandX / 1.0.0, непустые |
| APP_ENV | development; допустимы test, production |
| HTTP_HOST / HTTP_PORT | 127.0.0.1 / 8000, порт 1–65535 |
| DEBUG | true локально; false в production |
| ALLOWED_HOSTS | localhost,127.0.0.1; непустой список |
| DJANGO_SECRET_KEY | Только локальный fallback; для DEBUG=false/production нужен собственный секрет от 32 символов |
| DATABASE_URL | sqlite:///:memory:; пока не используется маршрутом |

Значения процесса имеют приоритет над `.env`. Загрузка настроек не изменяет `os.environ`. `.env.example` не содержит ключей и паролей. Тестовые настройки используют отдельную SQLite в памяти. Django runserver предназначен для локальной разработки; настройки полноценного развёртывания относятся к дальнейшим этапам.

## Структура

```text
lab3/
├── app/
│   ├── config/       настройки и Django-конфигурация
│   ├── controller/   DRF HTTP-адаптер и сериализатор
│   ├── service/      health без зависимости от HTTP
│   ├── repository/   пока без реализации БД
│   ├── urls.py       сборка зависимостей и маршрутов
│   ├── asgi.py
│   └── wsgi.py
├── tests/
├── .env.example
├── main.py
├── manage.py
└── requirements.txt
```

## Контрольные вопросы

1. **Почему сервис не должен зависеть от HTTP?** Один сценарий можно вызвать из контроллера, CLI и теста; сервис получает значения и зависимости вместо request/Response.
2. **Почему секреты не хранят в исходниках?** Они распространяются вместе с репозиторием и сохраняются в истории. `.env` исключён из Git, продакшен-секрет задаётся окружением.
3. **Зачем .env.example?** Документирует формат локальных настроек и помогает запустить приложение без копирования чужих секретов.
4. **Что проверяет health?** Только ответ процесса API. Доступность БД, SSH-хостов и AI он не проверяет; для них позже нужен отдельный readiness-контракт.
5. **Зачем инверсия зависимостей?** Контроллер получает HealthService при сборке URL. В дальнейшем сервис получает интерфейс репозитория, а ORM-реализацию передают снаружи.

Ветка для сдачи: [lab3](https://github.com/bendyou/RSP/tree/lab3). Следующий агент должен сначала прочитать [AGENTS.md](../AGENTS.md). Лабораторная №4 не выполнялась.
