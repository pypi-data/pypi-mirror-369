"""Unit-тесты для OrderManager: ордера, валидация, edge-cases."""

import sys
import types

import pytest

from mt5_trading_lib.config import Config, MT5Credentials, RetrySettings
from mt5_trading_lib.exceptions import OrderSendError
from mt5_trading_lib.retry_manager import RetryManager
from mt5_trading_lib.security_manager import SecurityManager


def install_fake_mt5():
    """Подмена модуля MetaTrader5 для тестов OrderManager.

    Удаляет кэш `MetaTrader5` и `mt5_trading_lib.order_manager` для корректной подстановки.
    Возвращает (state, module).
    """
    sys.modules.pop("MetaTrader5", None)
    sys.modules.pop("mt5_trading_lib.order_manager", None)

    state = {
        "symbols": {},
        "orders": {},
        "positions": {},
        "order_send_calls": 0,
        "last_error": (1, "err"),
        "next_order_ticket": 1000,
        "order_send_returns_none": False,
        "order_send_retcode": None,  # если None -> DONE
        "order_send_comment": "ok",
    }

    mod = types.ModuleType("MetaTrader5")

    # Константы, используемые в OrderManager
    mod.ORDER_TYPE_BUY = 0
    mod.ORDER_TYPE_SELL = 1
    mod.TRADE_ACTION_DEAL = 7
    mod.TRADE_ACTION_SLTP = 3
    mod.TRADE_ACTION_MODIFY = 2
    mod.ORDER_TIME_GTC = 1
    mod.ORDER_FILLING_IOC = 2
    mod.TRADE_RETCODE_DONE = 10009
    mod.SYMBOL_TRADE_MODE_DEAL = 0
    mod.SYMBOL_TRADE_MODE_POSITION = 1

    class SymbolInfo:
        def __init__(
            self,
            visible=True,
            trade_mode=mod.SYMBOL_TRADE_MODE_DEAL,
            volume_min=0.01,
            volume_max=100.0,
            bid=1.23,
            ask=1.24,
        ):
            self.visible = visible
            self.trade_mode = trade_mode
            self.volume_min = volume_min
            self.volume_max = volume_max
            self.bid = bid
            self.ask = ask

    class Order:
        def __init__(self, ticket, price_open=1.2, sl=0.0, tp=0.0):
            self.ticket = ticket
            self.price_open = price_open
            self.sl = sl
            self.tp = tp

    class Position:
        def __init__(self, ticket, symbol, type_, volume=1.0, sl=0.0, tp=0.0):
            self.ticket = ticket
            self.symbol = symbol
            self.type = type_
            self.volume = volume
            self.sl = sl
            self.tp = tp

    class Result:
        def __init__(self, retcode, comment="", order=None):
            self.retcode = retcode
            self.comment = comment
            self.order = order

    def symbol_info(symbol: str):
        info = state["symbols"].get(symbol)
        return info

    def last_error():
        return state["last_error"]

    def orders_get(ticket=None):
        if ticket is None:
            return list(state["orders"].values())
        ord_ = state["orders"].get(ticket)
        return [ord_] if ord_ else None

    def positions_get(ticket=None):
        if ticket is None:
            return list(state["positions"].values())
        pos = state["positions"].get(ticket)
        return [pos] if pos else None

    def order_send(request: dict):
        state["order_send_calls"] += 1
        if state["order_send_returns_none"]:
            return None
        ret = (
            state["order_send_retcode"]
            if state["order_send_retcode"] is not None
            else mod.TRADE_RETCODE_DONE
        )
        # эмулируем создание ордера/позиции
        ticket = state["next_order_ticket"]
        state["next_order_ticket"] += 1
        return Result(retcode=ret, comment=state["order_send_comment"], order=ticket)

    mod.symbol_info = symbol_info
    mod.last_error = last_error
    mod.orders_get = orders_get
    mod.positions_get = positions_get
    mod.order_send = order_send
    mod.SymbolInfo = SymbolInfo
    mod.Order = Order
    mod.Position = Position
    mod.__version__ = "5.0.0"

    sys.modules["MetaTrader5"] = mod
    return state, mod


class FakeConnector:
    def __init__(self, connected: bool):
        self._connected = connected

    def is_connected(self) -> bool:
        return self._connected


def build_config(attempts: int = 2, base_delay: float = 0.01) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        retry=RetrySettings(attempts=attempts, base_delay=base_delay),
    )


def build_components(connected: bool = True):
    cfg = build_config()
    retry = RetryManager(cfg)
    # SecurityManager не критичен, просто передадим рабочий экземпляр
    sec = SecurityManager(cfg)
    conn = FakeConnector(connected)
    # Переимпорт OrderManager после подмены mt5
    sys.modules.pop("mt5_trading_lib.order_manager", None)
    from mt5_trading_lib.order_manager import OrderManager

    return cfg, retry, sec, conn, OrderManager


def test_send_market_order_success_buy():
    state, mod = install_fake_mt5()
    # Разрешенный символ
    state["symbols"]["EURUSD"] = mod.SymbolInfo(
        visible=True, trade_mode=mod.SYMBOL_TRADE_MODE_DEAL
    )

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ticket = om.send_market_order("EURUSD", 1.0, "BUY")
    assert isinstance(ticket, int)
    assert state["order_send_calls"] == 1


def test_send_market_order_validation_error_returns_none():
    state, mod = install_fake_mt5()
    # Нет символа
    # state["symbols"] пуст

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ticket = om.send_market_order("BAD", 1.0, "BUY")
    assert ticket is None
    assert state["order_send_calls"] == 0


def test_send_market_order_order_send_none_raises():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["order_send_returns_none"] = True

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    with pytest.raises(OrderSendError):
        om.send_market_order("EURUSD", 1.0, "BUY")


def test_send_market_order_retcode_not_done_raises():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["order_send_retcode"] = 10010  # любой код кроме DONE

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    with pytest.raises(OrderSendError):
        om.send_market_order("EURUSD", 1.0, "BUY")


def test_send_market_order_not_connected_returns_none():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()

    cfg, retry, sec, conn, OrderManager = build_components(connected=False)
    om = OrderManager(cfg, conn, retry, sec)

    ticket = om.send_market_order("EURUSD", 1.0, "BUY")
    assert ticket is None


def test_modify_order_exception_in_response_is_caught_and_false():
    state, mod = install_fake_mt5()
    state["orders"][2] = mod.Order(ticket=2)

    # Сломаем order_send чтобы он бросал исключение
    def boom(req):
        raise RuntimeError("boom")

    mod.order_send = boom

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.modify_order(2, new_price=1.1) is False


def test_close_order_exception_in_response_is_caught_and_false():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["positions"][10] = mod.Position(
        ticket=10, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )

    def boom(req):
        raise RuntimeError("boom")

    mod.order_send = boom

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.close_order(10) is False


def test_modify_order_position_success():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    # Есть позиция с ticket=1
    state["positions"][1] = mod.Position(
        ticket=1, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ok = om.modify_order(1, new_sl=1.1, new_tp=1.2)
    assert ok is True
    assert state["order_send_calls"] == 1


def test_modify_order_not_found_returns_false():
    state, mod = install_fake_mt5()
    # Ни ордеров, ни позиций

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ok = om.modify_order(999, new_sl=1.1)
    assert ok is False


def test_modify_order_order_exists_retcode_not_done_returns_false():
    state, mod = install_fake_mt5()
    # Есть отложенный ордер
    state["orders"][2] = mod.Order(ticket=2)
    # Отправка модификации вернёт ошибку
    state["order_send_retcode"] = 10010

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ok = om.modify_order(2, new_price=1.111)
    assert ok is False


def test_modify_order_no_params_returns_false():
    state, mod = install_fake_mt5()
    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.modify_order(1) is False


def test_close_order_success():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["positions"][10] = mod.Position(
        ticket=10, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)

    ok = om.close_order(10)
    assert ok is True
    assert state["order_send_calls"] == 1


def test_close_order_not_connected_returns_false():
    state, mod = install_fake_mt5()
    state["positions"][10] = mod.Position(
        ticket=10, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )

    cfg, retry, sec, conn, OrderManager = build_components(connected=False)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.close_order(10) is False


def test_send_market_order_retcode_done_success_path():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    # retcode оставляем DONE по умолчанию
    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    ticket = om.send_market_order("EURUSD", 1.0, "BUY")
    assert isinstance(ticket, int)


def test_close_order_position_not_found_returns_false():
    state, mod = install_fake_mt5()
    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.close_order(999) is False


def test_close_order_order_send_none_returns_false():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["positions"][10] = mod.Position(
        ticket=10, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )
    state["order_send_returns_none"] = True

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.close_order(10) is False


def test_close_order_retcode_not_done_returns_false():
    state, mod = install_fake_mt5()
    state["symbols"]["EURUSD"] = mod.SymbolInfo()
    state["positions"][10] = mod.Position(
        ticket=10, symbol="EURUSD", type_=mod.ORDER_TYPE_BUY, volume=1.0
    )
    state["order_send_retcode"] = 10010

    cfg, retry, sec, conn, OrderManager = build_components(connected=True)
    om = OrderManager(cfg, conn, retry, sec)
    assert om.close_order(10) is False
