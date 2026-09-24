"""Tests: key_manager.py (INI, Masking, kein Key im Log) + api_key_detector.py."""

from __future__ import annotations

import logging

import key_manager
import api_key_detector as detector


# ---------------------------------------------------------------- Detector
def test_detect_gemini() -> None:
    key = "AIzaSy" + "A" * 34
    service, msg = detector.detect(key)
    assert service == "gemini"
    assert "Gemini" in msg


def test_detect_huggingface() -> None:
    key = "hf_" + "B" * 30
    service, _ = detector.detect(key)
    assert service == "huggingface"


def test_detect_openai() -> None:
    key = "sk-" + "C" * 44
    service, _ = detector.detect(key)
    assert service == "openai"


def test_detect_unknown() -> None:
    assert detector.detect("12345")[0] is None
    assert detector.detect("")[0] is None
    assert detector.detect("sk-zu-kurz")[0] is None


def test_detect_and_store(tmp_ini) -> None:
    key = "hf_" + "D" * 30
    service, msg = detector.detect_and_store(key)
    assert service == "huggingface"
    assert key_manager.get_key("huggingface") == key


# ---------------------------------------------------------------- Manager
def test_set_get_clear(tmp_ini) -> None:
    assert key_manager.get_key("gemini") is None
    key_manager.set_key("gemini", "AIzaSy" + "E" * 34)
    assert key_manager.get_key("gemini").startswith("AIza")
    key_manager.set_key("gemini", "")
    assert key_manager.get_key("gemini") is None


def test_ini_file_created(tmp_ini) -> None:
    key_manager.set_key("openai", "sk-" + "F" * 44)
    assert tmp_ini.exists()
    content = tmp_ini.read_text(encoding="utf-8")
    assert "openai" in content


def test_invalid_service(tmp_ini) -> None:
    import pytest
    with pytest.raises(ValueError):
        key_manager.get_key("openweather")
    with pytest.raises(ValueError):
        key_manager.set_key("openweather", "x")


def test_mask_key() -> None:
    assert key_manager.mask_key(None) == "(nicht gesetzt)"
    assert key_manager.mask_key("12345678") == "********"
    key = "AIzaSy" + "G" * 30
    masked = key_manager.mask_key(key)
    assert masked.startswith("AIza") and masked.endswith(key[-4:])
    assert key[4:-4] not in masked


def test_mask_all(tmp_ini) -> None:
    key = "AIzaSy" + "G" * 34
    key_manager.set_key("gemini", key)
    masked = key_manager.mask_all()
    assert set(masked) == {"gemini", "huggingface", "openai"}
    assert masked["gemini"].startswith("AIza")
    assert "*" * 10 in masked["gemini"]       # Mittelteil maskiert
    assert key[4:-4] not in masked["gemini"]


def test_keys_never_logged(tmp_ini, caplog) -> None:
    key = "AIzaSy" + "H" * 34
    with caplog.at_level(logging.INFO, logger="genesis.keys"):
        key_manager.set_key("gemini", key)
    assert key not in caplog.text
    assert "gesetzt" in caplog.text


def test_clear_all(tmp_ini) -> None:
    key_manager.set_key("gemini", "AIzaSy" + "I" * 34)
    key_manager.clear_all()
    assert not tmp_ini.exists()
    assert key_manager.get_key("gemini") is None
