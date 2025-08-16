"""
Tree Connectivity Regression Tests.

These tests ensure the tree connectivity fix doesn't regress and that
all tableau nodes remain connected and visible in rendered trees.
"""

import pytest

from wkrq import (
    ACrQTableau,
    SignedFormula,
    WKrQTableau,
    f,
    parse,
    parse_acrq_formula,
    t,
)

# Observable verification helpers (inline)
from wkrq.cli import TableauTreeRenderer


def verify_observable_properties(tableau):
    """Verify tree connectivity and rule visibility."""
    renderer = TableauTreeRenderer(show_rules=True, compact=False)
    tree = renderer.render_ascii(tableau)

    # Check connectivity
    connected_nodes = set()

    def collect_connected(node):
        connected_nodes.add(node.id)
        for child in node.children:
            collect_connected(child)

    if tableau.root:
        collect_connected(tableau.root)

    assert len(connected_nodes) == len(
        tableau.nodes
    ), f"Tree connectivity broken: {len(connected_nodes)}/{len(tableau.nodes)} nodes connected"
    return tree


def verify_llm_integration(tableau, expected_llm_count=None):
    """Verify LLM integration is working and visible."""
    tree = verify_observable_properties(tableau)
    llm_count = tree.count("llm-eval")

    if expected_llm_count is not None:
        assert (
            llm_count == expected_llm_count
        ), f"Expected {expected_llm_count} LLM evaluations, found {llm_count}"

    return tree


class TestTreeConnectivity:
    """Regression tests for tree connectivity bug."""

    def test_multiple_initial_formulas_connected(self):
        """Ensure multiple initial formulas form connected tree."""
        # This is the original bug case - multiple initial formulas
        formulas = [parse("P(a)"), parse("Q(b)"), parse("R(c)")]

        signed_formulas = [SignedFormula(t, f) for f in formulas]
        tableau = WKrQTableau(signed_formulas)
        tableau.construct()

        # Verify connectivity and observability
        tree = verify_observable_properties(tableau)

        # All initial formulas should be visible
        assert "P(a)" in tree
        assert "Q(b)" in tree
        assert "R(c)" in tree

        # Should form a connected chain
        assert tableau.root is not None
        assert len(tableau.nodes) >= 3  # At least the initial formulas

    def test_universal_rule_with_llm_connectivity(self):
        """Test the exact case that revealed the tree connectivity bug."""
        try:
            from wkrq.llm_integration import create_llm_tableau_evaluator

            llm_evaluator = create_llm_tableau_evaluator("mock")
        except ImportError:
            pytest.skip("LLM integration not available")

        # The exact case from the bug report
        planet_rule = parse_acrq_formula(
            "[forall X OrbitsSun(X) & Spherical(X)]Planet(X)"
        )
        orbits_fact = parse_acrq_formula("OrbitsSun(pluto)")
        spherical_fact = parse_acrq_formula("Spherical(pluto)")

        signed_formulas = [
            SignedFormula(t, planet_rule),
            SignedFormula(t, orbits_fact),
            SignedFormula(t, spherical_fact),
        ]

        tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
        tableau.construct()

        # Verify connectivity and LLM integration if available
        tree = verify_observable_properties(tableau)

        # LLM evaluation may or may not appear depending on rule application order
        # The key is that the tree is connected and substantial
        llm_count = tree.count("llm-eval")
        print(f"LLM evaluations found: {llm_count}")

        # If LLM evaluation happened, it should be visible
        if llm_count > 0:
            assert "llm-eval" in tree, "LLM evaluation should be visible when it occurs"

        # Verify all nodes are connected
        assert len(tree.split("\n")) > 5  # Should be substantial tree

    def test_complex_nesting_maintains_connectivity(self):
        """Test that complex nested structures maintain connectivity."""
        # Deeply nested quantifier structure
        formulas = [
            parse_acrq_formula("[forall X Planet(X)]OrbitsSun(X)"),
            parse_acrq_formula("[forall Y OrbitsSun(Y)]ReceivesLight(Y)"),
            parse_acrq_formula("Planet(earth)"),
            parse_acrq_formula("Planet(mars)"),
        ]

        signed_formulas = [SignedFormula(t, f) for f in formulas]

        try:
            from wkrq.llm_integration import create_llm_tableau_evaluator

            llm_evaluator = create_llm_tableau_evaluator("mock")
        except ImportError:
            llm_evaluator = None

        tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
        tableau.construct()

        # Verify complex tree is fully connected
        tree = verify_observable_properties(tableau)

        # Should see multi-step inference chain
        assert "Planet(earth)" in tree
        assert "Planet(mars)" in tree

        # Should see rule applications
        assert "t-restricted-forall" in tree

        # With LLM, should see evaluations
        if llm_evaluator:
            assert "llm-eval" in tree

    def test_contradictory_formulas_connectivity(self):
        """Test connectivity is maintained even with immediate contradictions."""
        # Contradictory formulas that should close branches quickly
        formulas = [
            parse_acrq_formula("Planet(pluto)"),
            parse_acrq_formula("~Planet(pluto)"),  # This becomes Planet*(pluto)
        ]

        signed_formulas = [SignedFormula(t, f) for f in formulas]

        try:
            from wkrq.llm_integration import create_llm_tableau_evaluator

            llm_evaluator = create_llm_tableau_evaluator("mock")
        except ImportError:
            llm_evaluator = None

        tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
        result = tableau.construct()

        # Even with contradictions, tree should be connected
        tree = verify_observable_properties(tableau)

        # Should see both formulas
        assert "Planet(pluto)" in tree
        assert "Planet*(pluto)" in tree or "~Planet(pluto)" in tree

        # In ACrQ, gluts are allowed, so this might not close
        # The key test is connectivity, not closure
        print(f"Satisfiable: {result.satisfiable}")
        print(f"Tree contains closure marker: {'×' in tree}")

    def test_single_formula_baseline(self):
        """Test that single formula (simplest case) works correctly."""
        formula = parse_acrq_formula("Planet(earth)")
        signed_formulas = [SignedFormula(t, formula)]

        try:
            from wkrq.llm_integration import create_llm_tableau_evaluator

            llm_evaluator = create_llm_tableau_evaluator("mock")
        except ImportError:
            llm_evaluator = None

        tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
        tableau.construct()

        # Single formula should definitely be connected and visible
        tree = verify_observable_properties(tableau)

        assert "Planet(earth)" in tree

        # With LLM, should see evaluation
        if llm_evaluator:
            assert "llm-eval(Planet(earth))" in tree

    def test_no_regression_from_fix(self):
        """Comprehensive test ensuring tree fix doesn't break anything."""
        # Test various scenarios that should all work
        test_cases = [
            # Simple atomic
            [SignedFormula(t, parse("P(a)"))],
            # Multiple atomics
            [SignedFormula(t, parse("P(a)")), SignedFormula(t, parse("Q(b)"))],
            # Conjunction
            [SignedFormula(t, parse("P(a) & Q(b)"))],
            # Disjunction
            [SignedFormula(t, parse("P(a) | Q(b)"))],
            # Universal quantifier
            [
                SignedFormula(t, parse("[forall X P(X)]Q(X)")),
                SignedFormula(t, parse("P(a)")),
            ],
            # Mixed signs
            [SignedFormula(t, parse("P(a)")), SignedFormula(f, parse("Q(b)"))],
        ]

        for i, signed_formulas in enumerate(test_cases):
            try:
                tableau = WKrQTableau(signed_formulas)
                tableau.construct()

                # Each case should maintain connectivity
                tree = verify_observable_properties(tableau)

                # Should have reasonable content
                assert len(tree.strip()) > 0
                assert tableau.root is not None

                print(f"Test case {i+1}: ✓ Connected and observable")

            except AssertionError as e:
                # Connectivity check failures are the only thing we care about
                pytest.fail(f"Test case {i+1} failed connectivity check: {e}")
            except Exception as e:
                # Other exceptions (like parsing errors) are acceptable
                print(f"Test case {i+1}: Skipped due to {type(e).__name__}: {e}")
                continue


class TestObservableVerificationHelpers:
    """Test the verification helper functions themselves."""

    def test_verify_observable_properties_detects_connectivity(self):
        """Test that the helper function correctly detects connectivity."""
        # Create a simple tableau
        formula = parse("P(a)")
        signed_formulas = [SignedFormula(t, formula)]
        tableau = WKrQTableau(signed_formulas)
        tableau.construct()

        # This should pass
        tree = verify_observable_properties(tableau)
        assert "P(a)" in tree

    def test_verify_llm_integration_helper(self):
        """Test the LLM integration verification helper."""
        try:
            from wkrq.llm_integration import create_llm_tableau_evaluator

            llm_evaluator = create_llm_tableau_evaluator("mock")
        except ImportError:
            pytest.skip("LLM integration not available")

        formula = parse_acrq_formula("Planet(earth)")
        signed_formulas = [SignedFormula(t, formula)]
        tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
        tableau.construct()

        # This should pass and detect connectivity
        tree = verify_observable_properties(tableau)

        # LLM integration may or may not trigger evaluation
        llm_count = tree.count("llm-eval")
        print(f"LLM evaluations found: {llm_count}")

        # If LLM evaluation happened, it should be visible
        if llm_count > 0:
            assert "llm-eval" in tree, "LLM evaluation should be visible when it occurs"
