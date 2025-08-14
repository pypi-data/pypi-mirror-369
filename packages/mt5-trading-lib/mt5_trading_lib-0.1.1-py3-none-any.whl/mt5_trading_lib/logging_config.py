"""
Модуль для настройки структурированного логирования с использованием structlog.
Этот модуль предоставляет функцию `get_logger`, которая возвращает настроенный
экземпляр логгера.
"""

import logging
import os

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.stdlib import LoggerFactory

# Получаем уровень логирования из переменных окружения или используем INFO по умолчанию
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
# Проверяем, нужно ли использовать JSON формат (например, для продакшена)
USE_JSON_LOGGING = os.getenv("USE_JSON_LOGGING", "false").lower() == "true"


def setup_logging():
    """
    Настраивает глобальное логирование для всего приложения.
    Должна быть вызвана один раз при запуске приложения.
    """
    # Определяем уровень логирования
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    # Настраиваем стандартную библиотеку logging
    logging.basicConfig(
        level=level,
        format="%(message)s",  # structlog будет обрабатывать форматирование
        handlers=[logging.StreamHandler()],  # Выводим в консоль
    )

    # Настраиваем процессоры structlog
    processors = [
        structlog.stdlib.add_logger_name,  # Добавляет имя логгера
        structlog.stdlib.add_log_level,  # Добавляет уровень лога
        structlog.stdlib.PositionalArgumentsFormatter(),  # Форматирует позиционные аргументы
        TimeStamper(fmt="iso"),  # Добавляет временную метку в формате ISO
        structlog.processors.StackInfoRenderer(),  # Добавляет информацию о стеке при наличии
        format_exc_info,  # Форматирует информацию об исключениях
    ]

    # Выбираем рендерер в зависимости от настроек
    if USE_JSON_LOGGING:
        processors.append(JSONRenderer())  # JSON формат для машинной обработки
    else:
        processors.append(
            ConsoleRenderer(colors=True)
        )  # Человекочитаемый формат с цветами

    # Конфигурируем structlog
    structlog.configure(
        processors=processors,
        context_class=dict,  # Используем стандартный словарь для контекста
        logger_factory=LoggerFactory(),  # Используем фабрику логгеров из stdlib
        wrapper_class=structlog.stdlib.BoundLogger,  # Обёртка для логгера
        cache_logger_on_first_use=True,  # Кэшируем логгер для повышения производительности
    )


def get_logger(name: str = None):
    """
    Возвращает настроенный экземпляр structlog.BoundLogger.

    Args:
        name (str, optional): Имя логгера. Если не указано, будет использовано имя модуля,
                              из которого вызвана функция.

    Returns:
        structlog.BoundLogger: Настроенный логгер.
    """
    if name is None:
        # Получаем имя вызывающего модуля
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals["__name__"]
    return structlog.get_logger(name)


# Пример использования (обычно вызывается при старте приложения)
# setup_logging()
# logger = get_logger(__name__)
# logger.info("Логирование настроено", extra_field="some_value")
