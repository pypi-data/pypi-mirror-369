"""Дополнительные тесты для AsyncMt5Client: покрытие методов данных и ордеров."""

import asyncio

import pytest

from mt5_trading_lib.config import Config, MT5Credentials


class StubConnector:
    def __init__(self):
        self.is_initialized = True

    def is_connected(self):
        return True

    def disconnect(self):
        # no-op for tests
        self.is_initialized = False


class StubDataFetcher:
    def __init__(self):
        self.account_called = False
        self.hist_called = False
        self.rt_called = False
        self.cache_inv_called = False
        self.cache_clear_called = False

    def get_account_info(self):
        self.account_called = True
        return {"ok": 1}

    def get_historical_quotes(self, symbol, timeframe, start_pos, count):
        self.hist_called = True
        import pandas as pd

        return pd.DataFrame({"a": [1]})

    def get_real_time_quotes(self, symbol):
        self.rt_called = True
        return {"bid": 1.0}

    def invalidate_account_info_cache(self):
        self.cache_inv_called = True
        return True

    def clear_all_data_cache(self):
        self.cache_clear_called = True


class StubOrderManager:
    def __init__(self):
        self.sent = False
        self.modified = False
        self.closed = False

    def send_market_order(self, *args, **kwargs):
        self.sent = True
        return 123

    def modify_order(self, *args, **kwargs):
        self.modified = True
        return True

    def close_order(self, *args, **kwargs):
        self.closed = True
        return True


def build_client_with_stubs():
    from mt5_trading_lib.async_client import AsyncMt5Client

    cfg = Config(mt5=MT5Credentials(login=1, password="p", server="s"))
    client = AsyncMt5Client(cfg)
    client._connector = StubConnector()
    client._data_fetcher = StubDataFetcher()
    client._order_manager = StubOrderManager()
    return client


@pytest.mark.asyncio
async def test_async_client_data_and_orders_methods():
    client = build_client_with_stubs()

    assert await client.get_account_info() == {"ok": 1}

    # Для TIMEFRAME подставим произвольные числа, так как DataFetcher здесь — стаб
    import random

    df = await client.get_historical_quotes("EURUSD", 1, 0, 1)
    assert list(df.columns) == ["a"]

    rt = await client.get_real_time_quotes("EURUSD")
    assert rt["bid"] == 1.0

    ticket = await client.send_market_order("EURUSD", 1.0, "BUY")
    assert ticket == 123

    assert await client.modify_order(1, new_sl=1.1)
    assert await client.close_order(1)

    assert await client.invalidate_account_info_cache() is True
    await client.clear_all_data_cache()
    # Дополнительно покроем is_connected
    assert await client.is_connected() is True


@pytest.mark.asyncio
async def test_run_in_executor_kwargs_and_disconnect_branch():
    client = build_client_with_stubs()

    # kwargs-ветка
    def foo(a=None, b=None):
        return (a, b)

    assert await client._run_in_executor(foo, a=1, b=2) == (1, 2)

    # disconnect when connector exists (покрывает ветку if self._connector)
    await client.disconnect()
