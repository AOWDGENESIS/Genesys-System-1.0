"""Tests: text_layout_engine.py (8 Layouts, no_text, Fehlerfälle)."""

from __future__ import annotations

import pytest
from PIL import Image

import text_layout_engine as tle


@pytest.fixture()
def base() -> Image.Image:
    return Image.new("RGB", (500, 500), (120, 160, 200))


def test_eight_layouts() -> None:
    assert tle.TEXT_LAYOUTS == (
        "speech_bubble", "thought_bubble", "banner_top", "banner_bottom",
        "stamp", "free_top", "free_bottom", "no_text")


@pytest.mark.parametrize("layout", tle.TEXT_LAYOUTS)
def test_all_layouts_render(base, layout) -> None:
    out = tle.draw_text_layout(base, layout, "Test Text", style="bold")
    assert out.size == (500, 500)


def test_no_text_returns_same_pixels(base) -> None:
    out = tle.draw_text_layout(base, "no_text", "Sollte nicht erscheinen")
    assert out.tobytes() == base.convert("RGB").tobytes()


def test_layout_changes_pixels(base) -> None:
    out = tle.draw_text_layout(base, "free_top", "Oben steht was")
    assert out.tobytes() != base.convert("RGB").tobytes()


def test_empty_text_no_crash(base) -> None:
    out = tle.draw_text_layout(base, "speech_bubble", "   ")
    assert out.size == (500, 500)


def test_invalid_layout_raises(base) -> None:
    with pytest.raises(ValueError):
        tle.draw_text_layout(base, "schräg", "Text")


def test_original_not_modified(base) -> None:
    before = base.tobytes()
    tle.draw_text_layout(base, "stamp", "Stempel")
    assert base.tobytes() == before
