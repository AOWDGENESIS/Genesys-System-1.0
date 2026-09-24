"""Tests: icon_engine.py (25 Figuren + 21 Objekte, Aliase, Alpha)."""

from __future__ import annotations

import pytest

import icon_engine


def test_counts_match_spec() -> None:
    assert len(icon_engine.FIGURES) == 25
    assert len(icon_engine.OBJECTS) == 21
    assert len(icon_engine.KNOWN_ICONS) == 46


def test_no_overlap_figure_object() -> None:
    # Dubletten wie eis/eiscreme sind Aliase, keine Zweit-Einträge
    assert not (set(icon_engine.FIGURES) & set(icon_engine.OBJECTS))


@pytest.mark.parametrize("name", icon_engine.FIGURES + icon_engine.OBJECTS)
def test_render_every_icon(name) -> None:
    img = icon_engine.draw_icon(name, 400)
    assert img.size == (400, 400)
    assert img.mode == "RGBA"
    # Icon muss sichtbare Pixel haben
    alpha = img.getchannel("A")
    assert alpha.getextrema()[1] > 0


@pytest.mark.parametrize("alias,target", [
    ("eiscreme", "eis"), ("coffee", "kaffee"), ("heart", "herz"),
    ("beer", "bier"), ("book", "buch"), ("phone", "handy"),
    ("guitar", "gitarre"), ("cake", "kuchen"),
])
def test_aliases_render(alias, target) -> None:
    a = icon_engine.draw_icon(alias, 300)
    b = icon_engine.draw_icon(target, 300)
    assert a.tobytes() == b.tobytes()


def test_icons_differ() -> None:
    a = icon_engine.draw_icon("pinguin", 300)
    b = icon_engine.draw_icon("katze", 300)
    assert a.tobytes() != b.tobytes()


def test_unknown_icon_raises() -> None:
    with pytest.raises(ValueError):
        icon_engine.draw_icon("drache3d")


def test_is_known() -> None:
    assert icon_engine.is_known("Pinguin")
    assert icon_engine.is_known("coffee")
    assert not icon_engine.is_known("einhorn2")


def test_icons_have_transparency() -> None:
    img = icon_engine.draw_icon("pizza", 300)
    alpha = img.getchannel("A")
    assert alpha.getextrema()[0] == 0  # transparenter Hintergrund da
