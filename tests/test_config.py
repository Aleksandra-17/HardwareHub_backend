"""Tests for src.config."""

import configparser
import os
from unittest.mock import patch

import pytest

from src import config
from src.config import PostgresCfg, RedisCfg, redis_cfg, uvicorn_cfg


class TestConfigEnvVars:
    """Test config reads from env vars."""

    def test_postgres_cfg_from_env(self):
        """PostgresCfg reads from env vars."""
        with patch.dict(
            os.environ,
            {
                "POSTGRES_IP": "dbhost",
                "POSTGRES_DATABASE_NAME": "mydb",
                "POSTGRES_USERNAME": "user",
                "POSTGRES_PASSWORD": "secret",
                "POSTGRES_PORT": "5433",
            },
            clear=False,
        ):
            cfg = PostgresCfg()
            assert cfg.ip == "dbhost"
            assert cfg.database_name == "mydb"
            assert cfg.username == "user"
            assert cfg.password == "secret"
            assert cfg.port == 5433

    def test_postgres_url(self):
        """PostgresCfg.url builds connection string."""
        with patch.dict(
            os.environ,
            {
                "POSTGRES_USERNAME": "u",
                "POSTGRES_PASSWORD": "p",
                "POSTGRES_IP": "host",
                "POSTGRES_PORT": "5432",
                "POSTGRES_DATABASE_NAME": "db",
            },
            clear=False,
        ):
            cfg = PostgresCfg()
            url = cfg.url
            assert "postgresql+asyncpg://u:p@host:5432/db" == url

    def test_uvicorn_cfg(self):
        """UvicornCfg has expected structure."""
        assert hasattr(uvicorn_cfg, "host")
        assert hasattr(uvicorn_cfg, "port")
        assert hasattr(uvicorn_cfg, "workers")
        assert isinstance(uvicorn_cfg.port, int)

    def test_redis_cfg(self):
        """RedisCfg has expected structure."""
        assert hasattr(redis_cfg, "host")
        assert hasattr(redis_cfg, "port")
        assert hasattr(redis_cfg, "db")
        assert hasattr(redis_cfg, "password")
        assert hasattr(redis_cfg, "dict")

    def test_redis_cfg_dict(self):
        """RedisCfg.dict returns dict for Redis client."""
        d = redis_cfg.dict()
        assert "host" in d
        assert "port" in d
        assert "db" in d
        assert "password" in d


class TestConfigFallback:
    """Test config fallback to config.ini."""

    def test_get_raises_when_missing(self):
        """_get raises ValueError when required key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(config, "_config", None):
                with pytest.raises(ValueError, match="Missing config"):
                    config._get("DATABASE_NAME", section="POSTGRES")

    def test_get_uses_config_ini_when_env_unset(self):
        """_get uses config.ini when env var is unset."""
        mock_config = configparser.ConfigParser()
        mock_config.add_section("POSTGRES")
        mock_config.set("POSTGRES", "DATABASE_NAME", "from_ini")

        old_val = os.environ.pop("POSTGRES_DATABASE_NAME", None)
        try:
            with patch.object(config, "_config", mock_config):
                val = config._get("DATABASE_NAME", section="POSTGRES")
                assert val == "from_ini"
        finally:
            if old_val is not None:
                os.environ["POSTGRES_DATABASE_NAME"] = old_val
