"""Tests: sales_tracker.py (Tiers, 30-Tage-Analyse, Persistenz)."""

from __future__ import annotations

import pytest

import sales_tracker as st


@pytest.fixture()
def tracker(tmp_storage) -> st.SalesTracker:
    return st.SalesTracker(tmp_storage / "sales_data.json")


def test_tier_thresholds() -> None:
    assert st.tier_for(100, 100) == "STAR"     # 100 %
    assert st.tier_for(70, 100) == "STAR"      # >= 70 %
    assert st.tier_for(69, 100) == "GOOD"
    assert st.tier_for(35, 100) == "GOOD"      # >= 35 %
    assert st.tier_for(34, 100) == "OK"
    assert st.tier_for(10, 100) == "OK"        # >= 10 %
    assert st.tier_for(9, 100) == "WEAK"
    assert st.tier_for(0, 0) == "WEAK"


def test_add_sale(tracker) -> None:
    d = tracker.add_sale("design1", "redbubble", 2)
    assert d.total == 2
    assert d.platforms == {"redbubble": 2}
    assert len(d.history) == 1


def test_add_sale_multiple(tracker) -> None:
    tracker.add_sale("d", "redbubble", 1)
    tracker.add_sale("d", "teepublic", 3)
    d = tracker.designs["d"]
    assert d.total == 4
    assert d.platforms == {"redbubble": 1, "teepublic": 3}


def test_invalid_count(tracker) -> None:
    with pytest.raises(ValueError):
        tracker.add_sale("d", "x", 0)


def test_set_total_negative(tracker) -> None:
    with pytest.raises(ValueError):
        tracker.set_total("d", -1)


def test_tiers(tracker) -> None:
    tracker.add_sale("best", "redbubble", 10)
    tracker.add_sale("mid", "redbubble", 4)
    tracker.add_sale("low", "redbubble", 1)
    tiers = tracker.tiers()
    assert tiers == {"best": "STAR", "mid": "GOOD", "low": "OK"}


def test_30_day_analysis(tracker) -> None:
    tracker.add_sale("d1", "redbubble", 2, day="2026-09-01")
    tracker.add_sale("d1", "teepublic", 1, day="2026-09-02")
    tracker.add_sale("d2", "redbubble", 5, day="2020-01-01")  # alt → zählt nicht
    a = tracker.analyze_last_days(30)
    assert a["total"] == 3
    assert a["per_platform"]["redbubble"] == 2
    assert "d2" not in a["per_design"]


def test_report(tracker) -> None:
    tracker.add_sale("d1", "redbubble", 2)
    report = tracker.report()
    assert "VERKAUFSBERICHT" in report
    assert "d1" in report
    assert "Bestseller" in report


def test_persistence(tmp_storage) -> None:
    path = tmp_storage / "sales_data.json"
    t1 = st.SalesTracker(path)
    t1.add_sale("dauerbrenner", "redbubble", 7)
    t2 = st.SalesTracker(path)
    assert t2.designs["dauerbrenner"].total == 7
    assert t2.bestseller() == 7


def test_summary(tracker) -> None:
    tracker.add_sale("a", "redbubble", 3)
    tracker.add_sale("b", "teepublic", 1)
    s = tracker.summary()
    assert s["designs"] == 2 and s["total_sales"] == 4
    assert s["bestseller"] == "a"


def test_corrupt_file(tmp_storage) -> None:
    bad = tmp_storage / "bad.json"
    bad.write_text("{kein json", encoding="utf-8")
    t = st.SalesTracker(bad)
    assert t.designs == {}
