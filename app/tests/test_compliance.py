"""Tests: compliance_engine.py + compliance_rules.yaml (9 Kategorien, 141+ Begriffe)."""

from __future__ import annotations

import pytest

from compliance_engine import (
    ComplianceEngine,
    levenshtein,
    normalize,
    similarity,
)


@pytest.fixture(scope="module")
def engine() -> ComplianceEngine:
    return ComplianceEngine()


# ---------------------------------------------------------------- Laden
def test_schema_and_categories(engine) -> None:
    stats = engine.stats()
    assert stats["schema"] == "PRUEFSYSTEM_SCHEMA_V1.0"
    assert stats["categories"] == 9


def test_term_count_at_least_spec(engine) -> None:
    # Spezifikation: 141 geschützte Begriffe
    assert engine.term_count() >= 141, engine.term_count()


def test_check_order_sequence(engine) -> None:
    orders = [c.check_order for c in engine.categories]
    assert orders == sorted(orders)
    assert [c.id for c in engine.categories][:3] == [
        "extremism", "hate_symbols", "sovereign"]


def test_no_duplicates_within_category(engine) -> None:
    for cat in engine.categories:
        assert len(cat.terms) == len(set(cat.terms)), cat.id


# ---------------------------------------------------------------- Blocking
@pytest.mark.parametrize("text,category", [
    ("Nike Running Club", "brands"),
    ("Adidas Style Shirt", "brands"),
    ("Coca Cola Lover", "brands"),
    ("Mickey Mouse Fan", "characters"),
    ("Harry Potter Fan", "characters"),
    ("Star Wars Nerd", "copyright"),
    ("Hakenkreuz Design", "hate_symbols"),
    ("Swastika Print", "hate_symbols"),
    ("Nazi文字 Text", "extremism"),
    ("White Power Shirt", "extremism"),
])
def test_blocked_texts(engine, text, category) -> None:
    result = engine.check_text(text)
    assert result.blocked, text
    assert any(f.category == category for f in result.findings), (text, result.findings)


@pytest.mark.parametrize("text", [
    "But First Coffee",
    "Montag Sollte Verboten Sein",
    "Cat Mom Life",
    "Pizza Is My Soul Mate",
    "Eat Sleep Code Repeat",
    "Zeichen setzen jeden Tag",
])
def test_safe_texts(engine, text) -> None:
    result = engine.check_text(text)
    assert result.ok, (text, result.summary())


# ---------------------------------------------------------------- Whitelist
def test_whitelist_apple_pie(engine) -> None:
    result = engine.check_text("Apple Pie Lover")
    assert not result.blocked
    assert result.ok  # auch keine Warnung


def test_apple_brand_alone_blocks(engine) -> None:
    assert engine.check_text("Apple Shirt").blocked


def test_whitelist_rainforest(engine) -> None:
    result = engine.check_text("Amazon Rainforest Trip")
    assert result.ok


# ---------------------------------------------------------------- Ähnlichkeit
def test_levenshtein_basics() -> None:
    assert levenshtein("nike", "nike") == 0
    assert levenshtein("nike", "nikke") == 1
    assert similarity("adidass", "adidas") == pytest.approx(1 - 1 / 7, abs=0.01)


def test_similar_variant_flags(engine) -> None:
    result = engine.check_text("Adidass Laufschuh")  # Tippfehler
    assert result.blocked
    assert any(f.via == "similar" and f.term == "adidas"
               for f in result.findings)


def test_short_terms_no_typo_false_positives(engine) -> None:
    # Kurze Marken (nike, yoda, elsa, lego) dürfen KEINE Tippfehler-Alarme
    # auf ganz anderen Wörtern auslösen
    for text in ("I Like Coffee", "Yoga Lover Shirt", "Or Else Design",
                 "Legion Of Heroes Print"):
        assert engine.check_text(text).ok, text


def test_fuzzy_word_not_flagged(engine) -> None:
    # "nichts" ist kein "nike" (Ähnlichkeit zu gering)
    result = engine.check_text("Nichts Ist Umsonst")
    assert result.ok


# ---------------------------------------------------------------- Severity
def test_warn_categories_do_not_block(engine) -> None:
    result = engine.check_text("FBI Agent Design")
    assert not result.blocked
    assert result.warnings
    assert not result.ok


# ---------------------------------------------------------------- Normalize
def test_normalize_folds_umlaute() -> None:
    assert normalize("HÄKENKREUZ äöü ß") == "hakenkreuz aou ss"


def test_empty_text_ok(engine) -> None:
    assert engine.check_text("").ok
    assert engine.check_text("   ").ok


def test_batch(engine) -> None:
    results = engine.check_batch(["Nike", "Coffee", "Puma"])
    assert len(results) == 3
    assert sum(1 for r in results.values() if r.blocked) == 2


# ---------------------------------------------------------------- Fehlerfälle
def test_missing_rules_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        ComplianceEngine(tmp_path / "gibtsnicht.yaml")


def test_invalid_yaml(tmp_path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("categories: []", encoding="utf-8")
    with pytest.raises(ValueError):
        ComplianceEngine(bad)
