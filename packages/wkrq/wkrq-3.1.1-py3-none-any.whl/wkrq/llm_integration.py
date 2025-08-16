"""
Seamless integration with bilateral-truth package for LLM evaluation.

This module provides automatic LLM integration for ACrQ tableau construction,
requiring only LLM provider specification from users.
"""

from typing import Any, Callable, Optional

from .formula import BilateralPredicateFormula, Formula, PredicateFormula
from .semantics import FALSE, TRUE, UNDEFINED, BilateralTruthValue

try:
    from bilateral_truth import Assertion, create_llm_evaluator, zeta_c
    from bilateral_truth.truth_values import TruthValueComponent

    BILATERAL_TRUTH_AVAILABLE = True
except ImportError:
    BILATERAL_TRUTH_AVAILABLE = False


def create_llm_tableau_evaluator(
    provider: str = "openai", model: Optional[str] = None, **kwargs: Any
) -> Optional[Callable[[Formula], Optional[BilateralTruthValue]]]:
    """
    Create an LLM evaluator for ACrQ tableau using bilateral-truth package.

    This is all users need to call - just specify the provider and model.

    Note: LLM integration is only available for ACrQ tableau, not base wKrQ,
    because ACrQ's bilateral predicates naturally handle LLM uncertainty
    (gaps) and conflicting information (gluts).

    Args:
        provider: LLM provider ('openai', 'anthropic', 'google', 'local', etc.)
        model: Model name (defaults to provider's default model)
        **kwargs: Additional provider-specific configuration

    Returns:
        Evaluator function compatible with ACrQ tableau, or None if unavailable

    Example:
        >>> from wkrq import ACrQTableau, SignedFormula, t
        >>> from wkrq.llm_integration import create_llm_tableau_evaluator
        >>>
        >>> # That's it! Just specify your LLM
        >>> evaluator = create_llm_tableau_evaluator('openai', model='gpt-4')
        >>>
        >>> # Use it with tableau
        >>> tableau = ACrQTableau(
        ...     [SignedFormula(t, parse_acrq_formula("Planet(pluto)"))],
        ...     llm_evaluator=evaluator
        ... )
        >>> result = tableau.construct()
    """
    if not BILATERAL_TRUTH_AVAILABLE:
        import warnings

        warnings.warn(
            "bilateral-truth package not installed. "
            "Install with: pip install wkrq[llm] or pip install bilateral-truth",
            ImportWarning,
            stacklevel=2,
        )
        return None

    # Create the bilateral-truth evaluator with user's specifications
    try:
        # Mock evaluator doesn't accept model parameter
        if provider == "mock":
            bt_evaluator = create_llm_evaluator("mock")
        elif model:
            bt_evaluator = create_llm_evaluator(provider, model=model, **kwargs)
        else:
            bt_evaluator = create_llm_evaluator(provider, **kwargs)
    except Exception as e:
        import warnings

        warnings.warn(
            f"Failed to create LLM evaluator: {e}", RuntimeWarning, stacklevel=2
        )
        return None

    # Cache for bilateral predicates to avoid redundant LLM calls
    cache: dict[str, BilateralTruthValue] = {}

    def tableau_evaluator(formula: Formula) -> Optional[BilateralTruthValue]:
        """
        Evaluate a formula using the bilateral-truth LLM.

        Handles:
        - Regular predicates: P(x)
        - Bilateral predicates: P*(x)
        - Caching to avoid redundant LLM calls
        - Automatic bilateral relationship management
        """
        # Only evaluate atomic formulas
        if not formula.is_atomic():
            return None

        # Get the base predicate name and whether it's negative
        if isinstance(formula, BilateralPredicateFormula):
            is_negative = formula.is_negative
            formula_str = str(formula).replace("*", "")  # Remove * for LLM query
        elif isinstance(formula, PredicateFormula):
            is_negative = False
            formula_str = str(formula)
        else:
            # Propositional atoms or other types
            # base_name = str(formula)  # Not used currently
            is_negative = False
            formula_str = str(formula)

        # Check cache first
        cache_key = formula_str
        if cache_key in cache:
            cached_value = cache[cache_key]
            # For bilateral predicates, we might need to swap components
            if is_negative:
                # For P*, swap positive and negative components
                return BilateralTruthValue(
                    positive=cached_value.negative, negative=cached_value.positive
                )
            return cached_value

        # Query LLM via bilateral-truth
        try:
            assertion = Assertion(formula_str)
            generalized_truth = zeta_c(assertion, bt_evaluator.evaluate_bilateral)

            # Convert bilateral-truth (u,v) to wKrQ BilateralTruthValue
            u_value = _convert_component(generalized_truth.u)
            v_value = _convert_component(generalized_truth.v)

            # Create bilateral truth value
            # u (verifiability) → positive evidence for P
            # v (refutability) → negative evidence for P (positive for P*)
            bilateral_value = BilateralTruthValue(positive=u_value, negative=v_value)

            # Cache the result
            cache[cache_key] = bilateral_value

            # For P*, swap the components
            if is_negative:
                return BilateralTruthValue(
                    positive=bilateral_value.negative, negative=bilateral_value.positive
                )

            return bilateral_value

        except Exception:
            # On error, return None to let tableau proceed without LLM
            return None

    return tableau_evaluator


def _convert_component(component: "TruthValueComponent") -> Any:
    """Convert bilateral-truth component to wKrQ truth value."""
    from bilateral_truth.truth_values import TruthValueComponent

    mapping = {
        TruthValueComponent.TRUE: TRUE,
        TruthValueComponent.FALSE: FALSE,
        TruthValueComponent.UNDEFINED: UNDEFINED,
    }

    return mapping.get(component, UNDEFINED)


# Convenience functions for common providers
def create_openai_evaluator(
    model: str = "gpt-4", **kwargs: Any
) -> Optional[Callable[[Formula], Optional[BilateralTruthValue]]]:
    """Create an OpenAI LLM evaluator."""
    return create_llm_tableau_evaluator("openai", model=model, **kwargs)


def create_anthropic_evaluator(
    model: str = "claude-3-opus-20240229", **kwargs: Any
) -> Optional[Callable[[Formula], Optional[BilateralTruthValue]]]:
    """Create an Anthropic Claude evaluator."""
    return create_llm_tableau_evaluator("anthropic", model=model, **kwargs)


def create_google_evaluator(
    model: str = "gemini-pro", **kwargs: Any
) -> Optional[Callable[[Formula], Optional[BilateralTruthValue]]]:
    """Create a Google Gemini evaluator."""
    return create_llm_tableau_evaluator("google", model=model, **kwargs)


def create_local_evaluator(
    model: str = "llama2", **kwargs: Any
) -> Optional[Callable[[Formula], Optional[BilateralTruthValue]]]:
    """Create a local LLM evaluator (e.g., via Ollama)."""
    return create_llm_tableau_evaluator("local", model=model, **kwargs)
