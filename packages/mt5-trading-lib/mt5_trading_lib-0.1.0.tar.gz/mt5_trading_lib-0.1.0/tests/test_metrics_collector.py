"""Unit-тесты для MetricsCollector: инкременты и экспорт."""

from mt5_trading_lib.metrics_collector import MetricsCollector


def test_metrics_update_and_export():
    mc = MetricsCollector()
    mc.inc_connection_attempts("success")
    mc.inc_orders_sent("failure")
    mc.inc_data_fetches("account", "success")
    mc.set_cache_size(5)
    mc.set_circuit_breaker_state(1)
    mc.set_connection_status(True)

    data = mc.generate_metrics()
    assert isinstance(data, (bytes, bytearray))
    assert b"mt5_connection_attempts_total" in data
