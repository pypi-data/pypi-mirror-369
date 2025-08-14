# mt5_trading_lib/security_manager.py
"""
Модуль для обеспечения безопасности: шифрование/дешифрование учетных данных
и безопасное логирование.
Использует библиотеку cryptography для симметричного шифрования.
"""

import base64
import logging
import os
from typing import Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import Config
from .exceptions import CredentialEncryptionError, SecurityError
from .logging_config import get_logger

logger = get_logger(__name__)


class SecurityManager:
    """
    Класс для управления аспектами безопасности:
    - Шифрование и дешифрование данных.
    - Генерация ключей.
    - Безопасное логирование.
    """

    def __init__(self, config: Config):
        """
        Инициализирует SecurityManager с конфигурацией.

        Args:
            config (Config): Экземпляр класса Config с настройками безопасности.
        """
        self.config = config
        self._fernet: Optional[Fernet] = None
        self._setup_encryption()

    def _setup_encryption(self) -> None:
        """
        Настраивает механизм шифрования на основе конфигурации.
        """
        key_b64 = self.config.security.encryption_key_base64
        if not key_b64:
            logger.warning(
                "Ключ шифрования (ENCRYPTION_KEY_BASE64) не найден в конфигурации. "
                "Шифрование/дешифрование учетных данных будет недоступно."
            )
            self._fernet = None
            return

        try:
            # Валидируем ключ: он должен декодироваться в 32 байта,
            # но в Fernet нужно передавать base64-представление ключа
            raw_key = base64.urlsafe_b64decode(key_b64.encode("utf-8"))
            if len(raw_key) != 32:
                raise CredentialEncryptionError(
                    "Неверная длина ключа шифрования. Ожидается 32 байта (256 бит)."
                )
            # Передаём именно base64-ключ, как того требует Fernet
            self._fernet = Fernet(key_b64.encode("utf-8"))
            logger.debug("Механизм шифрования успешно настроен.")
        except (ValueError, TypeError) as e:
            logger.error(
                "Ошибка при декодировании ключа шифрования из base64.", exc_info=True
            )
            raise CredentialEncryptionError(
                "Неверный формат ключа шифрования (ENCRYPTION_KEY_BASE64). "
                "Он должен быть корректной строкой base64, представляющей 32-байтный ключ."
            ) from e

    @staticmethod
    def generate_key() -> str:
        """
        Генерирует новый 32-байтный ключ для Fernet и возвращает его в формате base64.

        Returns:
            str: Новый ключ, закодированный в base64.
        """
        key = (
            Fernet.generate_key()
        )  # Генерирует 32-байтный ключ и кодирует его в base64
        logger.info("Новый ключ шифрования сгенерирован.")
        return key.decode("utf-8")  # Возвращаем как строку

    @staticmethod
    def generate_key_from_password(password: str, salt: Optional[bytes] = None) -> str:
        """
        Генерирует 32-байтный ключ из пароля с использованием PBKDF2.
        Это альтернативный способ получения ключа, если у вас есть пароль.

        Args:
            password (str): Исходный пароль.
            salt (bytes, optional): Соль. Если не указана, генерируется новая.

        Returns:
            str: Ключ, закодированный в base64.
        """
        if salt is None:
            salt = os.urandom(16)  # Рекомендуемая длина соли

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Рекомендуемое количество итераций
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        logger.debug("Ключ шифрования сгенерирован из пароля.")
        return key.decode("utf-8")

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Шифрует строку или байты.

        Args:
            data (Union[str, bytes]): Данные для шифрования.

        Returns:
            str: Зашифрованные данные, закодированные в base64.

        Raises:
            CredentialEncryptionError: Если шифрование не настроено или произошла ошибка.
        """
        if self._fernet is None:
            raise CredentialEncryptionError(
                "Шифрование не настроено: отсутствует ключ (ENCRYPTION_KEY_BASE64)."
            )

        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            encrypted_data = self._fernet.encrypt(data)
            # Fernet возвращает bytes, кодируем в base64 string для удобства хранения
            return base64.urlsafe_b64encode(encrypted_data).decode("utf-8")

        except Exception as e:
            logger.error("Ошибка при шифровании данных.", exc_info=True)
            raise CredentialEncryptionError("Не удалось зашифровать данные.") from e

    def decrypt(self, encrypted_data_b64: str) -> str:
        """
        Дешифрует данные, закодированные в base64.

        Args:
            encrypted_data_b64 (str): Зашифрованные данные в формате base64.

        Returns:
            str: Расшифрованные данные.

        Raises:
            CredentialEncryptionError: Если шифрование не настроено или произошла ошибка.
        """
        if self._fernet is None:
            raise CredentialEncryptionError(
                "Дешифрование не настроено: отсутствует ключ (ENCRYPTION_KEY_BASE64)."
            )

        try:
            # Декодируем base64 обратно в bytes
            encrypted_data = base64.urlsafe_b64decode(
                encrypted_data_b64.encode("utf-8")
            )
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return decrypted_data.decode("utf-8")

        except InvalidToken:
            logger.error("Неверный токен при дешифровании. Возможно, неверный ключ.")
            raise CredentialEncryptionError(
                "Не удалось дешифровать данные: неверный токен. Проверьте ключ шифрования."
            )
        except Exception as e:
            logger.error("Ошибка при дешифровании данных.", exc_info=True)
            raise CredentialEncryptionError("Не удалось дешифровать данные.") from e

    def secure_log(self, message: str, sensitive_data: str) -> str:
        """
        Создает безопасное сообщение для логирования, заменяя чувствительные данные
        на маску.

        Args:
            message (str): Исходное сообщение.
            sensitive_data (str): Данные, которые нужно скрыть.

        Returns:
            str: Сообщение с замаскированными чувствительными данными.
        """
        if not sensitive_data:
            return message
        # Заменяем все вхождения чувствительных данных на звездочки
        # Длина маски соответствует длине оригинальных данных для дополнительной безопасности
        mask_length = max(3, len(sensitive_data) // 2)  # Минимум 3 звездочки
        mask = "*" * mask_length
        safe_message = message.replace(sensitive_data, mask)
        return safe_message


# --- Пример использования ---
# if __name__ == "__main__":
#     from mt5_trading_lib.config import Config
#     from mt5_trading_lib.logging_config import setup_logging
#
#     setup_logging()
#
#     # --- Генерация нового ключа ---
#     # new_key = SecurityManager.generate_key()
#     # print(f"Сгенерированный ключ (поместите его в .env как ENCRYPTION_KEY_BASE64):\n{new_key}")
#     # ---
#
#     try:
#         config = Config.load_config()
#         security_manager = SecurityManager(config)
#
#         secret = "MySecretPassword123!"
#         print(f"Оригинал: {secret}")
#
#         # Шифрование
#         encrypted = security_manager.encrypt(secret)
#         print(f"Зашифровано: {encrypted}")
#
#         # Дешифрование
#         decrypted = security_manager.decrypt(encrypted)
#         print(f"Расшифровано: {decrypted}")
#
#         # Безопасное логирование
#         log_msg = f"Попытка подключения с паролем: {secret}"
#         safe_log_msg = security_manager.secure_log(log_msg, secret)
#         print(f"Безопасное логирование: {safe_log_msg}")
#         # logger.info(safe_log_msg) # Используйте это в реальном коде
#
#     except Exception as e:
#         logger.error(f"Ошибка в примере использования SecurityManager: {e}", exc_info=True)
