# mt5_trading_lib/event_bus.py
"""
Модуль для реализации шины событий (Event Bus).
Предоставляет класс EventBus для публикации и подписки на события
внутри библиотеки, обеспечивая loose coupling между компонентами.
"""

import asyncio
import logging
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Set

from .logging_config import get_logger

logger = get_logger(__name__)


class EventBus:
    """
    Централизованная шина событий для обмена сообщениями между компонентами.
    Поддерживает синхронные и асинхронные обработчики событий.
    Использует weakref для хранения подписчиков, чтобы избежать утечек памяти.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Реализует Singleton паттерн для EventBus.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventBus, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Инициализирует EventBus. Выполняется только один раз благодаря Singleton.
        """
        if self._initialized:
            return

        # Словарь для хранения подписчиков: {event_name: set of weak references to handlers}
        self._subscribers: Dict[str, Set[weakref.ref]] = {}
        # Блокировка для потокобезопасной работы со словарем подписчиков
        self._subscribers_lock = threading.RLock()

        # Пул потоков для выполнения синхронных обработчиков
        self._executor = ThreadPoolExecutor(max_workers=4)

        # Для асинхронных обработчиков
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None

        self._initialized = True
        logger.debug("EventBus инициализирован.")

    def set_async_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Устанавливает event loop для асинхронных обработчиков.
        Должен быть вызван в основном асинхронном потоке приложения.

        Args:
            loop (asyncio.AbstractEventLoop): Event loop.
        """
        self._async_loop = loop
        logger.debug("Event loop для EventBus установлен.")

    # --- Методы управления подпиской ---
    def subscribe(self, event_name: str, handler: Callable[[str, Any], None]) -> None:
        """
        Подписывается на событие.

        Args:
            event_name (str): Название события.
            handler (Callable[[str, Any], None]): Функция-обработчик.
                                                Принимает (event_name, event_data).
        """
        with self._subscribers_lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = set()

            # Используем weakref, чтобы не мешать сборщику мусора удалять обработчики
            # weakref.ref(handler) может не сработать для bound methods, поэтому оборачиваем
            try:
                handler_ref = weakref.ref(handler, self._cleanup_handler_ref)
                self._subscribers[event_name].add(handler_ref)
                logger.debug(f"Подписчик добавлен на событие '{event_name}'.")
            except TypeError:
                # Если объект не поддерживает weakref, сохраняем напрямую (менее безопасно)
                # Это может привести к утечке памяти, если обработчик не отписывается
                logger.warning(
                    f"Обработчик для события '{event_name}' не поддерживает weakref. "
                    f"Это может привести к утечке памяти. Рекомендуется использовать функции или bound methods от живых объектов."
                )
                # Для простоты в этом примере пропустим такой случай
                # В production коде можно реализовать более сложную логику
                pass

    def _cleanup_handler_ref(self, handler_ref: weakref.ref) -> None:
        """Callback для очистки сломавшихся weakref."""
        with self._subscribers_lock:
            # Нужно найти и удалить handler_ref из всех множеств
            for event_name, handlers_set in self._subscribers.items():
                if handler_ref in handlers_set:
                    handlers_set.discard(handler_ref)
                    logger.debug(
                        f"Удален сломавшийся weakref для события '{event_name}'."
                    )

    def unsubscribe(self, event_name: str, handler: Callable[[str, Any], None]) -> bool:
        """
        Отписывается от события.

        Args:
            event_name (str): Название события.
            handler (Callable[[str, Any], None]): Функция-обработчик.

        Returns:
            bool: True, если отписка прошла успешно, иначе False.
        """
        with self._subscribers_lock:
            if event_name in self._subscribers:
                # Нам нужно найти weakref, ссылающийся на handler
                for handler_ref in list(self._subscribers[event_name]):
                    handler_obj = handler_ref()  # Получаем реальный объект
                    if handler_obj is handler:
                        self._subscribers[event_name].discard(handler_ref)
                        logger.debug(f"Подписчик удален от события '{event_name}'.")
                        return True
        logger.debug(f"Подписчик для отписки от события '{event_name}' не найден.")
        return False

    # --- Методы публикации событий ---
    def publish(self, event_name: str, event_data: Any = None) -> None:
        """
        Публикует событие синхронно. Все синхронные обработчики выполняются
        в пуле потоков. Асинхронные обработчики выполняются в заданном event loop.

        Args:
            event_name (str): Название события.
            event_data (Any, optional): Данные события. По умолчанию None.
        """
        logger.debug(f"Публикация события '{event_name}'.")

        handlers_to_call_sync = []
        handlers_to_call_async = []

        with self._subscribers_lock:
            if event_name in self._subscribers:
                for handler_ref in list(self._subscribers[event_name]):
                    handler = handler_ref()  # Получаем реальный объект обработчика
                    if handler is not None:
                        import inspect

                        # Проверяем, является ли обработчик асинхронной функцией
                        if inspect.iscoroutinefunction(handler):
                            handlers_to_call_async.append(handler)
                        else:
                            handlers_to_call_sync.append(handler)
                    else:
                        # weakref стал None, удаляем его
                        self._subscribers[event_name].discard(handler_ref)

        # Выполняем синхронные обработчики в пуле потоков
        for handler in handlers_to_call_sync:
            try:
                # Используем submit для неблокирующего выполнения
                future = self._executor.submit(handler, event_name, event_data)
                # Можно добавить future.add_done_callback для обработки исключений
                # future.add_done_callback(self._handle_future_exception)
            except Exception as e:
                logger.error(
                    f"Ошибка при постановке синхронного обработчика в очередь для события '{event_name}': {e}",
                    exc_info=True,
                )

        # Выполняем асинхронные обработчики
        if handlers_to_call_async:
            if self._async_loop is None:
                logger.warning(
                    f"Найдены асинхронные обработчики для события '{event_name}', "
                    f"но event loop не установлен. Они не будут выполнены. "
                    f"Вызовите set_async_loop()."
                )
            else:
                for handler in handlers_to_call_async:
                    try:
                        # Планируем выполнение корутины в указанном loop
                        asyncio.run_coroutine_threadsafe(
                            handler(event_name, event_data), self._async_loop
                        )
                    except Exception as e:
                        logger.error(
                            f"Ошибка при планировании асинхронного обработчика для события '{event_name}': {e}",
                            exc_info=True,
                        )

    # def _handle_future_exception(self, future):
    #     """Обработчик исключений из futures пула потоков."""
    #     try:
    #         future.result() # Получаем результат или вызываем исключение
    #     except Exception as e:
    #         logger.error(f"Ошибка в синхронном обработчике события: {e}", exc_info=True)

    def publish_async(self, event_name: str, event_data: Any = None) -> asyncio.Future:
        """
        Асинхронно публикует событие. Возвращает Future, который завершится,
        когда все синхронные обработчики будут отправлены в пул и все асинхронные
        обработчики будут запланированы.

        Args:
            event_name (str): Название события.
            event_data (Any, optional): Данные события. По умолчанию None.

        Returns:
            asyncio.Future: Future, представляющий завершение публикации.
        """
        loop = asyncio.get_event_loop()
        # Оборачиваем синхронный publish в coroutine
        return loop.run_in_executor(None, self.publish, event_name, event_data)

    # --- Методы для удобства ---
    def get_subscribers_count(self, event_name: str) -> int:
        """
        Возвращает количество подписчиков на конкретное событие.

        Args:
            event_name (str): Название события.

        Returns:
            int: Количество подписчиков.
        """
        with self._subscribers_lock:
            return len(self._subscribers.get(event_name, set()))

    def shutdown(self) -> None:
        """
        Корректно завершает работу EventBus, останавливая пул потоков.
        """
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Пул потоков EventBus остановлен.")
        logger.info("EventBus выключен.")


# --- Примеры обработчиков событий ---
def sync_event_handler(event_name: str, data: Any) -> None:
    """Пример синхронного обработчика."""
    logger.info(f"[Синхронный обработчик] Событие: {event_name}, Данные: {data}")


async def async_event_handler(event_name: str, data: Any) -> None:
    """Пример асинхронного обработчика."""
    logger.info(f"[Асинхронный обработчик] Событие: {event_name}, Данные: {data}")
    # Имитируем асинхронную работу
    await asyncio.sleep(0.01)
    logger.info(f"[Асинхронный обработчик] Завершена обработка события: {event_name}")


# --- Пример использования ---
# import asyncio
# from mt5_trading_lib.logging_config import setup_logging
#
# async def main():
#     setup_logging()
#
#     # Получаем экземпляр EventBus (Singleton)
#     event_bus = EventBus()
#     # Устанавливаем event loop для асинхронных обработчиков
#     event_bus.set_async_loop(asyncio.get_event_loop())
#
#     # Подписываемся на события
#     event_bus.subscribe("test_event", sync_event_handler)
#     event_bus.subscribe("test_event", async_event_handler)
#     event_bus.subscribe("another_event", sync_event_handler)
#
#     print(f"Подписчиков на 'test_event': {event_bus.get_subscribers_count('test_event')}")
#
#     # Публикуем события
#     print("--- Синхронная публикация ---")
#     event_bus.publish("test_event", {"message": "Hello from sync publish!"})
#     event_bus.publish("another_event", 42)
#
#     # Ждем немного, чтобы синхронные обработчики из пула успели выполниться
#     await asyncio.sleep(0.1)
#
#     print("--- Асинхронная публикация ---")
#     await event_bus.publish_async("test_event", {"message": "Hello from async publish!"})
#
#     # Ждем немного, чтобы асинхронные обработчики успели выполниться
#     await asyncio.sleep(0.1)
#
#     # Отписываемся
#     event_bus.unsubscribe("test_event", sync_event_handler)
#     print(f"После отписки, подписчиков на 'test_event': {event_bus.get_subscribers_count('test_event')}")
#
#     # Завершаем работу
#     event_bus.shutdown()
#
# if __name__ == "__main__":
#     asyncio.run(main())
