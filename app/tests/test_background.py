"""Tests: background_engine.py (15 Hintergründe + 4 Muster)."""

from __future__ import annotations

import random

import pytest

import background_engine


def test_fifteen_backgrounds() -> None:
    assert len(background_engine.BACKGROUNDS) == 15
    expected = ("pastel_warm", "pastel_cool", "pastel_green", "pastel_pink",
                "sunny", "sky", "sunset", "ocean", "forest", "night",
                "neon_dark", "vintage_warm", "clean_white", "clean_cream",
                "clean_black")
    assert expected == background_engine.BACKGROUNDS


def test_patterns_available() -> None:
    assert set(background_engine.PATTERNS) == {
        "polka_dots", "stripes_h", "stripes_v", "stars", "confetti"}


@pytest.mark.parametrize("bg", background_engine.BACKGROUNDS)
def test_render_all_backgrounds(bg) -> None:
    img = background_engine.create_background(bg, 300)
    assert img.size == (300, 300)
    assert img.mode == "RGB"


@pytest.mark.parametrize("pattern", background_engine.PATTERNS)
def test_render_all_patterns(pattern) -> None:
    img = background_engine.create_background("pastel_warm", 300, pattern)
    assert img.size == (300, 300)


def test_pattern_changes_pixels() -> None:
    plain = background_engine.create_background("clean_white", 300)
    dotted = background_engine.create_background("clean_white", 300, "polka_dots")
    assert plain.tobytes() != dotted.tobytes()


def test_deterministic_with_seed() -> None:
    a = background_engine.create_background("sunny", 300, "confetti",
                                            random.Random(1))
    b = background_engine.create_background("sunny", 300, "confetti",
                                            random.Random(1))
    assert a.tobytes() == b.tobytes()


def test_invalid_names_raise() -> None:
    with pytest.raises(ValueError):
        background_engine.create_background("regenbogen")
    with pytest.raises(ValueError):
        background_engine.create_background("sky", 300, "herzen")


def test_random_helpers() -> None:
    rng = random.Random(0)
    assert background_engine.random_background(rng) in background_engine.BACKGROUNDS
    assert background_engine.random_pattern(rng) in (
        None, *background_engine.PATTERNS)
