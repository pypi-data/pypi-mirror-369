"""Unit-тесты для RetryManager и SimpleCircuitBreaker."""

import time

import pytest

from mt5_trading_lib.config import Config, MT5Credentials, RetrySettings
from mt5_trading_lib.exceptions import Mt5TradingLibError, RetryExhaustedError
from mt5_trading_lib.retry_manager import CircuitState, RetryManager


def build_config(attempts: int = 3, base_delay: float = 0.01) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        retry=RetrySettings(attempts=attempts, base_delay=base_delay),
    )


def test_execute_with_retry_success_after_failures():
    cfg = build_config(attempts=3, base_delay=0.01)
    rm = RetryManager(cfg)

    call_state = {"count": 0}

    def flaky():
        call_state["count"] += 1
        if call_state["count"] < 3:
            # первая и вторая попытки падают
            raise ConnectionError("temporary error")
        return "ok"

    result = rm.execute_with_retry(flaky)
    assert result == "ok"
    assert call_state["count"] == 3


def test_execute_with_circuit_breaker_fail_fast_when_open():
    cfg = build_config(attempts=2, base_delay=0.01)
    rm = RetryManager(cfg)

    def fail():
        raise Mt5TradingLibError("boom")

    # Открываем breaker
    try:
        rm.execute_with_circuit_breaker(fail)
    except Mt5TradingLibError:
        pass
    try:
        rm.execute_with_circuit_breaker(fail)
    except Mt5TradingLibError:
        pass

    # Теперь breaker открыт; третья попытка должна падать сразу таким же исключением
    with pytest.raises(Mt5TradingLibError):
        rm.execute_with_circuit_breaker(lambda: "should not run")


def test_execute_with_retry_exhausted():
    cfg = build_config(attempts=2, base_delay=0.01)
    rm = RetryManager(cfg)

    def always_fail():
        # Ретраим только сетевые ошибки
        raise ConnectionError("boom")

    with pytest.raises(RetryExhaustedError):
        rm.execute_with_retry(always_fail)


def test_circuit_breaker_opens_and_recovers():
    cfg = build_config(attempts=2, base_delay=0.01)  # threshold=2, recovery≈0.1s
    rm = RetryManager(cfg)

    def fail():
        raise Mt5TradingLibError("cb-fail")

    # Две последовательные ошибки открывают breaker
    with pytest.raises(Mt5TradingLibError):
        rm.execute_with_circuit_breaker(fail)
    with pytest.raises(Mt5TradingLibError):
        rm.execute_with_circuit_breaker(fail)

    assert rm.get_circuit_breaker_state() == CircuitState.OPEN

    # Имитируем истечение recovery_timeout
    rm.circuit_breaker.last_failure_time = time.time() - (
        rm.circuit_breaker.recovery_timeout + 0.01
    )

    # Успешный вызов в HALF_OPEN закрывает breaker
    def ok():
        return "ok"

    result = rm.execute_with_circuit_breaker(ok)
    assert result == "ok"
    assert rm.get_circuit_breaker_state() == CircuitState.CLOSED


def test_execute_with_retry_and_circuit_breaker_wraps_connection_errors():
    cfg = build_config(attempts=2, base_delay=0.01)
    rm = RetryManager(cfg)

    def fail():
        raise ConnectionError("net")

    with pytest.raises(RetryExhaustedError):
        rm.execute_with_retry_and_circuit_breaker(fail)


def test_retry_manager_strategy_reraises_disabled():
    cfg = build_config(attempts=1, base_delay=0.01)
    rm = RetryManager(cfg)

    def fail_once():
        raise ConnectionError("net")

    with pytest.raises(RetryExhaustedError):
        rm.execute_with_retry(fail_once)
