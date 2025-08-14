"""
Модуль для управления конфигурацией библиотеки mt5_trading_lib.
Использует pydantic для валидации и загрузки настроек из .env файла.
Поддерживает базовую валидацию и загрузку значений из переменных окружения.
Hot-reload в текущей реализации не реализован, но структура позволяет его добавить.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError, Mt5TradingLibError
from .logging_config import get_logger

# Получаем логгер для этого модуля
logger = get_logger(__name__)


class MT5Credentials(BaseModel):
    """
    Pydantic модель для учетных данных MetaTrader 5.
    """

    login: int = Field(..., description="Логин торгового счёта MT5")
    password: str = Field(..., description="Пароль торгового счёта MT5")
    server: str = Field(..., description="Сервер брокера для подключения")


class CacheSettings(BaseModel):
    """
    Pydantic модель для настроек кэширования.
    """

    ttl: int = Field(default=300, ge=0, description="Время жизни кэша в секундах")
    maxsize: int = Field(
        default=1000, ge=1, description="Максимальный размер локального кэша"
    )


class RetrySettings(BaseModel):
    """
    Pydantic модель для настроек повторных попыток.
    """

    attempts: int = Field(
        default=3, ge=1, description="Максимальное количество попыток"
    )
    base_delay: float = Field(
        default=1.0, gt=0, description="Базовая задержка между попытками (сек)"
    )


class SecuritySettings(BaseModel):
    """
    Pydantic модель для настроек безопасности.
    """

    # В текущей реализации ключ передается как base64 строка.
    # В будущем можно добавить загрузку из файла или другого источника.
    encryption_key_base64: Optional[str] = Field(
        default=None, description="Base64-закодированный 32-байтный ключ для шифрования"
    )


class LoggingSettings(BaseModel):
    """
    Pydantic модель для настроек логирования.
    """

    level: str = Field(default="INFO", description="Уровень логирования")


class AsyncSettings(BaseModel):
    """
    Pydantic модель для настроек асинхронных операций.
    """

    timeout: int = Field(
        default=30, ge=1, description="Таймаут для асинхронных операций (сек)"
    )


class Config(BaseSettings):
    """
    Основной класс конфигурации. Загружает настройки из .env файла и переменных окружения.
    Использует pydantic_settings для автоматической загрузки и валидации.
    """

    model_config = SettingsConfigDict(
        env_file=".env",  # Указывает файл .env для загрузки
        env_file_encoding="utf-8",  # Кодировка файла .env
        case_sensitive=False,  # Имена переменных нечувствительны к регистру
        env_nested_delimiter="__",  # Позволяет использовать вложенные модели (например, mt5__login)
        extra="ignore",  # Игнорировать неизвестные ключи из окружения/файла .env
    )

    # --- Основные настройки ---
    mt5: MT5Credentials
    cache: CacheSettings = CacheSettings()
    retry: RetrySettings = RetrySettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    async_: AsyncSettings = AsyncSettings()

    # --- Валидаторы ---
    @field_validator("mt5")
    @classmethod
    def validate_mt5_credentials(cls, v):
        """
        Валидатор для учетных данных MT5.
        Проверяет, что все обязательные поля заполнены.
        """
        if not v.login or not v.password or not v.server:
            raise ValueError(
                "MT5 credentials (login, password, server) must be provided."
            )
        return v

    @classmethod
    def load_config(cls, env_file: str = ".env") -> "Config":
        """
        Загружает и валидирует конфигурацию.

        Args:
            env_file (str, optional): Путь к файлу .env. По умолчанию ".env".

        Returns:
            Config: Экземпляр класса Config с загруженными настройками.

        Raises:
            ConfigurationError: Если конфигурация недействительна или файл .env не найден.
        """
        try:
            # 1) Загрузим переменные окружения из .env, если он есть.
            if os.path.exists(env_file):
                load_dotenv(env_file, override=False)
                logger.info(f"Загружены переменные окружения из {env_file}.")
            else:
                # Фоллбек: использовать env.example только если запрошен дефолтный .env
                # Это сохраняет ожидаемое поведение тестов, где передаётся кастомный путь.
                example_path = "env.example"
                if env_file in (None, ".env") and os.path.exists(example_path):
                    logger.warning(
                        f"Файл {env_file} не найден. Временный фоллбек: загружаю {example_path}. "
                        "Рекомендуется создать свой .env."
                    )
                    load_dotenv(example_path, override=False)
                else:
                    logger.warning(
                        f"Файл конфигурации {env_file} не найден. Используются только переменные окружения."
                    )

            # 2) Совместимость: поддержим старые имена переменных без вложенного синтаксиса
            fallback_map = {
                # MT5 creds
                "MT5_LOGIN": "MT5__LOGIN",
                "MT5_PASSWORD": "MT5__PASSWORD",
                "MT5_SERVER": "MT5__SERVER",
                # Cache settings
                "CACHE_TTL": "CACHE__TTL",
                "CACHE_MAXSIZE": "CACHE__MAXSIZE",
                # Retry settings
                "RETRY_ATTEMPTS": "RETRY__ATTEMPTS",
                "RETRY_BACKOFF_FACTOR": "RETRY__BASE_DELAY",
            }
            for legacy, nested in fallback_map.items():
                if legacy in os.environ and nested not in os.environ:
                    os.environ[nested] = os.environ[legacy]
                    logger.debug(
                        f"Установлен алиас переменной окружения: {legacy} -> {nested}"
                    )

            # 3) Загружаем и валидируем конфигурацию (pydantic_settings возьмёт из env)
            config = cls()
            logger.info("Конфигурация успешно загружена и провалидирована.")
            return config

        except ValidationError as ve:
            logger.error("Ошибка валидации конфигурации", errors=ve.errors())
            raise ConfigurationError(
                f"Ошибка валидации конфигурации: {ve}",
                error_code=getattr(
                    ve, "error_code", None
                ),  # Можно добавить кастомные коды
            ) from ve
        except Exception as e:
            logger.error("Неожиданная ошибка при загрузке конфигурации", exc_info=True)
            raise ConfigurationError(
                f"Неожиданная ошибка при загрузке конфигурации: {e}",
                error_code=getattr(e, "error_code", None),
            ) from e

    def reload_config(self, env_file: str = ".env"):
        """
        Перезагружает конфигурацию из файла .env.
        В текущей реализации pydantic_settings это не делает автоматически.
        Эта функция демонстрирует возможный подход, но требует пересоздания экземпляра Config.
        Для "настоящего" hot-reload потребуется более сложная логика (например, наблюдение за файлом).

        Args:
            env_file (str, optional): Путь к файлу .env. По умолчанию ".env".
        """
        logger.info(
            "Перезагрузка конфигурации (требует пересоздания экземпляра Config)."
        )
        # В pydantic v2 перезагрузка не так проста, как в v1.
        # Лучший способ - создать новый экземпляр Config.
        # Здесь мы просто логируем, что перезагрузка запрошена.
        # Реализация hot-reload требует дополнительной работы.


# --- Пример использования ---
# if __name__ == "__main__":
#     try:
#         config = Config.load_config()
#         print("MT5 Login:", config.mt5.login)
#         print("Cache TTL:", config.cache.ttl)
#         print("Retry Attempts:", config.retry.attempts)
#     except ConfigurationError as e:
#         print(f"Ошибка конфигурации: {e}")
