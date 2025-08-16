"""
Tests for ACrQ DeMorgan transformation rules.

These tests verify that Ferguson's Definition 18 DeMorgan transformations
are correctly implemented in the ACrQ tableau system.
"""

import pytest

from wkrq import SyntaxMode, parse_acrq_formula
from wkrq.acrq_tableau import ACrQTableau
from wkrq.signs import SignedFormula, f, t


class TestACrQDeMorganTransformations:
    """Test DeMorgan transformation rules in ACrQ."""

    def test_demorgan_conjunction_valid(self):
        """Test that ~(P & Q) -> (~P | ~Q) is valid in ACrQ."""
        formula_str = "~(P(a) & Q(a)) -> (~P(a) | ~Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau(
            [SignedFormula(f, formula)]
        )  # Test validity by checking negation
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan conjunction should be valid in ACrQ"

    def test_demorgan_disjunction_valid(self):
        """Test that ~(P | Q) -> (~P & ~Q) is valid in ACrQ."""
        formula_str = "~(P(a) | Q(a)) -> (~P(a) & ~Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan disjunction should be valid in ACrQ"

    def test_demorgan_conjunction_reverse(self):
        """Test that (~P | ~Q) -> ~(P & Q) is valid in ACrQ."""
        formula_str = "(~P(a) | ~Q(a)) -> ~(P(a) & Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "Reverse DeMorgan conjunction should be valid in ACrQ"

    def test_demorgan_disjunction_reverse(self):
        """Test that (~P & ~Q) -> ~(P | Q) is valid in ACrQ."""
        formula_str = "(~P(a) & ~Q(a)) -> ~(P(a) | Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "Reverse DeMorgan disjunction should be valid in ACrQ"

    def test_demorgan_biconditional(self):
        """Test that DeMorgan laws work as biconditionals in ACrQ."""
        # Test both directions separately since biconditional isn't supported
        # Conjunction forward: ~(P & Q) -> (~P | ~Q)
        formula1_fwd = parse_acrq_formula("~(P(a) & Q(a)) -> (~P(a) | ~Q(a))")
        tableau1_fwd = ACrQTableau([SignedFormula(f, formula1_fwd)])
        tableau1_fwd.construct()

        # Conjunction reverse: (~P | ~Q) -> ~(P & Q)
        formula1_rev = parse_acrq_formula("(~P(a) | ~Q(a)) -> ~(P(a) & Q(a))")
        tableau1_rev = ACrQTableau([SignedFormula(f, formula1_rev)])
        tableau1_rev.construct()

        assert all(
            branch.is_closed for branch in tableau1_fwd.branches
        ), "DeMorgan conjunction forward should be valid"
        assert all(
            branch.is_closed for branch in tableau1_rev.branches
        ), "DeMorgan conjunction reverse should be valid"

        # Disjunction tests similarly
        formula2_fwd = parse_acrq_formula("~(P(a) | Q(a)) -> (~P(a) & ~Q(a))")
        tableau2_fwd = ACrQTableau([SignedFormula(f, formula2_fwd)])
        tableau2_fwd.construct()

        formula2_rev = parse_acrq_formula("(~P(a) & ~Q(a)) -> ~(P(a) | Q(a))")
        tableau2_rev = ACrQTableau([SignedFormula(f, formula2_rev)])
        tableau2_rev.construct()

        assert all(
            branch.is_closed for branch in tableau2_fwd.branches
        ), "DeMorgan disjunction forward should be valid"
        assert all(
            branch.is_closed for branch in tableau2_rev.branches
        ), "DeMorgan disjunction reverse should be valid"

    def test_demorgan_with_error_values(self):
        """Test DeMorgan transformations preserve error semantics."""
        # When P(a) = error, ~(P(a) & Q(a)) should transform to (~P(a) | ~Q(a))
        # The transformation should be applied by the tableau rules
        formula = parse_acrq_formula("~(P(a) & Q(a))")

        # Check that the formula is satisfiable (not a tautology)
        tableau = ACrQTableau([SignedFormula(t, formula)])
        tableau.construct()

        # Should have open branches (formula can be true, false, or error)
        has_open = any(not branch.is_closed for branch in tableau.branches)
        assert has_open, "Formula should be satisfiable"

    def test_demorgan_nested_negations(self):
        """Test DeMorgan with nested negations."""
        # ~(~P & ~Q) should become (~~P | ~~Q)
        # But ~~P does NOT equal P in weak Kleene - could be error!
        # So this formula is NOT valid
        formula_str = "~(~P(a) & ~Q(a)) -> (P(a) | Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        # This should NOT be valid because ~~P ≠ P in weak Kleene
        has_open = any(not branch.is_closed for branch in tableau.branches)
        assert has_open, "Double negation elimination does not hold in weak Kleene"

    def test_demorgan_complex_formula(self):
        """Test DeMorgan with more complex formulas."""
        # ~((P & Q) | R) -> (~(P & Q) & ~R) -> ((~P | ~Q) & ~R)
        formula_str = "~((P(a) & Q(a)) | R(a)) -> ((~P(a) | ~Q(a)) & ~R(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "Complex DeMorgan should be valid"


class TestACrQQuantifierDeMorgan:
    """Test DeMorgan transformation rules for quantifiers in ACrQ."""

    def test_demorgan_universal_quantifier(self):
        """Test ~[∀xP(x)]Q(x) -> [∃xP(x)]~Q(x)."""
        # Use proper quantifier syntax supported by the parser
        formula_str = "~[∀x P(x)]Q(x) -> [∃x P(x)]~Q(x)"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan for universal quantifier should be valid"

    def test_demorgan_existential_quantifier(self):
        """Test ~[∃xP(x)]Q(x) -> [∀xP(x)]~Q(x)."""
        # Use proper quantifier syntax supported by the parser
        formula_str = "~[∃x P(x)]Q(x) -> [∀x P(x)]~Q(x)"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan for existential quantifier should be valid"

    def test_quantifier_demorgan_reverse(self):
        """Test reverse direction of quantifier DeMorgan."""
        # [∃xP(x)]~Q(x) -> ~[∀xP(x)]Q(x)
        formula1_str = "[∃x P(x)]~Q(x) -> ~[∀x P(x)]Q(x)"
        formula1 = parse_acrq_formula(formula1_str)
        tableau1 = ACrQTableau([SignedFormula(f, formula1)])
        tableau1.construct()
        assert all(
            branch.is_closed for branch in tableau1.branches
        ), "Reverse DeMorgan for universal should be valid"

        # [∀xP(x)]~Q(x) -> ~[∃xP(x)]Q(x)
        formula2_str = "[∀x P(x)]~Q(x) -> ~[∃x P(x)]Q(x)"
        formula2 = parse_acrq_formula(formula2_str)
        tableau2 = ACrQTableau([SignedFormula(f, formula2)])
        tableau2.construct()
        assert all(
            branch.is_closed for branch in tableau2.branches
        ), "Reverse DeMorgan for existential should be valid"

    def test_quantifier_demorgan_biconditional(self):
        """Test quantifier DeMorgan as biconditionals."""
        # Biconditional not supported, test both directions
        # Forward: ~[∀x P(x)]Q(x) -> [∃x P(x)]~Q(x)
        formula1_fwd_str = "~[∀x P(x)]Q(x) -> [∃x P(x)]~Q(x)"
        formula1_fwd = parse_acrq_formula(formula1_fwd_str)
        tableau1_fwd = ACrQTableau([SignedFormula(f, formula1_fwd)])
        tableau1_fwd.construct()

        # Reverse: [∃x P(x)]~Q(x) -> ~[∀x P(x)]Q(x)
        formula1_rev_str = "[∃x P(x)]~Q(x) -> ~[∀x P(x)]Q(x)"
        formula1_rev = parse_acrq_formula(formula1_rev_str)
        tableau1_rev = ACrQTableau([SignedFormula(f, formula1_rev)])
        tableau1_rev.construct()

        assert all(
            branch.is_closed for branch in tableau1_fwd.branches
        ), "Universal DeMorgan forward should be valid"
        assert all(
            branch.is_closed for branch in tableau1_rev.branches
        ), "Universal DeMorgan reverse should be valid"

        # Forward: ~[∃x P(x)]Q(x) -> [∀x P(x)]~Q(x)
        formula2_fwd_str = "~[∃x P(x)]Q(x) -> [∀x P(x)]~Q(x)"
        formula2_fwd = parse_acrq_formula(formula2_fwd_str)
        tableau2_fwd = ACrQTableau([SignedFormula(f, formula2_fwd)])
        tableau2_fwd.construct()

        # Reverse: [∀x P(x)]~Q(x) -> ~[∃x P(x)]Q(x)
        formula2_rev_str = "[∀x P(x)]~Q(x) -> ~[∃x P(x)]Q(x)"
        formula2_rev = parse_acrq_formula(formula2_rev_str)
        tableau2_rev = ACrQTableau([SignedFormula(f, formula2_rev)])
        tableau2_rev.construct()

        assert all(
            branch.is_closed for branch in tableau2_fwd.branches
        ), "Existential DeMorgan forward should be valid"
        assert all(
            branch.is_closed for branch in tableau2_rev.branches
        ), "Existential DeMorgan reverse should be valid"

    def test_nested_quantifier_demorgan(self):
        """Test DeMorgan with nested quantifiers."""
        # ~[∀x P(x)][∃y Q(y)]R(y) -> [∃x P(x)]~[∃y Q(y)]R(y)
        # Which further transforms to [∃x P(x)][∀y Q(y)]~R(y)
        formula_str = "~[∀x P(x)][∃y Q(y)]R(y) -> [∃x P(x)][∀y Q(y)]~R(y)"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "Nested quantifier DeMorgan should be valid"


class TestACrQDeMorganInteraction:
    """Test interaction of DeMorgan rules with other ACrQ features."""

    def test_demorgan_with_bilateral_predicates(self):
        """Test DeMorgan with bilateral predicates."""
        # In transparent mode, ~P becomes P*
        # So ~(P & Q) becomes ~(P & Q) which transforms to (~P | ~Q) = (P* | Q*)
        formula = parse_acrq_formula("~(P(a) & Q(a))", SyntaxMode.TRANSPARENT)

        # Test if formula is satisfiable (not a tautology)
        tableau = ACrQTableau([SignedFormula(t, formula)])
        tableau.construct()

        # The formula should be satisfiable with appropriate models
        has_open = any(not branch.is_closed for branch in tableau.branches)
        assert has_open, "Single negated conjunction should be satisfiable"

    def test_demorgan_preserves_gluts(self):
        """Test that DeMorgan transformations preserve glut handling."""
        # Test that gluts (P(a) & P*(a)) can exist after DeMorgan transformations
        # Simply check that a glut is satisfiable
        formula_str = "P(a) & P*(a)"
        formula = parse_acrq_formula(formula_str, SyntaxMode.BILATERAL)
        tableau = ACrQTableau([SignedFormula(t, formula)])
        tableau.construct()
        # This should be satisfiable (gluts are allowed in ACrQ)
        has_open = any(not branch.is_closed for branch in tableau.branches)
        assert has_open, "Gluts should be satisfiable in ACrQ"

    def test_demorgan_with_implication(self):
        """Test DeMorgan interacting with implication."""
        # ~(P -> Q) is not directly a DeMorgan case, but
        # P -> Q ≡ ~P | Q, so ~(P -> Q) ≡ ~(~P | Q) ≡ (P & ~Q)
        formula_str = "~(P(a) -> Q(a)) -> (P(a) & ~Q(a))"
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "DeMorgan with implication should work"

    def test_demorgan_chain(self):
        """Test chained DeMorgan transformations."""
        # Multiple negations that trigger multiple transformations
        # ~(~(P & Q) & ~(R | S))
        # -> ~((~P | ~Q) & (~R & ~S))  [after DeMorgan on inner]
        # -> (~(~P | ~Q) | ~(~R & ~S))  [after DeMorgan on outer]
        # -> ((P & Q) | (R | S))        [after more DeMorgan]
        formula_str = (
            "~(~(P(a) & Q(a)) & ~(R(a) | S(a))) -> ((P(a) & Q(a)) | (R(a) | S(a)))"
        )
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(f, formula)])
        tableau.construct()
        assert all(
            branch.is_closed for branch in tableau.branches
        ), "Chained DeMorgan should be valid"


class TestACrQDeMorganCorrectness:
    """Test that DeMorgan rules are applied correctly in tableau construction."""

    def test_tableau_applies_demorgan_rule(self):
        """Verify the tableau actually applies DeMorgan transformation."""
        from wkrq.acrq_rules import get_acrq_negation_rule
        from wkrq.formula import CompoundFormula, Constant, PredicateFormula
        from wkrq.signs import SignedFormula, t

        # Create ~(P(a) & Q(a))
        p_a = PredicateFormula("P", [Constant("a")])
        q_a = PredicateFormula("Q", [Constant("a")])
        conj = CompoundFormula("&", [p_a, q_a])
        neg_conj = CompoundFormula("~", [conj])
        signed = SignedFormula(t, neg_conj)

        # Get the rule
        rule = get_acrq_negation_rule(signed)

        assert rule is not None, "DeMorgan rule should be found for ~(P & Q)"
        assert rule.name == "t-demorgan-conjunction", f"Wrong rule name: {rule.name}"
        assert len(rule.conclusions) == 1, "Should have one conclusion"
        assert len(rule.conclusions[0]) == 1, "Should have one formula in conclusion"

        # Check the conclusion is (~P | ~Q)
        conclusion = rule.conclusions[0][0]
        assert conclusion.sign == t
        result_formula = conclusion.formula
        assert isinstance(result_formula, CompoundFormula)
        assert result_formula.connective == "|", "Should be disjunction"

        # Check left and right are negations
        left, right = result_formula.subformulas
        assert isinstance(left, CompoundFormula) and left.connective == "~"
        assert isinstance(right, CompoundFormula) and right.connective == "~"

    def test_no_general_negation_elimination(self):
        """Verify general negation elimination is NOT applied in ACrQ."""
        from wkrq.acrq_rules import get_acrq_negation_rule
        from wkrq.formula import CompoundFormula, Constant, PredicateFormula
        from wkrq.signs import SignedFormula, t

        # Create ~(P(a) -> Q(a)) - implication is not covered by DeMorgan
        p_a = PredicateFormula("P", [Constant("a")])
        q_a = PredicateFormula("Q", [Constant("a")])
        impl = CompoundFormula("->", [p_a, q_a])
        neg_impl = CompoundFormula("~", [impl])
        signed = SignedFormula(t, neg_impl)

        # Get the rule - should be None as we don't have general negation elimination
        rule = get_acrq_negation_rule(signed)

        assert rule is None, "No rule should apply to ~(P -> Q) in ACrQ"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
