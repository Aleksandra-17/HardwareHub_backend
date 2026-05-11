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
| GET   | `/`  | Список типов   | Bearer      |

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

| Метод  | Путь       | Описание       | Авторизация |
|--------|------------|----------------|-------------|
| GET    | `/`        | Список локаций | Bearer      |
| POST   | `/`        | Создать        | Bearer      |
| DELETE | `/{id}`    | Удалить        | Bearer      |

#### GET /api/locations

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

#### POST /api/locations

**Request:**
```json
{
  "name": "Каб. 102",
  "building": "Корпус А",
  "floor": "1",
  "description": "Бухгалтерия"
}
```

**Response 201:** объект LocationRead (как в GET).

#### DELETE /api/locations/{id}

**Response:** 204 No Content.
- **404** — локация не найдена
- **409** — нельзя удалить, есть привязанные устройства

---

### Люди (`/api/people`)

| Метод  | Путь       | Описание                 | Авторизация |
|--------|------------|--------------------------|-------------|
| GET    | `/`        | Список ответственных лиц | Bearer      |
| POST   | `/`        | Создать                  | Bearer      |
| DELETE | `/{id}`    | Удалить                  | Bearer      |

#### GET /api/people

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

#### POST /api/people

**Request:**
```json
{
  "fullName": "Петров Пётр Петрович",
  "position": "Бухгалтер",
  "department": "Бухгалтерия",
  "email": "petrov@company.ru",
  "phone": "+7 (999) 222-33-44"
}
```

**Response 201:** объект PersonRead (как в GET).

#### DELETE /api/people/{id}

**Response:** 204 No Content.
- **404** — ответственное лицо не найдено
- **409** — нельзя удалить, есть привязанные устройства

---

### Устройства (`/api/devices`)

| Метод | Путь             | Описание           | Авторизация |
|-------|------------------|--------------------|-------------|
| GET   | `/`              | Список устройств   | Bearer      |
| GET   | `/{id}`          | Устройство по ID (обновляет lastCheckDate) | Bearer |
| GET   | `/{id}/audit`    | История изменений  | Bearer      |
| POST  | `/`              | Создать устройство | Bearer      |
| POST  | `/{id}/qr-code`  | Сгенерировать QR-код | Bearer    |
| PATCH | `/{id}`          | Обновить           | Bearer      |
| PUT   | `/{id}`          | Обновить (аналог PATCH) | Bearer  |
| DELETE| `/{id}`          | Удалить (только scrapped/archived) | Bearer |

#### GET /api/devices

**Query params:**

| Параметр | Тип   | Описание                                           |
|----------|-------|----------------------------------------------------|
| `search` | string| Поиск по inventoryNumber, name, serialNumber       |
| `status` | string| Фильтр: `in_use`, `repair`, `scrapped`, `archived` или `all` |
| `type`   | string| Фильтр по `deviceTypeId` или `all`                 |
| `location` | string| Фильтр по `locationId` или `all`                 |
| `person` | string| Фильтр по `personId` или `all`                     |
| `sort`   | string| Поле: `inventoryNumber`, `name`, `status`, `commissionDate`, `purchaseDate`, `purchasePrice` |
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
- `repair` — в ремонте
- `scrapped` — списано
- `archived` — в архиве

**DeviceCreate** — все поля, кроме опциональных, обязательны.  
**DeviceUpdate (PATCH/PUT)** — все поля опциональны, обновляются только переданные.

**DELETE** — 409 если статус не scrapped/archived.

#### POST /api/devices/{id}/qr-code

**Response 200:**
```json
{
  "qrCode": "data:image/png;base64,iVBORw0KGgo..."
}
```

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

### Отчёты (`/api/reports`)

| Метод | Путь             | Описание              | Авторизация |
|-------|------------------|-----------------------|-------------|
| POST  | `/devices/export`| Экспорт в CSV/Excel   | Bearer      |
| POST  | `/inventory`     | Акт инвентаризации    | Bearer      |

#### POST /api/reports/devices/export

**Request:**
```json
{
  "format": "csv",
  "locationId": "uuid",
  "personId": "uuid"
}
```

`format`: `csv` или `xlsx`. `locationId` и `personId` — опциональные фильтры.

**Response:** файл (Content-Disposition: attachment).

#### POST /api/reports/inventory

**Request:**
```json
{
  "locationId": "uuid",
  "personId": "uuid",
  "startDate": "2024-01-01",
  "endDate": "2024-03-09"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "documentNumber": "АКТ-2024-ABCD12",
  "date": "2024-03-09",
  "locationName": "Кабинет 101",
  "personName": "Иван Петров",
  "deviceCount": 15,
  "totalPrice": 450000,
  "devices": [
    {
      "inventoryNumber": "INV-2024-001",
      "name": "Ноутбук Lenovo",
      "serialNumber": "SN12345",
      "status": "в использовании",
      "purchasePrice": 45000
    }
  ]
}
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
| 409 | Конфликт (напр. нельзя удалить устройство) |
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
