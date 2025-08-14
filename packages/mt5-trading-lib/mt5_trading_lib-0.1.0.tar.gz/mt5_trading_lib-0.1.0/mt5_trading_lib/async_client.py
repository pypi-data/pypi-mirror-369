# mt5_trading_lib/async_client.py
"""
Модуль для асинхронного взаимодействия с MetaTrader 5.
Предоставляет класс AsyncMt5Client, который оборачивает синхронные компоненты
в асинхронный интерфейс, используя asyncio для конкурентности.
"""

import asyncio
import concurrent.futures
import functools
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd

from .cache_manager import CacheManager
from .config import Config
from .connector import Mt5Connector
from .data_fetcher import DataFetcher
from .exceptions import AsyncOperationError, Mt5TradingLibError
from .logging_config import get_logger
from .order_manager import OrderManager
from .retry_manager import RetryManager
from .security_manager import SecurityManager

logger = get_logger(__name__)


class AsyncMt5Client:
    """
    Асинхронный клиент для взаимодействия с MetaTrader 5.
    Оборачивает синхронные компоненты в асинхронный интерфейс.
    Использует ThreadPoolExecutor для выполнения блокирующих MT5 операций.
    """

    def __init__(self, config: Config):
        """
        Инициализирует асинхронный клиент.

        Args:
            config (Config): Экземпляр класса Config.
        """
        self.config = config

        # Инициализируем синхронные компоненты
        # Важно: Mt5Connector должен быть инициализирован в том же потоке, где будут вызываться MT5 функции.
        # Поэтому инициализацию соединения мы сделаем в методе connect.
        self._connector: Optional[Mt5Connector] = None
        self._cache_manager: Optional[CacheManager] = CacheManager(config)
        self._retry_manager: Optional[RetryManager] = RetryManager(config)
        self._security_manager: Optional[SecurityManager] = SecurityManager(config)

        # Компоненты, зависящие от connector
        self._data_fetcher: Optional[DataFetcher] = None
        self._order_manager: Optional[OrderManager] = None

        # Пул потоков для выполнения блокирующих операций
        # Используем ThreadPoolExecutor, так как MT5 API блокирующий
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        logger.debug("AsyncMt5Client инициализирован.")

    async def connect(self) -> bool:
        """
        Асинхронно инициализирует подключение к MT5.

        Returns:
            bool: True, если подключение успешно, иначе False.
        """
        logger.info("Асинхронная попытка подключения к MetaTrader 5...")

        def _sync_connect():
            # Инициализируем коннектор внутри рабочего потока
            self._connector = Mt5Connector(self.config)
            # Инициализируем зависимые компоненты
            self._data_fetcher = DataFetcher(
                self.config, self._connector, self._cache_manager, self._retry_manager
            )
            self._order_manager = OrderManager(
                self.config,
                self._connector,
                self._retry_manager,
                self._security_manager,
            )
            return self._connector.connect()

        try:
            # Выполняем синхронную инициализацию в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._executor, _sync_connect)
            if result:
                logger.info(
                    "Асинхронное подключение к MetaTrader 5 успешно установлено."
                )
            else:
                logger.error("Асинхронное подключение к MetaTrader 5 не удалось.")
            return result
        except Exception as e:
            logger.error(
                f"Ошибка при асинхронном подключении к MT5: {e}", exc_info=True
            )
            return False

    async def disconnect(self) -> None:
        """
        Асинхронно закрывает подключение к MT5.
        """
        logger.info("Асинхронное закрытие подключения к MetaTrader 5...")

        if self._connector:

            def _sync_disconnect():
                self._connector.disconnect()
                # Останавливаем пул потоков
                self._executor.shutdown(wait=True)
                logger.info("Пул потоков остановлен.")

            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self._executor, _sync_disconnect)
                logger.info("Асинхронное подключение к MetaTrader 5 закрыто.")
            except Exception as e:
                logger.error(
                    f"Ошибка при асинхронном отключении от MT5: {e}", exc_info=True
                )
        else:
            logger.debug(
                "Попытка закрыть неинициализированное асинхронное подключение."
            )

    async def is_connected(self) -> bool:
        """
        Асинхронно проверяет, активно ли подключение к MT5.

        Returns:
            bool: True, если подключение активно, иначе False.
        """
        if not self._connector:
            return False

        def _sync_is_connected():
            return self._connector.is_connected()

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, _sync_is_connected)
        except Exception as e:
            logger.error(
                f"Ошибка при асинхронной проверке соединения: {e}", exc_info=True
            )
            return False

    # --- Вспомогательный метод для выполнения синхронных функций асинхронно ---
    async def _run_in_executor(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет синхронную функцию в пуле потоков.

        Args:
            func (Callable): Синхронная функция для выполнения.
            *args: Позиционные аргументы для функции.
            **kwargs: Именованные аргументы для функции.

        Returns:
            Any: Результат выполнения функции.

        Raises:
            AsyncOperationError: Если произошла ошибка при выполнении.
        """
        if not self._connector or not self._connector.is_initialized:
            raise AsyncOperationError("Нет активного подключения к MT5.")

        try:
            # Оборачиваем функцию и аргументы, если есть kwargs
            if kwargs:
                wrapped_func = functools.partial(func, *args, **kwargs)
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(self._executor, wrapped_func)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(self._executor, func, *args)
        except Mt5TradingLibError:
            # Пробрасываем наши кастомные исключения как есть
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при асинхронном выполнении {func.__name__}: {e}", exc_info=True
            )
            raise AsyncOperationError(
                f"Ошибка при выполнении {func.__name__}: {e}"
            ) from e

    # --- Асинхронные методы для получения данных ---
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Асинхронно получает информацию о торговом счете.

        Returns:
            Optional[Dict[str, Any]]: Словарь с информацией о счете или None в случае ошибки.
        """
        if not self._data_fetcher:
            raise AsyncOperationError("DataFetcher не инициализирован.")

        return await self._run_in_executor(self._data_fetcher.get_account_info)

    async def get_historical_quotes(
        self, symbol: str, timeframe: int, start_pos: int = 0, count: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Асинхронно получает исторические котировки.

        Args:
            symbol (str): Название символа.
            timeframe (int): Таймфрейм.
            start_pos (int, optional): Начальная позиция. По умолчанию 0.
            count (int, optional): Количество баров. По умолчанию 1000.

        Returns:
            Optional[pd.DataFrame]: DataFrame с историческими данными или None.
        """
        if not self._data_fetcher:
            raise AsyncOperationError("DataFetcher не инициализирован.")

        return await self._run_in_executor(
            self._data_fetcher.get_historical_quotes,
            symbol,
            timeframe,
            start_pos,
            count,
        )

    async def get_real_time_quotes(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Асинхронно получает последние (реал-тайм) котировки.

        Args:
            symbol (str): Название символа.

        Returns:
            Optional[Dict[str, Any]]: Словарь с последними котировками или None.
        """
        if not self._data_fetcher:
            raise AsyncOperationError("DataFetcher не инициализирован.")

        return await self._run_in_executor(
            self._data_fetcher.get_real_time_quotes, symbol
        )

    # --- Асинхронные методы для управления ордерами ---
    async def send_market_order(
        self,
        symbol: str,
        volume: float,
        order_type: str,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: int = 20,
        comment: str = "",
    ) -> Optional[int]:
        """
        Асинхронно отправляет рыночный ордер.

        Args:
            symbol (str): Символ.
            volume (float): Объем.
            order_type (str): Тип ордера ("BUY" или "SELL").
            sl (float, optional): Stop Loss.
            tp (float, optional): Take Profit.
            deviation (int, optional): Максимальное отклонение цены. По умолчанию 20.
            comment (str, optional): Комментарий к ордеру. По умолчанию "".

        Returns:
            Optional[int]: Идентификатор ордера (ticket) или None в случае ошибки.
        """
        if not self._order_manager:
            raise AsyncOperationError("OrderManager не инициализирован.")

        return await self._run_in_executor(
            self._order_manager.send_market_order,
            symbol,
            volume,
            order_type,
            sl,
            tp,
            deviation,
            comment,
        )

    async def modify_order(
        self,
        order_ticket: int,
        new_price: Optional[float] = None,
        new_sl: Optional[float] = None,
        new_tp: Optional[float] = None,
    ) -> bool:
        """
        Асинхронно модифицирует существующий ордер.

        Args:
            order_ticket (int): Номер ордера (ticket).
            new_price (float, optional): Новая цена.
            new_sl (float, optional): Новый Stop Loss.
            new_tp (float, optional): Новый Take Profit.

        Returns:
            bool: True, если модификация успешна, иначе False.
        """
        if not self._order_manager:
            raise AsyncOperationError("OrderManager не инициализирован.")

        # _run_in_executor возвращает awaitable, результат функции
        return await self._run_in_executor(
            self._order_manager.modify_order, order_ticket, new_price, new_sl, new_tp
        )

    async def close_order(
        self, order_ticket: int, volume: Optional[float] = None
    ) -> bool:
        """
        Асинхронно закрывает позицию по ордеру.

        Args:
            order_ticket (int): Номер ордера (ticket) позиции.
            volume (float, optional): Объем для закрытия. Если None, закрывается вся позиция.

        Returns:
            bool: True, если закрытие успешно, иначе False.
        """
        if not self._order_manager:
            raise AsyncOperationError("OrderManager не инициализирован.")

        return await self._run_in_executor(
            self._order_manager.close_order, order_ticket, volume
        )

    # --- Асинхронные методы управления кэшем ---
    async def invalidate_account_info_cache(self) -> bool:
        """
        Асинхронно инвалидирует кэш информации о счете.

        Returns:
            bool: True, если кэш был успешно инвалидирован, иначе False.
        """
        if not self._data_fetcher:
            raise AsyncOperationError("DataFetcher не инициализирован.")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, self._data_fetcher.invalidate_account_info_cache
        )

    async def clear_all_data_cache(self) -> None:
        """
        Асинхронно очищает весь кэш данных.
        """
        if not self._data_fetcher:
            raise AsyncOperationError("DataFetcher не инициализирован.")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor, self._data_fetcher.clear_all_data_cache
        )


# --- Пример использования ---
# import asyncio
# from mt5_trading_lib.config import Config
# from mt5_trading_lib.logging_config import setup_logging
#
# async def main():
#     setup_logging()
#
#     config = Config.load_config()
#     async_client = AsyncMt5Client(config)
#
#     if await async_client.connect():
#         print("Асинхронное подключение установлено.")
#
#         # Получение информации о счете
#         account_info = await async_client.get_account_info()
#         if account_info:
#             print("Информация о счете (асинхронно):")
#             print(account_info)
#
#         # Получение исторических данных
#         import MetaTrader5 as mt5
#         symbol = "EURUSD"
#         hist_data = await async_client.get_historical_quotes(symbol, mt5.TIMEFRAME_M1, count=10)
#         if hist_data is not None:
#             print(f"\nИсторические данные для {symbol} (асинхронно):")
#             print(hist_data.head())
#
#         await async_client.disconnect()
#         print("Асинхронное подключение закрыто.")
#     else:
#         print("Не удалось установить асинхронное подключение.")
#
# if __name__ == "__main__":
#     asyncio.run(main())
