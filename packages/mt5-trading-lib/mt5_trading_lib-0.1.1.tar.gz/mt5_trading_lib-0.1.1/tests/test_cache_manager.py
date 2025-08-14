"""Unit-тесты для CacheManager."""

import time

from mt5_trading_lib.cache_manager import CacheManager
from mt5_trading_lib.config import CacheSettings, Config, MT5Credentials


def build_config(ttl: int = 1) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        cache=CacheSettings(ttl=ttl),
    )


def test_set_get_simple_key():
    cfg = build_config(ttl=5)
    cm = CacheManager(cfg)
    cm.set("k", "v")
    assert cm.get("k") == "v"


def test_set_get_complex_key_tuple():
    cfg = build_config(ttl=5)
    cm = CacheManager(cfg)
    key = ("get_data", "EURUSD", "M1", 100)
    value = {"data": [1, 2, 3]}
    cm.set(key, value)
    assert cm.get(key) == value


def test_invalidate_key():
    cfg = build_config(ttl=5)
    cm = CacheManager(cfg)
    cm.set("to_del", 123)
    assert cm.invalidate("to_del") is True
    assert cm.get("to_del", default=None) is None


def test_clear_cache():
    cfg = build_config(ttl=5)
    cm = CacheManager(cfg)
    cm.set("a", 1)
    cm.set("b", 2)
    assert cm.get_stats()["local_cache_currsize"] >= 2
    cm.clear()
    assert cm.get_stats()["local_cache_currsize"] == 0


def test_ttl_expiration():
    cfg = build_config(ttl=1)
    cm = CacheManager(cfg)
    cm.set("short", "live")
    assert cm.get("short") == "live"
    time.sleep(1.1)
    assert cm.get("short", default=None) is None
