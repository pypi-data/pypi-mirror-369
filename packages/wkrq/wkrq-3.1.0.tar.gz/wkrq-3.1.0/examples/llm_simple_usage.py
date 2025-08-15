#!/usr/bin/env python3
"""
Simplified LLM Integration Example

Shows how easy it is to use LLM evaluation with wKrQ.
Users only need to specify their LLM provider and model.
"""

from wkrq import (
    ACrQTableau,
    SignedFormula,
    parse_acrq_formula,
    t,
)

# Try to import LLM integration
try:
    from wkrq import create_openai_evaluator

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LLM integration not available. Install with: pip install wkrq[llm]")


def main():
    """Demonstrate simple LLM integration."""

    if not LLM_AVAILABLE:
        print("This example requires the bilateral-truth package.")
        print("Install with: pip install wkrq[llm]")
        return

    print("=" * 60)
    print("Simple LLM Integration with wKrQ")
    print("=" * 60)
    print()

    # Step 1: Create an LLM evaluator - THAT'S IT!
    # Users only specify the model they want
    print("Step 1: Create LLM evaluator (one line!)")
    print("evaluator = create_openai_evaluator(model='gpt-4')")
    print()

    # In practice, this would actually call OpenAI
    # For demo, we'll create a mock evaluator
    def mock_evaluator(formula):
        """Mock evaluator for demonstration."""
        from wkrq import FALSE, TRUE, BilateralTruthValue

        knowledge = {
            "Planet(earth)": BilateralTruthValue(TRUE, FALSE),  # Earth is a planet
            "Planet(pluto)": BilateralTruthValue(FALSE, TRUE),  # Pluto is not
            "Human(socrates)": BilateralTruthValue(TRUE, FALSE),  # Socrates is human
        }

        formula_str = str(formula).replace("*", "")
        return knowledge.get(formula_str, BilateralTruthValue(FALSE, FALSE))

    # Step 2: Use it with ACrQ tableau
    print("Step 2: Use with tableau (standard usage)")
    print()

    # Example 1: Check if Pluto is a planet
    print("Example 1: Is Pluto a planet?")
    print("-" * 40)

    formula = parse_acrq_formula("Planet(pluto)")
    tableau = ACrQTableau(
        [SignedFormula(t, formula)],
        llm_evaluator=mock_evaluator,  # Would be create_openai_evaluator() in practice
    )
    result = tableau.construct()

    print("Formula: t: Planet(pluto)")
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: LLM knows Pluto is not a planet → contradiction")
    print()

    # Example 2: Check if Earth is a planet
    print("Example 2: Is Earth a planet?")
    print("-" * 40)

    formula = parse_acrq_formula("Planet(earth)")
    tableau = ACrQTableau([SignedFormula(t, formula)], llm_evaluator=mock_evaluator)
    result = tableau.construct()

    print("Formula: t: Planet(earth)")
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: LLM confirms Earth is a planet → satisfiable")
    print()

    # Example 3: Classical syllogism with LLM knowledge
    print("Example 3: Classical Syllogism")
    print("-" * 40)

    formulas = [
        SignedFormula(t, parse_acrq_formula("[∀X Human(X)]Mortal(X)")),
        SignedFormula(t, parse_acrq_formula("Human(socrates)")),
    ]

    tableau = ACrQTableau(formulas, llm_evaluator=mock_evaluator)
    result = tableau.construct()

    print("Rules:")
    print("  [∀X Human(X)]Mortal(X)  (All humans are mortal)")
    print("  Human(socrates)         (Socrates is human)")
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: LLM confirms Socrates is human, formal logic derives mortality")
    print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("With bilateral-truth package installed:")
    print("1. Import: from wkrq import create_openai_evaluator")
    print("2. Create: evaluator = create_openai_evaluator(model='gpt-4')")
    print("3. Use: ACrQTableau(formulas, llm_evaluator=evaluator)")
    print()
    print("That's it! The bilateral-truth package handles:")
    print("- LLM API connections")
    print("- Prompt engineering")
    print("- Response parsing")
    print("- Error handling")
    print("- Caching")
    print()
    print("Supported providers:")
    print("- OpenAI (GPT-3.5, GPT-4, etc.)")
    print("- Anthropic (Claude)")
    print("- Google (Gemini)")
    print("- Local models (Ollama, etc.)")


if __name__ == "__main__":
    main()
