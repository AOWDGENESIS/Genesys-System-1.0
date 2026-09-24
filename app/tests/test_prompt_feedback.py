"""Tests: prompt_feedback.py (10 Kategorien, Schwellwert-Logik, Persistenz)."""

from __future__ import annotations

import pytest

import prompt_feedback as pf


def test_ten_categories() -> None:
    assert len(pf.PROBLEM_CATEGORIES) == 10
    assert set(pf.PROBLEM_CATEGORIES) == {
        "missing_foot", "text_in_image", "wrong_text", "bad_anatomy",
        "wrong_character", "too_dark", "blurry", "bad_background",
        "wrong_style", "too_complex"}


def test_every_category_has_fix() -> None:
    assert set(pf.AUTO_FIXES) == set(pf.PROBLEM_CATEGORIES)


def test_documented_fix_example() -> None:
    assert pf.AUTO_FIXES["missing_foot"] == \
        "both feet clearly visible, full body shot"


def test_add_report(tmp_path) -> None:
    store = pf.FeedbackStore(tmp_path / "fb.json")
    store.add_report(["missing_foot", "too_dark"], rating=2, prompt="p")
    assert store.problem_counts()["missing_foot"] == 1
    assert store.problem_counts()["too_dark"] == 1
    assert len(store.reports) == 1


def test_threshold_activates_fix(tmp_path) -> None:
    store = pf.FeedbackStore(tmp_path / "fb.json")
    store.add_report(["missing_foot"], rating=2)
    assert store.active_fixes() == []          # 1x noch nicht
    store.add_report(["missing_foot"], rating=3)
    assert pf.AUTO_FIXES["missing_foot"] in store.active_fixes()  # 2x aktiv


def test_invalid_inputs(tmp_path) -> None:
    store = pf.FeedbackStore(tmp_path / "fb.json")
    with pytest.raises(ValueError):
        store.add_report(["gibtsnicht"])
    with pytest.raises(ValueError):
        store.add_report(["blurry"], rating=9)


def test_enhance_prompt(tmp_path) -> None:
    store = pf.FeedbackStore(tmp_path / "fb.json")
    store.add_report(["text_in_image"], rating=1)
    store.add_report(["text_in_image"], rating=1)
    result = pf.enhance_prompt("a cute penguin", store)
    assert "no text" in result
    assert result.startswith("a cute penguin")


def test_enhance_prompt_no_fixes(tmp_path) -> None:
    store = pf.FeedbackStore(tmp_path / "fb.json")
    assert pf.enhance_prompt("a cute penguin", store) == "a cute penguin"


def test_persistence(tmp_path) -> None:
    p = tmp_path / "fb.json"
    store = pf.FeedbackStore(p)
    store.add_report(["blurry"], rating=2)
    store2 = pf.FeedbackStore(p)
    assert store2.problem_counts()["blurry"] == 1


def test_corrupt_store_starts_empty(tmp_path) -> None:
    p = tmp_path / "fb.json"
    p.write_text("{{{", encoding="utf-8")
    store = pf.FeedbackStore(p)
    assert store.reports == []


def test_analyze_without_backend(tmp_path, monkeypatch) -> None:
    # ohne gemini-SDK/Key: leere Antwort, kein Crash
    from pathlib import Path
    monkeypatch.setattr(pf, "_analyze_openai", lambda *_: "")
    result = pf.analyze_with_ai(Path("gibts/nicht.png"), provider="openai")
    assert isinstance(result, str)
