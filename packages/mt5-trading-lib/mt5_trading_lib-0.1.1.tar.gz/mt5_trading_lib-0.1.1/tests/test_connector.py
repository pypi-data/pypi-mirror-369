"""Unit-тесты для Mt5Connector c моками MetaTrader5 и сценариями circuit breaker."""

import sys
import time
import types

import pytest

from mt5_trading_lib.config import Config, MT5Credentials, RetrySettings
from mt5_trading_lib.exceptions import (
    ConnectionError,
    HealthCheckError,
    InitializationError,
)
from mt5_trading_lib.retry_manager import CircuitState, RetryManager


def install_fake_mt5():
    """Устанавливает подмену модуля MetaTrader5 в sys.modules и возвращает (state, module).

    Гарантирует, что ранее импортированный реальный модуль и модуль коннектора
    будут выгружены для корректной подстановки.
    """
    # Удаляем возможные кэши
    sys.modules.pop("MetaTrader5", None)
    sys.modules.pop("mt5_trading_lib.connector", None)
    state = {
        "initialize_returns": True,
        "last_error": (1, "err"),
        "terminal_info": object(),
        "account_info": object(),
        "shutdown_called": False,
    }

    mod = types.ModuleType("MetaTrader5")

    def initialize(**kwargs):
        return state["initialize_returns"]

    def last_error():
        return state["last_error"]

    def terminal_info():
        return state["terminal_info"]

    def account_info():
        return state["account_info"]

    def shutdown():
        state["shutdown_called"] = True

    mod.initialize = initialize
    mod.last_error = last_error
    mod.terminal_info = terminal_info
    mod.account_info = account_info
    mod.shutdown = shutdown
    mod.__version__ = "5.0.0"

    sys.modules["MetaTrader5"] = mod
    return state, mod


def build_config(attempts: int = 3, base_delay: float = 0.01) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        retry=RetrySettings(attempts=attempts, base_delay=base_delay),
    )


def test_connect_success():
    state, _ = install_fake_mt5()
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    assert conn.connect() is True
    assert conn.is_initialized is True


def test_connect_failure_initialization():
    state, _ = install_fake_mt5()
    state["initialize_returns"] = False
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    with pytest.raises(InitializationError):
        conn.connect()
    assert conn.is_initialized is False


def test_connect_exception_converted_to_connection_error():
    state, mod = install_fake_mt5()

    # заменить initialize на выбрасывающий исключение
    def boom(**kwargs):
        raise RuntimeError("boom")

    mod.initialize = boom
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    with pytest.raises(ConnectionError):
        conn.connect()


def test_health_check_success():
    state, _ = install_fake_mt5()
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    conn.is_initialized = True
    assert conn.health_check() is True


def test_health_check_not_initialized():
    state, _ = install_fake_mt5()
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    with pytest.raises(HealthCheckError):
        conn.health_check()


def test_health_check_terminal_none():
    state, mod = install_fake_mt5()

    # вернуть None из terminal_info
    def terminal_none():
        return None

    mod.terminal_info = terminal_none

    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    conn.is_initialized = True
    with pytest.raises(HealthCheckError):
        conn.health_check()


def test_disconnect_calls_shutdown():
    state, mod = install_fake_mt5()
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config()
    conn = Mt5Connector(cfg)
    conn.is_initialized = True
    conn.disconnect()
    assert state["shutdown_called"] is True
    assert conn.is_initialized is False


def test_circuit_breaker_with_connector():
    state, _ = install_fake_mt5()
    from mt5_trading_lib.connector import Mt5Connector

    cfg = build_config(attempts=2, base_delay=0.01)
    conn = Mt5Connector(cfg)

    # две неудачные инициализации откроют breaker
    state["initialize_returns"] = False
    rm = RetryManager(cfg)

    with pytest.raises(Exception):
        rm.execute_with_circuit_breaker(conn.connect)
    with pytest.raises(Exception):
        rm.execute_with_circuit_breaker(conn.connect)

    assert rm.get_circuit_breaker_state() == CircuitState.OPEN

    # эмулируем истечение таймера восстановления и успешный вызов
    rm.circuit_breaker.last_failure_time = time.time() - (
        rm.circuit_breaker.recovery_timeout + 0.01
    )
    state["initialize_returns"] = True

    assert rm.execute_with_circuit_breaker(conn.connect) is True
    assert rm.get_circuit_breaker_state() == CircuitState.CLOSED
