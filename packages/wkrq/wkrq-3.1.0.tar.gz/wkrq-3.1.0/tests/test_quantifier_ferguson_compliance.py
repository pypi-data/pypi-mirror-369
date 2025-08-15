"""
Test quantifier rules against Ferguson's Definition 9 specification.

This module tests whether our simplified quantifier implementation
is logically equivalent to Ferguson's complex rules with m/n signs.
"""

import pytest

from wkrq import e, f, solve, t
from wkrq.formula import (
    Constant,
    PredicateFormula,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Variable,
)
from wkrq.signs import SignedFormula
from wkrq.wkrq_rules import (
    get_restricted_existential_rule,
    get_restricted_universal_rule,
)


class TestUniversalQuantifierCompliance:
    """Test universal quantifier rules against Ferguson Definition 9."""

    def test_t_universal_ferguson_spec(self):
        """
        Ferguson: t:[∀xP(x)]Q(x) → m:P(c) ○ m:Q(c) ○ (n:P(a) + t:Q(a))

        This should create a complex branching structure with m and n signs.
        Our implementation simplifies to: f:P(c) | t:Q(c)

        Need to verify if these are logically equivalent.
        """
        # Create the formula [∀xP(x)]Q(x)
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedUniversalFormula(x, p_x, q_x)
        signed = SignedFormula(t, formula)

        # Get the rule
        c1 = Constant("c1")
        rule = get_restricted_universal_rule(signed, c1)

        assert rule is not None
        assert rule.name == "t-restricted-forall"

        # Our implementation has 2 branches: f:P(c) | t:Q(c)
        assert len(rule.conclusions) == 2

        # Check if this matches the semantic intention
        # Ferguson's rule with m and n would eventually branch to similar cases
        # m:P(c) branches to t:P(c) | f:P(c)
        # m:Q(c) branches to t:Q(c) | f:Q(c)
        # n:P(a) branches to f:P(a) | e:P(a)
        # The combination would create many branches

        # Our simplification captures the main cases but may miss edge cases

    def test_f_universal_matches_ferguson(self):
        """
        Ferguson: f:[∀xP(x)]Q(x) → t:P(c) ○ f:Q(c)

        This should match exactly - counterexample case.
        """
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedUniversalFormula(x, p_x, q_x)
        signed = SignedFormula(f, formula)

        c1 = Constant("c1")
        rule = get_restricted_universal_rule(signed, c1)

        assert rule is not None
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 2  # Both on same branch

        # Should be t:P(c) and f:Q(c) on same branch
        p_c = p_x.substitute_term({"x": c1})
        q_c = q_x.substitute_term({"x": c1})
        assert SignedFormula(t, p_c) in rule.conclusions[0]
        assert SignedFormula(f, q_c) in rule.conclusions[0]

    def test_e_universal_matches_ferguson(self):
        """
        Ferguson: e:[∀xP(x)]Q(x) → e:P(a) + e:Q(a)

        Error propagation case with branching.
        """
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedUniversalFormula(x, p_x, q_x)
        signed = SignedFormula(e, formula)

        c1 = Constant("c1")
        rule = get_restricted_universal_rule(signed, c1)

        assert rule is not None
        assert len(rule.conclusions) == 2  # Two branches

        # Each branch should have one formula with e sign
        p_c = p_x.substitute_term({"x": c1})
        q_c = q_x.substitute_term({"x": c1})
        assert rule.conclusions[0] == [SignedFormula(e, p_c)]
        assert rule.conclusions[1] == [SignedFormula(e, q_c)]


class TestExistentialQuantifierCompliance:
    """Test existential quantifier rules against Ferguson Definition 9."""

    def test_t_existential_matches_ferguson(self):
        """
        Ferguson: t:[∃xP(x)]Q(x) → t:P(c) ○ t:Q(c)

        Simple case - both must be true with witness c.
        """
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedExistentialFormula(x, p_x, q_x)
        signed = SignedFormula(t, formula)

        c1 = Constant("c1")
        rule = get_restricted_existential_rule(signed, c1)

        assert rule is not None
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 2  # Both on same branch

        p_c = p_x.substitute_term({"x": c1})
        q_c = q_x.substitute_term({"x": c1})
        assert SignedFormula(t, p_c) in rule.conclusions[0]
        assert SignedFormula(t, q_c) in rule.conclusions[0]

    def test_f_existential_complex_rule(self):
        """
        Ferguson: f:[∃xP(x)]Q(x) → m:P(c) ○ m:Q(c) ○ (n:P(a) + n:Q(a))

        Complex rule with two constants and m/n signs.
        """
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedExistentialFormula(x, p_x, q_x)
        signed = SignedFormula(f, formula)

        c1 = Constant("c1")
        c2 = Constant("c2")  # Second constant for 'a' in Ferguson
        rule = get_restricted_existential_rule(signed, c1, c2)

        assert rule is not None
        # This rule should have complex branching with m and n signs
        # Our implementation may simplify this

    def test_e_existential_error_branching(self):
        """
        Ferguson: e:[∃xP(x)]Q(x) → e:P(a) + e:Q(a)

        Error propagation with branching.
        """
        x = Variable("x")
        p_x = PredicateFormula("P", [x])
        q_x = PredicateFormula("Q", [x])
        formula = RestrictedExistentialFormula(x, p_x, q_x)
        signed = SignedFormula(e, formula)

        c1 = Constant("c1")
        rule = get_restricted_existential_rule(signed, c1)

        assert rule is not None
        assert len(rule.conclusions) == 2  # Two branches

        p_c = p_x.substitute_term({"x": c1})
        q_c = q_x.substitute_term({"x": c1})
        assert rule.conclusions[0] == [SignedFormula(e, p_c)]
        assert rule.conclusions[1] == [SignedFormula(e, q_c)]


class TestQuantifierSimplificationEquivalence:
    """Test if our simplifications are logically equivalent to Ferguson's rules."""

    @pytest.mark.skip(reason="Need to implement semantic equivalence checking")
    def test_t_universal_simplification_sound(self):
        """
        Verify that our simplification of t-universal is sound.

        Ferguson: m:P(c) ○ m:Q(c) ○ (n:P(a) + t:Q(a))
        Ours: f:P(c) | t:Q(c)

        Need to check if these produce equivalent results.
        """
        # This would require implementing the full Ferguson rules
        # and comparing tableau outcomes
        pass

    def test_quantifier_examples_from_paper(self):
        """Test examples mentioned in Ferguson's paper."""
        # "All dogs are mammals" type examples
        # These should work correctly even with our simplifications

        # [∀x Dog(x)]Mammal(x) - "All dogs are mammals"
        # Note: Our parser uses different syntax
        from wkrq.formula import PredicateFormula, RestrictedUniversalFormula, Variable

        x = Variable("x")
        dog_x = PredicateFormula("Dog", [x])
        mammal_x = PredicateFormula("Mammal", [x])
        formula = RestrictedUniversalFormula(x, dog_x, mammal_x)

        # This should be satisfiable when true
        result = solve(formula, t)
        assert result.satisfiable

        # Test with counterexample
        result = solve(formula, f)
        # Should find a model where Dog(c) is true but Mammal(c) is false
        assert result.satisfiable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
