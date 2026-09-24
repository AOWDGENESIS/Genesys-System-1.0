"""Auto-Erkennung von API-Keys anhand ihres Formats.

Erkannt:
  Gemini:      AIza…        (Google Cloud API-Key)
  HuggingFace: hf_…         (Read/Write Token)
  OpenAI:      sk-…         (Secret Key)
"""

from __future__ import annotations

import re

GEMINI_PATTERN = re.compile(r"^AIza[0-9A-Za-z_\-]{30,}$")
HF_PATTERN = re.compile(r"^hf_[0-9A-Za-z]{20,}$")
OPENAI_PATTERN = re.compile(r"^sk-[A-Za-z0-9_\-]{40,}$")


def detect(key: str) -> tuple[str | None, str]:
    """Erkennt den Service für einen Key. Gibt (service, beschreibung) zurück.

    service=None wenn nicht erkannt.
    """
    key = key.strip()
    if not key:
        return None, "Leerer Key."
    if GEMINI_PATTERN.match(key):
        return "gemini", "Google Gemini API-Key erkannt (AIza…)."
    if HF_PATTERN.match(key):
        return "huggingface", "HuggingFace-Token erkannt (hf_…)."
    if OPENAI_PATTERN.match(key):
        return "openai", "OpenAI-Secret-Key erkannt (sk-…)."
    return None, ("Unbekanntes Key-Format. Erkannt werden: Gemini (AIza…), "
                  "HuggingFace (hf_…), OpenAI (sk-…).")


def detect_and_store(key: str) -> tuple[str | None, str]:
    """Erkennt den Service und speichert den Key direkt. Gibt (service, message)."""
    import key_manager

    service, msg = detect(key)
    if service:
        key_manager.set_key(service, key)
    return service, msg
