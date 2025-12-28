# Parser of Domclick (parser-domclick)

[![CI](https://github.com/cursay/parser-domclick/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cursay/parser-domclick/actions/workflows/ci.yml)

Парсер объявлений с сайта domclick.ru на базе Selenium и FastAPI.

Этот репозиторий и сервис являются частью большого проекта команды **Name Later team**.
Проект разработан и поддерживался студентом **Ярославом Харловым**.
API этой программы используется ИИ-агентом для подбора объявлений с сайта **domclick.ru**.

Описание
-------

`parser-domclick` — небольшой сервис, который использует Selenium для получения данных о
недвижимости с Cian.ru и предоставляет результаты через HTTP API (FastAPI). Подойдёт
для сбора и фильтрации объявлений по городу, цене, площади и типу сделки (продажа/аренда).

Кому полезен
- Аналитикам, которым нужно собрать офферы для последующего анализа.
- Для автоматизации мониторинга цен и наличия объявлений.

Ключевые возможности
- Запуск локально или в Docker Compose вместе с Selenium Standalone (Chrome).
- REST API на FastAPI с интерактивной документацией (`/docs`).
- Конфигурация через переменные окружения.

Требования
- Python 3.11
- Библиотеки и версии в `requirements.txt`.

Установка (локально)
---------------------

1. Клонируйте репозиторий и перейдите в папку проекта.

2. Создайте виртуальное окружение и активируйте его:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Скопируйте файл конфигурации окружения и при необходимости отредактируйте:

```bash
cp .env.example .env
```

Запуск приложения (локально)
---------------------------

Запустить FastAPI приложение можно командой:

```bash
uvicorn parser_domclick.app:app --reload --host 127.0.0.1 --port 8000
```

Откройте `http://127.0.0.1:8000/docs` для интерактивной документации.

Запуск в Docker Compose
-----------------------

Для удобства есть `docker-compose.yml`, который поднимает API и контейнер с Selenium:

```bash
docker compose up --build
```

После запуска API будет доступно по `http://localhost:8000`.

Конфигурация (основные переменные)
---------------------------------

- `API_URL` — (пример) базовый URL Cian API, используется в парсере (см. `.env.example`).
- `SELENIUM_HOST` — хост Selenium (по умолчанию `localhost` или `selenium-server` в compose).
- `SELENIUM_PORT` — порт Selenium (обычно `4444`).
- `SELENIUM_TIMEOUT` — таймаут ожидания WebDriver.

API
---

Основные эндпоинты:
- `GET /` — информация о сервисе.
- `GET /health` — проверка статуса.
- `GET /v1/search` — поиск объявлений. Параметры (query string):
	- `city` (string, обязательно)
	- `price_gte`, `price_lte` (целые числа, опционально)
	- `area_gte`, `area_lte` (целые числа, опционально)
	- `sale` (boolean, опционально — true = продажа, false = аренда)

Интерактивная документация доступна по `/docs` (Swagger) и `/redoc`.

Примеры использования
---------------------

1) Пример cURL

```bash
curl -s "http://localhost:8000/v1/search?city=Moscow&price_gte=2000000&price_lte=5000000&area_gte=50&sale=true" \
	| jq .
```

Пример ожидаемого JSON-ответа (сокращённо):

```json
{
	"query": "Moscow",
	"total_found": 42,
	"filtered_count": 10,
	"offers": [
		{
			"offer_id": 123456,
			"title": "2-комнатная квартира, 60 м²",
			"price": 3500000,
			"area": 60,
			"url": "https://cian.ru/offer/123456"
		}
	]
}
```

2) Пример на Python (requests)

```python
import requests

resp = requests.get(
		"http://localhost:8000/v1/search",
		params={
				"city": "Moscow",
				"price_gte": 2000000,
				"price_lte": 5000000,
				"area_gte": 50,
				"sale": True,
		},
)
data = resp.json()
print(f"Found {data.get('filtered_count')} offers (total: {data.get('total_found')})")
for o in data.get('offers', [])[:3]:
		print(f"- {o.get('title')} — {o.get('price')} ₽ — {o.get('area')} м²")
```

Ожидаемый вывод (пример):

```
Found 10 offers (total: 42)
- 2-комнатная квартира, 60 м² — 3500000 ₽ — 60 м²
```

Примечание: результаты зависят от текущего состояния сайта Cian.ru и настроек парсера; пример вывода приведён в демонстративных целях.

Структура проекта
-----------------

- `parser_domclick/` — основной пакет проекта
	- `app.py` — FastAPI приложение и конфигурация.
	- `constants.py` — константы и настройки по-умолчанию.
	- `__main__.py` — запуск модуля.
	- `api/v1/` — маршруты и модели API.
	- `domclick/` — модуль с логикой парсера и обёртками Selenium.

- `requirements.txt` — зависимости проекта.
- `Dockerfile`, `docker-compose.yml` — контейнеризация и интеграция с Selenium.
- `.env.example` — пример переменных окружения.

Файлы в репозитории можно найти здесь:

- [README.md](README.md)
- [parser_domclick/app.py](parser_domclick/app.py)
- [parser_domclick/domclick/parser.py](parser_domclick/domclick/parser.py)
- [parser_domclick/domclick/browser.py](parser_domclick/domclick/browser.py)

Разработка и тестирование
------------------------

- Для быстрой проверки запустите сервис вместе с Selenium через Docker Compose.
- Для отладки используйте `uvicorn` с `--reload`.
- Рекомендуется добавить автоматические тесты на маршруты API и интеграционные тесты для парсера.

Дальнейшие улучшения
--------------------

- Добавить кеширование и очереди для долгих парсинг-задач.
- Добавить unit/integration тесты и CI (GitHub Actions).
- Поддерживать rate-limit и прокси для Selenium при массовом парсинге.

Поддержка
---------

Если нужно помочь с развёртыванием, тестами или расширением функционала — создайте issue.

Лицензия
--------


CI/CD / GitHub Actions
----------------------

В репозитории есть workflow: `.github/workflows/docker-publish.yml`.
Ниже краткая документация — что он делает и как им пользоваться.

Что делает workflow
- Триггеры: `push` в ветки `main` и `dev`, пуш семантических тегов `v*.*.*`, и ручной запуск (`workflow_dispatch`).
- Логику: проверяет код, собирает Docker-образ с помощью Buildx, формирует набор тегов (semver, sha, `latest` для основной ветки) и публикует образ в GitHub Container Registry (`ghcr.io`).
- Использует `docker/metadata-action` для генерации тегов и `docker/build-push-action` для сборки и пуша.

Права и настройки
- Workflow использует `GITHUB_TOKEN` для логина в GHCR. В настройках репозитория на GitHub в разделе `Settings → Actions → General` убедитесь, что у Actions включены права `Read and write permissions` и разрешено `Access to GitHub Packages`.
- Для приватных репозиториев или особых сценариев можно настроить personal access token (PAT) с правами `packages:write` и сохранить его в `secrets`.

Какие теги образа публикуются
- Семантические теги при пуше версий (`v1.2.3`, `v1.2`, `v1`)
- `sha`-тег с идентификатором коммита
- `latest` для образа, собранного из основной ветки (по умолчанию)

Как получить опубликованный образ

Пример команды для скачивания и запуска (замените `<OWNER>` и `<REPO>` или используйте `ghcr.io/<OWNER>/<IMAGE>:<TAG>`):

```bash
docker pull ghcr.io/<OWNER>/<REPO>:v1.2.3
docker run --rm -p 8000:8000 ghcr.io/<OWNER>/<REPO>:v1.2.3
```

Если образ приватный, выполните вход в GHCR перед `docker pull`:

```bash
echo $PAT | docker login ghcr.io -u <USERNAME> --password-stdin
```

(где `PAT` — personal access token с правами `packages:read`).

Где смотреть детали
- Конфигурация шагов, используемые действия и формирование тегов находятся в `.github/workflows/docker-publish.yml`.
- Логи запусков доступны в Actions-tab на GitHub для репозитория.


Лицензия
--------

Этот проект распространяется под **MIT License** (публичная лицензия). Файл с текстом лицензии добавлен в `LICENSE`.
