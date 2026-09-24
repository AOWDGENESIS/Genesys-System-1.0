"""Tests: validator.py CLI + brand_check.py Wrapper."""

from __future__ import annotations


import validator
from brand_check import check, is_blocked, is_safe


def test_cli_safe_text(capsys) -> None:
    assert validator.main(["But First Coffee"]) == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_cli_blocked_text(capsys) -> None:
    assert validator.main(["Nike Air Style"]) == 2
    out = capsys.readouterr().out
    assert "BLOCKIERT" in out


def test_cli_warning_text(capsys) -> None:
    assert validator.main(["FBI Open Up"]) == 1


def test_cli_stats(capsys) -> None:
    from compliance_engine import default_engine
    assert validator.main(["--stats"]) == 0
    out = capsys.readouterr().out
    assert "Kategorien:  9" in out
    # Spezifikation: mindestens 141 geschützte Begriffe
    assert str(default_engine().term_count()) in out
    assert default_engine().term_count() >= 141


def test_cli_batch(capsys) -> None:
    assert validator.main(["--batch"]) == 0
    out = capsys.readouterr().out
    assert "Geprüft:" in out


def test_cli_file(tmp_path, capsys) -> None:
    f = tmp_path / "texte.txt"
    f.write_text("But First Coffee\n# Kommentar\nNike Shirt\n", encoding="utf-8")
    assert validator.main(["--file", str(f)]) == 2


def test_cli_missing_file() -> None:
    assert validator.main(["--file", "/gibt/es/nicht.txt"]) == 3


def test_cli_no_input(capsys) -> None:
    assert validator.main([]) == 3


# ---------------------------------------------------------------- Wrapper
def test_brand_check_wrapper() -> None:
    assert is_safe("But First Coffee")
    assert not is_safe("Puma Style")
    assert is_blocked("Puma Style")
    assert not is_blocked("Coffee First")
    result = check("Adidas")
    assert result.blocked and result.findings
