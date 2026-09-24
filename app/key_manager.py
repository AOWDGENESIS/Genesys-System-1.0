"""API-Key-Verwaltung: INI-basiert, Keys werden NIEMALS geloggt.

- Speicher: config_private.ini (lokal, gitignored)
- Lesen/Schreiben/Testen von Keys pro Service
- Maskierte Darstellung für GUI (nur erste/letzte 4 Zeichen)
"""

from __future__ import annotations

import configparser
import logging
from pathlib import Path

import config

logger = logging.getLogger("genesis.keys")

SERVICES = ("gemini", "huggingface", "openai")
SECTION = "API_KEYS"

_PLACEHOLDER = "___NICHT_SET___"

def _ini_path() -> Path:
    return config.PRIVATE_INI

def _read_ini(path: Path | None = None) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    p = path or _ini_path()
    if p.exists():
        parser.read(p, encoding="utf-8")
    return parser

def get_key(service: str) -> str | None:
    """Liefert den API-Key für einen Service (oder None)."""
    if service not in SERVICES:
        raise ValueError(f"Unbekannter Service {service!r}. Erlaubt: {SERVICES}")
    parser = _read_ini()
    key = parser.get(SECTION, service, fallback="").strip()
    return key or None

def set_key(service: str, key: str) -> None:
    """Speichert einen API-Key (leerer String löscht)."""
    if service not in SERVICES:
        raise ValueError(f"Unbekannter Service {service!r}. Erlaubt: {SERVICES}")
    parser = _read_ini()
    if not parser.has_section(SECTION):
        parser.add_section(SECTION)
    key = key.strip()
    if key:
        parser.set(SECTION, service, key)
    else:
        parser.remove_option(SECTION, service)
    with open(_ini_path(), "w", encoding="utf-8") as fh:
        parser.write(fh)
    # bewusst OHNE Key-Inhalt loggen
    logger.info("API-Key für %s %s.", service, "gesetzt" if key else "gelöscht")

def mask_key(key: str | None) -> str:
    """Maskiert einen Key für die Anzeige."""
    if not key:
        return "(nicht gesetzt)"
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"

def mask_all() -> dict[str, str]:
    """Alle Services maskiert (für GUI)."""
    return {s: mask_key(get_key(s)) for s in SERVICES}

def clear_all(path: Path | None = None) -> None:
    """Löscht alle Keys (für Tests)."""
    p = path or _ini_path()
    if p.exists():
        p.unlink()
    logger.info("Alle API-Keys gelöscht.")

def test_connection(service: str) -> tuple[bool, str]:
    """Verbindungstest pro Service. Gibt (ok, message) zurück — ohne Keys zu loggen."""
    key = get_key(service)
    if not key:
        return False, f"Kein Key für {service} gesetzt."

    import requests

    try:
        if service == "gemini":
            r = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
                timeout=15,
            )
        elif service == "huggingface":
            r = requests.get("https://huggingface.co/api/whoami-v2",
                             headers={"Authorization": f"Bearer {key}"}, timeout=15)
        else:  # openai
            r = requests.get("https://api.openai.com/v1/models",
                             headers={"Authorization": f"Bearer {key}"}, timeout=15)
        if r.status_code in (401, 403):
            return False, f"{service}: Key ungültig (HTTP {r.status_code})."
        if r.status_code == 429:
            return True, f"{service}: Key OK, Rate-Limit erreicht (HTTP 429)."
        if r.ok:
            return True, f"{service}: Verbindung OK."
        return False, f"{service}: HTTP {r.status_code}."
    except requests.RequestException as exc:
        return False, f"{service}: Netzwerkfehler ({exc.__class__.__name__})."
