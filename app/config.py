"""GENESIS SYSTEM / Zeichenwerk — zentrale Konfiguration.

Verbesserungen gegenüber V1:
- Portable Pfade: Windows (F:\\GENESIS_STORAGE), Env-Override (GENESIS_STORAGE),
  Linux/macOS-Fallback (~/.zeichenwerk/GENESIS_STORAGE) — kein hartkodiertes F:\\ mehr.
- Zentrales, key-sicheres Logging (API-Keys werden in Logs maskiert).
- Alle Konstanten an einem Ort, typisiert.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

# ------------------------------------------------------------------ Meta
APP_NAME = "GENESIS SYSTEM"
BRAND = "Zeichenwerk"
SLOGAN_DE = "Zeichen setzen. Jeden Tag."
SLOGAN_EN = "Bold designs for bold people."
VERSION = "2.0.0"
COMPLIANCE_SCHEMA = "PRUEFSYSTEM_SCHEMA_V1.0"

SYSTEM_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------------------ Storage
def _resolve_storage() -> Path:
    """Ermittelt das Storage-Verzeichnis (portabel, übersteuerbar)."""
    env = os.environ.get("GENESIS_STORAGE")
    if env:
        return Path(env)
    if sys.platform == "win32":
        classic = Path(r"F:\GENESIS_STORAGE")
        if classic.exists():
            return classic
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "Zeichenwerk" / "GENESIS_STORAGE"
    return Path.home() / ".zeichenwerk" / "GENESIS_STORAGE"


STORAGE_DIR = _resolve_storage()
DESIGNS_DIR = STORAGE_DIR / "designs"
UPLOAD_READY_DIR = STORAGE_DIR / "upload_ready"
MOCKUPS_DIR = STORAGE_DIR / "mockups"
LOGS_DIR = STORAGE_DIR / "logs"
STATUS_CSV = STORAGE_DIR / "status.csv"

# ------------------------------------------------------------------ Design
DEFAULT_SIZE = 2000  # Standard-Design-Auflösung (px)
MOCKUP_SIZE = (1200, 1400)
PUTER_PORT = 7788
PUTER_RESULT_TIMEOUT = 300  # Sekunden auf Browser-Ergebnis

PRIVATE_INI = SYSTEM_DIR / "config_private.ini"
RULES_FILE = SYSTEM_DIR / "compliance_rules.yaml"

# Levenshtein-Ähnlichkeitsschwelle für Markenschutz (1.0 = identisch)
SIMILARITY_THRESHOLD = 0.88

# ------------------------------------------------------------------ Logging
_KEY_PATTERNS = [
    re.compile(r"(AIza[0-9A-Za-z_\-]{20,})"),          # Google/Gemini
    re.compile(r"(hf_[0-9A-Za-z]{20,})"),               # HuggingFace
    re.compile(r"(sk-[A-Za-z0-9_\-]{20,})"),            # OpenAI
]


class _KeyMaskFilter(logging.Filter):
    """Maskiert API-Keys in jedem Log-Eintrag (Datenschutz-Verbesserung)."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in _KEY_PATTERNS:
                msg = pattern.sub(lambda m: m.group(1)[:6] + "****MASKIERT****", msg)
            record.msg = msg
        return True


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Konfiguriert Console- + File-Logging und gibt den Root-Logger zurück."""
    logger = logging.getLogger("genesis")
    if logger.handlers:  # bereits konfiguriert
        return logger
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)-7s %(name)s: %(message)s")

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(fmt)
    console.addFilter(_KeyMaskFilter())
    logger.addHandler(console)

    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        filehandler = logging.FileHandler(LOGS_DIR / "generator.log", encoding="utf-8")
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(fmt)
        filehandler.addFilter(_KeyMaskFilter())
        logger.addHandler(filehandler)
    except OSError:  # Storage nicht schreibbar → nur Console
        logger.warning("Log-Verzeichnis nicht schreibbar, nur Console-Logging aktiv.")
    logger.propagate = False
    return logger


def ensure_directories() -> None:
    """Erstellt alle Storage-Verzeichnisse bei Bedarf."""
    for d in (STORAGE_DIR, DESIGNS_DIR, UPLOAD_READY_DIR, MOCKUPS_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)


setup_logging()
