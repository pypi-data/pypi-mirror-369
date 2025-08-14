# mt5_trading_lib/cache_manager.py
"""
Модуль для управления кэшированием данных.
Предоставляет класс CacheManager для локального кэширования с TTL
и потенциальной поддержкой внешнего кэша (например, Redis).
Использует библиотеку cachetools для локального кэша.
"""

import hashlib
import json
import threading
from typing import Any, Callable, Optional, Union

from cachetools import TTLCache

from .config import Config
from .exceptions import CacheError
from .logging_config import get_logger

# В будущем можно добавить поддержку Redis
# try:
#     import redis
#     REDIS_AVAILABLE = True
# except ImportError:
#     REDIS_AVAILABLE = False
#     redis = None


logger = get_logger(__name__)


class CacheManager:
    """
    Класс для управления кэшированием данных.
    Поддерживает локальный кэш с TTL. Архитектура позволяет добавить
    поддержку внешнего кэша (например, Redis) в будущем.
    """

    def __init__(self, config: Config):
        """
        Инициализирует менеджер кэша с конфигурацией.

        Args:
            config (Config): Экземпляр класса Config с настройками кэша.
        """
        self.config = config
        self.local_cache: TTLCache = TTLCache(
            maxsize=getattr(config.cache, "maxsize", 1000),
            ttl=config.cache.ttl,
        )
        # Для потокобезопасности при работе с локальным кэшем
        self._lock = threading.RLock()

        # В будущем можно инициализировать подключение к Redis
        # self.redis_client: Optional[redis.Redis] = None
        # if REDIS_AVAILABLE and self.config.cache.redis_url:
        #     try:
        #         self.redis_client = redis.Redis.from_url(self.config.cache.redis_url)
        #         # Пингуем, чтобы проверить соединение
        #         self.redis_client.ping()
        #         logger.info("Подключение к Redis установлено.")
        #     except Exception as e:
        #         logger.error(f"Не удалось подключиться к Redis: {e}")
        #         self.redis_client = None

        logger.debug(
            f"CacheManager инициализирован. Локальный TTL: {config.cache.ttl} секунд."
        )

    def _make_key(self, key: Union[str, Callable, tuple, dict]) -> str:
        """
        Создает строковый ключ для кэширования из различных типов входных данных.
        Это позволяет использовать сложные структуры (например, кортежи аргументов)
        в качестве ключей.

        Args:
            key (Union[str, Callable, tuple, dict]): Исходный ключ.

        Returns:
            str: Хешированный строковый ключ.
        """
        if isinstance(key, str):
            return key
        # Для функций используем их имя
        if callable(key):
            return key.__name__

        # Для сложных ключей (кортежи, словари) создаем хеш
        try:
            # Сортируем словари для консистентности хеша
            if isinstance(key, dict):
                key = json.dumps(key, sort_keys=True, default=str)
            elif isinstance(key, (list, tuple)):
                # Преобразуем в строку, рекурсивно обрабатывая элементы
                key = str(
                    tuple(sorted(key) if all(isinstance(i, dict) for i in key) else key)
                )
            else:
                key = str(key)

            # Создаем SHA256 хеш
            return hashlib.sha256(key.encode("utf-8")).hexdigest()
        except Exception as e:
            logger.error(f"Ошибка при создании ключа кэша: {e}")
            # В случае ошибки используем строковое представление
            return str(key)

    def get(self, key: Union[str, tuple, dict], default=None) -> Any:
        """
        Получает значение из кэша по ключу.

        Args:
            key (Union[str, tuple, dict]): Ключ для поиска в кэше.
            default (Any, optional): Значение по умолчанию, если ключ не найден.

        Returns:
            Any: Значение из кэша или значение по умолчанию.
        """
        cache_key = self._make_key(key)

        # Проверяем локальный кэш
        with self._lock:
            value = self.local_cache.get(cache_key, default)

        if value is not default:
            logger.debug(f"Кэш HIT для ключа: {cache_key[:10]}...")
        else:
            logger.debug(f"Кэш MISS для ключа: {cache_key[:10]}...")

        # В будущем можно проверить Redis, если значение не найдено локально
        # if value is default and self.redis_client:
        #     try:
        #         redis_value = self.redis_client.get(cache_key)
        #         if redis_value:
        #             value = json.loads(redis_value)
        #             # Также помещаем в локальный кэш для ускорения следующих запросов
        #             with self._lock:
        #                 self.local_cache[cache_key] = value
        #     except Exception as e:
        #         logger.error(f"Ошибка при получении значения из Redis: {e}")

        return value

    def set(self, key: Union[str, tuple, dict], value: Any) -> None:
        """
        Сохраняет значение в кэш по ключу.

        Args:
            key (Union[str, tuple, dict]): Ключ для сохранения значения.
            value (Any): Значение для кэширования.
        """
        cache_key = self._make_key(key)

        # Сохраняем в локальный кэш
        with self._lock:
            self.local_cache[cache_key] = value

        logger.debug(f"Значение сохранено в кэш по ключу: {cache_key[:10]}...")

        # В будущем можно сохранить в Redis
        # if self.redis_client:
        #     try:
        #         # Сериализуем значение в JSON
        #         serialized_value = json.dumps(value, default=str)
        #         self.redis_client.setex(
        #             name=cache_key,
        #             time=int(self.config.cache.ttl), # Используем TTL из конфига
        #             value=serialized_value
        #         )
        #     except Exception as e:
        #         logger.error(f"Ошибка при сохранении значения в Redis: {e}")

    def invalidate(self, key: Union[str, tuple, dict]) -> bool:
        """
        Удаляет значение из кэша по ключу.

        Args:
            key (Union[str, tuple, dict]): Ключ для удаления.

        Returns:
            bool: True, если ключ был найден и удален, иначе False.
        """
        cache_key = self._make_key(key)
        was_deleted = False

        # Удаляем из локального кэша
        with self._lock:
            if cache_key in self.local_cache:
                del self.local_cache[cache_key]
                was_deleted = True

        if was_deleted:
            logger.debug(f"Значение удалено из кэша по ключу: {cache_key[:10]}...")
        else:
            logger.debug(f"Ключ для удаления не найден в кэше: {cache_key[:10]}...")

        # В будущем можно удалить из Redis
        # if self.redis_client:
        #     try:
        #         result = self.redis_client.delete(cache_key)
        #         if result:
        #             logger.debug(f"Значение удалено из Redis по ключу: {cache_key[:10]}...")
        #             was_deleted = True # Обновляем статус, если удалили из Redis
        #     except Exception as e:
        #         logger.error(f"Ошибка при удалении значения из Redis: {e}")

        return was_deleted

    def clear(self) -> None:
        """
        Очищает весь локальный кэш.
        """
        with self._lock:
            self.local_cache.clear()
        logger.info("Локальный кэш очищен.")

        # В будущем можно очистить Redis
        # if self.redis_client:
        #     try:
        #         self.redis_client.flushdb() # Очищает текущую БД
        #         logger.info("Кэш Redis очищен.")
        #     except Exception as e:
        #         logger.error(f"Ошибка при очистке кэша Redis: {e}")

    def get_stats(self) -> dict:
        """
        Возвращает статистику использования кэша.

        Returns:
            dict: Словарь со статистикой.
        """
        with self._lock:
            stats = {
                "local_cache_hits": getattr(self.local_cache, "hits", "N/A"),
                "local_cache_misses": getattr(self.local_cache, "misses", "N/A"),
                "local_cache_currsize": len(self.local_cache),
                "local_cache_maxsize": self.local_cache.maxsize,
                "local_cache_ttl": self.local_cache.ttl,
                # "redis_available": REDIS_AVAILABLE,
                # "redis_connected": self.redis_client is not None
            }
        return stats


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     config = Config.load_config()
#     cache_manager = CacheManager(config)
#
#     # Простой ключ
#     cache_manager.set("test_key", "test_value")
#     print(cache_manager.get("test_key")) # test_value
#
#     # Сложный ключ
#     complex_key = ("get_data", "EURUSD", "M1", 100)
#     cache_manager.set(complex_key, {"data": [1, 2,3]})
# print(cache_manager.get(complex_key)) # {'data': [1, 2, 3]}
#
# # Инвалидация
# cache_manager.invalidate("test_key")
# print(cache_manager.get("test_key", "default")) # default
#
# # Статистика
# print(cache_manager.get_stats())
