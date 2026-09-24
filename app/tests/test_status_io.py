"""Tests: status_io.py (CSV-Tracking, atomar, Update, Pending)."""

from __future__ import annotations

import csv

from status_io import append_status, get_entry, mark_uploaded, pending_designs, read_status


def test_append_and_read(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="d1", kind="text", status="generated",
                  text="Hallo", path=tmp_path / "d1.png", csv_path=csv_path)
    rows = read_status(csv_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "d1"
    assert rows[0]["status"] == "generated"


def test_update_existing(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="d1", kind="text", text="A", csv_path=csv_path)
    append_status(name="d1", kind="text", status="uploaded",
                  text="A", csv_path=csv_path)
    rows = read_status(csv_path)
    assert len(rows) == 1  # kein Duplikat
    assert rows[0]["status"] == "uploaded"
    assert rows[0]["uploaded"]


def test_header_written(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="d1", kind="text", text="A", csv_path=csv_path)
    with open(csv_path, encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    assert header[0] == "name"


def test_mark_uploaded(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="d1", kind="text", text="A", csv_path=csv_path)
    assert mark_uploaded("d1", csv_path)
    assert not mark_uploaded("unbekannt", csv_path)
    assert read_status(csv_path)[0]["status"] == "uploaded"


def test_pending(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="a", kind="text", text="1", csv_path=csv_path)
    append_status(name="b", kind="text", text="2", csv_path=csv_path)
    mark_uploaded("a", csv_path)
    pending = pending_designs(csv_path)
    assert [r["name"] for r in pending] == ["b"]


def test_get_entry(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="x", kind="scene", text="S", csv_path=csv_path)
    assert get_entry("x", csv_path) is not None
    assert get_entry("y", csv_path) is None


def test_read_missing_file_returns_empty(tmp_path) -> None:
    assert read_status(tmp_path / "gibtsnicht.csv") == []


def test_comma_text_survives(tmp_path) -> None:
    csv_path = tmp_path / "status.csv"
    append_status(name="d1", kind="text", text="Komma, Satz, Mit", csv_path=csv_path)
    assert read_status(csv_path)[0]["text"] == "Komma, Satz, Mit"
