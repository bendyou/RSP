# CommandX

**Панель управления собственными серверами по SSH**

![Python](https://img.shields.io/badge/Python-3.12–3.14-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-149ECA?logo=react&logoColor=white)

Сквозной проект по дисциплине «Разработка серверных приложений». CommandX объединяет работу с собственными Linux-серверами: SSH-команды, файлы, Python-пакеты, мониторинг, профиль, подписки и опциональный AI-помощник.

## Тема и технологии

Клиент — React, TypeScript и Vite. Серверная часть — Python, Django REST Framework и SimpleJWT; подключения SSH выполняются через Paramiko. Для локальной разработки используется SQLite, при развёртывании — PostgreSQL.

Пользователь управляет своими серверами. Администратор дополнительно управляет пользователями и подписками; административная роль не даёт автоматического доступа к чужим SSH-серверам. Метрики собираются по запросу, AI подключается отдельно, реальный платёжный провайдер отсутствует.

## Лабораторные работы

Каждая работа находится в собственной ветке. Её файлы размещены непосредственно в корне этой ветки.

| Работа | Содержание | Открыть |
| --- | --- | --- |
| №1 | Архитектура, роли, Use Cases, C4, ERD и схема БД | [lab1](https://github.com/bendyou/RSP/tree/lab1) |
| №2 | REST API, OpenAPI и Swagger UI | [lab2](https://github.com/bendyou/RSP/tree/lab2) |
| №3 | Каркас Django/DRF, конфигурация и health-check | [lab3](https://github.com/bendyou/RSP/tree/lab3) |

В `main` находится обзор темы и навигация. Инструкции запуска и результаты проверок находятся в соответствующих рабочих ветках.

Лабораторная №4 пока не выполнялась. Правила продолжения проекта для агента: [AGENTS.md](AGENTS.md).
