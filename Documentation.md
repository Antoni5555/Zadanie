# Документация к файлу docker-compose.yml

Этот файл описывает конфигурацию Docker Compose для создания мультисервисного приложения, включающего FastAPI API-сервис, базу данных PostgreSQL, сервер хранения MinIO и Selenium для автоматизации работы с браузером.
Версия Docker Compose

    version: '3.8': Используется версия 3.8 файла конфигурации Docker Compose, поддерживающая расширенные возможности, такие как сети, зависимости между сервисами и общие тома.

## Описание сервисов 

## API (FastAPI)

build: Указывает путь к директории ./api, где находится Dockerfile для сборки образа FastAPI сервиса.

container_name: Имя контейнера будет fastapi_service.


ports: Контейнер использует порт 8000 для доступа к API-сервису. Внешний порт 8000 будет проброшен внутрь контейнера.
    "8000:8000": Перенаправляет запросы с хоста на порт 8000 внутрь контейнера.

environment: Устанавливаются переменные окружения для настройки работы сервиса:
    DATABASE_URL: Строка подключения к базе данных PostgreSQL.
    MINIO_URL: URL MinIO сервера для взаимодействия с хранилищем.
    MINIO_ACCESS_KEY и MINIO_SECRET_KEY: Ключи доступа и секретный ключ для подключения к MinIO.

depends_on: Определяет зависимости от других сервисов:
    db: FastAPI сервис зависит от сервиса базы данных PostgreSQL.
    minio: FastAPI требует MinIO для хранения файлов.
    selenium: Сервис взаимодействует с Selenium для автоматизации задач в браузере.
<br><br>

## DB (PostgreSQL)

image: Образ базы данных PostgreSQL для архитектуры arm64 с версией 13.
    arm64v8/postgres:13

container_name: Контейнер базы данных будет назван postgres_db.

environment: Настройка окружения для базы данных PostgreSQL:
    POSTGRES_USER: Имя пользователя для доступа к базе данных — postgres.
    POSTGRES_PASSWORD: Пароль для пользователя PostgreSQL — pg_password.
    POSTGRES_DB: Название базы данных — screenshot_db.

ports: Контейнер базы данных открывает порт 5432 для внешнего подключения к PostgreSQL.
    "5432:5432": Проброс порта 5432 с хоста на контейнер.

volumes: Связывает SQL-скрипт инициализации с контейнером, чтобы инициализировать базу данных при первом запуске.
    ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro: Локальный файл init.sql монтируется в контейнер в режиме только для чтения.
<br><br>

## MinIO (Object Storage)

image: Образ сервера MinIO для хранения данных:
    minio/minio:RELEASE.2023-09-30T07-02-29Z

container_name: Контейнер называется minio.

environment: Переменные окружения для MinIO:
    MINIO_ROOT_USER: Устанавливает имя root пользователя — minio.
    MINIO_ROOT_PASSWORD: Пароль для root пользователя — minio123.

command: Запуск MinIO сервера с указанием директории для хранения данных:
    server /data: MinIO будет хранить данные в каталоге /data.

ports: Контейнер открывает порт 9000 для взаимодействия с MinIO.
    "9000:9000": Проброс порта 9000 с хоста на контейнер.
<br><br>

## Selenium

image: Образ Selenium с поддержкой браузера Chromium для архитектуры arm:
seleniarm/standalone-chromium:latest

container_name: Имя контейнера Selenium — selenium.

ports: Контейнер открывает порт 4444 для подключения к Selenium.
"4444:4444": Проброс порта 4444 для взаимодействия с Selenium WebDriver.
<br><br>

## Зависимости

Сервис API (FastAPI) зависит от трёх других сервисов:

    db: для взаимодействия с PostgreSQL базой данных.
    minio: для хранения данных через MinIO.
    selenium: для выполнения задач автоматизации браузера.
<br>

## Как запустить

Для запуска всех сервисов используется команда:

    docker-compose up --build

Для подключения в контейнер postgres_db

    docker exec -it postgres_db psql -U postgres -d screenshot_db

Выполнить POST запрос для создания скриншота сайта

    curl -X POST "http://localhost:8000/screenshot/?url=https://google.com&is_fresh=true"

Достать скриншот из хранилища minio и переместить в нужную дирректорию

    mc cp local/screenshots/863234ab-e7e0-45ed-bc65-f841bf8ca21a.png D:\PythonProject\Zadanie\file