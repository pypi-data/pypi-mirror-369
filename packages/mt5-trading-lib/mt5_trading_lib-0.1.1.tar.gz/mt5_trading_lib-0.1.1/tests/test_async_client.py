"""Unit-тесты для AsyncMt5Client с использованием pytest-asyncio и моков."""

import asyncio
import sys
import types

import pytest

from mt5_trading_lib.config import (
    CacheSettings,
    Config,
    MT5Credentials,
    RetrySettings,
    SecuritySettings,
)


def install_fake_mt5_for_connect():
    """Подмена MetaTrader5 достаточная для работы Mt5Connector.connect()."""
    sys.modules.pop("MetaTrader5", None)
    # Сбрасываем импортированные модули, которые тянут реальный MetaTrader5
    for m in [
        "mt5_trading_lib.connector",
        "mt5_trading_lib.data_fetcher",
        "mt5_trading_lib.order_manager",
        "mt5_trading_lib.async_client",
    ]:
        sys.modules.pop(m, None)

    mod = types.ModuleType("MetaTrader5")
    mod.__version__ = "5.0.0"
    mod.initialize = lambda **kwargs: True
    mod.last_error = lambda: (1, "err")
    mod.account_info = lambda: object()
    mod.terminal_info = lambda: object()
    mod.shutdown = lambda: None
    sys.modules["MetaTrader5"] = mod
    return mod


def build_config() -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        retry=RetrySettings(attempts=2, base_delay=0.01),
        cache=CacheSettings(ttl=1),
        security=SecuritySettings(encryption_key_base64=None),
    )


@pytest.mark.asyncio
async def test_async_connect_and_is_connected():
    install_fake_mt5_for_connect()
    cfg = build_config()
    from mt5_trading_lib.async_client import AsyncMt5Client

    client = AsyncMt5Client(cfg)
    ok = await client.connect()
    assert ok is True
    assert await client.is_connected() is True
    await client.disconnect()


@pytest.mark.asyncio
async def test_async_data_methods_require_init():
    install_fake_mt5_for_connect()
    cfg = build_config()
    from mt5_trading_lib.async_client import AsyncMt5Client

    client = AsyncMt5Client(cfg)
    # Не вызывали connect, должен падать
    with pytest.raises(Exception):
        await client.get_account_info()


@pytest.mark.asyncio
async def test_async_cache_control_methods_require_init():
    install_fake_mt5_for_connect()
    cfg = build_config()
    from mt5_trading_lib.async_client import AsyncMt5Client

    client = AsyncMt5Client(cfg)
    with pytest.raises(Exception):
        await client.invalidate_account_info_cache()


@pytest.mark.asyncio
async def test_async_disconnect_without_connect_is_noop():
    install_fake_mt5_for_connect()
    cfg = build_config()
    from mt5_trading_lib.async_client import AsyncMt5Client

    client = AsyncMt5Client(cfg)
    # disconnect без connect не должен падать
    await client.disconnect()
