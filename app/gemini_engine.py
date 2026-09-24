"""Google Gemini-Engine (google-genai SDK).

- Modelle: gemini-2.5-flash, gemini-2.0-flash
- API-Key kostenlos; Bildgenerierung in der EU teilweise eingeschränkt (403/429)
- Ohne SDK/Key: saubere Fehlermeldung, kein Crash
"""

from __future__ import annotations

import base64
import io
import logging
import random
from pathlib import Path

from PIL import Image

import config
import key_manager

logger = logging.getLogger("genesis.gemini")

MODELS = ("gemini-2.5-flash", "gemini-2.0-flash")
DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiUnavailable(RuntimeError):
    """Raised wenn SDK/Key fehlen oder EU-Einschränkung greift."""


def _get_client():
    try:
        from google import genai
    except ImportError as exc:
        raise GeminiUnavailable(
            "google-genai ist nicht installiert (pip install google-genai)"
        ) from exc
    api_key = key_manager.get_key("gemini")
    if not api_key:
        raise GeminiUnavailable(
            "Kein Gemini-API-Key gefunden (API-Schlüssel-Tab / config_private.ini)"
        )
    return genai.Client(api_key=api_key)


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: int = config.DEFAULT_SIZE,
    seed: int | None = None,
    out_path: Path | None = None,
) -> Path:
    """Generiert ein Bild via Gemini (Imagen-Endpoint).

    Wirft GeminiUnavailable bei EU-Einschränkung (403/429) o.ä.
    """
    if model not in MODELS:
        raise ValueError(f"Unbekanntes Modell {model!r}. Erlaubt: {', '.join(MODELS)}")
    client = _get_client()
    _ = seed  # Gemini nutzt keinen Seed
    logger.info("Gemini-Generierung: %s", model)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt + ", generate an image",
        )
    except Exception as exc:  # noqa: BLE001 — SDK-Fehler sind vielfältig
        raise GeminiUnavailable(f"Gemini-API-Fehler (EU-Einschränkung?): {exc}") from exc

    # Antwort kann Text mit Inline-Bildern sein
    for part in getattr(response, "candidates", [])[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            img = Image.open(io.BytesIO(base64.b64decode(inline.data)))
            img = img.convert("RGB")
            if img.size != (size, size):
                img = img.resize((size, size), Image.LANCZOS)
            suffix = seed if seed is not None else random.randint(1000, 9999)
            out_path = out_path or config.DESIGNS_DIR / f"gemini_{suffix}.png"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(out_path, "PNG", optimize=True)
            logger.info("Gemini-Bild gespeichert: %s", out_path.name)
            return out_path
    raise GeminiUnavailable("Gemini hat kein Bild zurückgegeben (EU-Einschränkung möglich).")


def analyze_image(image_path: Path, question: str = "Describe this design.") -> str:
    """Bildanalyse (Text) via Gemini — für das Feedback-Tab."""
    client = _get_client()
    payload = {
        "parts": [
            {"text": question},
            {"inline_data": {"mime_type": "image/png",
                             "data": base64.b64encode(image_path.read_bytes()).decode()}},
        ]
    }
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL, contents=payload)
        return response.text or ""
    except Exception as exc:  # noqa: BLE001
        raise GeminiUnavailable(f"Gemini-Analyse fehlgeschlagen: {exc}") from exc


def translate_de_en(text: str) -> str:
    """Übersetzung DE→EN via Gemini (Fallback: lokale Wörterbuch-Übersetzung)."""
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=f"Translate to English, answer with the translation only: {text}",
        )
        return (response.text or text).strip()
    except GeminiUnavailable:
        import scene_engine
        return " ".join(scene_engine.translate_de_en(w) for w in text.split())


def available() -> bool:
    try:
        _get_client()
        return True
    except GeminiUnavailable:
        return False
