"""HuggingFace Inference-Engine (FLUX.1-schnell, SDXL, SD2.1, SD1.4).

- Nutzt huggingface_hub InferenceClient (die alte API-URL gibt 404 —
  genau deshalb der InferenceClient, siehe bekannte Einschränkungen V1)
- Token: kostenloser Read-Token, 1000 Bilder/Tag gratis
- Läuft ohne Token/hub-Modul nicht → saubere Fehlermeldungen, kein Crash
"""

from __future__ import annotations

import io
import logging
import random
from pathlib import Path

from PIL import Image

import config
import key_manager

logger = logging.getLogger("genesis.huggingface")

MODELS: dict[str, str] = {
    "flux_schnell": "black-forest-labs/FLUX.1-schnell",
    "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
    "sd21": "stabilityai/stable-diffusion-2-1",
    "sd14": "CompVis/stable-diffusion-v1-4",
}

DEFAULT_MODEL = "flux_schnell"
DEFAULT_SIZE = 1024  # HF-Inference-Standard


class HuggingFaceUnavailable(RuntimeError):
    """Raised wenn Client/Token fehlen."""


def _get_client():
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise HuggingFaceUnavailable(
            "huggingface_hub ist nicht installiert (pip install huggingface_hub)"
        ) from exc
    token = key_manager.get_key("huggingface")
    if not token:
        raise HuggingFaceUnavailable(
            "Kein HuggingFace-Token gefunden (API-Schlüssel-Tab / config_private.ini)"
        )
    return InferenceClient(token=token)


def generate_image(
    prompt: str,
    model_key: str = DEFAULT_MODEL,
    size: int = config.DEFAULT_SIZE,
    seed: int | None = None,
    out_path: Path | None = None,
) -> Path:
    """Generiert ein Bild via HuggingFace Inference. Gibt Speicherpfad zurück."""
    if model_key not in MODELS:
        raise ValueError(f"Unbekanntes Modell {model_key!r}. Erlaubt: {', '.join(MODELS)}")
    client = _get_client()
    if seed is None:
        seed = random.randint(0, 2**31 - 1)

    logger.info("HuggingFace-Generierung: %s (seed=%d)", MODELS[model_key], seed)
    try:
        result = client.text_to_image(
            prompt,
            model=MODELS[model_key],
            width=min(size, DEFAULT_SIZE),
            height=min(size, DEFAULT_SIZE),
            seed=seed,
        )
    except TypeError:
        # ältere hub-Versionen unterstützen width/height/seed nicht
        result = client.text_to_image(prompt, model=MODELS[model_key])

    if isinstance(result, bytes):
        img = Image.open(io.BytesIO(result))
    else:
        img = result  # PIL.Image bereits

    img = img.convert("RGB")
    if img.size != (size, size):
        img = img.resize((size, size), Image.LANCZOS)

    out_path = out_path or config.DESIGNS_DIR / f"hf_{seed}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    logger.info("HuggingFace-Bild gespeichert: %s", out_path.name)
    return out_path


def available() -> bool:
    """True, wenn Client + Token nutzbar sind."""
    try:
        _get_client()
        return True
    except HuggingFaceUnavailable:
        return False
