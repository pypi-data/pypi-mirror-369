"""Unit-тесты для EventBus: подписка/публикация/отписка и async-handlers."""

import asyncio
import time

from mt5_trading_lib.event_bus import EventBus


def test_subscribe_publish_unsubscribe_sync():
    bus = EventBus()

    received = []

    def handler(name, data):
        received.append((name, data))

    bus.subscribe("e1", handler)
    bus.publish("e1", {"x": 1})

    # Даем времени thread pool выполнить задачу
    time.sleep(0.05)
    assert ("e1", {"x": 1}) in received

    assert bus.unsubscribe("e1", handler) is True
    # Повторная отписка возвращает False
    assert bus.unsubscribe("e1", handler) is False


def test_async_handlers():
    bus = EventBus()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bus.set_async_loop(loop)

    received = []

    async def ah(name, data):
        await asyncio.sleep(0.01)
        received.append((name, data))

    bus.subscribe("e2", ah)
    bus.publish("e2", {"y": 2})

    loop.run_until_complete(asyncio.sleep(0.05))
    assert ("e2", {"y": 2}) in received

    bus.shutdown()
    loop.close()
