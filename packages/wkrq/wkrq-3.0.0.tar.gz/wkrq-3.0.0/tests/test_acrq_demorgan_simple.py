"""
Simple tests for ACrQ DeMorgan transformation rules.

These tests verify that Ferguson's Definition 18 DeMorgan transformations
are correctly implemented in the ACrQ tableau system.
"""

import pytest

from wkrq import parse_acrq_formula
from wkrq.acrq_rules import get_acrq_negation_rule
from wkrq.acrq_tableau import ACrQTableau
from wkrq.formula import CompoundFormula, Constant, PredicateFormula
from wkrq.signs import SignedFormula, f, t


class TestACrQDeMorganRules:
    """Test that DeMorgan transformation rules are correctly applied."""

    def test_demorgan_conjunction_rule(self):
        """Test the DeMorgan rule for ~(P & Q)."""
        # Create ~(P(a) & Q(a))
        p_a = PredicateFormula("P", [Constant("a")])
        q_a = PredicateFormula("Q", [Constant("a")])
        conj = CompoundFormula("&", [p_a, q_a])
        neg_conj = CompoundFormula("~", [conj])
        signed = SignedFormula(t, neg_conj)

        # Get the rule
        rule = get_acrq_negation_rule(signed)

        assert rule is not None, "DeMorgan rule should be found for ~(P & Q)"
        assert rule.name == "t-demorgan-conjunction"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 1

        # Check the conclusion is (~P | ~Q)
        conclusion = rule.conclusions[0][0]
        assert conclusion.sign == t
        result_formula = conclusion.formula
        assert isinstance(result_formula, CompoundFormula)
        assert result_formula.connective == "|"

        # Check both sides are negations
        left, right = result_formula.subformulas
        assert isinstance(left, CompoundFormula) and left.connective == "~"
        assert isinstance(right, CompoundFormula) and right.connective == "~"

    def test_demorgan_disjunction_rule(self):
        """Test the DeMorgan rule for ~(P | Q)."""
        # Create ~(P(a) | Q(a))
        p_a = PredicateFormula("P", [Constant("a")])
        q_a = PredicateFormula("Q", [Constant("a")])
        disj = CompoundFormula("|", [p_a, q_a])
        neg_disj = CompoundFormula("~", [disj])
        signed = SignedFormula(t, neg_disj)

        # Get the rule
        rule = get_acrq_negation_rule(signed)

        assert rule is not None, "DeMorgan rule should be found for ~(P | Q)"
        assert rule.name == "t-demorgan-disjunction"
        assert len(rule.conclusions) == 1

        # Check the conclusion is (~P & ~Q)
        conclusion = rule.conclusions[0][0]
        result_formula = conclusion.formula
        assert isinstance(result_formula, CompoundFormula)
        assert result_formula.connective == "&"

        # Check both sides are negations
        left, right = result_formula.subformulas
        assert isinstance(left, CompoundFormula) and left.connective == "~"
        assert isinstance(right, CompoundFormula) and right.connective == "~"

    def test_no_general_negation_elimination(self):
        """Verify general negation elimination is NOT applied in ACrQ."""
        # Create ~(P(a) -> Q(a))
        p_a = PredicateFormula("P", [Constant("a")])
        q_a = PredicateFormula("Q", [Constant("a")])
        impl = CompoundFormula("->", [p_a, q_a])
        neg_impl = CompoundFormula("~", [impl])
        signed = SignedFormula(t, neg_impl)

        # Get the rule - should be None
        rule = get_acrq_negation_rule(signed)

        assert rule is None, "No rule should apply to ~(P -> Q) in ACrQ"


class TestACrQDeMorganValidity:
    """Test that DeMorgan laws are valid in ACrQ after implementing the rules."""

    def test_demorgan_conjunction_valid(self):
        """Test that ~(P & Q) -> (~P | ~Q) is valid in ACrQ."""
        formula_str = "~(P(a) & Q(a)) -> (~P(a) | ~Q(a))"
        formula = parse_acrq_formula(formula_str)

        # Test validity by checking if negation leads to closed tableau
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()

        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan conjunction law should be valid in ACrQ"

    def test_demorgan_disjunction_valid(self):
        """Test that ~(P | Q) -> (~P & ~Q) is valid in ACrQ."""
        formula_str = "~(P(a) | Q(a)) -> (~P(a) & ~Q(a))"
        formula = parse_acrq_formula(formula_str)

        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()

        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan disjunction law should be valid in ACrQ"

    def test_demorgan_biconditional_conjunction(self):
        """Test that ~(P & Q) <-> (~P | ~Q) is valid in ACrQ."""
        # Test both directions
        formula1_str = "~(P(a) & Q(a)) -> (~P(a) | ~Q(a))"
        formula1 = parse_acrq_formula(formula1_str)
        tableau1 = ACrQTableau([SignedFormula(f, formula1)])
        tableau1.construct()

        formula2_str = "(~P(a) | ~Q(a)) -> ~(P(a) & Q(a))"
        formula2 = parse_acrq_formula(formula2_str)
        tableau2 = ACrQTableau([SignedFormula(f, formula2)])
        tableau2.construct()

        assert all(
            branch.is_closed for branch in tableau1.branches
        ), "DeMorgan conjunction forward direction should be valid"
        assert all(
            branch.is_closed for branch in tableau2.branches
        ), "DeMorgan conjunction reverse direction should be valid"

    def test_demorgan_nested(self):
        """Test DeMorgan with nested negations."""
        # ~(~P & ~Q) should become (~~P | ~~Q)
        # But ~~P ≠ P in weak Kleene! Double negation elimination doesn't hold
        formula_str = "~(~P(a) & ~Q(a)) -> (P(a) | Q(a))"
        formula = parse_acrq_formula(formula_str)

        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()

        # This should NOT be valid because ~~P ≠ P in weak Kleene
        has_open = any(not branch.is_closed for branch in tableau.branches)
        assert has_open, "Double negation elimination does not hold in weak Kleene"


class TestACrQQuantifierDeMorgan:
    """Test DeMorgan transformation rules for quantifiers."""

    def test_quantifier_demorgan_rules_exist(self):
        """Test that quantifier DeMorgan rules are implemented."""
        from wkrq.formula import (
            RestrictedExistentialFormula,
            RestrictedUniversalFormula,
            Variable,
        )

        # Test ~[∀xP(x)]Q(x)
        p_x = PredicateFormula("P", [Variable("x")])
        q_x = PredicateFormula("Q", [Variable("x")])
        univ = RestrictedUniversalFormula(Variable("x"), p_x, q_x)
        neg_univ = CompoundFormula("~", [univ])
        signed = SignedFormula(t, neg_univ)

        rule = get_acrq_negation_rule(signed)
        assert rule is not None, "DeMorgan rule should exist for negated universal"
        assert rule.name == "t-demorgan-universal"

        # Test ~[∃xP(x)]Q(x)
        exist = RestrictedExistentialFormula(Variable("x"), p_x, q_x)
        neg_exist = CompoundFormula("~", [exist])
        signed2 = SignedFormula(t, neg_exist)

        rule2 = get_acrq_negation_rule(signed2)
        assert rule2 is not None, "DeMorgan rule should exist for negated existential"
        assert rule2.name == "t-demorgan-existential"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
