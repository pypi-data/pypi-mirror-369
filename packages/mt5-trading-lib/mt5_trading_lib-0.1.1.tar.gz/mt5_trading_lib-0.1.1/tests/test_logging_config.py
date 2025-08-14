"""Unit-тесты для logging_config: проверка setup_logging и get_logger."""

import importlib
import os


def test_setup_logging_text(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.delenv("USE_JSON_LOGGING", raising=False)
    from mt5_trading_lib import logging_config

    importlib.reload(logging_config)
    logging_config.setup_logging()
    logger = logging_config.get_logger(__name__)
    logger.info("test message")


def test_setup_logging_json(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("USE_JSON_LOGGING", "true")
    from mt5_trading_lib import logging_config

    importlib.reload(logging_config)
    logging_config.setup_logging()
    logger = logging_config.get_logger(__name__)
    logger.info("json message")
