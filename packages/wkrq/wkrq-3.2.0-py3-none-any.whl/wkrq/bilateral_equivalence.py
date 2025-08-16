"""
Bilateral equivalence checking for ACrQ closure conditions.

Implements Ferguson's Lemma 5: Branches close when u:φ and v:ψ appear
with distinct signs where φ* = ψ* (bilateral equivalence).
"""

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Formula,
    PredicateFormula,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
)


def to_bilateral_form(formula: Formula) -> Formula:
    """
    Convert a formula to its bilateral form (φ*).

    This implements Ferguson's Definition 17 translation:
    - Atomic predicates P become themselves
    - Negated atomic predicates ~P become P*
    - Compound formulas are recursively transformed
    - DeMorgan rules are built into the translation

    Args:
        formula: The formula to convert

    Returns:
        The bilateral form of the formula
    """
    if isinstance(formula, BilateralPredicateFormula):
        # Already in bilateral form
        return formula

    elif isinstance(formula, PredicateFormula):
        # Regular predicate stays as is
        return formula

    elif isinstance(formula, CompoundFormula):
        if formula.connective == "~":
            # Handle negation
            sub = formula.subformulas[0]

            # ~P becomes P*
            if isinstance(sub, PredicateFormula):
                return BilateralPredicateFormula(
                    positive_name=sub.predicate_name,
                    terms=sub.terms,
                    is_negative=True,
                )

            # ~P* becomes P
            elif isinstance(sub, BilateralPredicateFormula):
                if sub.is_negative:
                    # ~P* becomes P
                    return PredicateFormula(
                        predicate_name=sub.positive_name,
                        terms=sub.terms,
                    )
                else:
                    # ~P becomes P* (shouldn't happen in well-formed)
                    return BilateralPredicateFormula(
                        positive_name=sub.positive_name,
                        terms=sub.terms,
                        is_negative=True,
                    )

            # ~~φ becomes φ*
            elif isinstance(sub, CompoundFormula) and sub.connective == "~":
                return to_bilateral_form(sub.subformulas[0])

            # ~(φ ∧ ψ) becomes (~φ)* ∨ (~ψ)* per Definition 17
            elif isinstance(sub, CompoundFormula) and sub.connective == "&":
                left_neg = CompoundFormula("~", [sub.subformulas[0]])
                right_neg = CompoundFormula("~", [sub.subformulas[1]])
                disj = CompoundFormula("|", [left_neg, right_neg])
                return to_bilateral_form(disj)

            # ~(φ ∨ ψ) becomes (~φ)* ∧ (~ψ)*
            elif isinstance(sub, CompoundFormula) and sub.connective == "|":
                left_neg = CompoundFormula("~", [sub.subformulas[0]])
                right_neg = CompoundFormula("~", [sub.subformulas[1]])
                conj = CompoundFormula("&", [left_neg, right_neg])
                return to_bilateral_form(conj)

            # ~(φ → ψ) needs special handling
            elif isinstance(sub, CompoundFormula) and sub.connective == "->":
                # ~(φ → ψ) is not directly covered by DeMorgan
                # But φ → ψ ≡ ~φ ∨ ψ, so ~(φ → ψ) ≡ ~(~φ ∨ ψ) ≡ φ ∧ ~ψ
                ant = sub.subformulas[0]
                cons = sub.subformulas[1]
                neg_cons = CompoundFormula("~", [cons])
                conj = CompoundFormula("&", [ant, neg_cons])
                return to_bilateral_form(conj)

            # ~[∀xP(x)]Q(x) becomes [∃xP(x)*](~Q(x))*
            elif isinstance(sub, RestrictedUniversalFormula):
                neg_matrix = CompoundFormula("~", [sub.matrix])
                exist = RestrictedExistentialFormula(
                    sub.var,
                    to_bilateral_form(sub.restriction),
                    to_bilateral_form(neg_matrix),
                )
                return exist

            # ~[∃xP(x)]Q(x) becomes [∀xP(x)*](~Q(x))*
            elif isinstance(sub, RestrictedExistentialFormula):
                neg_matrix = CompoundFormula("~", [sub.matrix])
                univ = RestrictedUniversalFormula(
                    sub.var,
                    to_bilateral_form(sub.restriction),
                    to_bilateral_form(neg_matrix),
                )
                return univ

            else:
                # Other negations - shouldn't happen after DeMorgan rules
                return formula

        else:
            # Non-negation compounds: recursively transform subformulas
            transformed_subs = [to_bilateral_form(sub) for sub in formula.subformulas]
            return CompoundFormula(formula.connective, transformed_subs)

    elif isinstance(
        formula, (RestrictedUniversalFormula, RestrictedExistentialFormula)
    ):
        # Transform restriction and matrix
        transformed_restriction = to_bilateral_form(formula.restriction)
        transformed_matrix = to_bilateral_form(formula.matrix)

        if isinstance(formula, RestrictedUniversalFormula):
            return RestrictedUniversalFormula(
                formula.var,
                transformed_restriction,
                transformed_matrix,
            )
        else:
            return RestrictedExistentialFormula(
                formula.var,
                transformed_restriction,
                transformed_matrix,
            )

    else:
        # Other formula types (constants, etc.) remain unchanged
        return formula


def formulas_are_bilateral_equivalent(formula1: Formula, formula2: Formula) -> bool:
    """
    Check if two formulas are equivalent after bilateral translation (φ* = ψ*).

    This implements the condition from Ferguson's Lemma 5 for ACrQ closure.

    Args:
        formula1: First formula
        formula2: Second formula

    Returns:
        True if the formulas have the same bilateral form
    """
    bilateral1 = to_bilateral_form(formula1)
    bilateral2 = to_bilateral_form(formula2)

    # Compare string representations for equality
    # This works because our Formula classes have consistent str representations
    return str(bilateral1) == str(bilateral2)


def check_acrq_closure(
    sign1: str, formula1: Formula, sign2: str, formula2: Formula
) -> bool:
    """
    Check if two signed formulas cause closure in ACrQ.

    Per Ferguson's Lemma 5: If u:φ and v:ψ for distinct u,v are on a branch
    such that φ* = ψ*, then the branch will close.

    Args:
        sign1: Sign of first formula (t, f, or e)
        formula1: First formula
        sign2: Sign of second formula (t, f, or e)
        formula2: Second formula

    Returns:
        True if these cause closure
    """
    # Only truth value signs (t, f, e) can cause closure
    # Meta-signs (m, n, v) are branching instructions, not truth values
    if sign1 not in ["t", "f", "e"] or sign2 not in ["t", "f", "e"]:
        return False

    # Signs must be distinct
    if sign1 == sign2:
        return False

    # Formulas must be bilateral equivalent
    return formulas_are_bilateral_equivalent(formula1, formula2)
