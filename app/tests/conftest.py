"""Pytest-Konfiguration: isolierter Storage + deterministische Umgebung."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


@pytest.fixture()
def tmp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Lenkt GENESIS_STORAGE in ein Test-Tempverzeichnis um."""
    import config

    storage = tmp_path / "genesis_storage"
    storage.mkdir(parents=True)
    monkeypatch.setattr(config, "STORAGE_DIR", storage)
    monkeypatch.setattr(config, "DESIGNS_DIR", storage / "designs")
    monkeypatch.setattr(config, "UPLOAD_READY_DIR", storage / "upload_ready")
    monkeypatch.setattr(config, "MOCKUPS_DIR", storage / "mockups")
    monkeypatch.setattr(config, "LOGS_DIR", storage / "logs")
    monkeypatch.setattr(config, "STATUS_CSV", storage / "status.csv")
    return storage


@pytest.fixture()
def tmp_ini(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Lenkt config_private.ini in ein Test-Tempverzeichnis um."""
    import config

    ini = tmp_path / "config_private.ini"
    monkeypatch.setattr(config, "PRIVATE_INI", ini)
    return ini
