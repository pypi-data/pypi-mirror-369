# mt5_trading_lib/middleware.py
"""
Модуль для реализации системы middleware.
Предоставляет абстрактный базовый класс Middleware и
конкретные реализации для логирования, ограничения скорости и потенциальной авторизации.
Middleware позволяет добавлять слои обработки (например, логирование, rate limiting)
вокруг вызовов методов основных компонентов библиотеки.
"""

import asyncio
import functools
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional, Union

from .config import Config
from .logging_config import get_logger
from .metrics_collector import MetricsCollector

logger = get_logger(__name__)


class Middleware(ABC):
    """
    Абстрактный базовый класс для middleware.
    Определяет интерфейс для синхронных и асинхронных обработчиков.
    """

    @abstractmethod
    def process_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        """
        Обрабатывает запрос до его выполнения.

        Args:
            name (str): Имя вызываемого метода или операции.
            kwargs (dict): Аргументы вызова.

        Returns:
            tuple[str, dict]: Кортеж из (новое имя, новые аргументы).
        """
        pass

    @abstractmethod
    def process_response(self, name: str, response: Any, execution_time: float) -> Any:
        """
        Обрабатывает ответ после выполнения запроса.

        Args:
            name (str): Имя вызванного метода или операции.
            response (Any): Ответ от метода.
            execution_time (float): Время выполнения запроса в секундах.

        Returns:
            Any: Обработанный или оригинальный ответ.
        """
        pass

    @abstractmethod
    async def aprocess_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        """
        Асинхронно обрабатывает запрос до его выполнения.

        Args:
            name (str): Имя вызываемого метода или операции.
            kwargs (dict): Аргументы вызова.

        Returns:
            tuple[str, dict]: Кортеж из (новое имя, новые аргументы).
        """
        pass

    @abstractmethod
    async def aprocess_response(
        self, name: str, response: Any, execution_time: float
    ) -> Any:
        """
        Асинхронно обрабатывает ответ после выполнения запроса.

        Args:
            name (str): Имя вызванного метода или операции.
            response (Any): Ответ от метода.
            execution_time (float): Время выполнения запроса в секундах.

        Returns:
            Any: Обработанный или оригинальный ответ.
        """
        pass


class MiddlewareChain:
    """
    Класс для управления цепочкой middleware.
    Позволяет добавлять middleware и применять их к функциям.
    """

    def __init__(self):
        self.middlewares: list[Middleware] = []

    def add_middleware(self, middleware: Middleware) -> None:
        """Добавляет middleware в цепочку."""
        self.middlewares.append(middleware)
        logger.debug(f"Middleware {middleware.__class__.__name__} добавлен в цепочку.")

    def wrap_function(
        self, func: Callable, operation_name: Optional[str] = None
    ) -> Callable:
        """
        Оборачивает синхронную функцию в цепочку middleware.

        Args:
            func (Callable): Функция для оборачивания.
            operation_name (Optional[str]): Имя операции. Если None, используется func.__name__.

        Returns:
            Callable: Обернутая функция.
        """
        op_name = operation_name if operation_name else func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Начальные имя и аргументы
            current_name = op_name
            current_kwargs = kwargs.copy()  # Копируем, чтобы не изменять оригинальные

            # Применяем process_request ко всем middleware
            for mw in self.middlewares:
                try:
                    current_name, current_kwargs = mw.process_request(
                        current_name, current_kwargs
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка в process_request middleware {mw.__class__.__name__}: {e}",
                        exc_info=True,
                    )
                    # Можно выбрасывать исключение или продолжать
                    raise

            start_time = time.perf_counter()
            try:
                # Выполняем оригинальную функцию
                result = func(*args, **current_kwargs)
            except Exception as e:
                # Даже в случае ошибки функции, мы должны обработать "ответ" (исключение)
                execution_time = time.perf_counter() - start_time
                # Применяем process_response (в обратном порядке) к исключению?
                # Или просто логируем? Для простоты, логируем время ошибки.
                logger.error(
                    f"Ошибка в функции {current_name} после middleware: {e}",
                    exc_info=True,
                )
                # Метрики ошибок можно инкрементировать здесь или в самих middleware
                # Например, в LoggingMiddleware
                raise  # Пробрасываем исключение дальше
            finally:
                execution_time = time.perf_counter() - start_time

            # Применяем process_response ко всем middleware (в обратном порядке для симметрии?)
            # Обычно middleware применяются в прямом порядке для request и в обратном для response.
            # Но для простоты применим в прямом.
            processed_result = result
            for mw in self.middlewares:
                try:
                    processed_result = mw.process_response(
                        current_name, processed_result, execution_time
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка в process_response middleware {mw.__class__.__name__}: {e}",
                        exc_info=True,
                    )
                    # Можно выбрасывать исключение или возвращать последний успешный результат
                    # Для простоты, игнорируем ошибку middleware и возвращаем результат функции
                    pass  # processed_result остается равным result или предыдущему результату middleware

            return processed_result

        return wrapper

    def wrap_async_function(
        self, func: Callable, operation_name: Optional[str] = None
    ) -> Callable:
        """
        Оборачивает асинхронную функцию в цепочку middleware.

        Args:
            func (Callable): Асинхронная функция (coroutine function) для оборачивания.
            operation_name (Optional[str]): Имя операции.

        Returns:
            Callable: Обернутая асинхронная функция (coroutine function).
        """
        op_name = operation_name if operation_name else func.__name__

        @functools.wraps(func)
        async def awrapper(*args, **kwargs):
            # Начальные имя и аргументы
            current_name = op_name
            current_kwargs = kwargs.copy()

            # Применяем aprocess_request ко всем middleware
            for mw in self.middlewares:
                try:
                    current_name, current_kwargs = await mw.aprocess_request(
                        current_name, current_kwargs
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка в aprocess_request middleware {mw.__class__.__name__}: {e}",
                        exc_info=True,
                    )
                    raise

            start_time = time.perf_counter()
            try:
                # Выполняем оригинальную асинхронную функцию
                result = await func(*args, **current_kwargs)
            except Exception as e:
                execution_time = time.perf_counter() - start_time
                logger.error(
                    f"Ошибка в асинхронной функции {current_name} после middleware: {e}",
                    exc_info=True,
                )
                raise
            finally:
                execution_time = time.perf_counter() - start_time

            # Применяем aprocess_response ко всем middleware
            processed_result = result
            for mw in self.middlewares:
                try:
                    processed_result = await mw.aprocess_response(
                        current_name, processed_result, execution_time
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка в aprocess_response middleware {mw.__class__.__name__}: {e}",
                        exc_info=True,
                    )
                    pass

            return processed_result

        return awrapper


# --- Конкретные реализации Middleware ---


class LoggingMiddleware(Middleware):
    """
    Middleware для логирования входящих запросов и исходящих ответов.
    """

    def __init__(self, config: Config):
        self.config = config
        # Получаем экземпляр MetricsCollector, если он уже создан
        # Это демонстрирует loose coupling через Singleton
        self.metrics_collector = MetricsCollector()

    def process_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        logger.info(f"[LoggingMiddleware] Вызов метода: {name}, Аргументы: {kwargs}")
        # Не изменяем имя и аргументы
        return name, kwargs

    def process_response(self, name: str, response: Any, execution_time: float) -> Any:
        logger.info(
            f"[LoggingMiddleware] Метод {name} завершен. Время выполнения: {execution_time:.4f}с."
        )
        # Можем использовать MetricsCollector здесь
        # Предположим, что у нас есть способ классифицировать успешность
        # Для примера, если response не None, считаем успехом
        # В реальности это зависит от контракта функции
        status = "success" if response is not None else "failure"
        # Или можно инкрементировать в OrderManager/DataFetcher после вызова
        # Для демонстрации сделаем здесь
        # Например, для ордеров:
        # if name.startswith("send_market_order"):
        #     self.metrics_collector.inc_orders_sent(status)

        # Или для получения данных:
        # if "account_info" in name:
        #     self.metrics_collector.inc_data_fetches("account", status)

        # В этом базовом примере просто логируем время
        # self.metrics_collector.observe_operation_duration(name, execution_time)
        return response

    async def aprocess_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        logger.info(
            f"[LoggingMiddleware-Async] Вызов метода: {name}, Аргументы: {kwargs}"
        )
        return name, kwargs

    async def aprocess_response(
        self, name: str, response: Any, execution_time: float
    ) -> Any:
        logger.info(
            f"[LoggingMiddleware-Async] Метод {name} завершен. Время выполнения: {execution_time:.4f}с."
        )
        # self.metrics_collector.observe_operation_duration(name, execution_time)
        return response


class RateLimitingMiddleware(Middleware):
    """
    Middleware для ограничения частоты вызовов (rate limiting).
    Использует простой токен-бакет алгоритм на уровне экземпляра.
    В реальном приложении может использовать Redis для распределенного rate limiting.
    """

    def __init__(self, config: Config, max_calls: int = 10, period: int = 1):
        """
        Инициализирует rate limiter.

        Args:
            config (Config): Конфигурация.
            max_calls (int): Максимальное количество вызовов за период. По умолчанию 10.
            period (int): Период в секундах. По умолчанию 1.
        """
        self.config = config
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self._lock = threading.Lock()

    def _is_allowed(self) -> bool:
        """Проверяет, разрешен ли текущий вызов."""
        now = time.time()
        # Удаляем вызовы, которые вышли за рамки периода
        with self._lock:
            self.calls = [
                call_time for call_time in self.calls if call_time > now - self.period
            ]
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False

    async def _ais_allowed(self) -> bool:
        """Асинхронная проверка разрешения вызова."""
        # Для простоты используем тот же блокирующий метод
        # В production может быть адаптирован для async/await
        return self._is_allowed()

    def process_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        if not self._is_allowed():
            logger.warning(
                f"[RateLimitingMiddleware] Превышен лимит вызовов для операции: {name}"
            )
            # Можно выбросить кастомное исключение
            from .exceptions import Mt5TradingLibError

            raise Mt5TradingLibError(
                f"Превышен лимит вызовов для операции '{name}' ({self.max_calls} вызовов/{self.period}сек)"
            )
        return name, kwargs

    def process_response(self, name: str, response: Any, execution_time: float) -> Any:
        # Нет пост-обработки для rate limiting
        return response

    async def aprocess_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
        if not await self._ais_allowed():
            logger.warning(
                f"[RateLimitingMiddleware-Async] Превышен лимит вызовов для операции: {name}"
            )
            from .exceptions import Mt5TradingLibError

            raise Mt5TradingLibError(
                f"Превышен лимит вызовов для операции '{name}' ({self.max_calls} вызовов/{self.period}сек)"
            )
        return name, kwargs

    async def aprocess_response(
        self, name: str, response: Any, execution_time: float
    ) -> Any:
        return response


# Пример фиктивного AuthMiddleware (требует доработки для реальной аутентификации)
# class AuthMiddleware(Middleware):
#     """
#     Middleware для проверки авторизации/токенов.
#     """
#     def __init__(self, config: Config):
#         self.config = config
#         # Здесь можно загрузить ключи, токены и т.д.
#
#     def process_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
#         # Проверка токена в kwargs или в глобальном контексте
#         # token = kwargs.get('auth_token') or get_current_token()
#         # if not token or not self._validate_token(token):
#         #     raise SecurityError("Неверный или отсутствующий токен авторизации.")
#         logger.debug("[AuthMiddleware] Проверка авторизации пройдена.")
#         return name, kwargs
#
#     def process_response(self, name: str, response: Any, execution_time: float) -> Any:
#         return response
#
#     async def aprocess_request(self, name: str, kwargs: dict) -> tuple[str, dict]:
#         # Асинхронная проверка
#         return name, kwargs
#
#     async def aprocess_response(self, name: str, response: Any, execution_time: float) -> Any:
#         return response
#
#     def _validate_token(self, token: str) -> bool:
#         # Реализация проверки токена
#         return True # Заглушка


# --- Пример использования ---
# def example_function(x: int, y: int) -> int:
#     """Пример функции для оборачивания."""
#     logger.info(f"Выполнение example_function с x={x}, y={y}")
#     time.sleep(0.1) # Имитируем работу
#     return x + y
#
# async def async_example_function(x: int, y: int) -> int:
#     """Пример асинхронной функции для оборачивания."""
#     logger.info(f"Выполнение async_example_function с x={x}, y={y}")
#     await asyncio.sleep(0.1) # Имитируем асинхронную работу
#     return x * y
#
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     config = Config.load_config()
#
#     # Создаем цепочку middleware
#     middleware_chain = MiddlewareChain()
#     middleware_chain.add_middleware(LoggingMiddleware(config))
#     middleware_chain.add_middleware(RateLimitingMiddleware(config, max_calls=2, period=1)) # Ограничим до 2 вызовов/сек
#
#     # Оборачиваем функцию
#     wrapped_func = middleware_chain.wrap_function(example_function, "add_operation")
#     wrapped_async_func = middleware_chain.wrap_async_function(async_example_function, "multiply_operation")
#
#     try:
#         # Выполняем обернутую функцию
#         result1 = wrapped_func(x=5, y=3)
#         print(f"Результат синхронной функции: {result1}")
#
#         result2 = wrapped_func(x=10, y=20)
#         print(f"Результат синхронной функции: {result2}")
#
#         # Третий вызов превысит лимит
#         # result3 = wrapped_func(x=1, y=1)
#         # print(f"Результат синхронной функции: {result3}")
#
#     except Exception as e:
#         logger.error(f"Ошибка при вызове обернутой функции: {e}")
#
#     # Для асинхронной функции
#     async def run_async():
#         try:
#             aresult1 = await wrapped_async_func(x=5, y=3)
#             print(f"Результат асинхронной функции: {aresult1}")
#
#             aresult2 = await wrapped_async_func(x=4, y=4)
#             print(f"Результат асинхронной функции: {aresult2}")
#
#             # Третий вызов превысит лимит
#             # aresult3 = await wrapped_async_func(x=2, y=2)
#             # print(f"Результат асинхронной функции: {aresult3}")
#
#         except Exception as e:
#             logger.error(f"Ошибка при вызове обернутой асинхронной функции: {e}")
#
#     # asyncio.run(run_async())
