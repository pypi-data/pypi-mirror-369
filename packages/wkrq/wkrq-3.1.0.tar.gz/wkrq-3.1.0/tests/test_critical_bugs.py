"""
Critical test cases for tableau correctness.

This module contains:
1. Regression tests for previously fixed bugs (error branches)
2. Documentation of deliberate simplifications from Ferguson's notation
"""

import pytest

from wkrq import SignedFormula, e, t
from wkrq.formula import CompoundFormula, Constant, PredicateFormula
from wkrq.wkrq_rules import get_applicable_rule as get_wkrq_rule


class TestMissingErrorBranches:
    """Test cases for missing error branches in t-disjunction and t-implication."""

    def test_t_disjunction_must_have_error_branch(self):
        """t: (P ∨ Q) must consider the case where both P and Q are error."""
        p = PredicateFormula("P", [])
        q = PredicateFormula("Q", [])
        disj = CompoundFormula("|", [p, q])
        signed = SignedFormula(t, disj)

        rule = get_wkrq_rule(signed, lambda: Constant("c1"))

        # Should have 3 branches: t:P, t:Q, and (e:P, e:Q)
        assert (
            len(rule.conclusions) == 3
        ), "t-disjunction must have 3 branches including error case"

        # Find the error branch
        error_branch = None
        for branch in rule.conclusions:
            if any(sf.sign == e for sf in branch):
                error_branch = branch
                break

        assert error_branch is not None, "Must have error branch"
        assert len(error_branch) == 2, "Error branch should have both e:P and e:Q"
        assert SignedFormula(e, p) in error_branch
        assert SignedFormula(e, q) in error_branch

    def test_t_implication_must_have_error_branch(self):
        """t: (P → Q) must consider the case where both P and Q are error."""
        p = PredicateFormula("P", [])
        q = PredicateFormula("Q", [])
        impl = CompoundFormula("->", [p, q])
        signed = SignedFormula(t, impl)

        rule = get_wkrq_rule(signed, lambda: Constant("c1"))

        # Should have 3 branches: f:P, t:Q, and (e:P, e:Q)
        assert (
            len(rule.conclusions) == 3
        ), "t-implication must have 3 branches including error case"

        # Find the error branch
        error_branch = None
        for branch in rule.conclusions:
            if len(branch) == 2 and all(sf.sign == e for sf in branch):
                error_branch = branch
                break

        assert error_branch is not None, "Must have error branch"
        assert SignedFormula(e, p) in error_branch
        assert SignedFormula(e, q) in error_branch

    def test_disjunction_completeness_with_errors(self):
        """Test that tableau is complete for disjunctions with error values."""
        # Create a formula that should be unsatisfiable:
        # (P ∨ Q) is true, but P is error and Q is error
        # Since e ∨ e = e (not t), this should be unsatisfiable

        # We need a way to force P and Q to be error in the tableau
        # This is a semantic test that's hard to express directly
        # but the missing branch means the tableau won't explore this case

        # For now, just verify the rule structure is wrong
        p = PredicateFormula("P", [])
        q = PredicateFormula("Q", [])
        disj = CompoundFormula("|", [p, q])

        # The tableau for t:(P∨Q) should explore:
        # 1. P is true (Q can be anything)
        # 2. Q is true (P can be anything)
        # 3. Both are error (which gives e ∨ e = e, contradicting t:(P∨Q))

        signed = SignedFormula(t, disj)
        rule = get_wkrq_rule(signed, lambda: Constant("c1"))

        # Currently only 2 branches, should be 3
        assert len(rule.conclusions) == 3


class TestMetaSignHandling:
    """Test cases for m and n sign handling bugs."""

    @pytest.mark.xfail(
        reason="SIMPLIFICATION: We use f:P instead of n:P for m:~P (Ferguson page 51)"
    )
    def test_m_negation_produces_n(self):
        """m: ¬P should produce n: P, not f: P."""
        from wkrq.signs import m, n

        p = PredicateFormula("P", [])
        neg = CompoundFormula("~", [p])
        signed = SignedFormula(m, neg)

        rule = get_wkrq_rule(signed, lambda: Constant("c1"))

        assert rule is not None
        assert rule.name == "m-negation"
        assert len(rule.conclusions) == 1
        assert rule.conclusions[0] == [
            SignedFormula(n, p)
        ], f"Expected n:P, got {rule.conclusions[0]}"

    @pytest.mark.xfail(
        reason="SIMPLIFICATION: We use t:P instead of m:P for n:~P (Ferguson page 51)"
    )
    def test_n_negation_produces_m(self):
        """n: ¬P should produce m: P, not t: P."""
        from wkrq.signs import m, n

        p = PredicateFormula("P", [])
        neg = CompoundFormula("~", [p])
        signed = SignedFormula(n, neg)

        rule = get_wkrq_rule(signed, lambda: Constant("c1"))

        assert rule is not None
        assert rule.name == "n-negation"
        assert len(rule.conclusions) == 1
        assert rule.conclusions[0] == [
            SignedFormula(m, p)
        ], f"Expected m:P, got {rule.conclusions[0]}"


class TestSemanticCorrectness:
    """Test that tableau results match weak Kleene semantics."""

    def test_error_propagation_in_disjunction(self):
        """Verify that error propagates correctly through disjunction."""
        # This is a higher-level test that checks if the tableau
        # correctly handles formulas where error values matter

        # If we could force P=e and Q=e, then (P∨Q)=e
        # The tableau should recognize this, but with missing branches it won't

        # This test would need a way to set up initial error values
        # which the current API doesn't directly support
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
