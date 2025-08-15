#!/usr/bin/env python3
"""
Simple demonstration of LLM evaluation with ACrQ tableau.
Shows how to use the bilateral-truth package for real-world knowledge integration.

REQUIRES: bilateral-truth package and configured LLM API key
Install with: pip install bilateral-truth
Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY
"""

from wkrq import ACrQTableau, SignedFormula, SyntaxMode, parse_acrq_formula, t
from wkrq.cli import TableauTreeRenderer


def get_llm_evaluator():
    """Get the LLM evaluator from bilateral-truth package."""
    try:
        from wkrq.llm_integration import create_llm_tableau_evaluator

        # Use the proper wkrq integration that handles bilateral-truth correctly
        llm_evaluator = create_llm_tableau_evaluator("mock")  # Uses mock if no API key

        if llm_evaluator:
            print("✓ Using bilateral-truth LLM evaluator (via wkrq integration)")
            return llm_evaluator
        else:
            print("✗ Could not create LLM evaluator")
            return None

    except ImportError:
        print("ERROR: bilateral-truth package not found")
        print("This demo REQUIRES the bilateral-truth package.")
        print("Install with: pip install bilateral-truth")
        print("\nThen set your LLM API key:")
        print("  export OPENAI_API_KEY=your-key")
        print("  # or")
        print("  export ANTHROPIC_API_KEY=your-key")
        print("  # or")
        print("  export GOOGLE_API_KEY=your-key")
        return None
    except Exception as e:
        print(f"ERROR: Could not create LLM evaluator: {e}")
        print("\nMake sure you have set your LLM API key:")
        print("  export OPENAI_API_KEY=your-key")
        print("  # or")
        print("  export ANTHROPIC_API_KEY=your-key")
        print("  # or")
        print("  export GOOGLE_API_KEY=your-key")
        return None


def test_simple_contradiction():
    """Test: Assert Tweety flies, but LLM knows penguins don't fly."""
    print("=" * 70)
    print("TEST 1: Simple Contradiction")
    print("=" * 70)

    # Get the LLM evaluator from bilateral-truth
    llm_evaluator = get_llm_evaluator()
    if not llm_evaluator:
        print("Cannot run test without LLM evaluator")
        return

    print("\nSetup:")
    print("  Formal assertion: t: Flies(tweety)")
    print("  LLM knowledge: Real-world knowledge about penguins")
    print("\nExpected: Result depends on LLM's knowledge")
    print()

    # Create tableau with single assertion
    formula = parse_acrq_formula("Flies(tweety)", SyntaxMode.TRANSPARENT)
    signed = SignedFormula(t, formula)

    tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator, trace=True)
    result = tableau.construct()

    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))

    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")

    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")


def test_complex_reasoning():
    """Test: Formal rules + LLM knowledge."""
    print("\n" + "=" * 70)
    print("TEST 2: Formal Rules + LLM Knowledge")
    print("=" * 70)

    # Get the LLM evaluator from bilateral-truth
    llm_evaluator = get_llm_evaluator()
    if not llm_evaluator:
        print("Cannot run test without LLM evaluator")
        return

    print("\nSetup:")
    print("  Rule: [∀X Penguin(X)]~Flies(X)  (penguins don't fly)")
    print("  Fact: Penguin(tweety)")
    print("  Claim: Flies(tweety)")
    print("  LLM: Will evaluate based on real-world knowledge")
    print("\nExpected: Formal logic and LLM should agree on contradiction")
    print()

    # Create formulas
    rule = parse_acrq_formula("[∀X Penguin(X)]~Flies(X)", SyntaxMode.TRANSPARENT)
    fact = parse_acrq_formula("Penguin(tweety)", SyntaxMode.TRANSPARENT)
    claim = parse_acrq_formula("Flies(tweety)", SyntaxMode.TRANSPARENT)

    signed_formulas = [
        SignedFormula(t, rule),
        SignedFormula(t, fact),
        SignedFormula(t, claim),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator, trace=True)
    result = tableau.construct()

    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))

    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")

    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")


def test_knowledge_gap():
    """Test: LLM has no knowledge about something."""
    print("\n" + "=" * 70)
    print("TEST 3: Knowledge Gap")
    print("=" * 70)

    # Get the LLM evaluator from bilateral-truth
    llm_evaluator = get_llm_evaluator()
    if not llm_evaluator:
        print("Cannot run test without LLM evaluator")
        return

    print("\nSetup:")
    print("  Assertion: t: Flies(xyzzy123)")
    print("  LLM knowledge: Unlikely to have information about 'xyzzy123'")
    print("\nExpected: Result depends on LLM's response to unknown entity")
    print()

    formula = parse_acrq_formula("Flies(xyzzy123)", SyntaxMode.TRANSPARENT)
    signed = SignedFormula(t, formula)

    tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator, trace=True)
    result = tableau.construct()

    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))

    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")

    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")

    print("\nNote: A knowledge gap means the LLM cannot determine truth or falsity")
    print("      This is represented as both positive and negative being false")


def test_planet_classification():
    """Test: Planet classification example."""
    print("\n" + "=" * 70)
    print("TEST 4: Planet Classification")
    print("=" * 70)

    # Get the LLM evaluator from bilateral-truth
    llm_evaluator = get_llm_evaluator()
    if not llm_evaluator:
        print("Cannot run test without LLM evaluator")
        return

    print("\nTesting planetary status with LLM knowledge:")

    # Test Earth (should be satisfiable)
    print("\n1. Earth:")
    earth_formula = parse_acrq_formula("Planet(earth)", SyntaxMode.TRANSPARENT)
    earth_tableau = ACrQTableau(
        [SignedFormula(t, earth_formula)], llm_evaluator=llm_evaluator
    )
    earth_result = earth_tableau.construct()
    print("   t: Planet(earth)")
    print(
        f"   Result: {'SATISFIABLE' if earth_result.satisfiable else 'UNSATISFIABLE'}"
    )
    print("   (LLM should confirm Earth is a planet)")

    # Test Pluto (should be unsatisfiable)
    print("\n2. Pluto:")
    pluto_formula = parse_acrq_formula("Planet(pluto)", SyntaxMode.TRANSPARENT)
    pluto_tableau = ACrQTableau(
        [SignedFormula(t, pluto_formula)], llm_evaluator=llm_evaluator
    )
    pluto_result = pluto_tableau.construct()
    print("   t: Planet(pluto)")
    print(
        f"   Result: {'SATISFIABLE' if pluto_result.satisfiable else 'UNSATISFIABLE'}"
    )
    print("   (LLM should know Pluto was reclassified in 2006)")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ACrQ with bilateral-truth LLM Integration")
    print("=" * 70)
    print("\nThis demo shows how ACrQ integrates with real-world knowledge")
    print("via the bilateral-truth package's LLM evaluator.\n")

    test_simple_contradiction()
    test_complex_reasoning()
    test_knowledge_gap()
    test_planet_classification()

    print("\n" + "=" * 70)
    print("  End of Demo")
    print("=" * 70)
