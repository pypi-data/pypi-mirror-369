"""Unit-тесты для DataFetcher: данные, кэш hit/miss, TTL, ошибки."""

import sys
import time
import types

import pandas as pd
import pytest

from mt5_trading_lib.cache_manager import CacheManager
from mt5_trading_lib.config import CacheSettings, Config, MT5Credentials, RetrySettings
from mt5_trading_lib.exceptions import InvalidSymbolError, InvalidTimeFrameError
from mt5_trading_lib.retry_manager import RetryManager


def install_fake_mt5():
    """Подмена модуля MetaTrader5 для тестов DataFetcher.

    Сбрасывает кэш модуля DataFetcher, чтобы он заново импортировал мок.
    Возвращает (state, module).
    """
    sys.modules.pop("MetaTrader5", None)
    sys.modules.pop("mt5_trading_lib.data_fetcher", None)

    state = {
        "valid_symbols": {"EURUSD", "USDJPY"},
        "account_calls": 0,
        "tick_calls": 0,
        "copy_rates_calls": 0,
        "account": {"balance": 1000.0, "equity": 1000.0},
        "tick": {"bid": 1.2345, "ask": 1.2347},
        "rates": [
            {
                "time": int(time.time()),
                "open": 1.23,
                "high": 1.24,
                "low": 1.22,
                "close": 1.235,
                "tick_volume": 10,
                "spread": 2,
                "real_volume": 10,
            }
        ],
        "last_error": (1, "err"),
    }

    mod = types.ModuleType("MetaTrader5")

    # TIMEFRAME константы, которые использует _validate_timeframe
    mod.TIMEFRAME_M1 = 1
    mod.TIMEFRAME_M2 = 2
    mod.TIMEFRAME_M3 = 3
    mod.TIMEFRAME_M4 = 4
    mod.TIMEFRAME_M5 = 5
    mod.TIMEFRAME_M6 = 6
    mod.TIMEFRAME_M10 = 10
    mod.TIMEFRAME_M12 = 12
    mod.TIMEFRAME_M15 = 15
    mod.TIMEFRAME_M20 = 20
    mod.TIMEFRAME_M30 = 30
    mod.TIMEFRAME_H1 = 60
    mod.TIMEFRAME_H2 = 120
    mod.TIMEFRAME_H3 = 180
    mod.TIMEFRAME_H4 = 240
    mod.TIMEFRAME_H6 = 360
    mod.TIMEFRAME_H8 = 480
    mod.TIMEFRAME_H12 = 720
    mod.TIMEFRAME_D1 = 1440
    mod.TIMEFRAME_W1 = 10080
    mod.TIMEFRAME_MN1 = 43200

    def symbol_info(symbol: str):
        return {} if symbol in state["valid_symbols"] else None

    def last_error():
        return state["last_error"]

    class _WithAsDict:
        def __init__(self, data):
            self._data = data

        def _asdict(self):
            return dict(self._data)

    def account_info():
        state["account_calls"] += 1
        return (
            _WithAsDict(state["account"]) if state.get("account") is not None else None
        )

    def symbol_info_tick(symbol: str):
        state["tick_calls"] += 1
        return _WithAsDict(state["tick"]) if state.get("tick") is not None else None

    def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int):
        state["copy_rates_calls"] += 1
        return list(state["rates"]) if state.get("rates") is not None else None

    mod.symbol_info = symbol_info
    mod.last_error = last_error
    mod.account_info = account_info
    mod.symbol_info_tick = symbol_info_tick
    mod.copy_rates_from_pos = copy_rates_from_pos
    mod.__version__ = "5.0.0"

    sys.modules["MetaTrader5"] = mod
    return state, mod


class FakeConnector:
    def __init__(self, connected: bool = True):
        self._connected = connected

    def is_connected(self) -> bool:
        return self._connected


def build_config(
    cache_ttl: int = 5, attempts: int = 2, base_delay: float = 0.01
) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        cache=CacheSettings(ttl=cache_ttl),
        retry=RetrySettings(attempts=attempts, base_delay=base_delay),
    )


def build_components(cache_ttl: int = 5):
    cfg = build_config(cache_ttl=cache_ttl)
    cache = CacheManager(cfg)
    retry = RetryManager(cfg)
    connector = FakeConnector(True)
    sys.modules.pop("mt5_trading_lib.data_fetcher", None)
    from mt5_trading_lib.data_fetcher import DataFetcher

    return cfg, cache, retry, connector, DataFetcher


def test_account_info_cache_hit_miss():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    df = DataFetcher(cfg, connector, cache, retry)

    # miss -> fetch
    res1 = df.get_account_info()
    assert isinstance(res1, dict)
    assert state["account_calls"] == 1

    # hit -> no fetch
    res2 = df.get_account_info()
    assert res2 == res1
    assert state["account_calls"] == 1


def test_account_info_cache_ttl_expiration():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=1)
    df = DataFetcher(cfg, connector, cache, retry)

    df.get_account_info()
    assert state["account_calls"] == 1
    time.sleep(1.1)
    df.get_account_info()
    assert state["account_calls"] == 2


def test_historical_quotes_cache():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    tf = sys.modules["MetaTrader5"].TIMEFRAME_M1
    df1 = dfetcher.get_historical_quotes("EURUSD", tf, count=1)
    assert isinstance(df1, pd.DataFrame)
    assert state["copy_rates_calls"] == 1

    df2 = dfetcher.get_historical_quotes("EURUSD", tf, count=1)
    assert isinstance(df2, pd.DataFrame)
    assert state["copy_rates_calls"] == 1  # из кэша


def test_historical_quotes_cache_ttl():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=1)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    tf = sys.modules["MetaTrader5"].TIMEFRAME_M1
    dfetcher.get_historical_quotes("EURUSD", tf, count=1)
    assert state["copy_rates_calls"] == 1
    time.sleep(1.1)
    dfetcher.get_historical_quotes("EURUSD", tf, count=1)
    assert state["copy_rates_calls"] == 2


def test_get_real_time_quotes_error_logged_and_none():
    state, mod = install_fake_mt5()

    # symbol_info_tick вызывает исключение
    def boom(symbol):
        raise RuntimeError("boom")

    mod.symbol_info_tick = boom
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    assert dfetcher.get_real_time_quotes("EURUSD") is None


def test_historical_quotes_invalid_symbol():
    state, mod = install_fake_mt5()
    mod.symbol_info = lambda s: None
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    with pytest.raises(InvalidSymbolError):
        dfetcher.get_historical_quotes("BAD", mod.TIMEFRAME_M1, count=1)


def test_historical_quotes_invalid_timeframe():
    state, mod = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    with pytest.raises(InvalidTimeFrameError):
        dfetcher.get_historical_quotes("EURUSD", 9999, count=1)


def test_real_time_quotes_ok():
    state, mod = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    data = dfetcher.get_real_time_quotes("EURUSD")
    assert isinstance(data, dict)
    assert state["tick_calls"] == 1


def test_real_time_quotes_invalid_symbol():
    state, mod = install_fake_mt5()
    mod.symbol_info = lambda s: None
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    with pytest.raises(InvalidSymbolError):
        dfetcher.get_real_time_quotes("BAD")


def test_historical_quotes_error_returns_none():
    state, mod = install_fake_mt5()
    mod.copy_rates_from_pos = lambda *a, **k: None
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    tf = mod.TIMEFRAME_M1
    res = dfetcher.get_historical_quotes("EURUSD", tf, count=1)
    assert res is None


def test_real_time_quotes_error_returns_none():
    state, mod = install_fake_mt5()
    mod.symbol_info_tick = lambda s: None
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)

    res = dfetcher.get_real_time_quotes("EURUSD")
    assert res is None


def test_account_info_not_connected_returns_none():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    # Не подключены
    connector._connected = False
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    assert dfetcher.get_account_info() is None


def test_account_info_mt5_none_returns_none():
    state, mod = install_fake_mt5()

    # account_info вернет None -> DataFetchError внутри fetch
    def account_none():
        return None

    mod.account_info = account_none
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    assert dfetcher.get_account_info() is None


def test_historical_quotes_not_connected_returns_none():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    connector._connected = False
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    tf = sys.modules["MetaTrader5"].TIMEFRAME_M1
    assert dfetcher.get_historical_quotes("EURUSD", tf, count=1) is None


def test_real_time_quotes_not_connected_returns_none():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    connector._connected = False
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    assert dfetcher.get_real_time_quotes("EURUSD") is None


def test_cache_invalidate_and_clear():
    state, _ = install_fake_mt5()
    cfg, cache, retry, connector, DataFetcher = build_components(cache_ttl=5)
    dfetcher = DataFetcher(cfg, connector, cache, retry)
    # Положим в кэш и инвалидируем
    dfetcher.cache_manager.set("account_info", {"a": 1})
    assert dfetcher.invalidate_account_info_cache() is True
    # Очистка всего кэша
    dfetcher.cache_manager.set("x", 1)
    dfetcher.clear_all_data_cache()
    assert dfetcher.cache_manager.get("x") is None
