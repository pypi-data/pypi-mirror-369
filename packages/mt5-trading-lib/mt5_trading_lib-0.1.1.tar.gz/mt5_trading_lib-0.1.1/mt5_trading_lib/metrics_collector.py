# mt5_trading_lib/metrics_collector.py
"""
Модуль для сбора метрик производительности и состояния библиотеки.
Использует prometheus-client для создания и обновления метрик.
Предоставляет класс MetricsCollector для централизованного управления метриками.
"""

import threading
import time
from typing import Any, Dict, Optional

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from .config import Config
from .logging_config import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """
    Класс для сбора и управления метриками библиотеки.
    Использует Prometheus для хранения и экспорта метрик.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: Optional[Config] = None):
        """
        Реализует Singleton паттерн для MetricsCollector.
        Это гарантирует, что будет создан только один экземпляр коллектора.
        """
        if cls._instance is None:
            with cls._lock:
                # Повторная проверка внутри блокировки на случай гонки потоков
                if cls._instance is None:
                    cls._instance = super(MetricsCollector, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[Config] = None):
        """
        Инициализирует MetricsCollector. Выполняется только один раз благодаря Singleton.

        Args:
            config (Optional[Config]): Экземпляр класса Config. Используется при первой инициализации.
        """
        if self._initialized:
            return

        self.config = config
        # Создаем отдельный реестр для наших метрик, чтобы не конфликтовать с другими
        self.registry = CollectorRegistry(auto_describe=True)

        # --- Определение метрик ---
        # Счетчики (Counter) для подсчета событий
        self.connection_attempts = Counter(
            "mt5_connection_attempts_total",
            "Total number of MT5 connection attempts",
            ["status"],  # Метка: 'success' или 'failure'
            registry=self.registry,
        )
        self.orders_sent = Counter(
            "mt5_orders_sent_total",
            "Total number of orders sent to MT5",
            ["status"],  # Метка: 'success' или 'failure'
            registry=self.registry,
        )
        self.data_fetches = Counter(
            "mt5_data_fetches_total",
            "Total number of data fetch attempts",
            [
                "data_type",
                "status",
            ],  # Метки: тип данных ('account', 'historical', 'realtime') и статус
            registry=self.registry,
        )

        # Гистограммы (Histogram) для измерения времени выполнения
        self.operation_duration = Histogram(
            "mt5_operation_duration_seconds",
            "Duration of MT5 operations",
            [
                "operation"
            ],  # Метка: название операции ('connect', 'fetch_data', 'send_order' и т.д.)
            registry=self.registry,
            buckets=(
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
                float("inf"),
            ),  # Пример buckets
        )

        # Гаuges (Gauge) для измерения текущего состояния
        self.cache_size = Gauge(
            "mt5_cache_size",
            "Current number of items in the cache",
            registry=self.registry,
        )
        self.circuit_breaker_state = Gauge(
            "mt5_circuit_breaker_state",
            "Current state of the circuit breaker (0=CLOSED, 1=OPEN, 2=HALF_OPEN)",
            registry=self.registry,
        )
        # Можно добавить больше gauge метрик, например, для состояния соединения
        self.is_connected = Gauge(
            "mt5_is_connected",
            "Indicates if the library is currently connected to MT5 (1=connected, 0=disconnected)",
            registry=self.registry,
        )

        self._initialized = True
        logger.debug("MetricsCollector инициализирован.")

    # --- Методы для обновления метрик ---

    def inc_connection_attempts(self, status: str):
        """Увеличивает счетчик попыток подключения."""
        self.connection_attempts.labels(status=status).inc()
        logger.debug(f"Метрика обновлена: connection_attempts[{status}] += 1")

    def inc_orders_sent(self, status: str):
        """Увеличивает счетчик отправленных ордеров."""
        self.orders_sent.labels(status=status).inc()
        logger.debug(f"Метрика обновлена: orders_sent[{status}] += 1")

    def inc_data_fetches(self, data_type: str, status: str):
        """Увеличивает счетчик попыток получения данных."""
        self.data_fetches.labels(data_type=data_type, status=status).inc()
        logger.debug(f"Метрика обновлена: data_fetches[{data_type}, {status}] += 1")

    def observe_operation_duration(self, operation: str, duration: float):
        """Записывает время выполнения операции в гистограмму."""
        self.operation_duration.labels(operation=operation).observe(duration)
        logger.debug(
            f"Метрика обновлена: operation_duration[{operation}] = {duration:.4f}s"
        )

    def set_cache_size(self, size: int):
        """Устанавливает значение размера кэша."""
        self.cache_size.set(size)
        logger.debug(f"Метрика обновлена: cache_size = {size}")

    def set_circuit_breaker_state(self, state_value: int):
        """
        Устанавливает значение состояния Circuit Breaker.
        0 - CLOSED,1 - OPEN, 2 - HALF_OPEN.
        """
        self.circuit_breaker_state.set(state_value)
        logger.debug(f"Метрика обновлена: circuit_breaker_state = {state_value}")

    def set_connection_status(self, is_connected: bool):
        """Устанавливает значение статуса подключения."""
        self.is_connected.set(1 if is_connected else 0)
        logger.debug(f"Метрика обновлена: is_connected = {is_connected}")

    # --- Методы для декорирования функций и автоматического сбора метрик ---
    def timer(self, operation_name: str):
        """
        Декоратор для измерения времени выполнения функции и записи в метрику.

        Args:
            operation_name (str): Название операции для метрики.

        Returns:
            Callable: Декоратор.
        """

        def decorator(func):
            import functools

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    self.observe_operation_duration(
                        operation_name, time.perf_counter() - start_time
                    )
                    return result
                except Exception as e:
                    # Время записываем даже в случае ошибки
                    self.observe_operation_duration(
                        operation_name, time.perf_counter() - start_time
                    )
                    raise e

            return wrapper

        return decorator

    # --- Метод для экспорта метрик ---
    def generate_metrics(self) -> bytes:
        """
        Генерирует текущие метрики в формате, пригодном для Prometheus.

        Returns:
            bytes: Байтовая строка с метриками.
        """
        try:
            # generate_latest возвращает bytes
            metrics_data = generate_latest(self.registry)
            logger.debug("Метрики успешно сгенерированы для экспорта.")
            return metrics_data
        except Exception as e:
            logger.error(f"Ошибка при генерации метрик: {e}", exc_info=True)
            # Возвращаем пустые метрики или ошибку в формате Prometheus
            return b"# ERROR: Failed to generate metrics\n"

    def get_content_type(self) -> str:
        """
        Возвращает правильный Content-Type для HTTP ответа с метриками.

        Returns:
            str: Content-Type.
        """
        return CONTENT_TYPE_LATEST


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     config = Config.load_config()
#
#     # Получаем экземпляр MetricsCollector (Singleton)
#     metrics_collector1 = MetricsCollector(config)
#     metrics_collector2 = MetricsCollector() # config не нужен при повторной инициализации
#
#     print(f"Один и тот же экземпляр? {metrics_collector1 is metrics_collector2}") # True
#
#     # Обновляем метрики
#     metrics_collector1.inc_connection_attempts("success")
#     metrics_collector1.inc_orders_sent("failure")
#     metrics_collector1.inc_data_fetches("account", "success")
#     metrics_collector1.set_cache_size(150)
#     metrics_collector1.set_circuit_breaker_state(0) # CLOSED
#     metrics_collector1.set_connection_status(True)
#
#     # Используем декоратор
#     @metrics_collector1.timer("test_operation")
#     def some_operation():
#         time.sleep(0.1) # Имитируем работу
#         return "Done"
#
#     result = some_operation()
#     print(f"Результат операции: {result}")
#
#     # Экспортируем метрики
#     metrics_data = metrics_collector1.generate_metrics()
#     print("\n--- Экспортированные метрики ---")
#     print(metrics_data.decode('utf-8'))
