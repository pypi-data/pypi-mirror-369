"""
Meta-sign expansion rules for atomic formulas.

Ferguson's tableau system requires that m and n signs be expanded
even for atomic formulas:
- m:p branches to (t:p) | (f:p)
- n:p branches to (f:p) | (e:p)

These are critical for the tableau to work correctly.
"""

from typing import Optional

from .formula import CompoundFormula
from .signs import SignedFormula, e, f, m, n, t
from .wkrq_rules import FergusonRule


def get_meta_sign_rule(signed_formula: SignedFormula) -> Optional[FergusonRule]:
    """Get meta-sign expansion rule for atomic formulas.

    Meta-signs m and n are branching instructions that must be expanded
    even for atomic formulas.
    """
    sign = signed_formula.sign
    formula = signed_formula.formula

    # Only apply to atomic formulas (compound formulas have their own rules)
    if isinstance(formula, CompoundFormula):
        return None

    if sign == m:
        # m:φ branches to (t:φ) | (f:φ)
        return FergusonRule(
            name="m-atomic",
            premise=signed_formula,
            conclusions=[[SignedFormula(t, formula)], [SignedFormula(f, formula)]],
        )
    elif sign == n:
        # n:φ branches to (f:φ) | (e:φ)
        return FergusonRule(
            name="n-atomic",
            premise=signed_formula,
            conclusions=[[SignedFormula(f, formula)], [SignedFormula(e, formula)]],
        )

    # No rule for t, f, e on atomic formulas
    return None
