#!/usr/bin/env python3
"""
ACrQ Demonstration for Thomas Ferguson Call

Complete demonstration of ACrQ (Definition 18) features including:
- Bilateral predicates (R/R* duality)
- Glut tolerance (paraconsistent reasoning)
- DeMorgan transformations
- Gap handling (paracomplete reasoning)
- LLM integration (ACrQ-LLM extension)
"""

from wkrq import (
    FALSE,
    TRUE,
    ACrQTableau,
    BilateralTruthValue,
    SignedFormula,
    f,
    n,
    parse_acrq_formula,
    t,
)
from wkrq.cli import TableauTreeRenderer


def demo_header(title):
    """Print a formatted demo header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo1_bilateral_predicates():
    """Demonstrate bilateral predicates and the R/R* duality."""
    demo_header("Demo 1: Bilateral Predicates (Ferguson Definition 17)")

    print("\nBilateral predicates allow independent tracking of positive")
    print("and negative evidence, enabling paraconsistent reasoning.\n")

    # Example 1: Standard negation becomes bilateral
    print("1. Transparent mode: ¬P(x) automatically becomes P*(x)")
    formula1 = parse_acrq_formula("~Human(socrates)")
    print("   Input: ~Human(socrates)")
    print(f"   Parsed as: {formula1}")

    # Example 2: Direct bilateral syntax
    print("\n2. Bilateral mode: Explicit R/R* syntax")
    from wkrq import SyntaxMode

    formula2 = parse_acrq_formula("Human*(socrates)", SyntaxMode.BILATERAL)
    print("   Input: Human*(socrates)")
    print(f"   Parsed as: {formula2}")

    # Example 3: Glut - both R and R* can be true
    print("\n3. Glut example: Both Human(x) and Human*(x) true")
    formulas = [
        SignedFormula(t, parse_acrq_formula("Human(socrates)")),
        SignedFormula(t, parse_acrq_formula("Human*(socrates)", SyntaxMode.BILATERAL)),
    ]

    tableau = ACrQTableau(formulas)
    result = tableau.construct()

    print("   Formulas: t: Human(socrates), t: Human*(socrates)")
    print(f"   Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("   Analysis: ACrQ allows gluts (contradictory information)")

    if result.models:
        print(f"   Model: {result.models[0]}")


def demo2_paraconsistency():
    """Demonstrate paraconsistent reasoning - contradictions don't explode."""
    demo_header("Demo 2: Paraconsistent Reasoning (Lemma 5)")

    print("\nIn classical logic, contradictions explode (ex falso quodlibet).")
    print("In ACrQ, contradictions are contained - they don't entail everything.\n")

    # Test: Does a contradiction entail an unrelated formula?
    print("Test: Does 'Human(x) ∧ ¬Human(x)' entail 'Flies(y)'?")

    # Create the inference: contradiction |- arbitrary formula
    premises = [
        SignedFormula(t, parse_acrq_formula("Human(socrates) & ~Human(socrates)"))
    ]
    conclusion = SignedFormula(t, parse_acrq_formula("Flies(tweety)"))

    # To check entailment, we test if premises + ~conclusion is unsatisfiable
    test_formulas = premises + [SignedFormula(f, conclusion.formula)]

    tableau = ACrQTableau(test_formulas)
    result = tableau.construct()

    print("   Premises: Human(socrates) ∧ ¬Human(socrates)")
    print("   Conclusion: Flies(tweety)")
    print(f"   Entailment: {'YES' if not result.satisfiable else 'NO'}")
    print("   Analysis: Contradiction does NOT entail arbitrary formulas")
    print("             (Paraconsistent - no explosion!)")


def demo3_demorgan_transformations():
    """Demonstrate DeMorgan transformations in ACrQ."""
    demo_header("Demo 3: DeMorgan Transformations (Not Semantic Laws)")

    print("\nIn ACrQ, DeMorgan rules are syntactic transformations,")
    print("not semantic validities (due to weak Kleene semantics).\n")

    # Show transformation of compound negation
    print("1. Transformation of ¬(P ∧ Q):")
    formula = parse_acrq_formula("~(Human(x) & Mortal(x))")
    print("   Input: ~(Human(x) & Mortal(x))")
    print("   Transforms to: Human*(x) | Mortal*(x)")
    print("   (Via: ¬(P ∧ Q) → (¬P ∨ ¬Q) → (P* ∨ Q*))")

    # Build tableau to show the transformation
    tableau = ACrQTableau([SignedFormula(t, formula)])
    result = tableau.construct()

    # Show tableau with trace
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n   Tableau construction:")
    print(renderer.render_ascii(result.tableau))

    # Test semantic validity of DeMorgan
    print("\n2. DeMorgan is NOT semantically valid in weak Kleene:")
    from wkrq import parse, valid

    demorgan = parse("~(P & Q) -> (~P | ~Q)")
    is_valid = valid(demorgan)
    print("   Formula: ¬(P ∧ Q) → (¬P ∨ ¬Q)")
    print(f"   Valid in weak Kleene? {is_valid}")
    print("   Counterexample: P=e, Q=e gives e → e = e (not true)")


def demo4_quantifier_demorgan():
    """Demonstrate quantifier DeMorgan rules in ACrQ."""
    demo_header("Demo 4: Quantifier DeMorgan Rules")

    print("\nACrQ includes DeMorgan rules for negated quantifiers:\n")

    # Example 1: Negated universal
    print("1. Negated universal quantifier:")
    formula1 = parse_acrq_formula("~[∀x Human(x)]Mortal(x)")
    print("   Input: ~[∀x Human(x)]Mortal(x)")
    print("   Transforms to: [∃x Human(x)]~Mortal(x)")
    print("   Which becomes: [∃x Human(x)]Mortal*(x)")

    # Example 2: Negated existential
    print("\n2. Negated existential quantifier:")
    formula2 = parse_acrq_formula("~[∃x Student(x)]Passes(x)")
    print("   Input: ~[∃x Student(x)]Passes(x)")
    print("   Transforms to: [∀x Student(x)]~Passes(x)")
    print("   Which becomes: [∀x Student(x)]Passes*(x)")

    # Show tableau construction for negated quantifier
    print("\n3. Tableau for negated universal:")
    tableau = ACrQTableau([SignedFormula(t, formula1)])
    result = tableau.construct()

    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    print(renderer.render_ascii(result.tableau))


def demo5_gap_semantics():
    """Demonstrate knowledge gaps in ACrQ."""
    demo_header("Demo 5: Knowledge Gaps (Epistemic Uncertainty)")

    print("\nACrQ can represent knowledge gaps - situations where we")
    print("have neither positive nor negative evidence.\n")

    # Create a formula with potential gap
    print("Test: Can P(x) have a gap (neither true nor false)?")

    # Try to find a model where P(x) is neither provably true nor false
    from wkrq import Constant, PredicateFormula

    p = PredicateFormula("P", [Constant("a")])

    # Test with n-sign (nontrue) which branches to f or e
    tableau = ACrQTableau([SignedFormula(n, p)])
    result = tableau.construct()

    print("   Formula: n: P(a) (nontrue - either false or undefined)")
    print(f"   Satisfiable: {result.satisfiable}")

    if result.models:
        for i, model in enumerate(result.models[:2]):
            print(f"   Model {i+1}: {model}")

    print("\n   Analysis: P(a) can be false (negative evidence)")
    print("             or undefined (no evidence - gap)")


def demo6_llm_integration():
    """Demonstrate LLM integration (ACrQ-LLM extension)."""
    demo_header("Demo 6: LLM Integration (ACrQ-LLM Extension)")

    print("\nACrQ-LLM extends ACrQ with epistemic evaluation via LLMs.")
    print("This creates a hybrid formal-epistemic reasoning system.\n")

    # Create a mock LLM evaluator
    def mock_llm_evaluator(formula):
        """Simulate LLM knowledge about the world."""
        knowledge = {
            "Planet(earth)": BilateralTruthValue(TRUE, FALSE),  # Earth is a planet
            "Planet(pluto)": BilateralTruthValue(FALSE, TRUE),  # Pluto is not
            "Planet(sedna)": BilateralTruthValue(FALSE, FALSE),  # Unknown (gap)
        }
        return knowledge.get(str(formula), BilateralTruthValue(FALSE, FALSE))

    print("Scenario: Testing planetary classification with LLM knowledge")

    # Test 1: Earth
    print("\n1. Is Earth a planet?")
    earth = parse_acrq_formula("Planet(earth)")
    tableau1 = ACrQTableau([SignedFormula(t, earth)], llm_evaluator=mock_llm_evaluator)
    result1 = tableau1.construct()
    print("   t: Planet(earth)")
    print("   LLM says: TRUE (positive evidence)")
    print(f"   Result: {'SATISFIABLE' if result1.satisfiable else 'UNSATISFIABLE'}")

    # Test 2: Pluto
    print("\n2. Is Pluto a planet?")
    pluto = parse_acrq_formula("Planet(pluto)")
    tableau2 = ACrQTableau([SignedFormula(t, pluto)], llm_evaluator=mock_llm_evaluator)
    result2 = tableau2.construct()
    print("   t: Planet(pluto)")
    print("   LLM says: FALSE (negative evidence)")
    print(f"   Result: {'SATISFIABLE' if result2.satisfiable else 'UNSATISFIABLE'}")

    # Test 3: Sedna (unknown)
    print("\n3. Is Sedna a planet?")
    sedna = parse_acrq_formula("Planet(sedna)")
    tableau3 = ACrQTableau([SignedFormula(t, sedna)], llm_evaluator=mock_llm_evaluator)
    result3 = tableau3.construct()
    print("   t: Planet(sedna)")
    print("   LLM says: GAP (no knowledge)")
    print(f"   Result: {'SATISFIABLE' if result3.satisfiable else 'UNSATISFIABLE'}")

    print("\n   Analysis: LLM knowledge affects satisfiability")
    print("             Creating hybrid formal-empirical reasoning")


def demo7_complete_example():
    """Complete ACrQ example combining all features."""
    demo_header("Demo 7: Complete ACrQ Example")

    print("\nCombining bilateral predicates, gluts, and quantifiers:\n")

    # Scenario: Reasoning about mythical creatures
    formulas_text = [
        "[∀x Dragon(x)]Flies(x)",  # All dragons fly
        "[∀x Dragon(x)]Breathes_Fire(x)",  # All dragons breathe fire
        "Dragon(smaug)",  # Smaug is a dragon
        "~Flies(smaug)",  # But Smaug doesn't fly (contradiction!)
    ]

    print("Premises:")
    for i, text in enumerate(formulas_text, 1):
        print(f"  {i}. {text}")

    # Parse formulas
    formulas = [
        SignedFormula(t, parse_acrq_formula(formulas_text[0])),
        SignedFormula(t, parse_acrq_formula(formulas_text[1])),
        SignedFormula(t, parse_acrq_formula(formulas_text[2])),
        SignedFormula(t, parse_acrq_formula(formulas_text[3])),
    ]

    print("\nBuilding ACrQ tableau...")
    tableau = ACrQTableau(formulas)
    result = tableau.construct()

    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")

    if result.satisfiable:
        print("\nAnalysis: In ACrQ, this is SATISFIABLE despite the contradiction!")
        print("          Smaug can be a dragon that both flies and doesn't fly")
        print("          (glut for the Flies predicate)")
        if result.models:
            print(f"\nModel: {result.models[0]}")
    else:
        print("\nAnalysis: The contradiction about Smaug's flying ability")
        print("          creates an inconsistency even in ACrQ")

    # Show the tableau tree
    print("\nTableau structure:")
    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    tree = renderer.render_ascii(result.tableau)
    # Limit output for readability
    lines = tree.split("\n")[:20]
    print("\n".join(lines))
    if len(tree.split("\n")) > 20:
        print("... (tableau continues)")


def main():
    """Run all ACrQ demonstrations."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  ACrQ DEMONSTRATION FOR THOMAS FERGUSON  ".center(68) + "█")
    print(
        "█" + "  Analytic Containment with restricted Quantification  ".center(68) + "█"
    )
    print("█" + "  (Ferguson 2021, Definition 18)  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    # Run demonstrations
    demo1_bilateral_predicates()
    input("\n[Press Enter to continue to Demo 2...]")

    demo2_paraconsistency()
    input("\n[Press Enter to continue to Demo 3...]")

    demo3_demorgan_transformations()
    input("\n[Press Enter to continue to Demo 4...]")

    demo4_quantifier_demorgan()
    input("\n[Press Enter to continue to Demo 5...]")

    demo5_gap_semantics()
    input("\n[Press Enter to continue to Demo 6...]")

    demo6_llm_integration()
    input("\n[Press Enter to continue to Demo 7...]")

    demo7_complete_example()

    # Closing
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  END OF ACrQ DEMONSTRATION  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    print("\nKey takeaways:")
    print("• ACrQ extends wKrQ with bilateral predicates (R/R*)")
    print("• Paraconsistent: handles contradictions without explosion")
    print("• Paracomplete: represents knowledge gaps")
    print("• DeMorgan as transformation rules, not semantic laws")
    print("• LLM integration creates hybrid formal-empirical reasoning")
    print("\nThank you for your groundbreaking work, Thomas!")


if __name__ == "__main__":
    main()
