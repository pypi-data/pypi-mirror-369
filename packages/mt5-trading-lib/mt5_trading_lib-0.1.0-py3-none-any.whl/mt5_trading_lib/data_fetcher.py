# mt5_trading_lib/data_fetcher.py
"""
Модуль для получения данных из терминала MetaTrader 5.
Предоставляет класс DataFetcher с методами для получения информации о счете,
исторических и реал-тайм котировок. Интегрируется с CacheManager для
умного кэширования и RetryManager для обработки ошибок.
"""

import time
from typing import Any, Dict, List, Optional, Union

import MetaTrader5 as mt5
import pandas as pd

from .cache_manager import CacheManager
from .config import Config
from .connector import Mt5Connector
from .exceptions import (
    DataFetchError,
    InvalidSymbolError,
    InvalidTimeFrameError,
    Mt5TradingLibError,
)
from .logging_config import get_logger
from .retry_manager import RetryManager

logger = get_logger(__name__)


class DataFetcher:
    """
    Класс для получения данных из MetaTrader5 с поддержкой кэширования и повторных попыток.
    """

    def __init__(
        self,
        config: Config,
        connector: Mt5Connector,
        cache_manager: CacheManager,
        retry_manager: RetryManager,
    ):
        """
        Инициализирует DataFetcher с необходимыми зависимостями.

        Args:
            config (Config): Экземпляр класса Config.
            connector (Mt5Connector): Экземпляр класса Mt5Connector для взаимодействия с MT5.
            cache_manager (CacheManager): Экземпляр класса CacheManager.
            retry_manager (RetryManager): Экземпляр класса RetryManager.
        """
        self.config = config
        self.connector = connector
        self.cache_manager = cache_manager
        self.retry_manager = retry_manager
        logger.debug("DataFetcher инициализирован.")

    # --- Вспомогательные методы ---

    def _validate_symbol(self, symbol: str) -> None:
        """
        Проверяет, существует ли символ в терминале MT5.

        Args:
            symbol (str): Название символа (например, "EURUSD").

        Raises:
            InvalidSymbolError: Если символ не найден.
        """
        # Этот метод может быть вынесен в отдельный utils модуль в будущем
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            last_error = mt5.last_error()
            error_msg = (
                f"Символ '{symbol}' не найден в терминале MT5. Ошибка: {last_error}"
            )
            logger.error(error_msg)
            raise InvalidSymbolError(error_msg)

    def _validate_timeframe(self, timeframe: int) -> None:
        """
        Проверяет, является ли таймфрейм допустимым значением MT5.

        Args:
            timeframe (int): Таймфрейм (например, mt5.TIMEFRAME_M1).

        Raises:
            InvalidTimeFrameError: Если таймфрейм недопустим.
        """
        # Список допустимых таймфреймов MT5 (основные)
        valid_timeframes = [
            mt5.TIMEFRAME_M1,
            mt5.TIMEFRAME_M2,
            mt5.TIMEFRAME_M3,
            mt5.TIMEFRAME_M4,
            mt5.TIMEFRAME_M5,
            mt5.TIMEFRAME_M6,
            mt5.TIMEFRAME_M10,
            mt5.TIMEFRAME_M12,
            mt5.TIMEFRAME_M15,
            mt5.TIMEFRAME_M20,
            mt5.TIMEFRAME_M30,
            mt5.TIMEFRAME_H1,
            mt5.TIMEFRAME_H2,
            mt5.TIMEFRAME_H3,
            mt5.TIMEFRAME_H4,
            mt5.TIMEFRAME_H6,
            mt5.TIMEFRAME_H8,
            mt5.TIMEFRAME_H12,
            mt5.TIMEFRAME_D1,
            mt5.TIMEFRAME_W1,
            mt5.TIMEFRAME_MN1,
        ]
        if timeframe not in valid_timeframes:
            error_msg = f"Недопустимый таймфрейм: {timeframe}."
            logger.error(error_msg)
            raise InvalidTimeFrameError(error_msg)

    # --- Методы получения данных ---

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о торговом счете с кэшированием.

        Returns:
            Optional[Dict[str, Any]]: Словарь с информацией о счете или None в случае ошибки.
        """
        cache_key = "account_info"
        logger.debug("Запрос информации о счете...")

        # Проверяем кэш
        cached_info = self.cache_manager.get(cache_key)
        if cached_info is not None:
            logger.debug("Информация о счете получена из кэша.")
            return cached_info

        def _fetch_account_info():
            if not self.connector.is_connected():
                raise DataFetchError(
                    "Нет подключения к MT5 для получения информации о счете."
                )

            account_info = mt5.account_info()
            if account_info is None:
                last_error = mt5.last_error()
                raise DataFetchError(
                    f"Не удалось получить информацию о счете. Ошибка: {last_error}"
                )

            # Преобразуем_namedtuple в словарь для сериализации и кэширования
            return account_info._asdict()

        try:
            # Выполняем с retry и circuit breaker
            account_data = self.retry_manager.execute_with_retry_and_circuit_breaker(
                _fetch_account_info
            )

            # Сохраняем в кэш
            self.cache_manager.set(cache_key, account_data)
            logger.info("Информация о счете успешно получена и закэширована.")
            return account_data

        except Mt5TradingLibError:
            logger.error("Ошибка при получении информации о счете.", exc_info=True)
            return None  # Возвращаем None вместо проброса исключения, чтобы не ломать вызывающий код
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при получении информации о счете: {e}",
                exc_info=True,
            )
            return None

    def get_historical_quotes(
        self, symbol: str, timeframe: int, start_pos: int = 0, count: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Получает исторические котировки для символа с кэшированием.

        Args:
            symbol (str): Название символа (например, "EURUSD").
            timeframe (int): Таймфрейм (например, mt5.TIMEFRAME_M1).
            start_pos (int, optional): Начальная позиция (0 - текущий бар). По умолчанию 0.
            count (int, optional): Количество баров для получения. По умолчанию 1000.

        Returns:
            Optional[pd.DataFrame]: DataFrame с историческими данными или None в случае ошибки.
        """
        # Валидация входных данных
        self._validate_symbol(symbol)
        self._validate_timeframe(timeframe)

        # Создаем уникальный ключ для кэша
        cache_key = ("historical_quotes", symbol, timeframe, start_pos, count)
        logger.debug(f"Запрос исторических данных для {symbol}...")

        # Проверяем кэш
        cached_data = self.cache_manager.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Исторические данные для {symbol} получены из кэша.")
            # Кэш хранит DataFrame в виде словарника, преобразуем обратно
            return pd.DataFrame(cached_data)

        def _fetch_historical_data():
            if not self.connector.is_connected():
                raise DataFetchError(
                    f"Нет подключения к MT5 для получения исторических данных {symbol}."
                )

            # Получаем данные
            rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
            if rates is None or len(rates) == 0:
                last_error = mt5.last_error()
                raise DataFetchError(
                    f"Не удалось получить исторические данные для {symbol}. "
                    f"Timeframe: {timeframe}, Start: {start_pos}, Count: {count}. "
                    f"Ошибка: {last_error}"
                )

            # Преобразуем в DataFrame
            df = pd.DataFrame(rates)
            # Преобразуем время из timestamp в datetime
            df["time"] = pd.to_datetime(df["time"], unit="s")
            return df

        try:
            # Выполняем с retry и circuit breaker
            df_data = self.retry_manager.execute_with_retry_and_circuit_breaker(
                _fetch_historical_data
            )

            # Сохраняем в кэш (DataFrame нужно сериализовать)
            self.cache_manager.set(cache_key, df_data.to_dict("records"))
            logger.info(
                f"Исторические данные для {symbol} успешно получены и закэшированы."
            )
            return df_data

        except (InvalidSymbolError, InvalidTimeFrameError):
            # Эти ошибки не retry'им, сразу пробрасываем
            logger.error(f"Ошибка валидации для {symbol}.", exc_info=True)
            raise
        except Mt5TradingLibError:
            logger.error(
                f"Ошибка при получении исторических данных для {symbol}.", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при получении исторических данных для {symbol}: {e}",
                exc_info=True,
            )
            return None

    def get_real_time_quotes(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Получает последние (реал-тайм) котировки для символа без кэширования
        (так как данные постоянно меняются).

        Args:
            symbol (str): Название символа (например, "EURUSD").

        Returns:
            Optional[Dict[str, Any]]: Словарь с последними котировками или None в случае ошибки.
        """
        # Валидация входных данных
        self._validate_symbol(symbol)

        logger.debug(f"Запрос реал-тайм котировок для {symbol}...")

        def _fetch_real_time_data():
            if not self.connector.is_connected():
                raise DataFetchError(
                    f"Нет подключения к MT5 для получения реал-тайм данных {symbol}."
                )

            # Получаем тиковые данные
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                last_error = mt5.last_error()
                raise DataFetchError(
                    f"Не удалось получить реал-тайм данные для {symbol}. Ошибка: {last_error}"
                )

            # Преобразуем_namedtuple в словарь
            return tick._asdict()

        try:
            # Выполняем с retry и circuit breaker
            tick_data = self.retry_manager.execute_with_retry_and_circuit_breaker(
                _fetch_real_time_data
            )
            logger.info(f"Реал-тайм котировки для {symbol} успешно получены.")
            return tick_data

        except InvalidSymbolError:
            # Эта ошибка не retry'им
            logger.error(f"Ошибка валидации для {symbol}.", exc_info=True)
            raise
        except Mt5TradingLibError:
            logger.error(
                f"Ошибка при получении реал-тайм данных для {symbol}.", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при получении реал-тайм данных для {symbol}: {e}",
                exc_info=True,
            )
            return None

    # --- Методы управления кэшем для данных ---

    def invalidate_account_info_cache(self) -> bool:
        """
        Инвалидирует кэш информации о счете.

        Returns:
            bool: True, если кэш был успешно инвалидирован, иначе False.
        """
        cache_key = "account_info"
        return self.cache_manager.invalidate(cache_key)

    def invalidate_historical_quotes_cache(
        self, symbol: str, timeframe: int, start_pos: int = 0, count: int = 1000
    ) -> bool:
        """
        Инвалидирует кэш исторических котировок для конкретного запроса.

        Args:
            symbol (str): Название символа.
            timeframe (int): Таймфрейм.
            start_pos (int, optional): Начальная позиция. По умолчанию 0.
            count (int, optional): Количество баров. По умолчанию 1000.

        Returns:
            bool: True, если кэш был успешно инвалидирован, иначе False.
        """
        cache_key = ("historical_quotes", symbol, timeframe, start_pos, count)
        return self.cache_manager.invalidate(cache_key)

    def clear_all_data_cache(self) -> None:
        """
        Очищает весь кэш, связанный с данными (локальный кэш DataFetcher).
        """
        # В простом случае очищаем весь кэш менеджера.
        # В более сложном можно реализовать тэггирование кэша.
        self.cache_manager.clear()
        logger.info("Весь кэш данных очищен.")


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.connector import Mt5Connector
#     from mt5_trading_lib.cache_manager import CacheManager
#     from mt5_trading_lib.retry_manager import RetryManager
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     try:
#         config = Config.load_config()
#         connector = Mt5Connector(config)
#         cache_manager = CacheManager(config)
#         retry_manager = RetryManager(config)
#
#         if connector.connect():
#             data_fetcher = DataFetcher(config, connector, cache_manager, retry_manager)
#
#             # Получение информации о счете
#             account_info = data_fetcher.get_account_info()
#             if account_info:
#                 print("Информация о счете:")
#                 print(account_info)
#
#             # Получение исторических данных
#             symbol = "EURUSD"
#             hist_data = data_fetcher.get_historical_quotes(symbol, mt5.TIMEFRAME_M1, count=10)
#             if hist_data is not None:
#                 print(f"\nИсторические данные для {symbol}:")
#                 print(hist_data.head())
#
#             # Получение реал-тайм данных
#             real_time_data = data_fetcher.get_real_time_quotes(symbol)
#             if real_time_data:
#                 print(f"\nРеал-тайм данные для {symbol}:")
#                 print(real_time_data)
#
#             connector.disconnect()
#         else:
#             print("Не удалось подключиться к MT5.")
#
#     except Exception as e:
#         logger.error(f"Критическая ошибка в примере: {e}", exc_info=True)
