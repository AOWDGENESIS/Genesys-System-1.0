"""Tests: text_database.py (Keywords, Texte, Beispiele aus der Doku)."""

from __future__ import annotations

import random

import text_database as tdb


def test_languages() -> None:
    assert tdb.SUPPORTED_LANGUAGES == ("en", "de")


def test_keyword_counts_spec() -> None:
    # Spezifikation: 16 EN-Keywords, 11 DE-Keywords
    assert len(tdb.keywords("en")) == 16
    assert len(tdb.keywords("de")) == 11


def test_expected_keywords_present() -> None:
    en = tdb.keywords("en")
    for kw in ("coffee", "work", "sarcasm", "monday", "cat", "dog", "nurse",
               "gym", "dad", "mom", "coding", "pizza", "beer", "teacher",
               "firefighter", "random"):
        assert kw in en, kw
    de = tdb.keywords("de")
    for kw in ("coffee", "work", "sarcasm", "monday", "cat", "dog",
               "firefighter", "nurse", "dad", "mom", "random"):
        assert kw in de, kw


def test_texts_per_keyword_range() -> None:
    # Spezifikation: 6-18 Sprüche pro Keyword
    for lang in tdb.SUPPORTED_LANGUAGES:
        for kw in tdb.keywords(lang):
            n = len(tdb.texts_for(lang, kw))
            assert 6 <= n <= 18, f"{lang}/{kw}: {n} Texte"


def test_documentation_examples_exist() -> None:
    assert "But First Coffee" in tdb.texts_for("en", "coffee")
    assert "Error 404 Motivation Not Found" in tdb.texts_for("en", "work")
    assert "Sarcasm Is My Love Language" in tdb.texts_for("en", "sarcasm")
    assert "Monday Should Be Illegal" in tdb.texts_for("en", "monday")
    assert "Erstmal Kaffee" in tdb.texts_for("de", "coffee")
    assert "Montag Sollte Verboten Sein" in tdb.texts_for("de", "monday")
    assert "Meine Geduld Hat Gekuendigt" in tdb.texts_for("de", "sarcasm")
    assert "Retten Loeschen Bergen Schuetzen" in tdb.texts_for("de", "firefighter")


def test_random_text_deterministic() -> None:
    rng1, rng2 = random.Random(7), random.Random(7)
    assert tdb.random_text("en", rng=rng1) == tdb.random_text("en", rng=rng2)


def test_random_text_invalid() -> None:
    import pytest
    with pytest.raises(ValueError):
        tdb.random_text("fr")
    with pytest.raises(ValueError):
        tdb.random_text("en", "gibtsnicht")


def test_texts_are_compliance_safe() -> None:
    """Alle eigenen Sprüche müssen das eigene Regelwerk passieren."""
    from compliance_engine import default_engine
    engine = default_engine()
    for lang in tdb.SUPPORTED_LANGUAGES:
        for kw in tdb.keywords(lang):
            for text in tdb.texts_for(lang, kw):
                result = engine.check_text(text)
                assert not result.blocked, f"{lang}/{kw}: {text} -> {result.summary()}"
