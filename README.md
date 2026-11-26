# Лабораторная №3 · CommandX

**Базовый каркас приложения, Clean / Layered Architecture и настройка окружения**

Выполнено по [методичке ЛР3, 5 страниц](https://drive.google.com/file/d/1ItS06gGjfcJxSDQE92Z3sed-lO74Onh0/view). Проект — панель управления собственными серверами по SSH. Backend: Python, Django 5.2 и Django REST Framework, как в исходном CommandX.

[Архитектура](ARCHITECTURE.md) · [OpenAPI](openapi.yaml) · [Сверка задания](docs/ASSIGNMENT.md) · [Проверки](docs/REVIEW.md)

## Результат

Каркас разделён на конфигурацию, HTTP-контроллер, сервис и каталог репозиториев. Health-check возвращает статус, название, версию, окружение и uptime. JWT, CRUD, модели и внешние интеграции в этот этап не входят.

| URL | Назначение |
| --- | --- |
| `GET /api/v1/health` | Основной маршрут сдачи, указанный в методичке |
| `GET /health` | Короткий маршрут, разрешённый заданием |
| `GET /api/health/` | Совместимость с контрактом №2 |

Все три URL отвечают непосредственно `200 OK` и `application/json`, без JWT, БД и перенаправлений.

## Запуск

Python 3.12–3.14, из корня ветки lab3:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/init_env.py
.venv/bin/python main.py
```

`init_env.py` создаёт `.env` из `.env.example` с новым случайным секретом Django. Если `.env` уже существует, сохраняются его параметры; добавляется только отсутствующий или пустой `DJANGO_SECRET_KEY`. Существующий непустой секрет не меняется. Секрет не выводится, `.env` исключён из Git.

`main.py` читает host/port из конфигурации. По умолчанию: `127.0.0.1:8000`. Остановка — Ctrl+C. Альтернативный запуск с явным адресом: `.venv/bin/python manage.py runserver 127.0.0.1:8000`.

## Демонстрация

В другом терминале:

```sh
curl -i http://127.0.0.1:8000/api/v1/health
curl -i http://127.0.0.1:8000/health
```

Ожидается HTTP 200, `Content-Type: application/json`:

```json
{
  "status": "pass",
  "app_name": "CommandX",
  "version": "1.0.0",
  "environment": "development",
  "uptime_seconds": 0
}
```

Uptime — целые секунды с создания сервиса; значение растёт. В примере JSON методички четыре строковых поля, а практическая часть дополнительно требует uptime — реализация учитывает оба пункта.

## Структура

```text
.
├── app/
│   ├── config/          загрузка .env и настройки Django
│   ├── controller/      HTTP-адаптер и сериализатор ответа
│   ├── service/         HealthService и независимый ServiceInfo
│   ├── repository/      место для будущего доступа к данным
│   ├── urls.py          сборка зависимостей и маршруты
│   ├── asgi.py
│   └── wsgi.py
├── tests/
├── tools/
│   ├── init_env.py
│   └── check_contract.py
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── openapi.yaml
├── main.py
├── manage.py
└── requirements.txt
```

`cmd/app` и `internal` в методичке приведены как пример для разных языков. Здесь их ответственность выполняют `main.py`/`manage.py` и `app/`, с явным разделением четырёх слоёв. Репозиторий БД не реализован и не вызывается: health не нуждается в данных.

## Настройки

| Переменная | Значение / правило |
| --- | --- |
| APP_NAME / APP_VERSION | CommandX / 1.0.0, непустые |
| APP_ENV | development, test либо production |
| HTTP_HOST / HTTP_PORT | 127.0.0.1 / 8000; порт 1–65535 |
| DEBUG | true локально; в production только false |
| ALLOWED_HOSTS | Непустой список hostname через запятую |
| DJANGO_SECRET_KEY | Собственный секрет от 32 символов, обязательный во всех окружениях |
| DATABASE_URL | SQLite в памяти по умолчанию; health не подключается к БД |

Переменные процесса имеют приоритет над `.env`; загрузка не меняет `os.environ`. Неверные обязательные значения останавливают запуск с понятной ошибкой. Секрет в исходниках отсутствует. `runserver` предназначен для локальной демонстрации.

## Проверки

```sh
.venv/bin/python -m pip install -r requirements-validation.txt
.venv/bin/python manage.py check
.venv/bin/python manage.py test tests --settings=app.config.test_settings
.venv/bin/python tools/check_contract.py
.venv/bin/python tools/check_docs.py
git check-ignore .env
git ls-files --error-unmatch .env.example .gitignore
git diff --check
```

Тестовые настройки не читают рабочий `.env`; секрет тестового процесса генерируется заново. SimpleTestCase запрещает SQL. Проверяются точные маршруты задания, JSON, HEAD/405, uptime, настройки и подготовка `.env`. Проверка OpenAPI сверяет все три реальных ответа со схемой при запрете SQL. CI повторяет проверки на Python 3.12/3.13/3.14.

В `openapi.yaml` сохранены операции №2 с пометкой `x-lab3-implemented=false`. Реализованы только три health-операции. Полный Swagger UI остаётся в [lab2](https://github.com/bendyou/RSP/tree/lab2).

## Контрольные вопросы

1. **Почему сервис не должен знать HTTP?** Он получает обычные значения и решает сценарий. Разбор запроса и HTTP-ответ относятся к контроллеру. Сервис можно вызвать из CLI или теста, не связывая его с заголовками и JSON.
2. **Чем опасны секреты в коде?** Они распространяются с репозиторием, сохраняются в истории и повторяются в его копиях. Здесь секрет берётся из окружения или локального `.env`; рабочего значения в коде и `.env.example` нет.
3. **Зачем `.env.example`?** Он документирует имена переменных и безопасные значения без раскрытия локальных секретов. На его основе `init_env.py` создаёт локальные настройки и новый секрет.
4. **Для чего health-check?** Оператор, балансировщик или оркестратор проверяет, отвечает ли процесс. Этот маршрут не утверждает готовность БД, SSH или AI.
5. **Как помогает Dependency Inversion?** Сценарий зависит от абстракций, а HTTP/ORM-адаптеры связываются с ним снаружи. Здесь urls.py передаёт сервис контроллеру, а ServiceInfo — сервису. При добавлении БД сервис получит интерфейс репозитория; ORM-реализацию подключат при сборке.

Публикация — в [lab3](https://github.com/bendyou/RSP/tree/lab3) согласно выбранной организации веток. Main остаётся обзором. №4 не выполнялась; инструкция следующему агенту — [AGENTS.md](AGENTS.md).
