# HardwareHub Backend — документация для фронтенда

Краткое руководство по интеграции фронтенда с API бэкенда.

---

## Базовый URL

```
http://localhost:8000   # development
```

Продакшн URL уточняйте у команды бэкенда.

---

## OpenAPI / Swagger

- **Swagger UI:** `GET /api/docs` — интерактивная документация (может требовать HTTP Basic Auth)
- **OpenAPI JSON:** `GET /api/openapi.json` — спецификация для генерации клиентов

---

## Аутентификация (JWT)

Используется Bearer JWT. При логине выдаются два токена:

| Токен         | Назначение                         | Срок жизни      |
|---------------|------------------------------------|-----------------|
| `access_token`| Заголовок `Authorization` для API  | 30 минут        |
| `refresh_token`| Обновление пары токенов           | 7 дней          |

### Заголовок запроса

Для защищённых эндпоинтов:

```
Authorization: Bearer <access_token>
```

### Поток аутентификации

1. **Логин** → получаете `access_token` и `refresh_token`
2. Используете `access_token` в заголовке для API
3. При 401 — запрашиваете новые токены через `/api/auth/refresh`
4. При выходе — вызываете `/api/auth/logout` с `refresh_token` (по желанию)

---

## Эндпоинты

### Auth (`/api/auth`)

| Метод | Путь      | Описание                    | Авторизация |
|-------|-----------|-----------------------------|-------------|
| POST  | `/login`  | Вход                        | —           |
| POST  | `/refresh`| Обновить токены             | —           |
| POST  | `/logout` | Выход (инвалидация refresh) | —           |
| GET   | `/me`     | Текущий пользователь        | Bearer      |
| POST  | `/users`  | Создать пользователя        | Admin       |

#### POST /api/auth/login

**Request:**
```json
{
  "username": "root",
  "password": "root"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST /api/auth/refresh

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:** то же, что у `/login` — новая пара токенов.

#### POST /api/auth/logout

**Request (optional):**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** 204 No Content.

#### GET /api/auth/me

**Response 200:**
```json
{
  "id": "uuid",
  "username": "root",
  "role": "admin",
  "is_active": true
}
```

#### POST /api/auth/users (admin only)

**Request:**
```json
{
  "username": "newuser",
  "role": "user"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "username": "newuser",
  "role": "user",
  "password": "auto-generated-password"
}
```

⚠️ Пароль возвращается только при создании. Сохраните его на клиенте или покажите пользователю.

---

### Health (`/api/root`)

| Метод | Путь     | Описание      | Авторизация |
|-------|-----------|---------------|-------------|
| GET   | `/health` | Проверка сервиса | —        |

**Response 200:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

**Response 503:** если БД или Redis недоступны.

---

### Типы устройств (`/api/device-types`)

| Метод | Путь | Описание       | Авторизация |
|-------|------|----------------|-------------|
| GET   | `/`  | Список типов   | —           |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "name": "Ноутбук",
    "code": "NB-001",
    "category": "computing",
    "description": "Портативный компьютер",
    "deviceCount": 12
  }
]
```

---

### Локации (`/api/locations`)

| Метод | Путь | Описание   | Авторизация |
|-------|------|------------|-------------|
| GET   | `/`  | Список локаций | —        |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "name": "Каб. 101",
    "building": "Корпус А",
    "floor": "1",
    "description": "Приёмная",
    "deviceCount": 4
  }
]
```

---

### Люди (`/api/people`)

| Метод | Путь | Описание           | Авторизация |
|-------|------|--------------------|-------------|
| GET   | `/`  | Список ответственных лиц | —      |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "fullName": "Иванов Иван Иванович",
    "position": "Системный администратор",
    "department": "IT-отдел",
    "email": "ivanov@company.ru",
    "phone": "+7 (999) 111-22-33",
    "deviceCount": 5
  }
]
```

---

### Устройства (`/api/devices`)

| Метод | Путь           | Описание           | Авторизация |
|-------|----------------|--------------------|-------------|
| GET   | `/`            | Список устройств   | —           |
| GET   | `/{id}`        | Устройство по ID   | —           |
| GET   | `/{id}/audit`  | История изменений  | —           |
| POST  | `/`            | Создать устройство | —           |
| PATCH | `/{id}`        | Обновить           | —           |
| PUT   | `/{id}`        | Обновить (аналог PATCH) | —      |
| DELETE| `/{id}`        | Удалить            | —           |

#### GET /api/devices

**Query params:**

| Параметр | Тип   | Описание                                           |
|----------|-------|----------------------------------------------------|
| `search` | string| Поиск по inventoryNumber, name, serialNumber       |
| `status` | string| Фильтр: `in_use`, `reserve`, `decommissioned`, `repair` или `all` |
| `type`   | string| Фильтр по `deviceTypeId` или `all`                 |
| `location` | string| Фильтр по `locationId` или `all`                 |
| `person` | string| Фильтр по `personId` или `all`                     |
| `sort`   | string| Поле сортировки (default: `inventoryNumber`)       |
| `order`  | string| `asc` или `desc` (default: `asc`)                  |

#### Схема устройства (Device)

**Чтение (DeviceRead) / Создание (DeviceCreate):**

```json
{
  "id": "uuid",
  "inventoryNumber": "INV-001",
  "name": "Ноутбук Dell",
  "deviceTypeId": "uuid",
  "serialNumber": "SN123",
  "model": "Latitude 5420",
  "manufacturer": "Dell",
  "status": "in_use",
  "locationId": "uuid",
  "personId": "uuid",
  "commissionDate": "2024-01-15",
  "lastCheckDate": "2025-01-10",
  "notes": "Заметки",
  "purchasePrice": 59999.00,
  "purchaseDate": "2023-12-01",
  "qrCode": null
}
```

**Статусы устройства (`status`):**

- `in_use` — в использовании
- `reserve` — в резерве
- `decommissioned` — списано
- `repair` — в ремонте

**DeviceCreate** — все поля, кроме опциональных, обязательны.  
**DeviceUpdate (PATCH/PUT)** — все поля опциональны, обновляются только переданные.

#### GET /api/devices/{id}/audit

**Response 200:**
```json
[
  {
    "id": "uuid",
    "date": "2025-03-09",
    "action": "created",
    "user": "root"
  }
]
```

---

## Именование полей (camelCase)

Ответы API используют **camelCase** для полей:

- `inventoryNumber`, `deviceTypeId`, `locationId`, `personId`
- `commissionDate`, `lastCheckDate`, `purchasePrice`, `purchaseDate`, `qrCode`
- `deviceCount`, `fullName`

При отправке в body тоже можно использовать camelCase (алиасы в Pydantic).

---

## Ошибки

Типичные коды:

| Код | Описание                      |
|-----|-------------------------------|
| 400 | Невалидные данные             |
| 401 | Нет или невалидный Bearer     |
| 403 | Нет прав (нужна роль admin)   |
| 404 | Ресурс не найден              |
| 422 | Ошибка валидации (Pydantic)   |
| 503 | Health: сервис недоступен     |

**Формат ошибки (пример):**
```json
{
  "detail": "Недействительный или истёкший токен"
}
```

или при 422:
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## CORS

CORS настроен на `allow_origins=["*"]`. В продакшне обычно ограничивают список origin.

---

## Тестовые учётные записи

После миграций в базе есть:

- **root** / **root** — администратор
- **admin** — создаётся только если задана `JWT_INITIAL_ADMIN_PASSWORD` при миграции

---

## Рекомендации для фронта

1. Храните `access_token` и `refresh_token` (localStorage/sessionStorage или secure cookie).
2. Для защищённых запросов добавляйте заголовок:  
   `Authorization: Bearer ${access_token}`.
3. При 401 вызывайте `/api/auth/refresh`, затем повторяйте исходный запрос.
4. При логине/логауте обновляйте состояние (user, tokens).
5. Для списков устройств используйте query-параметры фильтрации и сортировки.
6. Для дат используйте ISO 8601: `YYYY-MM-DD`.
7. `purchasePrice` — число (decimal), не строка.
