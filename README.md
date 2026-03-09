# FastAPI Template

A production-ready FastAPI boilerplate designed for rapid project setup — featuring clean architecture, Docker support, CI/CD, logging, and config via environment variables or INI.

## Features

- ⚡ **FastAPI** with Python 3.13
- 🐳 **Docker** & **Docker Compose** for development and production
- 🔄 **CI/CD** pipeline with GitHub Actions
- 🗄️ **PostgreSQL** database with SQLAlchemy
- 🔴 **Redis** for caching
- 🔒 **Nginx** reverse proxy with rate limiting
- 📝 **Alembic** for database migrations
- 🧪 **Pytest** for testing
- 📊 **Logging** configured and ready to use
- 🔧 **Makefile** for convenient development

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- Make (optional)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd fastapi-template
```

2. **Docker** (recommended): copy `.env.example` to `.env` and adjust values. Config is passed via docker-compose.
```bash
cp .env.example .env
```

   **Local dev without Docker**: copy `config.ini.example` to `config.ini` and edit.

### Running (Development)

#### Using Docker Compose:
```bash
make dev
# or
docker compose -f docker/docker-compose.dev.yml up --build
```

#### Locally (without Docker):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
# or
uvicorn src.main:app --reload
```

Application will be available at: http://localhost:8000

API documentation:
- Swagger UI: http://localhost:8000/api/docs (protected)
- OpenAPI JSON: http://localhost:8000/api/openapi.json

### Running (Production)

```bash
make up
# or
docker compose -f docker/docker-compose.yml up -d
```

## Project Structure

```
fastapi-template/
├── .github/
│   └── workflows/
│       └── develop.yaml          # CI/CD pipeline
├── src/                          # Source code
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration (env vars or config.ini)
│   ├── dependencies.py           # Global dependencies
│   ├── schemas.py                # Shared Pydantic schemas
│   ├── configuration/
│   │   └── app.py                # FastAPI app initialization
│   ├── middlewares/              # HTTP middlewares
│   │   ├── __init__.py
│   │   └── database.py           # Database session middleware
│   ├── routers/                  # API routers
│   │   ├── __init__.py           # Router registration
│   │   └── root/                 # Root endpoints
│   │       ├── router.py         # Route definitions
│   │       ├── actions.py        # Business logic
│   │       ├── dal.py            # Data access layer
│   │       ├── models.py         # Database models
│   │       └── schemas.py        # Request/response schemas
│   ├── database/                 # Database configuration
│   │   ├── core.py               # Database engine and sessions
│   │   ├── base.py               # Base model class
│   │   ├── dependencies.py       # Database dependencies
│   │   ├── logging.py            # Session tracking
│   │   └── alembic/              # Database migrations
│   ├── redis_client/             # Redis operations
│   │   └── redis.py              # Redis controller with caching methods
│   ├── services/                 # External service integrations
│   └── misc/                     # Utilities
│       ├── security.py           # Security utilities
│       └── timezone.py           # Timezone utilities
├── docker/
│   ├── Dockerfile                # Production Dockerfile
│   ├── Dockerfile.dev            # Development Dockerfile
│   ├── docker-compose.yml        # Production stack
│   ├── docker-compose.dev.yml    # Development stack
│   └── nginx/
│       └── nginx.conf            # Nginx configuration
├── config.ini.example            # Config template (local dev without Docker)
├── .env.example                  # Env template (Docker Compose)
├── alembic.ini.example           # Alembic configuration template
├── requirements.txt              # Python dependencies
├── Makefile                      # Build commands
├── start.sh                      # Startup script
└── README.md                     # This file
```

## Makefile Commands

```bash
make help           # Show all available commands
make install        # Install dependencies
make dev            # Start development environment
make build          # Build production Docker image
make up             # Start production environment
make down           # Stop all containers
make logs           # Show logs
make clean          # Remove containers and volumes
make test           # Run tests
make lint           # Run linter
make format         # Format code
make migrate        # Apply migrations
make migrate-create # Create new migration
```

## CI/CD

GitHub Actions workflow automatically:
1. Runs tests on every PR
2. Checks code with linter
3. Builds Docker image
4. Deploys to production on push to main

### Required GitHub Secrets:

- `SSH_PRIVATE_KEY` - SSH key for server access
- `SSH_HOST` - Server host
- `SSH_USER` - Server user
- `POSTGRES_USER` - PostgreSQL username for production
- `POSTGRES_PASSWORD` - PostgreSQL password for production
- `POSTGRES_DB` - PostgreSQL database name for production
- `ALEMBIC_INI` - Contents of alembic.ini file for production
- `DOCKER_USERNAME` - Docker Hub username (optional)
- `DOCKER_PASSWORD` - Docker Hub password (optional)

## Configuration

**Docker Compose**: config is passed via `environment:` in docker-compose. Use `.env` for variable substitution (copy `.env.example` to `.env`).

**Local dev (without Docker)**: use `config.ini` (copy `config.ini.example` to `config.ini`).

**Env var names** (prefix + key): `POSTGRES_*`, `UVICORN_*`, `REDIS_*` (e.g. `POSTGRES_USERNAME`, `REDIS_HOST`, `UVICORN_PORT`).

### Key Features

#### Database Middleware
- Automatic session management per request
- Auto-commit on success, rollback on error
- Session tracking for debugging
- Request ID generation for tracing

#### Redis Client
- Simple caching interface with `get()`, `set()`, `delete()`, `update()`
- JSON serialization support with `get_json()` and `set_json()`
- TTL (Time To Live) management
- Multiple key deletion support

#### Health Check
- Database connectivity check
- Redis connectivity check
- Returns 200 (healthy) or 503 (unhealthy)
- Accessible at `/api/root/health`

## Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_api.py -v
```

## Development

### Creating new migration:
```bash
make migrate-create
# or
alembic revision --autogenerate -m "migration description"
```

### Applying migrations:
```bash
make migrate
# or
alembic upgrade head
```

### Code formatting:
```bash
make format
```

## License

MIT License - see [LICENSE](LICENSE) file
