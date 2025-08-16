"""
wKrQ - Weak Kleene logic with restricted quantification.

A three-valued logic system with restricted quantifiers for first-order reasoning.
Based on Ferguson (2021) semantics with tableau-based theorem proving.
"""

from .acrq_parser import SyntaxMode, parse_acrq_formula
from .acrq_tableau import ACrQTableau
from .api import Inference, check_inference
from .formula import (
    BilateralPredicateFormula,
    Constant,
    Formula,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Term,
    Variable,
)
from .parser import parse, parse_inference
from .semantics import (
    FALSE,
    TRUE,
    UNDEFINED,
    BilateralTruthValue,
    TruthValue,
    WeakKleeneSemantics,
)
from .signs import Sign, SignedFormula, e, f, m, n, t
from .tableau import Tableau, TableauResult, WKrQTableau, entails, solve, valid

__version__ = "3.1.2"

__all__ = [
    # Core types
    "Formula",
    "PropositionalAtom",
    "PredicateFormula",
    "BilateralPredicateFormula",
    "Variable",
    "Constant",
    "Term",
    "RestrictedExistentialFormula",
    "RestrictedUniversalFormula",
    # Semantics
    "WeakKleeneSemantics",
    "TruthValue",
    "BilateralTruthValue",
    "TRUE",
    "FALSE",
    "UNDEFINED",
    # Signs
    "Sign",
    "SignedFormula",
    "t",
    "f",
    "e",
    "m",
    "n",
    # Tableau
    "Tableau",
    "WKrQTableau",
    "ACrQTableau",
    "TableauResult",
    # Main functions
    "solve",
    "valid",
    "entails",
    "parse",
    "parse_inference",
    "check_inference",
    "Inference",
    # ACrQ parser (minimal)
    "parse_acrq_formula",
    "SyntaxMode",
    # LLM Integration (optional)
    "create_llm_tableau_evaluator",
    "create_openai_evaluator",
    "create_anthropic_evaluator",
    "create_google_evaluator",
    "create_local_evaluator",
]

# Conditional imports for LLM integration
try:
    from .llm_integration import (
        create_anthropic_evaluator,
        create_google_evaluator,
        create_llm_tableau_evaluator,
        create_local_evaluator,
        create_openai_evaluator,
    )
except ImportError:
    # LLM integration not available without bilateral-truth
    # Remove from __all__ if not available
    __all__ = [item for item in __all__ if not item.startswith("create_")]
