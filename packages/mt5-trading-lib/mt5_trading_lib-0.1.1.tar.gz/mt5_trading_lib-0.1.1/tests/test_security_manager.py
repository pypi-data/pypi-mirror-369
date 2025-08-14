"""Unit-тесты для SecurityManager."""

import pytest

from mt5_trading_lib.config import Config, MT5Credentials, SecuritySettings
from mt5_trading_lib.exceptions import CredentialEncryptionError
from mt5_trading_lib.security_manager import SecurityManager


def build_config_with_key(key_b64: str | None) -> Config:
    return Config(
        mt5=MT5Credentials(login=1, password="p", server="s"),
        security=SecuritySettings(encryption_key_base64=key_b64),
    )


def test_encrypt_without_key_raises():
    cfg = build_config_with_key(None)
    sm = SecurityManager(cfg)
    with pytest.raises(CredentialEncryptionError):
        sm.encrypt("secret")


def test_encrypt_decrypt_roundtrip():
    key = SecurityManager.generate_key()
    cfg = build_config_with_key(key)
    sm = SecurityManager(cfg)

    secret = "MyS3cret!"
    encrypted = sm.encrypt(secret)
    assert isinstance(encrypted, str)
    decrypted = sm.decrypt(encrypted)
    assert decrypted == secret


def test_encrypt_raises_without_key():
    # Без ключа должен бросить CredentialEncryptionError
    cfg = build_config_with_key(None)
    sm = SecurityManager(cfg)
    import pytest

    with pytest.raises(CredentialEncryptionError):
        sm.encrypt("x")


def test_decrypt_invalid_token_raises():
    key = SecurityManager.generate_key()
    cfg = build_config_with_key(key)
    sm = SecurityManager(cfg)
    import base64

    garbage = base64.urlsafe_b64encode(b"not-a-fernet-token").decode()
    import pytest

    with pytest.raises(CredentialEncryptionError):
        sm.decrypt(garbage)


def test_setup_encryption_wrong_length_key_raises():
    import base64
    import os

    short_key_b64 = base64.urlsafe_b64encode(os.urandom(16)).decode()
    import pytest

    with pytest.raises(CredentialEncryptionError):
        _ = SecurityManager(build_config_with_key(short_key_b64))


def test_secure_log_masks_sensitive():
    key = SecurityManager.generate_key()
    cfg = build_config_with_key(key)
    sm = SecurityManager(cfg)

    msg = "Attempt with password=MyS3cret!"
    masked = sm.secure_log(msg, "MyS3cret!")
    assert "MyS3cret!" not in masked
    assert "***" in masked


def test_decrypt_with_wrong_key_raises():
    # Генерируем два разных ключа
    key1 = SecurityManager.generate_key()
    key2 = SecurityManager.generate_key()

    cfg1 = build_config_with_key(key1)
    cfg2 = build_config_with_key(key2)

    sm1 = SecurityManager(cfg1)
    sm2 = SecurityManager(cfg2)

    secret = "TopSecret123"
    encrypted = sm1.encrypt(secret)
    with pytest.raises(CredentialEncryptionError):
        sm2.decrypt(encrypted)


def test_invalid_base64_key_raises_on_setup():
    bad_key = "not_base64@@@"
    with pytest.raises(CredentialEncryptionError):
        _ = SecurityManager(build_config_with_key(bad_key))


def test_secure_log_mask_length_rules():
    key = SecurityManager.generate_key()
    cfg = build_config_with_key(key)
    sm = SecurityManager(cfg)

    sensitive = "ABCDEFGHIJ"  # len=10, половина=5
    expected_mask = "*" * 5
    msg = f"token={sensitive}"
    masked = sm.secure_log(msg, sensitive)
    assert expected_mask in masked
    assert sensitive not in masked


def test_secure_log_when_sensitive_empty_returns_original():
    key = SecurityManager.generate_key()
    cfg = build_config_with_key(key)
    sm = SecurityManager(cfg)

    msg = "no secrets here"
    assert sm.secure_log(msg, "") == msg
