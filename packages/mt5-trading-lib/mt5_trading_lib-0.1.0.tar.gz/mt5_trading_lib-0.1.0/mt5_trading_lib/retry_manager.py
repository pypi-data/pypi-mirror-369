# mt5_trading_lib/retry_manager.py
"""
Модуль для управления повторными попытками (retry) и паттерном Circuit Breaker.
Предоставляет класс RetryManager для централизованной настройки и применения
политик повтора и состояния Circuit Breaker для различных операций.
Использует библиотеки tenacity для retry и circuitbreaker (или простую реализацию) для Circuit Breaker.
"""

import functools
import time
from enum import Enum
from typing import Any, Callable, Optional

from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import Config
from .exceptions import ConnectionError as Mt5LibConnectionError
from .exceptions import Mt5TradingLibError, RetryExhaustedError
from .logging_config import get_logger

# Для Circuit Breaker можно использовать стороннюю библиотеку, например, `circuitbreaker`.
# Устанавливается через `pip install circuitbreaker`.
# Если не устанавливать, можно реализовать базовую версию.
# from circuitbreaker import circuit
# В этом примере реализуем простую версию Circuit Breaker внутри модуля.


logger = get_logger(__name__)


class CircuitState(Enum):
    """Состояния Circuit Breaker."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class SimpleCircuitBreaker:
    """
    Простая реализация паттерна Circuit Breaker.
    """

    def __init__(
        self, failure_threshold: int, recovery_timeout: int, expected_exception: type
    ):
        """
        Инициализирует Circuit Breaker.

        Args:
            failure_threshold (int): Количество последовательных ошибок для перехода в OPEN.
            recovery_timeout (int): Время в секундах, после которого состояние переходит в HALF_OPEN.
            expected_exception (type): Тип исключения, который считается "провалом".
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет функцию с учетом состояния Circuit Breaker.

        Args:
            func (Callable): Функция для выполнения.
            *args: Позиционные аргументы для функции.
            **kwargs: Именованные аргументы для функции.

        Returns:
            Any: Результат выполнения функции.

        Raises:
            Exception: Исключение, выброшенное функцией или связанное с состоянием Circuit Breaker.
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.debug("Circuit Breaker перешел в состояние HALF_OPEN.")
            else:
                # Circuit is open, fail fast
                logger.warning("Circuit Breaker открыт. Вызов заблокирован.")
                raise self.expected_exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Проверяет, прошло ли достаточно времени для попытки восстановления."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) > self.recovery_timeout

    def _on_success(self):
        """Обработчик успешного вызова."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(
                "Circuit Breaker закрыт после успешного вызова в HALF_OPEN состоянии."
            )

    def _on_failure(self):
        """Обработчик провального вызова."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.error(f"Circuit Breaker: Ошибка #{self.failure_count}")
        if (
            self.state == CircuitState.HALF_OPEN
            or self.failure_count >= self.failure_threshold
        ):
            self.state = CircuitState.OPEN
            logger.critical(
                f"Circuit Breaker открыт после {self.failure_count} ошибок."
            )

    def get_state(self) -> CircuitState:
        """Возвращает текущее состояние Circuit Breaker."""
        return self.state


class RetryManager:
    """
    Класс для управления политиками повторных попыток и Circuit Breaker.
    """

    def __init__(self, config: Config):
        """
        Инициализирует менеджер с конфигурацией.

        Args:
            config (Config): Экземпляр класса Config с настройками retry и circuit breaker.
        """
        self.config = config
        # Инициализируем Circuit Breaker для MT5 операций
        # Используем общее исключение Mt5TradingLibError как триггер для Circuit Breaker
        # Можно уточнить до ConnectionError или других специфичных ошибок.
        self.circuit_breaker = SimpleCircuitBreaker(
            failure_threshold=config.retry.attempts,  # Например, 3 ошибки
            recovery_timeout=config.retry.base_delay * 10,  # Например, 10 секунд
            expected_exception=Mt5TradingLibError,  # Или более конкретное исключение
        )
        logger.debug("RetryManager инициализирован.")

    def get_retrying_strategy(self) -> Retrying:
        """
        Создает и возвращает объект Retrying с настройками из конфигурации.

        Returns:
            Retrying: Настроенный объект для выполнения retry.
        """
        # Ретраим только сетевые/транспортные ошибки, но не бизнес-ошибки (например, OrderSendError)
        strategy = Retrying(
            stop=stop_after_attempt(self.config.retry.attempts),
            wait=wait_exponential(multiplier=self.config.retry.base_delay),
            retry=retry_if_exception_type(
                (ConnectionError, TimeoutError, Mt5LibConnectionError)
            ),
            reraise=False,
        )
        return strategy

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет функцию с применением политики повтора.

        Args:
            func (Callable): Функция для выполнения.
            *args: Позиционные аргументы для функции.
            **kwargs: Именованные аргументы для функции.

        Returns:
            Any: Результат выполнения функции.

        Raises:
            RetryExhaustedError: Если все попытки исчерпаны.
        """
        logger.debug(f"Выполнение {func.__name__} с retry...")
        retrying_obj = self.get_retrying_strategy()
        try:
            # Используем tenacity для выполнения с retry
            result = retrying_obj(func, *args, **kwargs)
            logger.debug(f"Функция {func.__name__} успешно выполнена.")
            return result
        except RetryError as re:
            logger.error(
                f"Все попытки выполнения {func.__name__} исчерпаны.", exc_info=True
            )
            last_exc = re.last_attempt.exception() if re.last_attempt else None
            raise RetryExhaustedError(
                f"Функция {func.__name__} не выполнилась после {self.config.retry.attempts} попыток.",
                error_code=getattr(last_exc, "error_code", None),
            ) from (last_exc or re)
        except Exception:
            # Исключение не подпадает под ретраи — пробрасываем как есть
            raise

    def execute_with_circuit_breaker(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет функцию с применением Circuit Breaker.

        Args:
            func (Callable): Функция для выполнения.
            *args: Позиционные аргументы для функции.
            **kwargs: Именованные аргументы для функции.

        Returns:
            Any: Результат выполнения функции.

        Raises:
            Mt5TradingLibError: Исключение, выброшенное функцией или Circuit Breaker'ом.
        """
        logger.debug(f"Выполнение {func.__name__} с Circuit Breaker...")
        try:
            # Передаем вызов в Circuit Breaker
            result = self.circuit_breaker.call(func, *args, **kwargs)
            logger.debug(
                f"Функция {func.__name__} успешно выполнена через Circuit Breaker."
            )
            return result
        except Exception as e:
            logger.error(
                f"Ошибка выполнения {func.__name__} через Circuit Breaker.",
                exc_info=True,
            )
            # Исключение уже обернуто или является исходным, просто пробрасываем
            raise e

    def execute_with_retry_and_circuit_breaker(
        self, func: Callable, *args, **kwargs
    ) -> Any:
        """
        Выполняет функцию с применением и retry, и Circuit Breaker.
        Сначала проверяется Circuit Breaker, затем применяется retry.

        Args:
            func (Callable): Функция для выполнения.
            *args: Позиционные аргументы для функции.
            **kwargs: Именованные аргументы для функции.

        Returns:
            Any: Результат выполнения функции.

        Raises:
            RetryExhaustedError: Если все попытки исчерпаны.
            Mt5TradingLibError: Исключение, выброшенное функцией или Circuit Breaker'ом.
        """
        logger.debug(f"Выполнение {func.__name__} с retry и Circuit Breaker...")

        def _func_wrapper():
            # Внутри retry оборачиваем вызов с Circuit Breaker
            return self.circuit_breaker.call(func, *args, **kwargs)

        return self.execute_with_retry(_func_wrapper)

    def get_circuit_breaker_state(self) -> CircuitState:
        """
        Возвращает текущее состояние Circuit Breaker.

        Returns:
            CircuitState: Текущее состояние.
        """
        return self.circuit_breaker.get_state()

    # --- Декораторы ---
    def retry(self, func: Callable) -> Callable:
        """
        Декоратор для применения retry к функции.

        Args:
            func (Callable): Функция для декорирования.

        Returns:
            Callable: Декорированная функция.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute_with_retry(func, *args, **kwargs)

        return wrapper

    def circuit_breaker(self, func: Callable) -> Callable:
        """
        Декоратор для применения Circuit Breaker к функции.

        Args:
            func (Callable): Функция для декорирования.

        Returns:
            Callable: Декорированная функция.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute_with_circuit_breaker(func, *args, **kwargs)

        return wrapper

    def retry_and_circuit_breaker(self, func: Callable) -> Callable:
        """
        Декоратор для применения и retry, и Circuit Breaker к функции.

        Args:
            func (Callable): Функция для декорирования.

        Returns:
            Callable: Декорированная функция.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute_with_retry_and_circuit_breaker(func, *args, **kwargs)

        return wrapper


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     config = Config.load_config()
#     retry_manager = RetryManager(config)
#
#     def unreliable_function():
#         import random
#         if random.random() < 0.7: # 70% шанс ошибки
#             raise ConnectionError("Simulated connection error")
#         return "Success!"
#
#     try:
#         # result = retry_manager.execute_with_retry(unreliable_function)
#         # result = retry_manager.execute_with_circuit_breaker(unreliable_function)
#         result = retry_manager.execute_with_retry_and_circuit_breaker(unreliable_function)
#         print(f"Результат: {result}")
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         print(f"Состояние Circuit Breaker: {retry_manager.get_circuit_breaker_state()}")
