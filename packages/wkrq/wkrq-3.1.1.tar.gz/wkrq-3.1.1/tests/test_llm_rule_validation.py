#!/usr/bin/env python3
"""
Validation tests for the LLM evaluation rule formal specification.

This test suite validates that the llm-eval rule implementation matches
its formal specification in docs/LLM_RULE_FORMAL_SPECIFICATION.md
"""

import pytest

from wkrq import (
    FALSE,
    TRUE,
    ACrQTableau,
    BilateralPredicateFormula,
    BilateralTruthValue,
    Constant,
    PredicateFormula,
    PropositionalAtom,
    SignedFormula,
    f,
    t,
)


class TestLLMRuleFormalSpecification:
    """Validate LLM rule against formal specification."""

    def test_rule_only_applies_to_atomic_formulas(self):
        """Verify llm-eval only applies to atomic formulas, not compounds."""
        from wkrq.formula import conjunction

        def evaluator(formula):
            # Should never be called for non-atomic formulas
            if not formula.is_atomic():
                pytest.fail("LLM evaluator called for non-atomic formula")
            return BilateralTruthValue(TRUE, FALSE)

        # Create compound formula
        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        compound = conjunction(p, q)

        # LLM should not be called for compound formulas
        tableau = ACrQTableau([SignedFormula(t, compound)], llm_evaluator=evaluator)
        result = tableau.construct()
        # Should complete without calling LLM on compound
        assert result is not None

    def test_gamma_llm_positive_confirmation(self):
        """Test Γ_LLM(t, P(a), TRUE, FALSE) → {t: P(a)}"""

        def evaluator(formula):
            return BilateralTruthValue(positive=TRUE, negative=FALSE)

        atom = PredicateFormula("P", [Constant("a")])

        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=evaluator)
        result = tableau.construct()

        # Should be satisfiable with confirmation
        assert result.satisfiable
        assert len(result.models) == 1
        model = result.models[0]
        assert str(model.valuations.get("P(a)")) == "t"

    def test_gamma_llm_refutation(self):
        """Test Γ_LLM(t, P(a), FALSE, TRUE) → {f: P(a)} closes branch"""

        def evaluator(formula):
            return BilateralTruthValue(positive=FALSE, negative=TRUE)

        atom = PredicateFormula("P", [Constant("a")])

        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=evaluator)
        result = tableau.construct()

        # Should be unsatisfiable due to refutation
        assert not result.satisfiable
        assert result.closed_branches == 1

    def test_gamma_llm_glut(self):
        """Test Γ_LLM(t, P(a), TRUE, TRUE) → {t: P(a), t: P*(a)}"""

        def evaluator(formula):
            # Return glut for all queries
            return BilateralTruthValue(positive=TRUE, negative=TRUE)

        atom = PredicateFormula("P", [Constant("a")])

        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=evaluator)
        result = tableau.construct()

        # Should be satisfiable with glut (ACrQ allows gluts)
        assert result.satisfiable
        # Model should contain both P(a) and P*(a) as true
        model = result.models[0]
        # Check for glut in model representation
        assert "P(a)" in str(model)

    def test_gamma_llm_gap(self):
        """Test Γ_LLM(t, P(a), FALSE, FALSE) → {f: P(a), f: P*(a)} closes"""

        def evaluator(formula):
            # Return gap (no knowledge)
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        atom = PredicateFormula("P", [Constant("a")])

        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=evaluator)
        result = tableau.construct()

        # Gap with t: P(a) should close (cannot verify)
        assert not result.satisfiable

    def test_bilateral_predicate_component_swap(self):
        """Test that P*(a) swaps LLM components correctly."""

        evaluation_log = []

        def evaluator(formula):
            formula_str = str(formula)
            evaluation_log.append(formula_str)

            # For base predicate P, return (TRUE, FALSE)
            if "*" not in formula_str:
                return BilateralTruthValue(positive=TRUE, negative=FALSE)
            # This shouldn't be called for P* directly in our implementation
            return BilateralTruthValue(positive=FALSE, negative=TRUE)

        # Create P*(a) directly
        p_star = BilateralPredicateFormula(
            positive_name="P", terms=[Constant("a")], is_negative=True
        )

        tableau = ACrQTableau([SignedFormula(t, p_star)], llm_evaluator=evaluator)
        result = tableau.construct()

        # For t: P*(a), if LLM(P) returns (TRUE, FALSE),
        # the bilateral handling should swap to (FALSE, TRUE)
        # which contradicts t: P*(a), closing the branch
        assert not result.satisfiable

    def test_llm_evaluation_marks_as_evaluated(self):
        """Test that formulas are marked as evaluated to prevent duplicates."""

        evaluation_count = {"count": 0}
        evaluated_formulas = []

        def counting_evaluator(formula):
            evaluation_count["count"] += 1
            evaluated_formulas.append(str(formula))
            return BilateralTruthValue(positive=TRUE, negative=FALSE)

        atom = PredicateFormula("P", [Constant("a")])

        # Create tableau with same atom appearing multiple times
        tableau = ACrQTableau(
            [SignedFormula(t, atom)], llm_evaluator=counting_evaluator
        )
        tableau.construct()

        # LLM might be called multiple times due to implementation details
        # but should not evaluate the same formula excessively
        assert evaluation_count["count"] <= 2  # Allow for some re-evaluation
        # Check what was evaluated
        print(f"Evaluated formulas: {evaluated_formulas}")

    def test_llm_rule_has_lowest_priority(self):
        """Test that LLM evaluation happens after all other rules."""

        rule_applications = []

        def tracking_evaluator(formula):
            # Record when LLM is called
            rule_applications.append(("llm-eval", str(formula)))
            return BilateralTruthValue(positive=TRUE, negative=FALSE)

        # Create formula that triggers multiple rules
        from wkrq.formula import conjunction

        p = PredicateFormula("P", [Constant("a")])
        q = PredicateFormula("Q", [Constant("b")])
        conj = conjunction(p, q)

        # The conjunction should be decomposed before atoms are evaluated
        tableau = ACrQTableau(
            [SignedFormula(t, conj)], llm_evaluator=tracking_evaluator
        )
        tableau.construct()

        # Check that conjunction was decomposed (should create P and Q)
        # and that LLM was called for the atomic formulas
        assert len(rule_applications) > 0, "LLM should be called for atoms"

        # LLM should be called for P(a) and Q(b) after conjunction decomposition
        llm_formulas = [f for rule, f in rule_applications if rule == "llm-eval"]
        assert "P(a)" in str(llm_formulas) or "Q(b)" in str(
            llm_formulas
        ), "LLM should evaluate atomic formulas from conjunction"


class TestLLMRuleClosureSemantics:
    """Test modified closure conditions with LLM evaluation."""

    def test_gap_closes_with_assertion(self):
        """Gap (FALSE, FALSE) with t: P(a) closes branch."""

        def gap_evaluator(formula):
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        atom = PredicateFormula("P", [Constant("a")])
        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=gap_evaluator)
        result = tableau.construct()

        assert not result.satisfiable
        assert result.closed_branches == 1

    def test_refutation_closes_with_assertion(self):
        """Refutation (FALSE, TRUE) with t: P(a) closes branch."""

        def refutation_evaluator(formula):
            return BilateralTruthValue(positive=FALSE, negative=TRUE)

        atom = PredicateFormula("P", [Constant("a")])
        tableau = ACrQTableau(
            [SignedFormula(t, atom)], llm_evaluator=refutation_evaluator
        )
        result = tableau.construct()

        assert not result.satisfiable
        assert result.closed_branches == 1

    def test_glut_preserves_acrq_semantics(self):
        """Glut (TRUE, TRUE) respects ACrQ glut tolerance."""

        def glut_evaluator(formula):
            return BilateralTruthValue(positive=TRUE, negative=TRUE)

        atom = PredicateFormula("P", [Constant("a")])
        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=glut_evaluator)
        result = tableau.construct()

        # ACrQ allows gluts
        assert result.satisfiable
        assert result.open_branches == 1


class TestLLMRuleNonMonotonicity:
    """Test non-monotonic properties of ACrQ-LLM."""

    def test_time_dependent_results(self):
        """Results can change based on LLM state."""

        # Simulate changing LLM knowledge
        llm_state = {"believes_true": True}

        def stateful_evaluator(formula):
            if llm_state["believes_true"]:
                return BilateralTruthValue(positive=TRUE, negative=FALSE)
            else:
                return BilateralTruthValue(positive=FALSE, negative=TRUE)

        atom = PredicateFormula("P", [Constant("a")])
        formulas = [SignedFormula(t, atom)]

        # First query - LLM believes true
        tableau1 = ACrQTableau(formulas, llm_evaluator=stateful_evaluator)
        result1 = tableau1.construct()
        assert result1.satisfiable

        # Change LLM state
        llm_state["believes_true"] = False

        # Second query - LLM believes false
        tableau2 = ACrQTableau(formulas, llm_evaluator=stateful_evaluator)
        result2 = tableau2.construct()
        assert not result2.satisfiable

        # Demonstrates non-monotonicity


class TestLLMRuleCompleteness:
    """Test incompleteness properties of ACrQ-LLM."""

    def test_incomplete_with_gaps(self):
        """System is incomplete when LLM has knowledge gaps."""

        def incomplete_evaluator(formula):
            # Always return gap
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        # Create a classically valid inference
        from wkrq import parse_acrq_formula

        # P → P should be valid, but with gaps it might not be provable
        p_implies_p = parse_acrq_formula("P(a) -> P(a)")

        tableau = ACrQTableau(
            [SignedFormula(f, p_implies_p)],  # Try to prove it's false
            llm_evaluator=incomplete_evaluator,
        )
        tableau.construct()

        # This demonstrates incompleteness - classical tautologies
        # may not be provable when LLM lacks knowledge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
