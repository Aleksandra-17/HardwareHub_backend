import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine

from src.database.base import Base
from src.routers.auth.models import User  # noqa: F401
from src.routers.components.models import Component, ComputerComponent  # noqa: F401
from src.routers.device_types.models import DeviceType  # noqa: F401
from src.routers.devices.models import AuditEntry, Device  # noqa: F401
from src.routers.licenses.models import License  # noqa: F401
from src.routers.locations.models import Location  # noqa: F401
from src.routers.people.models import Person  # noqa: F401
from src.routers.workstations.models import Workstation, WorkstationRequirement  # noqa: F401


def _get_url() -> str:
    """URL для миграций: DATABASE_URL или из POSTGRES_* env, иначе из alembic.ini."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    ip = os.environ.get("POSTGRES_IP")
    if ip:
        user = os.environ.get("POSTGRES_USERNAME", "postgres")
        pwd = os.environ.get("POSTGRES_PASSWORD", "postgres")
        port = os.environ.get("POSTGRES_PORT", "5432")
        db = os.environ.get("POSTGRES_DATABASE_NAME", "fastapi_db")
        driver = os.environ.get("POSTGRES_DRIVER", "asyncpg")
        return f"postgresql+{driver}://{user}:{pwd}@{ip}:{port}/{db}"
    return context.config.get_main_option("sqlalchemy.url", "") or ""


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


def run_async_migrations_online() -> None:
    """Run migrations in 'online' mode with async support.

    This function provides async migration support for asyncpg driver.
    """
    url = _get_url()

    if not url:
        raise ValueError("No sqlalchemy.url found in configuration")

    # Create async engine for asyncpg
    async_engine = create_async_engine(url)

    async def do_run_migrations():
        async with async_engine.begin() as connection:
            # Use run_sync to run sync Alembic operations in async context
            await connection.run_sync(
                lambda sync_conn: context.configure(
                    connection=sync_conn, target_metadata=target_metadata
                )
            )

            # Run migrations in sync context
            await connection.run_sync(lambda _: context.run_migrations())

    # Run async migrations
    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Check if we're using asyncpg
    url = _get_url()
    if url and "asyncpg" in url:
        run_async_migrations_online()
    else:
        run_migrations_online()
