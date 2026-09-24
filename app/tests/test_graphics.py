"""Tests: graphics_engine.py (9 Templates, 10 Paletten, Determinismus)."""

from __future__ import annotations

import io

import pytest
from PIL import Image

import graphics_engine as ge


def test_nine_templates() -> None:
    assert len(ge.TEMPLATES) == 9
    assert set(ge.TEMPLATES) == {
        "bold_impact", "vintage_retro", "neon_glow", "minimalist_pro",
        "split_dynamic", "quote_premium", "grunge_street", "bold_color",
        "sticker_pop"}


def test_ten_palettes() -> None:
    assert len(ge.PALETTES) == 10
    expected = {"midnight", "crimson", "ocean", "forest", "golden", "purple",
                "rose", "arctic", "sand", "volt"}
    assert set(ge.PALETTES) == expected


@pytest.mark.parametrize("template", ge.TEMPLATES)
def test_render_all_templates(template) -> None:
    img = ge.render_template(template, "Test Design", "midnight", 500, seed=1)
    assert img.size == (500, 500)
    assert img.mode == "RGB"


@pytest.mark.parametrize("palette", ge.PALETTES)
def test_render_all_palettes(palette) -> None:
    img = ge.render_template("bold_impact", "Test", palette, 400, seed=2)
    assert img.size == (400, 400)


def test_multiline_render() -> None:
    img = ge.render_template("bold_impact",
                             "Dies Ist Ein Sehr Langer Mehrwortiger Spruch",
                             "ocean", 500, seed=3)
    assert img.size == (500, 500)


def test_deterministic_with_seed() -> None:
    a = ge.render_template("grunge_street", "Deterministisch", "volt", 400, seed=9)
    b = ge.render_template("grunge_street", "Deterministisch", "volt", 400, seed=9)
    assert a.tobytes() == b.tobytes()


def test_invalid_template_raises() -> None:
    with pytest.raises(ValueError):
        ge.render_template("unbekannt", "Text")


def test_invalid_palette_raises() -> None:
    with pytest.raises(ValueError):
        ge.render_template("bold_impact", "Text", "lila")


def test_png_roundtrip() -> None:
    img = ge.render_template("neon_glow", "Neon Test", "purple", 400, seed=4)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    reloaded = Image.open(buf)
    assert reloaded.size == (400, 400)
