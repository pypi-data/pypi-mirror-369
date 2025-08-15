#!/usr/bin/env python3
"""
Real LLM Integration Demo for ACrQ

This demonstrates the actual behavior of LLM integration with real API keys.
The LLM evaluation shows interesting patterns in how formal vs natural language
assertions are interpreted.
"""

import os

from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

from wkrq import ACrQTableau, SignedFormula, parse_acrq_formula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.llm_integration import create_llm_tableau_evaluator


def demo_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_basic_facts():
    """Test basic factual knowledge."""
    demo_header("Basic Factual Knowledge")

    # Create evaluator using Claude Sonnet
    evaluator = create_llm_tableau_evaluator(
        "anthropic", model="claude-3-5-sonnet-20241022"
    )
    if not evaluator:
        print("No LLM evaluator available")
        return

    print("\nTesting how Claude Sonnet evaluates basic facts:")

    facts = [
        ("Earth is a planet", "Planet(earth)", True),
        ("Moon is not a planet", "~Planet(moon)", True),
        ("Penguins cannot fly", "~CanFly(penguin)", True),
        ("Water is H2O", "ChemicalFormula(water, H2O)", True),
    ]

    for description, formula_str, expected_sat in facts:
        print(f"\n{description}:")
        formula = parse_acrq_formula(formula_str)
        tableau = ACrQTableau([SignedFormula(t, formula)], llm_evaluator=evaluator)
        result = tableau.construct()

        status = "✓" if (result.satisfiable == expected_sat) else "✗"
        print(f"  Formula: t: {formula_str}")
        print(f"  Result:  {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
        print(
            f"  {status} {'As expected' if result.satisfiable == expected_sat else 'Unexpected'}"
        )


def test_formal_vs_natural():
    """Show difference between formal and natural language."""
    demo_header("Formal Notation vs Natural Language")

    evaluator = create_llm_tableau_evaluator(
        "anthropic", model="claude-3-5-sonnet-20241022"
    )
    if not evaluator:
        print("No LLM evaluator available")
        return

    print("\nThe LLM may interpret formal notation differently than natural language.")
    print("This is an important consideration for ACrQ-LLM integration.\n")

    # Direct comparison
    from bilateral_truth import Assertion, create_llm_evaluator

    bt_evaluator = create_llm_evaluator("anthropic", model="claude-3-5-sonnet-20241022")

    comparisons = [
        ("Planet(pluto)", "Pluto is a planet"),
        ("Star(sun)", "The Sun is a star"),
        ("CanFly(penguin)", "Penguins can fly"),
    ]

    for formal, natural in comparisons:
        print(f"\nComparing: {formal} vs '{natural}'")

        # Test formal notation
        formal_assertion = Assertion(formal)
        formal_result = bt_evaluator.evaluate_bilateral(formal_assertion)

        # Test natural language
        natural_assertion = Assertion(natural)
        natural_result = bt_evaluator.evaluate_bilateral(natural_assertion)

        print(f"  Formal:  {formal_result}")
        print(f"  Natural: {natural_result}")

        if formal_result != natural_result:
            print("  ⚠ Different interpretations!")


def test_inference_with_llm():
    """Test logical inference combined with LLM knowledge."""
    demo_header("Logical Inference + LLM Knowledge")

    evaluator = create_llm_tableau_evaluator(
        "anthropic", model="claude-3-5-sonnet-20241022"
    )
    if not evaluator:
        print("No LLM evaluator available")
        return

    print("\nScenario: All birds fly, penguins are birds")
    print("Formal logic says: Penguins fly")
    print("Claude knows: Penguins don't fly")
    print("Result: Contradiction!\n")

    # Create the inference
    rule = parse_acrq_formula("[∀x Bird(x)]Flies(x)")
    fact = parse_acrq_formula("Bird(penguin)")
    claim = parse_acrq_formula("Flies(penguin)")

    formulas = [SignedFormula(t, rule), SignedFormula(t, fact), SignedFormula(t, claim)]

    tableau = ACrQTableau(formulas, llm_evaluator=evaluator)
    result = tableau.construct()

    print("Formulas:")
    print("  1. [∀x Bird(x)]Flies(x)  (All birds fly)")
    print("  2. Bird(penguin)         (Penguins are birds)")
    print("  3. Flies(penguin)        (Claim: Penguins fly)")

    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")

    if not result.satisfiable:
        print("\n✓ Correct! Claude's knowledge creates a contradiction")
        print("  with the formal rule, making the scenario unsatisfiable.")

    # Show tableau
    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    print("\nTableau tree:")
    tree_lines = renderer.render_ascii(result.tableau).split("\n")[:15]
    print("\n".join(tree_lines))
    if len(renderer.render_ascii(result.tableau).split("\n")) > 15:
        print("... (truncated)")


def main():
    """Run the full demo."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print(
        "█" + "  ACrQ with Real LLM Integration Demo (Claude Sonnet)  ".center(68) + "█"
    )
    print("█" + " " * 68 + "█")
    print("█" * 70)

    # Check for API keys
    if not any(
        [
            os.getenv("OPENAI_API_KEY"),
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
        ]
    ):
        print("\n⚠ No API keys found in environment")
        print("  Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")
        print("  The demo will use mock evaluator instead")
    else:
        print("\n✓ API keys loaded from .env file")
        print("  Using Claude 3 Sonnet for evaluation")

    # Run demos
    test_basic_facts()
    test_formal_vs_natural()
    test_inference_with_llm()

    # Summary
    demo_header("Summary")
    print("\nKey observations from real LLM integration:")
    print("• LLMs may interpret formal notation differently than natural language")
    print("• The bilateral-truth package handles uncertainty via <u,v> pairs")
    print("• ACrQ's bilateral predicates naturally handle LLM responses")
    print("• Conflicts between formal rules and LLM knowledge create contradictions")
    print("• This creates a hybrid formal-empirical reasoning system")
    print("\nThe ACrQ-LLM integration enables reasoning that combines:")
    print("• Formal logical rules (tableau calculus)")
    print("• Real-world knowledge (LLM evaluation)")
    print("• Paraconsistent handling of conflicts (ACrQ bilateral predicates)")


if __name__ == "__main__":
    main()
