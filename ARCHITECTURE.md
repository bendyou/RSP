# Архитектура CommandX

CommandX — панель управления собственными серверами по SSH. Backend: Python и Django REST Framework, frontend исходного проекта: React. Пользователь работает со своими серверами, администратор управляет пользователями.

В ЛР3 реализован только каркас и health-check:

- `main.py` — запуск приложения.
- `app/config.py` — настройки из `.env`.
- `app/controller.py` — HTTP-запрос и JSON-ответ.
- `app/service.py` — данные сервиса и расчёт uptime.
- `app/repository/` — место для будущей работы с БД, пока пустое.

Контроллер вызывает сервис; сервис не зависит от HTTP и базы данных.

[Полная архитектура ЛР1](https://github.com/bendyou/RSP/blob/lab1/ARCHITECTURE.md) · [Контракт API ЛР2](https://github.com/bendyou/RSP/blob/lab2/openapi.yaml).
