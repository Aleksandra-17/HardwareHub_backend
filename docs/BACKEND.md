# Документация бэкенда HardwareHub

Руководство по разработке бэкенда для веб-приложения учёта техники.

## Обзор

HardwareHub — система учёта оборудования: устройства, типы устройств, локации (кабинеты), ответственные лица, история изменений и отчёты.

Фронтенд работает с mock-данными. Бэкенд должен реализовать REST API, соответствующее спецификации в [BACKEND_API.md](./BACKEND_API.md).

---

## Рекомендуемый стек

| Компонент | Варианты |
|-----------|----------|
| Runtime | Node.js 20+, Python 3.11+, Go 1.21+ |
| Framework | Express, FastAPI, Gin |
| БД | PostgreSQL, SQLite (для dev), MySQL |
| ORM | Prisma, TypeORM, SQLAlchemy, GORM |

---

## Схема базы данных

### Таблицы

```
device_types      — справочник типов устройств
locations         — справочник локаций (кабинеты)
people            — ответственные лица
devices           — устройства (связь с device_types, locations, people)
audit_entries     — история изменений по устройствам
```

### Связи

- `devices.device_type_id` → `device_types.id`
- `devices.location_id` → `locations.id`
- `devices.person_id` → `people.id` (nullable для резерва/списания)
- `audit_entries.device_id` → `devices.id` (если хранить связь)

### Пример SQL (PostgreSQL)

```sql
CREATE TABLE device_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) NOT NULL UNIQUE,
  category VARCHAR(50) NOT NULL CHECK (category IN ('computing','office','network','other')),
  description TEXT
);

CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  building VARCHAR(255),
  floor VARCHAR(50),
  description TEXT
);

CREATE TABLE people (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name VARCHAR(255) NOT NULL,
  position VARCHAR(255),
  department VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(50)
);

CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inventory_number VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  device_type_id UUID REFERENCES device_types(id),
  serial_number VARCHAR(100),
  model VARCHAR(255),
  manufacturer VARCHAR(255),
  status VARCHAR(50) NOT NULL CHECK (status IN ('in_use','reserve','decommissioned','repair')),
  location_id UUID REFERENCES locations(id),
  person_id UUID REFERENCES people(id),
  commission_date DATE,
  last_check_date DATE,
  notes TEXT,
  purchase_price DECIMAL(12,2),
  purchase_date DATE,
  qr_code VARCHAR(100)
);

CREATE TABLE audit_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id UUID REFERENCES devices(id),
  date DATE NOT NULL,
  action TEXT NOT NULL,
  "user" VARCHAR(255) NOT NULL
);

CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_device_type ON devices(device_type_id);
CREATE INDEX idx_devices_location ON devices(location_id);
CREATE INDEX idx_devices_person ON devices(person_id);
CREATE INDEX idx_devices_inventory ON devices(inventory_number);
```

---

## CORS

Фронтенд и бэкенд на разных портах — нужен CORS:

- **Allow-Origin**: `http://localhost:8080` (dev), ваш production домен
- **Methods**: GET, POST, PATCH, PUT, DELETE
- **Headers**: Content-Type, Authorization

---

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `PORT` | Порт сервера | `3000` |
| `DATABASE_URL` | Подключение к БД | `postgresql://user:pass@localhost:5432/hardwarehub` |
| `CORS_ORIGIN` | Разрешённый origin для CORS | `http://localhost:8080` |

---

## Локальная разработка

1. Поднять БД (Docker или локально).
2. Запустить бэкенд на `http://localhost:3000`.
3. В корне фронтенда создать `.env`:
   ```
   VITE_API_URL=http://localhost:3000/api
   ```
4. Запустить фронтенд: `npm run dev`.

---

## Чек-лист реализации

- [ ] CRUD для device_types, locations, people
- [ ] CRUD для devices с фильтрацией и сортировкой
- [ ] История изменений (audit) при создании/обновлении устройств
- [ ] Эндпоинт экспорта (CSV/XLSX)
- [ ] Акт инвентаризации (опционально)
- [ ] Валидация входных данных
- [ ] Обработка ошибок (4xx, 5xx)
- [ ] Логирование запросов

---

## Ссылки

- [BACKEND_API.md](./BACKEND_API.md) — полная спецификация API (модели, эндпоинты, примеры)
