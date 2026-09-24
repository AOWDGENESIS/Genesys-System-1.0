"""Tests: mockup_engine.py (4 Farben, 1200x1400, Branding, Set)."""

from __future__ import annotations

import pytest
from PIL import Image

import mockup_engine


@pytest.fixture()
def design() -> Image.Image:
    return Image.new("RGB", (800, 800), (220, 30, 90))


def test_four_colors() -> None:
    assert set(mockup_engine.SHIRT_COLORS) == {"black", "white", "navy", "gray"}


def test_german_names() -> None:
    assert mockup_engine.SHIRT_NAMES["black"] == "Schwarz"
    assert len(mockup_engine.SHIRT_NAMES) == 4


@pytest.mark.parametrize("color", ["black", "white", "navy", "gray"])
def test_mockup_size_and_mode(design, color) -> None:
    img = mockup_engine.create_mockup(design, color)
    assert img.size == (1200, 1400)  # Spezifikation
    assert img.mode == "RGB"


def test_mockup_changes_with_color(design) -> None:
    a = mockup_engine.create_mockup(design, "black")
    b = mockup_engine.create_mockup(design, "white")
    assert a.tobytes() != b.tobytes()


def test_mockup_save(tmp_path, design) -> None:
    out = tmp_path / "mock.png"
    mockup_engine.create_mockup(design, "navy", out)
    assert out.exists()
    assert Image.open(out).size == (1200, 1400)


def test_mockup_set(tmp_storage, design) -> None:
    import config
    paths = mockup_engine.create_mockup_set(design, prefix="test")
    assert len(paths) == 4
    assert all(p.parent == config.MOCKUPS_DIR for p in paths)


def test_invalid_color_raises(design) -> None:
    with pytest.raises(ValueError):
        mockup_engine.create_mockup(design, "pink")


def test_wide_design_no_crash() -> None:
    wide = Image.new("RGB", (2400, 1000), (1, 2, 3))
    img = mockup_engine.create_mockup(wide, "gray")
    assert img.size == (1200, 1400)
