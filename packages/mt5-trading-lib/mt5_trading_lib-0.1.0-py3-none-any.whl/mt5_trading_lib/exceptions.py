"""
Модуль с кастомными исключениями для библиотеки mt5_trading_lib.
Определяет иерархию ошибок для более точной обработки различных ситуаций.
"""

# --- Базовые исключения ---


class Mt5TradingLibError(Exception):
    """
    Базовый класс для всех исключений, специфичных для библиотеки mt5_trading_lib.
    Это позволяет легко отлавливать ошибки, связанные именно с этой библиотекой.
    """

    def __init__(self, message: str, error_code: int = None):
        """
        Инициализирует исключение.

        Args:
            message (str): Сообщение об ошибке.
            error_code (int, optional): Код ошибки. Может использоваться для
                                      программной обработки.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        if self.error_code is not None:
            return f"[{self.error_code}] {self.message}"
        return self.message


# --- Исключения, связанные с конфигурацией ---


class ConfigurationError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с конфигурацией."""

    pass


# --- Исключения, связанные с подключением к MT5 ---


class ConnectionError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с подключением к терминалу MetaTrader 5."""

    pass


class InitializationError(ConnectionError):
    """Ошибка, возникающая при неудачной инициализации соединения с MT5."""

    pass


class HealthCheckError(ConnectionError):
    """Ошибка, возникающая при неудачной проверке состояния соединения с MT5."""

    pass


# --- Исключения, связанные с данными ---


class DataFetchError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с получением данных из MT5."""

    pass


class InvalidSymbolError(DataFetchError):
    """Ошибка, возникающая при попытке получить данные по несуществующему символу."""

    pass


class InvalidTimeFrameError(DataFetchError):
    """Ошибка, возникающая при попытке получить данные с недопустимым таймфреймом."""

    pass


# --- Исключения, связанные с торговыми операциями ---


class TradingOperationError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с выполнением торговых операций."""

    pass


class OrderSendError(TradingOperationError):
    """Ошибка, возникающая при отправке ордера."""

    pass


class OrderModifyError(TradingOperationError):
    """Ошибка, возникающая при модификации ордера."""

    pass


class OrderCloseError(TradingOperationError):
    """Ошибка, возникающая при закрытии ордера."""

    pass


class OrderValidationError(TradingOperationError):
    """Ошибка, возникающая при валидации параметров ордера."""

    pass


# --- Исключения, связанные с безопасностью ---


class SecurityError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с безопасностью (например, шифрование)."""

    pass


class CredentialEncryptionError(SecurityError):
    """Ошибка, возникающая при шифровании/дешифровании учетных данных."""

    pass


# --- Исключения, связанные с кэшированием ---


class CacheError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с кэшированием данных."""

    pass


# --- Исключения, связанные с повторными попытками (retry) ---


class RetryExhaustedError(Mt5TradingLibError):
    """Ошибка, возникающая когда все попытки повтора исчерпаны."""

    pass


# --- Асинхронные исключения ---


class AsyncOperationError(Mt5TradingLibError):
    """Ошибка, возникающая при проблемах с асинхронными операциями."""

    pass


# --- Примеры кодов ошибок ---
# Эти константы могут использоваться для программной обработки ошибок.
ERROR_CODE_CONFIG_INVALID = 1001
ERROR_CODE_MT5_INIT_FAILED = 2001
ERROR_CODE_MT5_HEALTH_CHECK_FAILED = 2002
ERROR_CODE_DATA_FETCH_FAILED = 3001
ERROR_CODE_INVALID_SYMBOL = 3002
ERROR_CODE_INVALID_TIMEFRAME = 3003
ERROR_CODE_ORDER_SEND_FAILED = 4001
ERROR_CODE_ORDER_MODIFY_FAILED = 4002
ERROR_CODE_ORDER_CLOSE_FAILED = 4003
ERROR_CODE_ORDER_VALIDATION_FAILED = 4004
ERROR_CODE_ENCRYPTION_FAILED = 5001
ERROR_CODE_CACHE_ERROR = 6001
ERROR_CODE_RETRY_EXHAUSTED = 7001
ERROR_CODE_ASYNC_ERROR = 8001
