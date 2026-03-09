# Backend API Specification

Спецификация API для интеграции бэкенда с фронтендом HardwareHub.

## Базовый URL

Рекомендуемый базовый URL: `http://localhost:3000/api` или через переменную окружения `VITE_API_URL`.

## Формат данных

- **Content-Type**: `application/json`
- Кодировка дат: `YYYY-MM-DD` (ISO 8601)
- Идентификаторы: строки (UUID или др.)

---

## Модели данных

### DeviceStatus

```
'in_use' | 'reserve' | 'decommissioned' | 'repair'
```

- `in_use` — В эксплуатации
- `reserve` — В резерве
- `decommissioned` — Списано
- `repair` — На ремонте

### DeviceType

| Поле | Тип | Описание |
|------|-----|----------|
| id | string | Уникальный идентификатор |
| name | string | Название (например, «Ноутбук») |
| code | string | Код (например, «NB-001») |
| category | string | `computing` \| `office` \| `network` \| `other` |
| description | string | Описание |
| deviceCount | number | Количество устройств (вычисляемое) |

### Location

| Поле | Тип | Описание |
|------|-----|----------|
| id | string | Уникальный идентификатор |
| name | string | Название (например, «Каб. 101») |
| building | string | Корпус/здание |
| floor | string | Этаж |
| description | string | Описание |
| deviceCount | number | Количество устройств (вычисляемое) |

### Person

| Поле | Тип | Описание |
|------|-----|----------|
| id | string | Уникальный идентификатор |
| fullName | string | ФИО |
| position | string | Должность |
| department | string | Отдел |
| email | string | Email |
| phone | string | Телефон |
| deviceCount | number | Количество устройств (вычисляемое) |

### Device

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| id | string | — | Уникальный идентификатор |
| inventoryNumber | string | да | Инвентарный номер |
| name | string | да | Наименование |
| deviceTypeId | string | да | ID типа устройства |
| serialNumber | string | — | Серийный номер |
| model | string | — | Модель |
| manufacturer | string | — | Производитель |
| status | DeviceStatus | да | Статус |
| locationId | string | да | ID локации |
| personId | string | — | ID ответственного (пустая строка для резерва/списания) |
| commissionDate | string | — | Дата ввода в эксплуатацию (YYYY-MM-DD) |
| lastCheckDate | string | — | Дата последней проверки |
| notes | string | — | Примечания |
| purchasePrice | number | — | Стоимость покупки (₽) |
| purchaseDate | string | — | Дата покупки |
| qrCode | string | — | QR-код (часто = inventoryNumber) |

### AuditEntry

| Поле | Тип | Описание |
|------|-----|----------|
| id | string | Уникальный идентификатор |
| date | string | Дата (YYYY-MM-DD) |
| action | string | Описание действия |
| user | string | Пользователь, выполнивший действие |

---

---

## Аутентификация (JWT)

### Логин

#### `POST /api/auth/login`

Вход по username и password.

**Request body:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

Используйте `access_token` в заголовке: `Authorization: Bearer <access_token>`.

### Обновление токенов

#### `POST /api/auth/refresh`

Получить новые access и refresh токены.

**Request body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK` — новые токены

### Выход

#### `POST /api/auth/logout`

Инвалидация refresh токена.

**Request body (опционально):**
```json
{
  "refresh_token": "eyJ..."
}
```

### Текущий пользователь

#### `GET /api/auth/me`

Информация о текущем пользователе (требует Bearer token).

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "username": "admin",
  "role": "admin",
  "is_active": true
}
```

### Создание пользователя (только admin)

#### `POST /api/auth/users`

Создание пользователя с автогенерированным паролем.

**Request body:**
```json
{
  "username": "newuser",
  "role": "user"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "username": "newuser",
  "role": "user",
  "password": "Xy9#kL2@mN4p"
}
```

**Важно:** пароль показывается только при создании. Сохраните его.

---

## Эндпоинты

### Device Types (Типы устройств)

#### `GET /device-types`

Список всех типов устройств.

**Response:** `200 OK`

```json
[
  {
    "id": "dt1",
    "name": "Ноутбук",
    "code": "NB-001",
    "category": "computing",
    "description": "Портативный компьютер",
    "deviceCount": 12
  }
]
```

---

### Locations (Локации)

#### `GET /locations`

Список всех локаций.

**Response:** `200 OK`

```json
[
  {
    "id": "l1",
    "name": "Каб. 101",
    "building": "Корпус А",
    "floor": "1",
    "description": "Приёмная",
    "deviceCount": 4
  }
]
```

---

### People (Ответственные)

#### `GET /people`

Список всех ответственных лиц.

**Response:** `200 OK`

```json
[
  {
    "id": "p1",
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

### Devices (Устройства)

#### `GET /devices`

Список устройств с поддержкой фильтрации и сортировки.

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| search | string | Поиск по `inventoryNumber`, `name`, `serialNumber` |
| status | string | Фильтр по статусу (или `all`) |
| type | string | Фильтр по `deviceTypeId` (или `all`) |
| location | string | Фильтр по `locationId` (или `all`) |
| person | string | Фильтр по `personId` (или `all`) |
| sort | string | Поле сортировки: `inventoryNumber`, `name`, `status`, `commissionDate` |
| order | string | `asc` или `desc` |

**Response:** `200 OK`

```json
[
  {
    "id": "d1",
    "inventoryNumber": "INV-2024-001",
    "name": "Ноутбук Lenovo ThinkPad E15",
    "deviceTypeId": "dt1",
    "serialNumber": "SN-LNV-001",
    "model": "ThinkPad E15 Gen 4",
    "manufacturer": "Lenovo",
    "status": "in_use",
    "locationId": "l3",
    "personId": "p3",
    "commissionDate": "2024-01-15",
    "lastCheckDate": "2025-12-01",
    "notes": "Для задач ML",
    "purchasePrice": 85000,
    "purchaseDate": "2023-12-20",
    "qrCode": "INV-2024-001"
  }
]
```

#### `GET /devices/:id`

Получить устройство по ID.

**Response:** `200 OK` — объект Device

**Response:** `404 Not Found` — устройство не найдено

#### `POST /devices`

Создать новое устройство.

**Request body:** объект Device без `id` (id генерирует сервер)

**Response:** `201 Created` — созданный Device

#### `PATCH /devices/:id` или `PUT /devices/:id`

Обновить устройство.

**Request body:** частичный объект Device (только изменённые поля)

**Response:** `200 OK` — обновлённый Device

#### `DELETE /devices/:id`

Удалить (списать) устройство.

**Response:** `204 No Content`

---

### Audit (История изменений)

#### `GET /devices/:id/audit`

История изменений устройства.

**Response:** `200 OK`

```json
[
  {
    "id": "a1",
    "date": "2025-12-01",
    "action": "Инвентаризация проведена",
    "user": "Иванов И.И."
  }
]
```

---

### Reports (Отчёты)

#### `GET /reports/devices/export`

Экспорт списка устройств.

**Query-параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| format | string | `csv` или `xlsx` |
| locationId | string | (опционально) Фильтр по локации |
| personId | string | (опционально) Фильтр по ответственному |

**Response:** файл (CSV или Excel)

#### `POST /reports/inventory`

Формирование акта инвентаризации.

**Request body:**

```json
{
  "locationId": "l1",
  "personId": "p1",
  "dateFrom": "2025-01-01",
  "dateTo": "2025-12-31"
}
```

**Response:** `200 OK` — файл акта (PDF/Excel)

---

## Справочники (константы)

Фронтенд ожидает следующие метки (могут быть захардкожены или возвращены с API):

### statusLabels

```json
{
  "in_use": "В эксплуатации",
  "reserve": "В резерве",
  "decommissioned": "Списано",
  "repair": "На ремонте"
}
```

### categoryLabels

```json
{
  "computing": "Вычислительная техника",
  "office": "Оргтехника",
  "network": "Сетевое оборудование",
  "other": "Прочее"
}
```

---

## Интеграция на фронтенде

1. Создайте `src/lib/api.ts` с функциями `fetch`/`axios` к эндпоинтам.
2. Замените импорты из `mock-data` на вызовы API.
3. Используйте React Query для кэширования (см. `QueryClientProvider` в `App.tsx`).
4. Задайте `VITE_API_URL` в `.env` для указания базового URL API.

---

## Пример минимального бэкенда

- **Node.js + Express** + SQLite/PostgreSQL
- **Python + FastAPI** + SQLAlchemy
- **Go + Gin** + GORM

Схема БД: таблицы `device_types`, `locations`, `people`, `devices`, `audit_entries` по структурам выше.
