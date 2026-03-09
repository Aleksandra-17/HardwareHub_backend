import configparser
import os
from dataclasses import asdict, dataclass


def _get_config_parser() -> configparser.ConfigParser | None:
    """Load config.ini if it exists (for local dev without Docker)."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
    if os.path.exists(config_path):
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        return cfg
    return None


_config = _get_config_parser()


def _get(key: str, default: str | None = None, section: str = "") -> str:
    """Read from env var first, then config.ini. Env: {SECTION}_{KEY} e.g. POSTGRES_USERNAME."""
    env_name = (
        f"{section}_{key}".upper().replace(".", "_") if section else key.upper().replace(".", "_")
    )
    val = os.environ.get(env_name)
    if val is not None:
        return val
    if _config and section and _config.has_section(section) and _config.has_option(section, key):
        return _config.get(section, key)
    if default is not None:
        return default
    raise ValueError(f"Missing config: {env_name} (env) or [{section}] {key} (config.ini)")


def _get_int(key: str, default: int | None = None, section: str = "") -> int:
    val = _get(key, default=str(default) if default is not None else None, section=section)
    return int(val) if val else 0


def _get_bool(key: str, default: bool = False, section: str = "") -> bool:
    val = _get(key, default=str(default).lower(), section=section)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")


class CfgBase:
    """Base for config classes."""

    dict: callable = asdict


class PostgresCfg(CfgBase):
    def __init__(self):
        self.database: str = _get("DATABASE", "postgresql", "POSTGRES")
        self.driver: str = _get("DRIVER", "asyncpg", "POSTGRES")
        self.database_name: str = _get("DATABASE_NAME", "fastapi_db", "POSTGRES")
        self.username: str = _get("USERNAME", "postgres", "POSTGRES")
        self.password: str = _get("PASSWORD", "postgres", "POSTGRES")
        self.ip: str = _get("IP", "localhost", "POSTGRES")
        self.port: int = _get_int("PORT", 5432, "POSTGRES")

        self.database_engine_pool_timeout: int = _get_int(
            "DATABASE_ENGINE_POOL_TIMEOUT", 30, "POSTGRES"
        )
        self.database_engine_pool_recycle: int = _get_int(
            "DATABASE_ENGINE_POOL_RECYCLE", 3600, "POSTGRES"
        )
        self.database_engine_pool_size: int = _get_int("DATABASE_ENGINE_POOL_SIZE", 5, "POSTGRES")
        self.database_engine_max_overflow: int = _get_int(
            "DATABASE_ENGINE_MAX_OVERFLOW", 10, "POSTGRES"
        )
        self.database_engine_pool_ping: bool = _get_bool(
            "DATABASE_ENGINE_POOL_PING", True, "POSTGRES"
        )
        self.database_echo: bool = _get_bool("DATABASE_ECHO", False, "POSTGRES")

    @property
    def url(self) -> str:
        return f"{self.database}+{self.driver}://{self.username}:{self.password}@{self.ip}:{self.port}/{self.database_name}"


def _uvicorn_cfg() -> "UvicornCfg":
    return UvicornCfg(
        host=_get("HOST", "0.0.0.0", "UVICORN"),
        port=_get_int("PORT", 8000, "UVICORN"),
        workers=_get_int("WORKERS", 4, "UVICORN"),
        loop=_get("LOOP", "uvloop", "UVICORN"),
        http=_get("HTTP", "httptools", "UVICORN"),
    )


@dataclass
class UvicornCfg(CfgBase):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    loop: str = "uvloop"
    http: str = "httptools"


def _redis_cfg() -> "RedisCfg":
    return RedisCfg(
        host=_get("HOST", "localhost", "REDIS"),
        port=_get_int("PORT", 6379, "REDIS"),
        db=_get_int("DB", 0, "REDIS"),
        password=_get("PASSWORD", "", "REDIS"),
    )


@dataclass
class RedisCfg(CfgBase):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""

    def dict(self):
        return asdict(self)


uvicorn_cfg = _uvicorn_cfg()
redis_cfg = _redis_cfg()
