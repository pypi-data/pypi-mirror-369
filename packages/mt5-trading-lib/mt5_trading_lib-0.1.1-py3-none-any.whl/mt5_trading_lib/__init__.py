# mt5_trading_lib/__init__.py
"""
Инициализация пакета mt5_trading_lib.
Этот файл определяет публичный API библиотеки, экспортируя основные классы и функции.
Пользователи библиотеки должны импортировать из этого пакета.
"""

# --- Импорт и экспорт основных классов ---

from .config import Config

# 1. Базовые модули
from .exceptions import (
    AsyncOperationError,
    CacheError,
    ConfigurationError,
    ConnectionError,
    CredentialEncryptionError,
    DataFetchError,
    HealthCheckError,
    InitializationError,
    InvalidSymbolError,
    InvalidTimeFrameError,
    Mt5TradingLibError,
    OrderCloseError,
    OrderModifyError,
    OrderSendError,
    OrderValidationError,
    RetryExhaustedError,
    SecurityError,
    TradingOperationError,
)
from .logging_config import get_logger, setup_logging


# Ленивые импорты для тяжёлых модулей, чтобы не тянуть зависимости при import mt5_trading_lib
def __getattr__(name):
    if name == "Mt5Connector":
        from .connector import Mt5Connector

        return Mt5Connector
    if name == "CacheManager":
        from .cache_manager import CacheManager

        return CacheManager
    if name == "RetryManager":
        from .retry_manager import RetryManager

        return RetryManager
    if name == "CircuitState":
        from .retry_manager import CircuitState

        return CircuitState
    if name == "SecurityManager":
        from .security_manager import SecurityManager

        return SecurityManager
    if name == "MetricsCollector":
        from .metrics_collector import MetricsCollector

        return MetricsCollector
    if name == "EventBus":
        from .event_bus import EventBus

        return EventBus
    if name == "Middleware":
        from .middleware import Middleware

        return Middleware
    if name == "MiddlewareChain":
        from .middleware import MiddlewareChain

        return MiddlewareChain
    if name == "LoggingMiddleware":
        from .middleware import LoggingMiddleware

        return LoggingMiddleware
    if name == "RateLimitingMiddleware":
        from .middleware import RateLimitingMiddleware

        return RateLimitingMiddleware
    if name == "DataFetcher":
        from .data_fetcher import DataFetcher

        return DataFetcher
    if name == "OrderManager":
        from .order_manager import OrderManager

        return OrderManager
    if name == "AsyncMt5Client":
        from .async_client import AsyncMt5Client

        return AsyncMt5Client
    raise AttributeError(name)


# --- Определение содержимого пакета (__all__) ---
# Это определяет, что будет импортировано при `from mt5_trading_lib import *`
# и помогает IDE и инструментам анализа кода понимать публичный API.

__all__ = [
    # Базовые модули
    "Mt5TradingLibError",
    "ConfigurationError",
    "ConnectionError",
    "InitializationError",
    "HealthCheckError",
    "DataFetchError",
    "InvalidSymbolError",
    "InvalidTimeFrameError",
    "TradingOperationError",
    "OrderSendError",
    "OrderModifyError",
    "OrderCloseError",
    "OrderValidationError",
    "SecurityError",
    "CredentialEncryptionError",
    "CacheError",
    "RetryExhaustedError",
    "AsyncOperationError",
    "Config",
    "setup_logging",
    "get_logger",
    # Инфраструктурные компоненты
    "Mt5Connector",
    "CacheManager",
    "RetryManager",
    "CircuitState",
    "SecurityManager",
    "MetricsCollector",
    "EventBus",
    "Middleware",
    "MiddlewareChain",
    "LoggingMiddleware",
    "RateLimitingMiddleware",
    # Основные компоненты
    "DataFetcher",
    "OrderManager",
    "AsyncMt5Client",
]

# --- Дополнительная инициализация пакета ---
# Можно выполнить какие-либо действия при импорте пакета, например, настройку логирования по умолчанию.
# Однако, обычно это делается явно пользователем. Здесь просто отметим.
# setup_logging() # Не вызываем автоматически, чтобы не конфликтовать с пользовательскими настройками

# --- Версия пакета ---
# Хорошей практикой является указание версии пакета.
# В будущем это будет управляться через setup.py/pyproject.toml.
__version__ = "0.1.1"

# --- Сообщение при импорте (опционально) ---
# import logging
# logging.getLogger(__name__).debug(f"Пакет mt5_trading_lib версии {__version__} импортирован.")
