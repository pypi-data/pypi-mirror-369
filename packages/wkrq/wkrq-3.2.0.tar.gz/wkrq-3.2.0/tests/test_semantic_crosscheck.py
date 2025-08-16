"""
Cross-validation with semantic evaluator.

This module implements a simple semantic evaluator for weak Kleene logic
and uses it to validate tableau results for ground formulas.
"""

from itertools import product

import pytest

from wkrq import parse, solve, t
from wkrq.formula import CompoundFormula, PredicateFormula, PropositionalAtom
from wkrq.semantics import FALSE, TRUE, UNDEFINED, WeakKleeneSemantics


class SemanticEvaluator:
    """Direct semantic evaluation of formulas in weak Kleene logic."""

    def __init__(self):
        self.wk = WeakKleeneSemantics()
        self.valuation = {}  # Maps atom names to TruthValue

    def set_value(self, atom_name: str, value):
        """Set the truth value of an atom."""
        self.valuation[atom_name] = value

    def evaluate(self, formula):
        """Evaluate a formula under the current valuation."""
        if isinstance(formula, PropositionalAtom):
            return self.valuation.get(formula.name, UNDEFINED)

        elif isinstance(formula, PredicateFormula):
            # For ground predicates, treat as atoms
            key = str(formula)
            return self.valuation.get(key, UNDEFINED)

        elif isinstance(formula, CompoundFormula):
            if formula.connective == "~":
                sub = self.evaluate(formula.subformulas[0])
                return self.wk.negation(sub)

            elif formula.connective == "&":
                left = self.evaluate(formula.subformulas[0])
                right = self.evaluate(formula.subformulas[1])
                return self.wk.conjunction(left, right)

            elif formula.connective == "|":
                left = self.evaluate(formula.subformulas[0])
                right = self.evaluate(formula.subformulas[1])
                return self.wk.disjunction(left, right)

            elif formula.connective == "->":
                left = self.evaluate(formula.subformulas[0])
                right = self.evaluate(formula.subformulas[1])
                return self.wk.implication(left, right)

            elif formula.connective == "<->":
                left = self.evaluate(formula.subformulas[0])
                right = self.evaluate(formula.subformulas[1])
                # Biconditional: (P → Q) ∧ (Q → P)
                forward = self.wk.implication(left, right)
                backward = self.wk.implication(right, left)
                return self.wk.conjunction(forward, backward)

        return UNDEFINED


class TestSemanticValidation:
    """Validate tableau results against semantic evaluation."""

    def test_simple_conjunction(self):
        """Test all truth values for P ∧ Q."""
        formula = parse("P & Q")
        evaluator = SemanticEvaluator()

        for p_val, q_val in product([TRUE, FALSE, UNDEFINED], repeat=2):
            evaluator.set_value("P", p_val)
            evaluator.set_value("Q", q_val)

            semantic_result = evaluator.evaluate(formula)

            # Check if tableau agrees
            # The tableau tests satisfiability, not direct evaluation
            # So we need to check if the formula with sign t is satisfiable
            # when the semantic value is TRUE

            if semantic_result == TRUE:
                result = solve(formula, t)
                assert (
                    result.satisfiable
                ), f"P={p_val}, Q={q_val}: semantic says true, tableau should find model"

            # Similar checks for FALSE and UNDEFINED
            # This requires more sophisticated API

    def test_simple_disjunction(self):
        """Test all truth values for P ∨ Q."""
        formula = parse("P | Q")
        evaluator = SemanticEvaluator()

        results = []
        for p_val, q_val in product([TRUE, FALSE, UNDEFINED], repeat=2):
            evaluator.set_value("P", p_val)
            evaluator.set_value("Q", q_val)

            semantic_result = evaluator.evaluate(formula)
            results.append((p_val, q_val, semantic_result))

        # Verify weak Kleene disjunction truth table
        assert (TRUE, TRUE, TRUE) in results
        assert (TRUE, FALSE, TRUE) in results
        assert (TRUE, UNDEFINED, UNDEFINED) in results  # Key weak Kleene property!
        assert (FALSE, TRUE, TRUE) in results
        assert (FALSE, FALSE, FALSE) in results
        assert (FALSE, UNDEFINED, UNDEFINED) in results
        assert (UNDEFINED, TRUE, UNDEFINED) in results
        assert (UNDEFINED, FALSE, UNDEFINED) in results
        assert (UNDEFINED, UNDEFINED, UNDEFINED) in results

    def test_implication(self):
        """Test all truth values for P → Q."""
        formula = parse("P -> Q")
        evaluator = SemanticEvaluator()

        for p_val, q_val in product([TRUE, FALSE, UNDEFINED], repeat=2):
            evaluator.set_value("P", p_val)
            evaluator.set_value("Q", q_val)

            semantic_result = evaluator.evaluate(formula)

            # Verify weak Kleene implication
            # In weak Kleene: P -> Q = UNDEFINED if either P or Q is UNDEFINED
            # UNLESS P is FALSE (then TRUE) or P is TRUE and Q is TRUE (then TRUE)
            if p_val == UNDEFINED or q_val == UNDEFINED:
                assert (
                    semantic_result == UNDEFINED
                ), f"P={p_val}, Q={q_val}: Should be UNDEFINED in weak Kleene"
            elif p_val == FALSE:
                assert (
                    semantic_result == TRUE
                ), f"P={p_val}, Q={q_val}: FALSE -> anything = TRUE"
            elif p_val == TRUE and q_val == TRUE:
                assert (
                    semantic_result == TRUE
                ), f"P={p_val}, Q={q_val}: TRUE -> TRUE = TRUE"
            elif p_val == TRUE and q_val == FALSE:
                assert (
                    semantic_result == FALSE
                ), f"P={p_val}, Q={q_val}: TRUE -> FALSE = FALSE"

    def test_negation(self):
        """Test negation for all truth values."""
        formula = parse("~P")
        evaluator = SemanticEvaluator()

        for p_val in [TRUE, FALSE, UNDEFINED]:
            evaluator.set_value("P", p_val)

            semantic_result = evaluator.evaluate(formula)

            if p_val == TRUE:
                assert semantic_result == FALSE
            elif p_val == FALSE:
                assert semantic_result == TRUE
            else:
                assert semantic_result == UNDEFINED

    def test_complex_formula(self):
        """Test a complex formula: (P ∧ Q) → (P ∨ R)."""
        formula = parse("(P & Q) -> (P | R)")
        evaluator = SemanticEvaluator()

        # This should be valid (always true) in classical logic
        # But in weak Kleene, it might not be when values are undefined

        all_true = True
        for p_val, q_val, r_val in product([TRUE, FALSE, UNDEFINED], repeat=3):
            evaluator.set_value("P", p_val)
            evaluator.set_value("Q", q_val)
            evaluator.set_value("R", r_val)

            semantic_result = evaluator.evaluate(formula)
            if semantic_result != TRUE:
                all_true = False
                # Document cases where it's not true
                if semantic_result == FALSE:
                    print(f"FALSE when P={p_val}, Q={q_val}, R={r_val}")

        # In weak Kleene, this is NOT always true
        assert not all_true, "Should not be a tautology in weak Kleene"

    def test_excluded_middle_fails(self):
        """Law of excluded middle fails in weak Kleene."""
        formula = parse("P | ~P")
        evaluator = SemanticEvaluator()

        # When P is undefined
        evaluator.set_value("P", UNDEFINED)
        semantic_result = evaluator.evaluate(formula)

        assert (
            semantic_result == UNDEFINED
        ), "P ∨ ¬P should be undefined when P is undefined"

        # Therefore it's not valid (not always true)
        # To show it's not valid, we need to check if there's a case where it's not true
        # In weak Kleene, P ∨ ¬P can be undefined (not true), but never false
        # So we check if the formula is NOT a tautology
        from wkrq import valid

        is_valid = valid(formula)
        assert not is_valid, "P ∨ ¬P should not be valid in weak Kleene logic"


class TestTableauSemanticAgreement:
    """Test that tableau and semantic evaluator agree on results."""

    @pytest.mark.skip(reason="Requires API extensions to set initial values")
    def test_random_formulas(self):
        """Generate random formulas and check tableau vs semantic evaluation."""
        # This would require:
        # 1. A way to set initial truth values in the tableau
        # 2. A way to extract the model found by the tableau
        # 3. Comparing the two evaluations
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
