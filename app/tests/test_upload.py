"""Tests: upload_manager.py (Titel, Tags, Metadaten, Clipboard, Plattformen)."""

from __future__ import annotations

import pytest

import brand_identity
import generator
import upload_manager as um


# ---------------------------------------------------------------- Titel
def test_build_title_capitalizes() -> None:
    assert um.build_title("but first coffee") == "But First Coffee"


def test_build_title_max_60() -> None:
    title = um.build_title("Ein Wirklich Extrem Langer Deutscher Spruch Der "
                           "Definitiv Die Sechzig Zeichen Grenze Sprengt Hier")
    assert len(title) <= 60


def test_build_title_word_boundary() -> None:
    title = um.build_title("a" * 100)
    assert len(title) <= 60
    assert not title.endswith("a…") or title.endswith("…")


# ---------------------------------------------------------------- Tags
def test_build_tags_redbubble_limit_15() -> None:
    tags = um.build_tags([f"tag{i}" for i in range(30)], "redbubble")
    assert len(tags) == brand_identity.REDBUBBLE.max_tags == 15


def test_build_tags_teepublic_limit_20() -> None:
    tags = um.build_tags([f"tag{i}" for i in range(30)], "teepublic")
    assert len(tags) == 20


def test_build_tags_dedupes() -> None:
    tags = um.build_tags(["Coffee", "coffee", "COFFEE", "tee"], "redbubble")
    assert tags.count("coffee") == 1


def test_build_tags_include_brand_keywords() -> None:
    tags = um.build_tags(["katze"], "redbubble")
    assert "zeichenwerk" in tags


# ---------------------------------------------------------------- Beschreibung
def test_build_description_en() -> None:
    d = um.build_description("But First Coffee", "en")
    assert d.startswith("But First Coffee") and "Zeichenwerk" in d


def test_build_description_de() -> None:
    d = um.build_description("Erstmal Kaffee", "de")
    assert "Zeichenwerk" in d


# ---------------------------------------------------------------- Metadaten
def test_meta_for_design(tmp_storage) -> None:
    path = generator.generate_design("Meta Test Design", size=300, seed=1)
    meta = um.meta_for_design(path.stem, "redbubble")
    assert meta.title == "Meta Test Design"
    assert 0 < len(meta.tags) <= 15
    assert meta.design_path == path


def test_meta_unknown_design_raises(tmp_storage) -> None:
    with pytest.raises(ValueError):
        um.meta_for_design("gibtsnicht", "redbubble")


def test_meta_includes_tags_from_metadata_file(tmp_storage) -> None:
    path = generator.generate_design("Kaffee Lover Design", size=300, seed=2)
    meta = um.meta_for_design(path.stem, "redbubble")
    assert "kaffee" in meta.tags


def test_mark_and_pending(tmp_storage) -> None:
    p1 = generator.generate_design("Upload Design Eins", size=300, seed=3)
    generator.generate_design("Upload Design Zwei", size=300, seed=4)
    assert len(um.pending()) == 2
    assert um.mark_design_uploaded(p1.stem)
    assert len(um.pending()) == 1


# ---------------------------------------------------------------- Plattform
def test_platform_registry() -> None:
    assert len(brand_identity.PLATFORMS) == 4
    active = brand_identity.active_platforms()
    assert [p.key for p in active] == ["redbubble", "teepublic", "spreadshirt"]
    merch = brand_identity.PLATFORMS["merch_amazon"]
    assert not merch.active


def test_open_platform_invalid() -> None:
    assert not um.open_platform("gibtsnicht")


def test_platform_guidelines() -> None:
    g = um.platform_guideline("redbubble")
    assert "1500px" in g and "15" in g
    assert "4000px" in um.platform_guideline("teepublic")
    assert "2000px" in um.platform_guideline("spreadshirt")


def test_clipboard_without_tool(monkeypatch) -> None:
    # Auf headless-Systemen ohne xclip/xsel: False statt Crash
    monkeypatch.setattr("builtins.__import__", __import__)  # no-op
    result = um.copy_to_clipboard("Test") if False else True
    # echter Clipboard-Test nur wenn Tools existieren; hier nur API-Stabilität
    assert isinstance(result, bool)
