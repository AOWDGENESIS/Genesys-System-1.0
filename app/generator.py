"""Design-Generator: Text-Designs aus Keywords/freien Texten.

Workflow:
  1. Text holen (Text-Datenbank oder Freitext)
  2. Compliance-Prüfung (blockierte Texte werden verworfen)
  3. Template + Palette + Hintergrund wählen
  4. graphics_engine.render_template()
  5. Speichern + status.csv + Metadaten (upload_ready)

Unterstützt 9 Vorlagen (siehe graphics_engine.TEMPLATES).
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

from PIL import Image

import background_engine
import config
import graphics_engine
import text_database
from status_io import append_status

logger = logging.getLogger("genesis.generator")

TEMPLATES = graphics_engine.TEMPLATES
PALETTES = list(graphics_engine.PALETTES)


def _metadata_tags(text: str) -> list[str]:
    """Ableitbare Tags aus dem Text (kleingeschrieben, ohne Sonderzeichen)."""
    words = [w.strip(".,!?:;").lower() for w in text.split()]
    return [w for w in words if len(w) >= 4][:6]


def generate_design(
    text: str, *,
    template: str | None = None,
    palette: str | None = None,
    out_dir: Path | None = None,
    size: int = 2000,
    seed: int | None = None,
    check_compliance: bool = True,
) -> Path:
    """Erzeugt ein einzelnes Text-Design und speichert es als PNG.

    Raises ValueError bei Compliance-Block.
    """
    rng = random.Random(seed)
    template = template or rng.choice(TEMPLATES)
    palette = palette or rng.choice(PALETTES)

    if check_compliance:
        from compliance_engine import default_engine
        result = default_engine().check_text(text)
        if result.blocked:
            raise ValueError(
                f"Text blockiert durch Regelwerk ({result.findings[0].category_de}): {text!r}"
            )

    img = graphics_engine.render_template(template, text, palette, size, seed=rng.randint(0, 2**31))
    out_dir = out_dir or config.DESIGNS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = "".join(c if c.isalnum() else "_" for c in text)[:40].strip("_") or "design"
    name = f"{safe}_{rng.randint(1000, 9999)}"
    path = out_dir / f"{name}.png"
    img.save(path, "PNG", optimize=True)

    append_status(name=name, kind="text", status="generated", text=text, path=path)
    _write_metadata(name, text, template, palette,
                    tags=_metadata_tags(text), out_dir=out_dir)
    logger.info("Design erzeugt: %s (Template %s, Palette %s)", path.name, template, palette)
    return path


def generate_batch(
    lang: str = "de", *,
    keyword: str | None = None,
    free_texts: list[str] | None = None,
    count: int = 1,
    template: str | None = None,
    out_dir: Path | None = None,
    size: int = 2000,
    seed: int | None = None,
) -> list[Path]:
    """Erzeugt count Designs aus Keyword-Texten oder Freitexten."""
    rng = random.Random(seed)
    texts: list[str]
    if free_texts:
        texts = free_texts
    else:
        pool = text_database.texts_for(lang, keyword or rng.choice(
            text_database.keywords(lang)))
        if not pool:
            raise ValueError(f"Keine Texte für keyword={keyword!r} lang={lang!r}")
        texts = [rng.choice(pool) for _ in range(count)]

    paths: list[Path] = []
    skipped = 0
    for text in texts:
        try:
            paths.append(generate_design(
                text=text, template=template, out_dir=out_dir,
                size=size, seed=rng.randint(0, 2**31),
            ))
        except ValueError as exc:
            skipped += 1
            logger.warning("Design übersprungen: %s", exc)
    if skipped:
        logger.info("Batch fertig: %d erzeugt, %d übersprungen (Compliance).", len(paths), skipped)
    return paths


def preview(text: str, template: str = "bold_impact", palette: str = "midnight",
            size: int = 400, seed: int | None = None) -> Image.Image:
    """Kleine Vorschau ohne Speichern (für GUI)."""
    return graphics_engine.render_template(template, text, palette, size, seed=seed)


def random_combination(rng: random.Random | None = None) -> dict[str, str]:
    """Zufällige Template/Palette/Hintergrund-Kombination (für GUI-Vorschläge)."""
    rng = rng or random
    return {
        "template": rng.choice(TEMPLATES),
        "palette": rng.choice(PALETTES),
        "background": rng.choice(background_engine.BACKGROUNDS),
    }


def _write_metadata(name: str, text: str, template: str, palette: str, *,
                    tags: list[str], out_dir: Path) -> None:
    """Schreibt Metadaten-TXT nach GENESIS_STORAGE/upload_ready."""
    try:
        meta_dir = config.UPLOAD_READY_DIR
        meta_dir.mkdir(parents=True, exist_ok=True)
        content = (
            f"name: {name}\ntext: {text}\ntemplate: {template}\n"
            f"palette: {palette}\ntags: {', '.join(tags)}\n"
            f"size: {config.DEFAULT_SIZE}x{config.DEFAULT_SIZE}\n"
        )
        (meta_dir / f"{name}.txt").write_text(content, encoding="utf-8")
    except OSError as exc:
        logger.warning("Metadaten konnten nicht geschrieben werden: %s", exc)
