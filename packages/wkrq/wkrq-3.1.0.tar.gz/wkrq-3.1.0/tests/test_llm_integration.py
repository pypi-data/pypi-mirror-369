#!/usr/bin/env python3
"""Tests for LLM integration with ACrQ tableau."""

from wkrq import (
    FALSE,
    TRUE,
    ACrQTableau,
    BilateralPredicateFormula,
    BilateralTruthValue,
    Constant,
    PredicateFormula,
    SignedFormula,
    f,
    t,
)


class TestBasicLLMIntegration:
    """Test basic LLM evaluator functionality."""

    def test_llm_positive_evidence(self):
        """Test LLM providing positive evidence."""

        def llm_evaluator(formula):
            if str(formula) == "Human(socrates)":
                return BilateralTruthValue(positive=TRUE, negative=FALSE)
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        socrates = Constant("socrates")
        human = PredicateFormula("Human", [socrates])

        # t:Human(socrates) should be satisfiable with LLM confirmation
        tableau = ACrQTableau([SignedFormula(t, human)], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        assert result.satisfiable
        assert len(result.models) == 1
        model = result.models[0]
        assert str(model.valuations.get("Human(socrates)")) == "t"

    def test_llm_negative_evidence(self):
        """Test LLM providing negative evidence."""

        def llm_evaluator(formula):
            if str(formula) == "Robot(socrates)":
                return BilateralTruthValue(positive=FALSE, negative=TRUE)
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        socrates = Constant("socrates")
        robot = PredicateFormula("Robot", [socrates])

        # t:Robot(socrates) should be unsatisfiable with LLM refutation
        tableau = ACrQTableau([SignedFormula(t, robot)], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        assert not result.satisfiable
        assert result.closed_branches == 1

    def test_llm_knowledge_gap(self):
        """Test LLM returning knowledge gap (no evidence)."""

        def llm_evaluator(formula):
            # Always return gap
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        unknown = Constant("unknown")
        predicate = PredicateFormula("Mystery", [unknown])

        # t:Mystery(unknown) with gap should close
        # (gap means cannot verify, which contradicts t)
        tableau_t = ACrQTableau(
            [SignedFormula(t, predicate)], llm_evaluator=llm_evaluator
        )
        result_t = tableau_t.construct()
        assert not result_t.satisfiable

        # f:Mystery(unknown) with gap should be satisfiable
        # (gap is consistent with f)
        tableau_f = ACrQTableau(
            [SignedFormula(f, predicate)], llm_evaluator=llm_evaluator
        )
        result_f = tableau_f.construct()
        assert result_f.satisfiable


class TestLLMWithBilateralPredicates:
    """Test LLM integration with bilateral predicates."""

    def test_llm_glut_with_bilateral(self):
        """Test LLM returning glut (conflicting evidence)."""

        def llm_evaluator(formula):
            # Need to handle both Flying and Flying*
            formula_str = str(formula)
            if formula_str == "Flying(tweety)" or formula_str == "Flying*(tweety)":
                # Both positive and negative evidence
                return BilateralTruthValue(positive=TRUE, negative=TRUE)
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        tweety = Constant("tweety")
        flying = PredicateFormula("Flying", [tweety])

        # t:Flying(tweety) with glut should be satisfiable in ACrQ
        tableau = ACrQTableau([SignedFormula(t, flying)], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        # This should be satisfiable because ACrQ allows gluts
        assert result.satisfiable, "ACrQ should allow gluts from LLM"
        assert len(result.models) == 1

        # The model should show both Flying(tweety) and Flying*(tweety) as true
        model = result.models[0]
        assert "Flying(tweety)" in str(model) or "Flying" in str(model)

    def test_bilateral_predicate_direct(self):
        """Test LLM with explicit bilateral predicates."""

        def llm_evaluator(formula):
            # Should understand bilateral predicates
            formula_str = str(formula)
            if "Human" in formula_str:
                # Human is definitely true, not robot
                if "*" in formula_str:
                    # Human* should be false
                    return BilateralTruthValue(positive=FALSE, negative=TRUE)
                else:
                    # Human should be true
                    return BilateralTruthValue(positive=TRUE, negative=FALSE)
            return BilateralTruthValue(positive=FALSE, negative=FALSE)

        socrates = Constant("socrates")
        human_pos = BilateralPredicateFormula(
            positive_name="Human", terms=[socrates], is_negative=False
        )
        human_neg = BilateralPredicateFormula(
            positive_name="Human", terms=[socrates], is_negative=True
        )

        # t:Human(socrates) should be satisfiable
        tableau1 = ACrQTableau(
            [SignedFormula(t, human_pos)], llm_evaluator=llm_evaluator
        )
        result1 = tableau1.construct()
        assert result1.satisfiable

        # t:Human*(socrates) should be unsatisfiable
        tableau2 = ACrQTableau(
            [SignedFormula(t, human_neg)], llm_evaluator=llm_evaluator
        )
        result2 = tableau2.construct()
        assert not result2.satisfiable


class TestLLMErrorHandling:
    """Test error handling in LLM integration."""

    def test_llm_exception_handling(self):
        """Test that LLM exceptions don't crash the tableau."""

        def failing_llm(formula):
            raise RuntimeError("LLM service unavailable")

        atom = PredicateFormula("P", [Constant("a")])

        # Should still work without LLM when it fails
        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=failing_llm)
        result = tableau.construct()

        # Should be satisfiable since LLM failure means no additional constraints
        assert result.satisfiable
        assert len(result.models) == 1

    def test_llm_returns_none(self):
        """Test LLM returning None."""

        def none_llm(formula):
            return None

        atom = PredicateFormula("P", [Constant("a")])

        # Should handle None gracefully
        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=none_llm)
        result = tableau.construct()

        # Should be satisfiable since None means no additional constraints
        assert result.satisfiable
