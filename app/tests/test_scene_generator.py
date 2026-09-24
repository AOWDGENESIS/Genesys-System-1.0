"""Tests: scene_generator.py + generator.py (Dateien, Status, Compliance)."""

from __future__ import annotations

import csv

import pytest
from PIL import Image

import generator
import scene_generator
from scene_engine import SceneSpec


# ---------------------------------------------------------------- Generator
def test_generate_design_creates_files(tmp_storage) -> None:
    path = generator.generate_design("Test Spruch Design", size=600, seed=5)
    assert path.exists()
    assert path.parent == tmp_storage / "designs"
    img = Image.open(path)
    assert img.size == (600, 600)
    # Metadaten
    meta = tmp_storage / "upload_ready" / f"{path.stem}.txt"
    assert meta.exists()
    assert "text: Test Spruch Design" in meta.read_text(encoding="utf-8")


def test_generate_design_blocked_text(tmp_storage) -> None:
    with pytest.raises(ValueError, match="blockiert"):
        generator.generate_design("Nike Is My Style", size=300)


def test_generate_design_check_can_be_disabled(tmp_storage) -> None:
    path = generator.generate_design("Nike Is My Style", size=300,
                                     check_compliance=False)
    assert path.exists()


def test_batch_from_keyword(tmp_storage) -> None:
    paths = generator.generate_batch(lang="en", keyword="coffee", count=3,
                                     seed=1)
    assert len(paths) == 3
    for p in paths:
        assert p.exists()


def test_batch_free_texts(tmp_storage) -> None:
    paths = generator.generate_batch(free_texts=["Eins", "Zwei"], count=2)
    assert len(paths) == 2


def test_batch_unknown_keyword(tmp_storage) -> None:
    with pytest.raises(ValueError):
        generator.generate_batch(lang="de", keyword="gibtsnicht")


def test_status_csv_written(tmp_storage) -> None:
    import config
    path = generator.generate_design("Status Test", size=300, seed=9)
    assert config.STATUS_CSV.exists()
    with open(config.STATUS_CSV, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["name"] == path.stem
    assert rows[0]["status"] == "generated"
    assert rows[0]["text"] == "Status Test"


def test_preview_no_files(tmp_storage) -> None:
    img = generator.preview("Preview Text", "bold_impact", "midnight", 300)
    assert img.size == (300, 300)
    assert not (tmp_storage / "designs").exists() or \
        not list((tmp_storage / "designs").glob("*.png"))


# ---------------------------------------------------------------- Szenen
def test_generate_scene_writes_status(tmp_storage) -> None:
    from status_io import read_status
    spec = SceneSpec(figure="pinguin", obj="eis", background="sky")
    path = scene_generator.generate_scene(spec, size=500)
    assert path.exists()
    rows = read_status()
    assert rows[0]["kind"] == "scene"
    assert rows[0]["name"] == path.stem


def test_generate_scene_blocked_text(tmp_storage) -> None:
    spec = SceneSpec(figure="katze", text="Nike Forever")
    with pytest.raises(ValueError):
        scene_generator.generate_scene(spec, size=300)


def test_random_scenes(tmp_storage) -> None:
    paths = scene_generator.generate_random_scenes(count=2, seed=4, size=400)
    assert len(paths) == 2


def test_preview_scenes_no_files(tmp_storage) -> None:
    previews = scene_generator.preview_scenes(count=2, size=300, seed=1)
    assert len(previews) == 2
    assert all(p.size == (300, 300) for p in previews)
