"""
Модуль для управления подключением к терминалу MetaTrader 5.
Содержит класс Mt5Connector, который инкапсулирует логику подключения,
проверки состояния и отключения от MT5.
"""

import time
from typing import Any, Dict, Optional

import MetaTrader5 as mt5
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import Config
from .exceptions import (
    ConnectionError,
    HealthCheckError,
    InitializationError,
    Mt5TradingLibError,
)
from .logging_config import get_logger

# Получаем логгер для этого модуля
logger = get_logger(__name__)


class Mt5Connector:
    """
    Класс для управления подключением к терминалу MetaTrader 5.
    Обеспечивает инициализацию, проверку состояния и закрытие соединения.
    Использует tenacity для повторных попыток при ошибках подключения.
    """

    def __init__(self, config: Config):
        """
        Инициализирует коннектор с заданной конфигурацией.

        Args:
            config (Config): Экземпляр класса Config с настройками подключения.
        """
        self.config = config
        self.is_initialized = False
        logger.debug("Экземпляр Mt5Connector создан.")

    def _get_mt5_version(self) -> Optional[str]:
        """
        Получает версию установленного пакета MetaTrader5.

        Returns:
            Optional[str]: Версия пакета или None, если не удалось получить.
        """
        try:
            # MetaTrader5 не предоставляет прямого способа получить версию пакета.
            # Можно попробовать через mt5.__version__ если доступно, или через pip show.
            # Для простоты, просто проверим, что модуль импортирован.
            # В реальном приложении можно использовать subprocess для `pip show MetaTrader5`
            return getattr(mt5, "__version__", "Неизвестна")
        except Exception as e:
            logger.warning(
                "Не удалось определить версию MetaTrader5 пакета.", exc_info=True
            )
            return None

    def connect(self) -> bool:
        """
        Инициализирует подключение к терминалу MetaTrader 5 с повторными попытками.

        Returns:
            bool: True, если подключение успешно, иначе False.

        Raises:
            InitializationError: Если инициализация не удалась после всех попыток.
        """
        logger.info("Попытка подключения к MetaTrader 5...")
        mt5_version = self._get_mt5_version()
        logger.info(f"Используется версия MetaTrader5 пакета: {mt5_version}")

        try:
            # Попытка инициализации соединения с MT5
            if not mt5.initialize(
                login=self.config.mt5.login,
                password=self.config.mt5.password,
                server=self.config.mt5.server,
                timeout=10000,  # Таймаут в миллисекундах
            ):
                # Если инициализация вернула False, получаем информацию об ошибке
                last_error = mt5.last_error()
                error_msg = f"Не удалось инициализировать подключение к MT5. Ошибка: {last_error}"
                logger.error(error_msg)
                raise InitializationError(error_msg)

            self.is_initialized = True
            logger.info("Подключение к MetaTrader 5 успешно установлено.")
            return True

        except InitializationError:
            # Передаем исключение дальше для повтора
            raise
        except Exception as e:
            error_msg = f"Неожиданная ошибка при подключении к MT5: {e}"
            logger.error(error_msg, exc_info=True)
            raise ConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """
        Закрывает подключение к терминалу MetaTrader 5.
        """
        if self.is_initialized:
            try:
                mt5.shutdown()
                self.is_initialized = False
                logger.info("Подключение к MetaTrader 5 закрыто.")
            except Exception as e:
                logger.error(
                    f"Ошибка при закрытии подключения к MT5: {e}", exc_info=True
                )
        else:
            logger.debug("Попытка закрыть неинициализированное подключение.")

    def is_connected(self) -> bool:
        """
        Проверяет, активно ли подключение к MT5.

        Returns:
            bool: True, если подключение активно, иначе False.
        """
        return self.is_initialized and mt5.terminal_info() is not None

    # --- Контекстный менеджер ---
    def __enter__(self):
        """
        Поддержка использования через контекстный менеджер:
        with Mt5Connector(config) as conn: ...
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()
        # Не подавляем исключения
        return False

    def health_check(self) -> bool:
        """
        Выполняет проверку состояния подключения к MT5 с повторными попытками.

        Returns:
            bool: True, если проверка пройдена, иначе False.

        Raises:
            HealthCheckError: Если проверка не удалась после всех попыток.
        """
        logger.debug("Выполнение проверки состояния подключения к MT5...")
        if not self.is_initialized:
            error_msg = (
                "Попытка выполнить health check для неинициализированного подключения."
            )
            logger.warning(error_msg)
            raise HealthCheckError(error_msg)

        try:
            # Получаем информацию о терминале
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                last_error = mt5.last_error()
                error_msg = f"Health check не пройден: terminal_info() вернул None. Ошибка: {last_error}"
                logger.error(error_msg)
                raise HealthCheckError(error_msg)

            # Дополнительная проверка: можно запросить информацию о счете
            account_info = mt5.account_info()
            if account_info is None:
                last_error = mt5.last_error()
                error_msg = f"Health check не пройден: account_info() вернул None. Ошибка: {last_error}"
                logger.error(error_msg)
                raise HealthCheckError(error_msg)

            logger.debug("Health check успешно пройден.")
            return True

        except HealthCheckError:
            # Передаем исключение дальше для повтора
            raise
        except Exception as e:
            error_msg = f"Неожиданная ошибка при выполнении health check: {e}"
            logger.error(error_msg, exc_info=True)
            raise HealthCheckError(error_msg) from e

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущем подключении.

        Returns:
            Dict[str, Any]: Словарь с информацией о подключении.
        """
        info = {
            "is_initialized": self.is_initialized,
            "is_connected": self.is_connected(),
            "mt5_version": self._get_mt5_version(),
            "config": {
                "login": self.config.mt5.login,
                "server": self.config.mt5.server,
                # Никогда не логгируем пароль!
            },
        }
        return info


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging() # Настройка логирования
#
#     try:
#         config = Config.load_config()
#         connector = Mt5Connector(config)
#
#         if connector.connect():
#             print("Подключение установлено.")
#             print(connector.get_connection_info())
#             if connector.health_check():
#                 print("Health check пройден.")
#             else:
#                 print("Health check не пройден.")
#         else:
#             print("Не удалось установить подключение.")
#
#         connector.disconnect()
#         print("Подключение закрыто.")
#
#     except Exception as e:
#         logger.error(f"Критическая ошибка: {e}", exc_info=True)
