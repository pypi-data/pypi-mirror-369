"""Unit-тесты для middleware: LoggingMiddleware и RateLimitingMiddleware."""

import pytest

from mt5_trading_lib.config import Config, MT5Credentials
from mt5_trading_lib.middleware import (
    LoggingMiddleware,
    MiddlewareChain,
    RateLimitingMiddleware,
)


def build_config():
    return Config(mt5=MT5Credentials(login=1, password="p", server="s"))


def test_logging_middleware_wraps_function():
    cfg = build_config()
    chain = MiddlewareChain()
    chain.add_middleware(LoggingMiddleware(cfg))

    def add(x: int, y: int) -> int:
        return x + y

    wrapped = chain.wrap_function(add, operation_name="add")
    assert wrapped(x=2, y=3) == 5


def test_rate_limiting_middleware_blocks_after_threshold():
    cfg = build_config()
    chain = MiddlewareChain()
    chain.add_middleware(RateLimitingMiddleware(cfg, max_calls=2, period=1))

    def f() -> int:
        return 1

    wrapped = chain.wrap_function(lambda: f(), operation_name="f")

    # Первые два вызова проходят
    assert wrapped() == 1
    assert wrapped() == 1

    # Третий вызов в пределах периода должен упасть
    with pytest.raises(Exception):
        wrapped()
