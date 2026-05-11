# HardwareHub Backend

REST API для веб-приложения **HardwareHub** (учёт техники: устройства, типы, локации, люди, отчёты, аудит, JWT-аутентификация). Репозиторий фронтенда: **HardwareHub-Frontend**.

## Стек

- **Python 3.13**, **FastAPI**, **SQLAlchemy** (async), **PostgreSQL**, **Redis**
- **Alembic** — миграции БД
- **Docker / Docker Compose** — dev и production
- **Nginx** (в production compose) — reverse proxy перед приложением
- **Pytest**, **Ruff** — тесты и линтинг

---

## Требования

- **Docker** и **Docker Compose** (рекомендуется для единообразного окружения)
- либо **Python 3.13+** для запуска без Docker (плюс локальные PostgreSQL и Redis)
- **Make** (опционально, для целей из `Makefile`)

---

## Клонирование

```bash
git clone https://github.com/<ваш-орг>/HardwareHub-Backend.git
cd HardwareHub-Backend
```

---

## Быстрый старт: разработка в Docker

Из **корня репозитория** (каталог, где лежит `Makefile`):

```bash
make dev
```

Эквивалент без Make:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

Что поднимается (см. `docker/docker-compose.dev.yml`):

- **fastapi-app-dev** — приложение на порту **8000** (хот-релоад через монтирование кода)
- **postgres** — PostgreSQL, порт **5432** на хосте
- **redis** — Redis, порт **6379** на хосте

После старта:

- API: **http://localhost:8000**
- Проверка здоровья: **http://localhost:8000/api/root/health**
- OpenAPI JSON: **http://localhost:8000/api/openapi.json**
- Swagger UI: **http://localhost:8000/api/docs** (защищён HTTP Basic; в коде по умолчанию логин/пароль для доступа к документации — заглушки **USERNAME** / **PASSWORD**, их нужно сменить в используемой среде согласно вашей политике безопасности)

Остановка:

```bash
docker compose -f docker/docker-compose.dev.yml down
```

или `make down` (останавливает и prod, и dev compose — см. `Makefile`).

### Миграции в dev

Образы **dev** и **production** используют **`docker/entrypoint.sh`**: при каждом старте контейнера приложения выполняется **`alembic upgrade head`** (с повторными попытками, пока PostgreSQL не готов). Если миграции не применились (ошибка в логах), выполните вручную:

```bash
docker exec -it fastapi-app-dev alembic upgrade head
```

Имя контейнера смотрите в `docker compose -f docker/docker-compose.dev.yml ps`.

---

## Локальный запуск без Docker (для отладки)

1. Поднимите **PostgreSQL** и **Redis** сами (или отдельными контейнерами) и создайте БД (в dev compose по умолчанию имя базы **hardwarehub**).

2. Виртуальное окружение и зависимости:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Настройка подключения к БД и сервисам: в проекте используются **переменные окружения** и/или **`config.ini`** (шаблоны в репозитории не меняем в рамках документации — копируйте примеры в локальные файлы по инструкциям в комментариях к шаблонам).

4. Миграции:

```bash
alembic upgrade head
```

5. Запуск:

```bash
python src/main.py
# или
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение: **http://localhost:8000**.

Скрипт `start.sh` создаёт venv, ставит зависимости, при наличии каталога миграций выполняет `alembic upgrade head` и запускает `python src/main.py` — удобен для «чистой» машины с уже настроенным `config.ini` / env.

---

## Production: Docker Compose

Из корня репозитория:

```bash
make up
```

или:

```bash
docker compose -f docker/docker-compose.yml up -d
```

Состав типового production-файла `docker/docker-compose.yml`:

- **fastapi-app** — приложение (порт приложения **8000**, наружу пробрасывается как `${PORT:-8000}:8000`)
- **postgres** — данные в именованном volume
- **redis** — кэш/сервисы в именованном volume
- **nginx** — прокси на 80 (и опционально 443); конфиг монтируется из `docker/nginx/nginx.conf`

Переменные окружения для подстановки в compose задаются через **`.env`** в корне проекта (шаблон в репозитории копируют в локальный `.env` на машине развёртывания — не коммитят секреты).

Образ приложения при старте выполняет **`alembic upgrade head`** (см. `docker/entrypoint.sh`), затем запускает `python src/main.py`.

Полезные команды:

```bash
make logs      # логи production-стека
make down      # остановка
```

---

## Аутентификация (JWT)

- **Логин:** `POST /api/auth/login` — тело: `username`, `password` → `access_token`, `refresh_token`
- **Обновление:** `POST /api/auth/refresh` — `refresh_token`
- **Текущий пользователь:** `GET /api/auth/me` (заголовок `Authorization: Bearer <access_token>`)
- **Создание пользователя (admin):** `POST /api/auth/users`

Первый администратор при миграциях: в README шаблона указано задать **`JWT_INITIAL_ADMIN_PASSWORD`** перед применением миграций — следуйте актуальной документации в коде миграций/скриптов.

---

## Префиксы API

Все маршруты приложения под префиксом **`/api`**:

| Префикс | Назначение |
|---------|------------|
| `/api/auth` | Аутентификация |
| `/api/root` | Служебное, в т.ч. `/api/root/health` |
| `/api/device-types` | Типы устройств |
| `/api/locations` | Локации |
| `/api/people` | Люди |
| `/api/devices` | Устройства |
| `/api/reports` | Отчёты |

Фронтенд по умолчанию ожидает базовый URL **`http://localhost:8000/api`** (переменная **`VITE_API_URL`** в репозитории фронта).

---

## CORS

В приложении подключён **CORSMiddleware** (см. `src/configuration/app.py`). Для продакшена рекомендуется сузить список `allow_origins` под домен фронтенда. Пока фронт и API на разных портах localhost, обычно достаточно текущих настроек для разработки.

---

## Makefile (кратко)

```bash
make help           # все цели
make install        # pip install -r requirements.txt
make dev            # dev docker compose
make build          # сборка production-образа
make up             # production stack в фоне
make down           # остановка compose
make logs           # логи production
make test           # pytest с покрытием
make lint           # ruff check
make format         # ruff format + fix
make migrate        # alembic upgrade head (на хосте с настроенным alembic.ini)
make migrate-create # интерактивное создание ревизии
```

---

## Тестирование

```bash
make test
# или
pytest tests/ -v --cov=src --cov-report=html
```

---

## Развёртывание на сервере и связка с фронтендом

Ниже — пошаговый ориентир без изменения файлов репозитория: секреты, `.env` и правки nginx вы делаете на сервере.

### 1. Подготовка сервера

- Установите **Docker** и **Docker Compose plugin**.
- (Рекомендуется) настройте **DNS** на IP сервера: например `api.example.com` для API.
- Откройте в firewall **22** (SSH), **80** и **443** (HTTP/HTTPS). Порты PostgreSQL/Redis **не** выставляйте в интернет, если нет отдельной необходимости.

### 2. Код и окружение

```bash
git clone https://github.com/<ваш-орг>/HardwareHub-Backend.git
cd HardwareHub-Backend
```

Создайте на сервере **`.env`** из шаблона проекта (как описано в комментариях к `.env.example`), задайте надёжные пароли, **`JWT_SECRET_KEY`**, имена БД и пользователей. Убедитесь, что значения согласованы с `docker-compose.yml` (имена сервисов `postgres`, `redis` используются приложением по умолчанию).

### 3. Запуск бэкенда

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Проверьте:

```bash
curl -s http://127.0.0.1:8000/api/root/health
# или с хоста, если PORT проброшен:
curl -s http://127.0.0.1:<PORT>/api/root/health
```

Если перед приложением стоит nginx из того же compose на порту **80**, снаружи может быть удобнее проверять:

```bash
curl -s http://127.0.0.1/health
```

(в шаблоне nginx есть `location /health` → прокси на backend health).

### 4. TLS

- Разместите сертификаты (например **Let’s Encrypt**) и подключите их в **nginx** на сервере. В `docker/nginx/nginx.conf` в репозитории есть закомментированный пример блока `listen 443 ssl`.
- Либо используйте внешний балансировщик (Cloudflare, Yandex ALB и т.д.), который терминирует TLS и проксирует HTTP на ваш сервер.

### 5. Связка с HardwareHub Frontend

1. API должен быть доступен с интернета по URL вида **`https://api.example.com`** с путями **`/api/...`** (либо один домен с префиксом `/api/` — см. ниже).
2. Соберите фронтенд с переменной:

   ```bash
   export VITE_API_URL=https://api.example.com/api
   npm run build
   ```

3. Разместите содержимое `dist/` или Docker-образ фронта за своим nginx / CDN.
4. Убедитесь, что CORS на бэкенде разрешает origin фронта (например `https://app.example.com`), если политика безопасности это требует.

**Один домен:** фронт на `https://example.com`, API за reverse proxy на `https://example.com/api/`. Тогда `VITE_API_URL=https://example.com/api`, а единый nginx отдаёт статику и проксирует `/api` на контейнер `fastapi-app:8000`. Репозиторий бэкенда уже содержит пример nginx только для API; объединение со статикой фронта — отдельный виртуальный хост на вашей стороне.

### 6. CI/CD и секреты GitHub

В `.github/workflows/` могут быть сценарии деплоя. Типичные секреты (уточняйте по актуальному workflow):

- `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`
- учётные данные БД для продакшена
- содержимое **`ALEMBIC_INI`** или иные артефакты, если workflow их подставляет
- при публикации образа: `DOCKER_USERNAME`, `DOCKER_PASSWORD`

---

## Структура проекта (сокращённо)

```
HardwareHub-Backend/
├── src/
│   ├── main.py                 # точка входа, защита /api/docs
│   ├── configuration/app.py   # FastAPI, CORS, роутеры
│   ├── routers/              # auth, devices, …
│   ├── database/             # engine, Alembic
│   └── ...
├── docker/
│   ├── Dockerfile, Dockerfile.dev
│   ├── docker-compose.yml, docker-compose.dev.yml
│   ├── entrypoint.sh
│   └── nginx/nginx.conf
├── tests/
├── requirements.txt
├── Makefile
└── start.sh
```

Дополнительная документация в каталоге **`docs/`** (например `docs/BACKEND.md`).

---

## Лицензия

MIT License — см. файл [LICENSE](LICENSE), если он присутствует в репозитории.
