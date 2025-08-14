# mt5_trading_lib/order_manager.py
"""
Модуль для управления торговыми операциями в MetaTrader 5.
Предоставляет класс OrderManager с методами для отправки, модификации и закрытия ордеров.
Интегрируется с Mt5Connector, SecurityManager и RetryManager.
"""

import time
from typing import Any, Dict, Optional, Union

import MetaTrader5 as mt5

from .config import Config
from .connector import Mt5Connector
from .exceptions import (
    Mt5TradingLibError,
    OrderCloseError,
    OrderModifyError,
    OrderSendError,
    OrderValidationError,
    TradingOperationError,
)
from .logging_config import get_logger
from .retry_manager import RetryManager
from .security_manager import SecurityManager

logger = get_logger(__name__)


class OrderManager:
    """
    Класс для управления торговыми ордерами: отправка, модификация, закрытие.
    Обеспечивает валидацию параметров и безопасное логирование.
    """

    def __init__(
        self,
        config: Config,
        connector: Mt5Connector,
        retry_manager: RetryManager,
        security_manager: SecurityManager,
    ):
        """
        Инициализирует OrderManager с необходимыми зависимостями.

        Args:
            config (Config): Экземпляр класса Config.
            connector (Mt5Connector): Экземпляр класса Mt5Connector.
            retry_manager (RetryManager): Экземпляр класса RetryManager.
            security_manager (SecurityManager): Экземпляр класса SecurityManager.
        """
        self.config = config
        self.connector = connector
        self.retry_manager = retry_manager
        self.security_manager = security_manager
        logger.debug("OrderManager инициализирован.")

    # --- Вспомогательные методы ---

    def _validate_order_params(
        self,
        symbol: str,
        volume: float,
        order_type: str,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Валидирует параметры ордера. Это упрощенная валидация, в реальном проекте
        она может быть значительно сложнее.

        Args:
            symbol (str): Символ.
            volume (float): Объем.
            order_type (str): Тип ордера ("BUY" или "SELL").
            price (float, optional): Цена для ордера (для рыночных ордеров может не требоваться).
            sl (float, optional): Stop Loss.
            tp (float, optional): Take Profit.
            deviation (int, optional): Максимальное отклонение цены.

        Returns:
            Dict[str, Any]: Словарь с провалидированными параметрами.

        Raises:
            OrderValidationError: Если параметры не прошли валидацию.
        """
        errors = []

        # Проверка символа
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            errors.append(f"Символ '{symbol}' не найден.")
        else:
            if not getattr(symbol_info, "visible", True):
                errors.append(f"Символ '{symbol}' не виден в терминале.")

            # Совместимость с различными наборами констант MT5 (DEAL/POSITION vs FULL/LONGONLY/SHORTONLY)
            trade_mode = getattr(symbol_info, "trade_mode", None)

            TM_DISABLED = getattr(mt5, "SYMBOL_TRADE_MODE_DISABLED", None)
            TM_CLOSEONLY = getattr(mt5, "SYMBOL_TRADE_MODE_CLOSEONLY", None)
            TM_FULL = getattr(mt5, "SYMBOL_TRADE_MODE_FULL", None)
            TM_LONGONLY = getattr(mt5, "SYMBOL_TRADE_MODE_LONGONLY", None)
            TM_SHORTONLY = getattr(mt5, "SYMBOL_TRADE_MODE_SHORTONLY", None)
            TM_DEAL = getattr(mt5, "SYMBOL_TRADE_MODE_DEAL", None)
            TM_POSITION = getattr(mt5, "SYMBOL_TRADE_MODE_POSITION", None)

            if trade_mode is not None:
                # Прямые запреты
                if TM_DISABLED is not None and trade_mode == TM_DISABLED:
                    errors.append(
                        f"Торговля по символу '{symbol}' отключена (DISABLED)."
                    )
                if TM_CLOSEONLY is not None and trade_mode == TM_CLOSEONLY:
                    errors.append(
                        f"Для символа '{symbol}' разрешено только закрытие позиций (CLOSEONLY)."
                    )

                # Ограничения по направлению
                if (
                    order_type == "BUY"
                    and TM_SHORTONLY is not None
                    and trade_mode == TM_SHORTONLY
                ):
                    errors.append(
                        f"По символу '{symbol}' разрешены только короткие позиции (SHORTONLY), BUY запрещён."
                    )
                if (
                    order_type == "SELL"
                    and TM_LONGONLY is not None
                    and trade_mode == TM_LONGONLY
                ):
                    errors.append(
                        f"По символу '{symbol}' разрешены только длинные позиции (LONGONLY), SELL запрещён."
                    )

                # Если доступны только кастомные константы DEAL/POSITION (как в тест-моках),
                # проверим, что значение принадлежит одному из них, если обе константы существуют.
                if TM_DEAL is not None and TM_POSITION is not None:
                    if trade_mode not in [TM_DEAL, TM_POSITION]:
                        errors.append(
                            f"Торговля по символу '{symbol}' запрещена (режим {trade_mode})."
                        )

        # Проверка объема
        if volume <= 0:
            errors.append("Объем ордера должен быть положительным числом.")
        else:
            # Проверка минимального и максимального объема
            if symbol_info:  # Убедимся, что symbol_info доступен
                if volume < symbol_info.volume_min:
                    errors.append(
                        f"Объем {volume} меньше минимально допустимого {symbol_info.volume_min}."
                    )
                if volume > symbol_info.volume_max:
                    errors.append(
                        f"Объем {volume} больше максимально допустимого {symbol_info.volume_max}."
                    )
                # Проверка шага объема
                # volume_step = symbol_info.volume_step
                # if volume_step > 0 and round(volume / volume_step) * volume_step != volume:
                #     errors.append(f"Объем {volume} не кратен шагу {volume_step}.")

        # Проверка типа ордера
        if order_type not in ["BUY", "SELL"]:
            errors.append("Тип ордера должен быть 'BUY' или 'SELL'.")

        # Другие проверки можно добавить по необходимости (цена, sl, tp и т.д.)

        if errors:
            error_msg = "Ошибка валидации параметров ордера: " + "; ".join(errors)
            logger.error(error_msg)
            raise OrderValidationError(error_msg)

        logger.debug("Параметры ордера прошли валидацию.")
        # Возвращаем словарь с параметрами для удобства
        return {
            "symbol": symbol,
            "volume": volume,
            "order_type": order_type,
            "price": price,
            "sl": 0.0 if sl is None else float(sl),
            "tp": 0.0 if tp is None else float(tp),
            "deviation": deviation,
        }

    def _log_order_action(self, action: str, details: Dict[str, Any]) -> None:
        """
        Логирует действие с ордером, заменяя чувствительные данные на маски.

        Args:
            action (str): Действие ("Отправка ордера", "Модификация ордера" и т.д.).
            details (Dict[str, Any]): Детали действия.
        """
        # Создаем копию деталей, чтобы не изменять оригинальный словарь
        safe_details = details.copy()

        # Маскируем потенциально чувствительные данные
        # В данном случае это может быть не столь критично, но показывает подход
        # Например, если бы был комментарий с паролем или токеном
        # comment = safe_details.get('comment', '')
        # if comment:
        #     safe_details['comment'] = self.security_manager.secure_log(comment, "SECRET_TOKEN")

        log_message = f"{action}: {safe_details}"
        logger.info(log_message)

    def _choose_fill_policy(self, symbol_info: Any, override: Optional[int]) -> int:
        """
        Выбирает допустимую политику заполнения (ORDER_TYPE_FILLING) в зависимости от режима исполнения символа
        и переданного override. Опирается на документацию:
        - TRADE_REQUEST_ACTIONS / ORDER_TYPE_FILLING / ORDER_TYPE_TIME
          https://www.mql5.com/ru/docs/python_metatrader5/mt5ordercheck_py#trade_request_actions
          https://www.mql5.com/ru/docs/python_metatrader5/mt5ordercheck_py#order_type_filling
        - Режимы исполнения символа: https://www.mql5.com/ru/docs/constants/environment_state/marketinfoconstants#enum_symbol_trade_execution
        """
        if override is not None:
            return int(override)

        # Значения констант
        FOK = getattr(mt5, "ORDER_FILLING_FOK", None)
        IOC = getattr(mt5, "ORDER_FILLING_IOC", None)
        RET = getattr(mt5, "ORDER_FILLING_RETURN", None)

        # Режим исполнения
        exec_mode = getattr(symbol_info, "trade_execution", None)
        EX_REQ = getattr(mt5, "SYMBOL_TRADE_EXECUTION_REQUEST", None)
        EX_INSTANT = getattr(mt5, "SYMBOL_TRADE_EXECUTION_INSTANT", None)
        EX_MARKET = getattr(mt5, "SYMBOL_TRADE_EXECUTION_MARKET", None)
        EX_EXCHANGE = getattr(mt5, "SYMBOL_TRADE_EXECUTION_EXCHANGE", None)

        # По документации:
        # - Exchange/Market: часто доступен RETURN
        # - Instant/Request: брокер может требовать FOK/IOC — используем IOC как более гибкий default
        if exec_mode in (EX_MARKET, EX_EXCHANGE):
            return RET if RET is not None else (IOC if IOC is not None else (FOK or 0))
        else:
            return IOC if IOC is not None else (FOK if FOK is not None else (RET or 0))

    def _get_fill_candidates(
        self, symbol_info: Any, override: Optional[int]
    ) -> list[int]:
        """
        Возвращает список кандидатов для type_filling в приоритетном порядке:
        override -> symbol_info.filling_mode -> [RETURN, IOC, FOK] (фильтруя None и дубликаты).
        Сформировано так, чтобы первая попытка была максимально вероятной для успеха
        и не вызывала лишних ошибок в журнале терминала.
        """
        candidates: list[int] = []
        if override is not None:
            candidates.append(int(override))
        fill_from_symbol = getattr(symbol_info, "filling_mode", None)
        if fill_from_symbol is not None and int(fill_from_symbol) not in candidates:
            candidates.append(int(fill_from_symbol))
        RET = getattr(mt5, "ORDER_FILLING_RETURN", None)
        IOC = getattr(mt5, "ORDER_FILLING_IOC", None)
        FOK = getattr(mt5, "ORDER_FILLING_FOK", None)
        for v in [RET, IOC, FOK]:
            if v is not None and int(v) not in candidates:
                candidates.append(int(v))
        return candidates

    # --- Методы управления ордерами ---

    def send_market_order(
        self,
        symbol: str,
        volume: float,
        order_type: str,  # "BUY" or "SELL"
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: int = 20,
        comment: str = "",
        type_filling: Optional[int] = None,
        type_time: Optional[int] = None,
    ) -> Optional[int]:
        """
        Отправляет рыночный ордер.

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
        logger.debug(f"Попытка отправки рыночного ордера {order_type} на {symbol}...")

        # Валидация параметров
        try:
            validated_params = self._validate_order_params(
                symbol, volume, order_type, sl=sl, tp=tp, deviation=deviation
            )
        except OrderValidationError:
            # Исключение уже залоггировано в _validate_order_params
            return None

        # Определяем тип ордера MT5
        mt5_order_type = (
            mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
        )
        time_policy = (
            type_time if type_time is not None else getattr(mt5, "ORDER_TIME_GTC", 0)
        )

        def _send_order():
            if not self.connector.is_connected():
                raise TradingOperationError(
                    "Нет подключения к MT5 для отправки ордера."
                )

            # Получаем текущую цену для рыночного ордера
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                raise OrderSendError(
                    f"Не удалось получить информацию о символе {symbol}."
                )
            # Если символ не виден, попробуем его выбрать
            if not getattr(symbol_info, "visible", True):
                try:
                    mt5.symbol_select(symbol, True)
                    symbol_info = mt5.symbol_info(symbol) or symbol_info
                except Exception:
                    pass

            # Цена из последнего тика (рекомендуется по документации), фоллбек на symbol_info
            tick = None
            try:
                tick = mt5.symbol_info_tick(symbol)
            except Exception:
                tick = None
            if tick is not None:
                price = tick.ask if mt5_order_type == mt5.ORDER_TYPE_BUY else tick.bid
            else:
                price = (
                    symbol_info.ask
                    if mt5_order_type == mt5.ORDER_TYPE_BUY
                    else symbol_info.bid
                )

            # Нормализация цены по количеству знаков инструмента
            try:
                digits = getattr(symbol_info, "digits", None)
                if isinstance(digits, int):
                    price = round(float(price), digits)
            except Exception:
                pass
            # Подготовим список кандидатов по type_filling
            candidates = self._get_fill_candidates(symbol_info, type_filling)

            last_check_error = None
            last_send_error = None

            for fill_policy in candidates:
                # Сформируем запрос
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": float(volume),
                    "type": mt5_order_type,
                    "price": float(price),
                    "sl": 0.0 if sl is None else float(sl),
                    "tp": 0.0 if tp is None else float(tp),
                    "deviation": int(deviation),
                    "magic": 10032024,
                    "comment": comment,
                    "type_time": time_policy,
                    "type_filling": int(fill_policy),
                }

                # Логирование попытки
                self._log_order_action("Отправка рыночного ордера", request)

                # order_check
                try:
                    order_check = getattr(mt5, "order_check", None)
                    if callable(order_check):
                        check_res = order_check(request)
                        if check_res is not None:
                            retcode_ok = {0}
                            if hasattr(mt5, "TRADE_RETCODE_DONE"):
                                retcode_ok.add(getattr(mt5, "TRADE_RETCODE_DONE"))
                            if getattr(check_res, "retcode", None) not in retcode_ok:
                                # Сохраним детализацию и попробуем следующий fill
                                last_check_error = self._format_check_error(check_res)
                                continue
                except Exception:
                    # Игнор, перейдём к отправке
                    pass

                # order_send
                result = mt5.order_send(request)
                if result is None:
                    last_send_error = mt5.last_error()
                    continue
                if result.retcode != getattr(mt5, "TRADE_RETCODE_DONE", 10009):
                    # Если брокер вернул Unsupported filling mode — попробуем следующий кандидат
                    unsupported_code = None
                    for attr in dir(mt5):
                        if (
                            attr.startswith("TRADE_RETCODE_")
                            and getattr(mt5, attr, None) == result.retcode
                        ):
                            if "UNSUPPORTED" in attr.upper() and "FILL" in attr.upper():
                                unsupported_code = attr
                            break
                    if unsupported_code:
                        last_send_error = (
                            result.retcode,
                            getattr(result, "comment", unsupported_code),
                        )
                        continue
                    last_send_error = (result.retcode, getattr(result, "comment", ""))
                    continue

                logger.info(f"Рыночный ордер успешно отправлен. Ticket: {result.order}")
                return result.order

            # Если дошли сюда — не удалось
            if last_check_error:
                raise OrderSendError(f"order_check не пройден: {last_check_error}")
            raise OrderSendError(
                f"Не удалось отправить ордер. last_send_error={last_send_error}"
            )

        try:
            # Выполняем с retry и circuit breaker
            order_ticket = self.retry_manager.execute_with_retry_and_circuit_breaker(
                _send_order
            )
            return order_ticket

        except (OrderValidationError, OrderSendError):
            # Эти ошибки не retry'им
            logger.error("Ошибка при отправке рыночного ордера.", exc_info=True)
            raise
        except Mt5TradingLibError:
            logger.error("Ошибка при отправке рыночного ордера (общая).", exc_info=True)
            return None

    def _format_check_error(self, check_res: Any) -> str:
        """
        Читабельное сообщение об ошибке order_check с расшифровкой retcode.
        """
        try:
            retcode = getattr(check_res, "retcode", None)
            # Попробуем отразить имя константы TRADE_RETCODE_*
            code_name = None
            for attr in dir(mt5):
                if (
                    attr.startswith("TRADE_RETCODE_")
                    and getattr(mt5, attr, None) == retcode
                ):
                    code_name = attr
                    break
            comment = getattr(check_res, "comment", None)
            return f"retcode={retcode}({code_name}), comment={comment}"
        except Exception:
            return str(check_res)
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при отправке рыночного ордера: {e}", exc_info=True
            )
            return None

    def modify_order(
        self,
        order_ticket: int,
        new_price: Optional[float] = None,
        new_sl: Optional[float] = None,
        new_tp: Optional[float] = None,
    ) -> bool:
        """
        Модифицирует существующий ордер.

        Args:
            order_ticket (int): Номер ордера (ticket).
            new_price (float, optional): Новая цена (для отложенных ордеров).
            new_sl (float, optional): Новый Stop Loss.
            new_tp (float, optional): Новый Take Profit.

        Returns:
            bool: True, если модификация успешна, иначе False.
        """
        logger.debug(f"Попытка модификации ордера {order_ticket}...")

        if new_sl is None and new_tp is None and new_price is None:
            logger.warning("Нет параметров для модификации ордера.")
            return False

        def _modify_order():
            if not self.connector.is_connected():
                raise TradingOperationError(
                    "Нет подключения к MT5 для модификации ордера."
                )

            # Получаем информацию об ордере
            # Для модификации ордера нам нужна вся его информация
            orders = mt5.orders_get(ticket=order_ticket)
            if orders is None or len(orders) == 0:
                # Проверим, может это позиция?
                positions = mt5.positions_get(ticket=order_ticket)
                if positions is None or len(positions) == 0:
                    last_error = mt5.last_error()
                    raise OrderModifyError(
                        f"Ордер или позиция с ticket {order_ticket} не найдены. Ошибка: {last_error}"
                    )
                else:
                    # Это позиция, модифицируем SL/TP позиции
                    position = positions[0]

                    # Подготавливаем запрос на модификацию позиции
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": position.symbol,
                        "ticket": position.ticket,
                        "sl": 0.0 if new_sl is None else float(new_sl),
                        "tp": 0.0 if new_tp is None else float(new_tp),
                    }

                    self._log_order_action("Модификация позиции (SL/TP)", request)

                    result = mt5.order_send(request)
                    if result is None:
                        last_error = mt5.last_error()
                        raise OrderModifyError(
                            f"order_send для SL/TP вернул None. Ошибка: {last_error}"
                        )

                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        raise OrderModifyError(
                            f"Не удалось модифицировать позицию. Код возврата: {result.retcode}, "
                            f"Описание: {result.comment}"
                        )

                    logger.info(
                        f"Позиция {order_ticket} успешно модифицирована (SL/TP)."
                    )
                    return True

            else:
                # Это отложенный ордер
                order = orders[0]

                # Подготавливаем запрос на модификацию ордера
                request = {
                    "action": mt5.TRADE_ACTION_MODIFY,
                    "ticket": order.ticket,
                    "price": order.price_open
                    if new_price is None
                    else float(new_price),
                    "sl": order.sl if new_sl is None else float(new_sl),
                    "tp": order.tp if new_tp is None else float(new_tp),
                }

                self._log_order_action("Модификация отложенного ордера", request)

                result = mt5.order_send(request)
                if result is None:
                    last_error = mt5.last_error()
                    raise OrderModifyError(
                        f"order_send для модификации ордера вернул None. Ошибка: {last_error}"
                    )

                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    raise OrderModifyError(
                        f"Не удалось модифицировать ордер. Код возврата: {result.retcode}, "
                        f"Описание: {result.comment}"
                    )

                logger.info(f"Отложенный ордер {order_ticket} успешно модифицирован.")
                return True

        try:
            # Выполняем с retry и circuit breaker
            self.retry_manager.execute_with_retry_and_circuit_breaker(_modify_order)
            return True  # Если исключения не было, значит успешно

        except OrderModifyError:
            logger.error("Ошибка при модификации ордера.", exc_info=True)
            return False
        except Mt5TradingLibError:
            logger.error("Ошибка при модификации ордера (общая).", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при модификации ордера: {e}", exc_info=True
            )
            return False

    def close_order(self, order_ticket: int, volume: Optional[float] = None) -> bool:
        """
        Закрывает позицию по ордеру.

        Args:
            order_ticket (int): Номер ордера (ticket) позиции.
            volume (float, optional): Объем для закрытия (частичное закрытие).
                                    Если None, закрывается вся позиция.

        Returns:
            bool: True, если закрытие успешно, иначе False.
        """
        logger.debug(f"Попытка закрытия позиции по ордеру {order_ticket}...")

        def _close_order():
            if not self.connector.is_connected():
                raise TradingOperationError(
                    "Нет подключения к MT5 для закрытия ордера."
                )

            # Получаем информацию о позиции
            positions = mt5.positions_get(ticket=order_ticket)
            if positions is None or len(positions) == 0:
                last_error = mt5.last_error()
                raise OrderCloseError(
                    f"Позиция с ticket {order_ticket} не найдена для закрытия. Ошибка: {last_error}"
                )

            position = positions[0]

            # Определяем тип ордера для закрытия (противоположный)
            close_type = (
                mt5.ORDER_TYPE_SELL
                if position.type == mt5.ORDER_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            )

            # Получаем цену для закрытия: используем тик, фоллбек на symbol_info
            symbol_info = mt5.symbol_info(position.symbol)
            if symbol_info is None:
                raise OrderCloseError(
                    f"Не удалось получить информацию о символе {position.symbol}."
                )

            tick = None
            try:
                tick = mt5.symbol_info_tick(position.symbol)
            except Exception:
                tick = None
            if tick is not None:
                price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask
            else:
                price = (
                    symbol_info.bid
                    if close_type == mt5.ORDER_TYPE_SELL
                    else symbol_info.ask
                )

            try:
                digits = getattr(symbol_info, "digits", None)
                if isinstance(digits, int):
                    price = round(float(price), digits)
            except Exception:
                pass

            # Определяем объем для закрытия
            close_volume = volume if volume is not None else position.volume

            # Подготавливаем запрос на закрытие
            request_base = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": close_volume,
                "type": close_type,
                "position": position.ticket,  # Указываем ticket позиции для закрытия
                "price": price,
                "deviation": 20,  # Можно сделать настраиваемым
                "magic": 10032024,
                "comment": f"Close position {position.ticket}",
            }

            # Перебор filling-мод для закрытия как и при открытии
            candidates = self._get_fill_candidates(symbol_info, override=None)
            # Приоритет закрытия: сначала RETURN (если доступен), затем IOC, затем FOK
            order_pref = []
            RET = getattr(mt5, "ORDER_FILLING_RETURN", None)
            IOC = getattr(mt5, "ORDER_FILLING_IOC", None)
            FOK = getattr(mt5, "ORDER_FILLING_FOK", None)
            for v in [RET, IOC, FOK]:
                if v is not None:
                    order_pref.append(int(v))
            # Сортируем кандидатов по предпочтению
            if order_pref:
                candidates = sorted(
                    candidates,
                    key=lambda x: (order_pref.index(x) if x in order_pref else 99),
                )
            last_send_error = None
            last_check_error = None
            for fill_policy in candidates:
                request = {
                    **request_base,
                    "type_time": getattr(mt5, "ORDER_TIME_GTC", 0),
                    "type_filling": int(fill_policy),
                }
                self._log_order_action("Закрытие позиции", request)
                # Предварительная проверка
                try:
                    order_check = getattr(mt5, "order_check", None)
                    if callable(order_check):
                        check_res = order_check(request)
                        if check_res is not None:
                            retcode_ok = {0}
                            if hasattr(mt5, "TRADE_RETCODE_DONE"):
                                retcode_ok.add(getattr(mt5, "TRADE_RETCODE_DONE"))
                            if getattr(check_res, "retcode", None) not in retcode_ok:
                                last_check_error = self._format_check_error(check_res)
                                continue
                except Exception:
                    pass

                result = mt5.order_send(request)
                if result is None:
                    last_send_error = mt5.last_error()
                    continue
                if result.retcode != getattr(mt5, "TRADE_RETCODE_DONE", 10009):
                    last_send_error = (result.retcode, getattr(result, "comment", ""))
                    continue

                logger.info(
                    f"Позиция {order_ticket} успешно закрыта. Закрыто {close_volume} из {position.volume}."
                )
                return True

            if last_check_error:
                raise OrderCloseError(
                    f"Не удалось закрыть позицию. order_check: {last_check_error}"
                )
            raise OrderCloseError(
                f"Не удалось закрыть позицию. last_send_error={last_send_error}"
            )

        try:
            # Выполняем с retry и circuit breaker
            self.retry_manager.execute_with_retry_and_circuit_breaker(_close_order)
            return True  # Если исключения не было, значит успешно

        except OrderCloseError:
            logger.error("Ошибка при закрытии позиции.", exc_info=True)
            return False
        except Mt5TradingLibError:
            logger.error("Ошибка при закрытии позиции (общая).", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при закрытии позиции: {e}", exc_info=True)
            return False


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.connector import Mt5Connector
#     from mt5_trading_lib.retry_manager import RetryManager
#     from mt5_trading_lib.security_manager import SecurityManager
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     try:
#         config = Config.load_config()
#         connector = Mt5Connector(config)
#         retry_manager = RetryManager(config)
#         security_manager = SecurityManager(config)
#
#         if connector.connect():
#             order_manager = OrderManager(config, connector, retry_manager, security_manager)
#
#             # Отправка рыночного ордера (убедитесь, что это демо-счет!)
#             # order_ticket = order_manager.send_market_order("EURUSD",0.1, "BUY")
# # if order_ticket:
# # print(f"Ордер отправлен. Ticket: {order_ticket}")
# #
# # # Модификация (если это позиция)
# # # success = order_manager.modify_order(order_ticket, new_sl=1.05, new_tp=1.15)
# # # print(f"Модификация: {'Успешна' if success else 'Ошибка'}")
# #
# # # Закрытие
# # # success = order_manager.close_order(order_ticket)
# # # print(f"Закрытие: {'Успешно' if success else 'Ошибка'}")
# # else:
# # print("Не удалось отправить ордер.")
#
# connector.disconnect()
# else:
# print("Не удалось подключиться к MT5.")
#
# except Exception as e:
# logger.error(f"Критическая ошибка в примере: {e}", exc_info=True)
