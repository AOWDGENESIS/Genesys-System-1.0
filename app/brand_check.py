"""Bequemer Wrapper um die Compliance-Engine (Abwärtskompatibel zu V1).

Nutzung:
    from brand_check import is_safe, check
    ok = is_safe("But First Coffee")            # True
    result = check("Nike Air Max Style")        # ComplianceResult
"""

from __future__ import annotations

from compliance_engine import ComplianceEngine, ComplianceResult, default_engine


def check(text: str, engine: ComplianceEngine | None = None) -> ComplianceResult:
    """Prüft einen Text und liefert das vollständige Ergebnis."""
    return (engine or default_engine()).check_text(text)


def is_safe(text: str, engine: ComplianceEngine | None = None) -> bool:
    """True, wenn der Text keine blockierenden Verstöße enthält."""
    return check(text, engine).ok


def is_blocked(text: str, engine: ComplianceEngine | None = None) -> bool:
    """True, wenn der Text definitiv blockiert werden muss."""
    return check(text, engine).blocked
