"""Scene-Generator: Orchestrierung für Batch-Erzeugung von Szenen-Designs.

Arbeitsweise:
  1. SceneSpec bauen (GUI oder zufällig)
  2. Compliance-Prüfung des Spruchs
  3. render_scene() aus scene_engine
  4. Speichern nach GENESIS_STORAGE/designs + status.csv aktualisieren
"""

from __future__ import annotations

import logging
import random
from dataclasses import asdict
from pathlib import Path

from PIL import Image

import config
import scene_engine
from scene_engine import SceneSpec
from status_io import append_status

logger = logging.getLogger("genesis.scene_generator")


def generate_scene(
    spec: SceneSpec,
    out_dir: Path | None = None,
    size: int = 2000,
    check_compliance: bool = True,
) -> Path:
    """Erzeugt eine einzelne Szene und speichert sie. Gibt Pfad zurück."""
    out_dir = out_dir or config.DESIGNS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    text = spec.text
    if text is None:
        text = scene_engine.speech_text(spec.figure, spec.obj, spec.lang)
        spec = SceneSpec(**{**asdict(spec), "text": text})

    if check_compliance and text:
        from compliance_engine import default_engine
        result = default_engine().check_text(text)
        if result.blocked:
            raise ValueError(f"Spruch blockiert ({result.findings[0].term}): {text!r}")
        if result.warnings:
            logger.warning("Compliance-Warnung für Szene %r/%r: %s",
                           spec.figure, spec.obj, result.summary())

    img = scene_engine.render_scene(spec, size)
    name = f"scene_{spec.figure}" + (f"_{spec.obj}" if spec.obj else "") + \
           f"_{random.randint(1000, 9999)}"
    path = out_dir / f"{name}.png"
    img.save(path, "PNG", optimize=True)
    append_status(name=name, kind="scene", status="generated",
                  text=text, path=path)
    logger.info("Szene erzeugt: %s", path.name)
    return path


def generate_random_scenes(
    count: int = 1,
    lang: str = "de",
    out_dir: Path | None = None,
    size: int = 2000,
    seed: int | None = None,
) -> list[Path]:
    """Erzeugt count zufällige Szenen (seed => reproduzierbar)."""
    rng = random.Random(seed)
    paths: list[Path] = []
    for _ in range(count):
        spec = scene_engine.random_scene_spec(rng, lang)
        paths.append(generate_scene(spec, out_dir, size))
    return paths


def preview_scenes(count: int = 8, size: int = 400, lang: str = "de",
                   seed: int | None = None) -> list[Image.Image]:
    """Erzeugt kleine Vorschau-Bilder ohne Speichern (für GUI)."""
    rng = random.Random(seed)
    previews = []
    for _ in range(count):
        spec = scene_engine.random_scene_spec(rng, lang)
        previews.append(scene_engine.render_scene(spec, size))
    return previews
