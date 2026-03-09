# FastAPI Template - Complete Overview

This document provides a complete overview of all files and configurations included in this template.

## 📋 Template Contents

### Core Configuration Files

| File | Description |
|------|-------------|
| `config.ini.example` | Application configuration template (INI format) |
| `alembic.ini.example` | Database migration configuration template |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore rules |
| `.editorconfig` | Editor configuration for consistent formatting |
| `ruff.toml` | Ruff linter and formatter configuration |

### Docker Files

| File | Description |
|------|-------------|
| `docker/Dockerfile` | Production Docker image (multi-stage, Python 3.13) |
| `docker/Dockerfile.dev` | Development Docker image with hot-reload |
| `docker/docker-compose.yml` | Production Docker Compose with PostgreSQL, Redis, Nginx |
| `docker/docker-compose.dev.yml` | Development Docker Compose setup |
| `docker/nginx/nginx.conf` | Nginx reverse proxy configuration with rate limiting |
| `.dockerignore` | Docker build context exclusions |

### CI/CD

| File | Description |
|------|-------------|
| `.github/workflows/develop.yaml` | GitHub Actions workflow for testing, building, and deployment |

### Deployment

| File | Description |
|------|-------------|
| `start.sh` | Startup script for running the application |

### Build Tools

| File | Description |
|------|-------------|
| `Makefile` | Convenient commands for development and deployment |

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Main project documentation |
| `DEPLOYMENT.md` | Detailed deployment guide |
| `CONTRIBUTING.md` | Contributing guidelines for developers |
| `TEMPLATE_INFO.md` | This file - template overview |

## 🎯 Key Features

### 1. Python 3.13 Support
- All Docker images use Python 3.13-slim
- CI/CD configured for Python 3.13
- Modern Python type hints support

### 2. Configuration
- Environment variables (Docker Compose) or `config.ini` (local dev)
- `alembic.ini` for database migrations
- Easy to read and modify
- Supports multiple environments

### 3. Docker Support
- **Production**: Multi-stage build, optimized image size
- **Development**: Hot-reload enabled, debugger support
- **Services**: PostgreSQL 15, Redis 7, Nginx
- Security: Non-root user, health checks

### 4. CI/CD Pipeline
- Automated testing on PRs
- Code quality checks (Ruff)
- Docker image building
- Automated deployment to production
- Health checks after deployment

### 5. Database
- PostgreSQL 15 Alpine
- SQLAlchemy ORM ready
- Alembic migrations configured
- Connection pooling support

### 6. Caching
- Redis 7 Alpine
- Ready for session storage and caching

### 7. Reverse Proxy
- Nginx with rate limiting
- Security headers configured
- WebSocket support
- SSL/TLS ready (commented out)

### 8. Development Tools
- Makefile with common commands
- Ruff for linting and formatting
- pytest for testing
- Hot-reload for development

## 🚀 Quick Start

### First Time Setup

1. **Copy configuration files:**
```bash
cp .env.example .env
cp alembic.ini.example alembic.ini
# For local dev without Docker: cp config.ini.example config.ini
```

2. **Edit .env with your values**

3. **Start development environment:**
```bash
make dev
```

That's it! Application runs at http://localhost:8000

## 📦 Configuration Structure

### config.ini Sections

```ini
[POSTGRES]
DATABASE = postgresql           # Database type
DRIVER = asyncpg                # Async driver for PostgreSQL
DATABASE_NAME = db_name         # Database name
USERNAME = postgres             # Database user
PASSWORD = password             # Database password
IP = localhost                  # Database host
PORT = 5432                     # Database port
DATABASE_ENGINE_POOL_TIMEOUT = 30      # Pool connection timeout (seconds)
DATABASE_ENGINE_POOL_RECYCLE = 3600    # Recycle connections after (seconds)
DATABASE_ENGINE_POOL_SIZE = 5          # Number of connections in pool
DATABASE_ENGINE_MAX_OVERFLOW = 10      # Max overflow connections
DATABASE_ENGINE_POOL_PING = true       # Pre-ping connections
DATABASE_ECHO = false                  # SQL logging (set to false in prod)

[UVICORN]
HOST = 0.0.0.0                  # Server host
PORT = 8000                     # Server port
WORKERS = 4                     # Number of worker processes
LOOP = uvloop                   # Event loop (asyncio/uvloop - uvloop is faster)
HTTP = httptools                # HTTP protocol (h11/httptools - httptools is faster)

[REDIS]
HOST = localhost                # Redis host
PORT = 6379                     # Redis port
DB = 0                          # Redis database number
PASSWORD =                      # Redis password (empty if none)
```

### Architecture Highlights

#### Middlewares
- **Database Middleware**: Automatic session management per request with auto-commit/rollback
- **Request ID**: UUID generation for request tracing
- **Session Tracking**: Debug session lifecycle with built-in tracker

#### Redis Client
- **Simple Interface**: `get()`, `set()`, `delete()`, `update()`
- **JSON Support**: `get_json()`, `set_json()` for automatic serialization
- **TTL Management**: Configurable time-to-live for cache entries
- **Bulk Operations**: `delete_many()` for multiple key deletion

#### Router Structure
Each router follows a consistent pattern:
- **router.py**: Route definitions and endpoint handlers
- **actions.py**: Business logic and orchestration
- **dal.py**: Data Access Layer (database queries)
- **models.py**: SQLAlchemy ORM models
- **schemas.py**: Pydantic request/response schemas

#### Health Check
- Endpoint: `/api/root/health`
- Checks: Database and Redis connectivity
- Returns: 200 (healthy) or 503 (unhealthy)

### alembic.ini

Standard Alembic configuration for database migrations.

## 🔧 Makefile Commands

```bash
make help           # Show all available commands
make install        # Install Python dependencies
make dev            # Start development environment (Docker)
make build          # Build production Docker image
make up             # Start production environment
make down           # Stop all containers
make logs           # Show container logs
make clean          # Remove containers and volumes
make test           # Run tests with pytest
make lint           # Run Ruff linter
make format         # Format code with Ruff
make migrate        # Apply database migrations
make migrate-create # Create new migration
make db-shell       # Open PostgreSQL shell
make redis-cli      # Open Redis CLI
```

## 🐳 Docker Services

### Production (docker-compose.yml)

- **fastapi-app**: Main application (port 8000)
- **postgres**: PostgreSQL 15 (port 5432)
- **redis**: Redis 7 (port 6379)
- **nginx**: Reverse proxy (ports 80, 443)

### Development (docker-compose.dev.yml)

- **fastapi-app**: Main application with hot-reload (ports 8000, 5678)
- **postgres**: PostgreSQL 15 (port 5432)
- **redis**: Redis 7 (port 6379)

## 🔐 GitHub Secrets Required

For CI/CD deployment:

- `SSH_PRIVATE_KEY`: SSH key for server access
- `SSH_HOST`: Server IP or domain
- `SSH_USER`: SSH username
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Production DB credentials
- `ALEMBIC_INI`: Production alembic.ini contents
- `DOCKER_USERNAME`: Docker Hub username (optional)
- `DOCKER_PASSWORD`: Docker Hub token (optional)

## 📝 Configuration Variables

### Application Environment Variables (via config.ini)

#### App Section
- `name`: Application name
- `environment`: development/production
- `debug`: Enable debug mode
- `host`: Host to bind
- `port`: Port to listen on
- `log_level`: Logging level

#### Database Section
- `url`: Full database URL
- `host`: Database host
- `port`: Database port
- `user`: Database user
- `password`: Database password
- `database`: Database name
- `pool_size`: Connection pool size
- `max_overflow`: Max overflow connections

#### Redis Section
- `url`: Full Redis URL
- `host`: Redis host
- `port`: Redis port
- `db`: Redis database number
- `password`: Redis password

#### Security Section
- `secret_key`: JWT secret key
- `algorithm`: JWT algorithm (HS256)
- `access_token_expire_minutes`: Token expiry time

#### CORS Section
- `origins`: Allowed origins (comma-separated)
- `allow_credentials`: Allow credentials
- `allow_methods`: Allowed methods
- `allow_headers`: Allowed headers

## 🏗️ Project Structure

```
fastapi-template/
├── .github/
│   └── workflows/
│       └── develop.yaml          # CI/CD pipeline
├── src/                          # Source code
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration loader (INI)
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
│   │   └── redis.py              # Redis controller
│   ├── services/                 # External service integrations
│   └── misc/                     # Utilities
│       ├── security.py           # Security utilities
│       └── timezone.py           # Timezone utilities
├── daemon-service/
│   └── fastapi-app.service       # Systemd service
├── docker/
│   ├── nginx/
│   │   └── nginx.conf            # Nginx config
│   ├── Dockerfile                # Production
│   ├── Dockerfile.dev            # Development
│   ├── docker-compose.yml        # Production compose
│   └── docker-compose.dev.yml    # Development compose
├── .dockerignore                 # Docker ignore
├── .editorconfig                 # Editor config
├── .gitignore                    # Git ignore
├── alembic.ini.example           # Alembic config template
├── config.ini.example            # App config (local dev without Docker)
├── .env.example                  # Docker Compose env template
├── CONTRIBUTING.md               # Contributing guide
├── DEPLOYMENT.md                 # Deployment guide
├── LICENSE                       # MIT License
├── Makefile                      # Build commands
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── ruff.toml                     # Ruff config
├── start.sh                      # Startup script
└── TEMPLATE_INFO.md              # This file
```

## 🎓 Next Steps

1. **Customize the template:**
   - Update `APP_NAME` in `.github/workflows/develop.yaml`
   - Modify `config.ini.example` with your defaults
   - Update `README.md` with your project details

2. **Add your application code:**
   - Create `app/` directory
   - Add your FastAPI routes in `app/api/`
   - Add models in `app/models/`
   - Add schemas in `app/schemas/`
   - Create `app/main.py` with FastAPI app

3. **Initialize Alembic:**
```bash
alembic init alembic
```

4. **Write your first test:**
```bash
mkdir tests
# Add your pytest tests
```

5. **Set up GitHub repository:**
   - Create repository on GitHub
   - Add required secrets
   - Push your code
   - CI/CD will run automatically

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)

## 💡 Tips

1. **Always use virtual environment** for local development
2. **Never commit** `config.ini` or `alembic.ini` to git
3. **Test migrations** both upgrade and downgrade
4. **Use type hints** everywhere for better IDE support
5. **Write tests** for all new features
6. **Run linter** before committing (`make lint`)
7. **Check logs** when debugging (`make logs`)

## 🆘 Getting Help

- Check `README.md` for quick start
- Read `DEPLOYMENT.md` for deployment help
- See `CONTRIBUTING.md` for development guidelines
- Check existing issues on GitHub
- Read application logs: `docker compose logs -f`

## ⚖️ License

MIT License - see LICENSE file for details

