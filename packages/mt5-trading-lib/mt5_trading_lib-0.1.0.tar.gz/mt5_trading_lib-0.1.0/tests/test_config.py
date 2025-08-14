"""Unit-тесты для модуля конфигурации (pydantic-settings)."""

import os
from unittest.mock import patch

import pytest

from mt5_trading_lib.config import (
    CacheSettings,
    Config,
    MT5Credentials,
    RetrySettings,
    SecuritySettings,
)
from mt5_trading_lib.exceptions import ConfigurationError


class TestConfigLoad:
    """Тесты загрузки конфигурации из переменных окружения."""

    @patch.dict(
        os.environ,
        {
            # nested settings use '__' как разделитель
            "MT5__LOGIN": "12345",
            "MT5__PASSWORD": "test_password",
            "MT5__SERVER": "test_server",
            "CACHE__TTL": "600",
            "RETRY__ATTEMPTS": "4",
            "RETRY__BASE_DELAY": "0.1",
            "LOGGING__LEVEL": "DEBUG",
        },
        clear=True,
    )
    def test_load_config_from_env(self):
        cfg = Config.load_config(env_file=".env-nonexistent")
        assert isinstance(cfg, Config)
        assert cfg.mt5.login == 12345
        assert cfg.mt5.password == "test_password"
        assert cfg.mt5.server == "test_server"
        assert cfg.cache.ttl == 600
        assert cfg.retry.attempts == 4
        assert pytest.approx(cfg.retry.base_delay, rel=1e-3) == 0.1

    @patch.dict(os.environ, {}, clear=True)
    def test_load_config_missing_required_raises(self):
        with pytest.raises(ConfigurationError):
            Config.load_config(env_file=".env-does-not-exist")


class TestConfigDirectInit:
    """Тесты прямой инициализации без .env."""

    def test_direct_init_valid(self):
        cfg = Config(
            mt5=MT5Credentials(login=1, password="p", server="s"),
            cache=CacheSettings(ttl=123),
            retry=RetrySettings(attempts=5, base_delay=1.5),
            security=SecuritySettings(encryption_key_base64=None),
        )
        assert cfg.mt5.login == 1
        assert cfg.cache.ttl == 123
        assert cfg.retry.attempts == 5
