"""Hybrid-Scene-Engine: KI-Bild + lokaler Text + Hintergrund.

Workflow:
  1. KI generiert Illustration OHNE Text (FLUX/DALL-E/Imagen/…)
  2. GENESIS wählt Hintergrund
  3. Illustration wird auf den Hintergrund gelegt (mit Maske/Alpha)
  4. GENESIS fügt Text mit perfekter Typografie ein
  5. 1-4 Varianten zur Auswahl

Falls kein KI-Backend verfügbar ist, erzeugt die Engine eine lokale
Fallback-Illustration (icon_engine) — der Workflow bleibt testbar.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass

from PIL import Image

import background_engine
import icon_engine
import prompt_feedback
import scene_engine
import text_layout_engine

logger = logging.getLogger("genesis.hybrid")

MAX_VARIANTS = 4

AI_PROVIDERS = ("puter", "huggingface", "gemini")


@dataclass
class HybridSpec:
    figure: str                      # z.B. "pinguin" (für Icon-Fallback + Prompt)
    text: str = ""
    lang: str = "de"
    layout: str = "free_bottom"
    style: str = "bold"
    background: str | None = None    # None = automatisch
    pattern: str | None = None
    variants: int = 2
    seed: int | None = None


def build_prompt(figure: str, obj: str | None = None) -> str:
    """KI-Prompt inkl. Anatomie-Regeln + gelernten Feedback-Fixes."""
    base = scene_engine.build_ai_prompt(figure, obj)
    return prompt_feedback.enhance_prompt(base)


def compose_variant(ai_image: Image.Image, spec: HybridSpec,
                    background: str, pattern: str | None,
                    rng: random.Random) -> Image.Image:
    """Eine Variante zusammensetzen: Hintergrund + KI-Illustration + Text."""
    size = max(ai_image.size)
    bg = background_engine.create_background(background, size, pattern, rng)

    # Illustration quadratisch skalieren und einpassen
    img = ai_image.convert("RGBA")
    scale = (size * 0.72) / max(img.size)
    img = img.resize((max(1, int(img.width * scale)),
                      max(1, int(img.height * scale))), Image.LANCZOS)
    # Weiche Schattenkante: leichte weiße Kontur via MaxFilter ist teuer —
    # einfache Version: direkt zentriert einfügen
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(img, ((size - img.width) // 2,
                                 (size - img.height) // 2))
    return text_layout_engine.draw_text_layout(
        canvas.convert("RGB"), spec.layout, spec.text, style=spec.style,
        accent_color=(15, 15, 15),
    )


def generate_hybrid(
    spec: HybridSpec,
    ai_image: Image.Image | None = None,
    rng: random.Random | None = None,
) -> list[Image.Image]:
    """Erzeugt 1-4 Varianten. ai_image=None → lokaler Icon-Fallback."""
    rng = rng or random.Random(spec.seed)
    if not 1 <= spec.variants <= MAX_VARIANTS:
        raise ValueError(f"variants muss 1..{MAX_VARIANTS} sein")

    if ai_image is None:
        logger.info("Kein KI-Bild gegeben — nutze lokalen Icon-Fallback für %r.", spec.figure)
        ai_image = _fallback_illustration(spec.figure, rng)

    backgrounds = (
        [spec.background] if spec.background
        else rng.sample(list(background_engine.BACKGROUNDS), spec.variants)
    )
    variants: list[Image.Image] = []
    for i in range(spec.variants):
        bg = backgrounds[i % len(backgrounds)]
        pattern = spec.pattern if spec.pattern else background_engine.random_pattern(rng)
        variants.append(compose_variant(ai_image, spec, bg, pattern, rng))
    return variants


def _fallback_illustration(figure: str, rng: random.Random) -> Image.Image:
    """Lokale Illustration: Icon auf transparenter 2000er Fläche."""
    if not icon_engine.is_known(figure):
        raise ValueError(f"Unbekannte Figur {figure!r} für Fallback-Illustration")
    canvas = Image.new("RGBA", (2000, 2000), (255, 255, 255, 0))
    icon = icon_engine.draw_icon(figure, 1600)
    canvas.alpha_composite(icon, (200, 200))
    return canvas
