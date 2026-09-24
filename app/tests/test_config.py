"""Tests: config.py (Pfade, Logging, Key-Masking)."""

from __future__ import annotations

import logging

import config


def test_meta_constants() -> None:
    assert config.APP_NAME == "GENESIS SYSTEM"
    assert config.BRAND == "Zeichenwerk"
    assert config.SLOGAN_DE == "Zeichen setzen. Jeden Tag."
    assert config.COMPLIANCE_SCHEMA == "PRUEFSYSTEM_SCHEMA_V1.0"
    assert config.DEFAULT_SIZE == 2000
    assert config.MOCKUP_SIZE == (1200, 1400)
    assert config.PUTER_PORT == 7788


def test_storage_directories(tmp_storage) -> None:
    config.ensure_directories()
    assert config.DESIGNS_DIR.parent == tmp_storage
    for sub in ("designs", "upload_ready", "mockups", "logs"):
        assert (tmp_storage / sub).exists()


def test_storage_env_override(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GENESIS_STORAGE", str(tmp_path / "custom"))
    import importlib
    importlib.reload(config)
    try:
        assert str(config.STORAGE_DIR).endswith("custom")
    finally:
        monkeypatch.delenv("GENESIS_STORAGE")
        importlib.reload(config)


def test_key_masking_in_logs(tmp_storage) -> None:
    """Der Mask-Filter muss Keys in Log-Nachrichten ersetzen."""
    secret_gemini = "AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567"
    secret_hf = "hf_" + "x" * 30
    secret_openai = "sk-" + "y" * 44

    fmt = logging.Formatter("%(message)s")
    for secret in (secret_gemini, secret_hf, secret_openai):
        record = logging.LogRecord("genesis", logging.WARNING, __file__, 1,
                                   "Key lautet " + secret, None, None)
        assert config._KeyMaskFilter().filter(record) is True
        rendered = fmt.format(record)
        assert secret not in rendered, secret
        assert "MASKIERT" in rendered
    # genesis-Logger loggt nie in den Root-Logger durch (Keys bleiben intern)
    logger = config.setup_logging()
    assert logger.propagate is False
