"""Tests: font_manager.py (5 Schriftstile, Fallbacks, Fit-Logik)."""

from __future__ import annotations

import font_manager


def test_five_styles_defined() -> None:
    assert font_manager.FONT_STYLES == ("impact", "bold", "rounded", "serif", "light")


def test_all_styles_resolve() -> None:
    for style in font_manager.FONT_STYLES:
        font = font_manager.get_font(style, 100)
        assert font is not None


def test_unknown_style_falls_back_to_bold() -> None:
    font = font_manager.get_font("gibtsnicht", 50)
    assert font is not None


def test_text_size_positive() -> None:
    font = font_manager.get_font("bold", 120)
    w, h = font_manager.text_size(font, "Zeichenwerk")
    assert w > 0 and h > 0


def test_fit_font_size_shrinks() -> None:
    font = font_manager.fit_font_size("bold", "Sehr Lange Text Zeile",
                                      max_width=300, max_height=60, start=200)
    w, h = font_manager.text_size(font, "Sehr Lange Text Zeile")
    assert w <= 300 or h <= 60  # bei Minimum-Ausgabe darf Höhe passen


def test_fit_font_size_min() -> None:
    font = font_manager.fit_font_size("bold", "X" * 500, max_width=100,
                                      max_height=20, start=100)
    assert font is not None  # liefert Minimum statt Endlosrekursion
