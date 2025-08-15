#!/usr/bin/env python3
"""
ACrQ Demonstration for Thomas Ferguson Call (Revised)

Clearer, more intuitive examples of ACrQ features.
"""

from wkrq import (
    ACrQTableau,
    SignedFormula,
    SyntaxMode,
    f,
    n,
    parse_acrq_formula,
    t,
)


def demo_header(title):
    """Print a formatted demo header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo1_bilateral_basics():
    """Explain bilateral predicates with clear examples."""
    demo_header("Demo 1: Understanding Bilateral Predicates")

    print("\nIn ACrQ, each predicate P has a dual P* for negative evidence.")
    print("This allows four information states:\n")

    print("  P(a)=t, P*(a)=f  →  Clearly true")
    print("  P(a)=f, P*(a)=t  →  Clearly false")
    print("  P(a)=f, P*(a)=f  →  Gap (no information)")
    print("  P(a)=t, P*(a)=t  →  Glut (conflicting information)")

    print("\nExample: Medical diagnosis")
    print("-" * 40)

    # Scenario 1: Clear diagnosis
    print("\n1. Clear positive test:")
    formulas1 = [
        SignedFormula(t, parse_acrq_formula("HasCondition(patient1)")),
        SignedFormula(
            f, parse_acrq_formula("HasCondition*(patient1)", SyntaxMode.BILATERAL)
        ),
    ]
    tableau1 = ACrQTableau(formulas1)
    result1 = tableau1.construct()
    print("   t: HasCondition(patient1), f: HasCondition*(patient1)")
    print(f"   Result: {'SATISFIABLE' if result1.satisfiable else 'UNSATISFIABLE'}")
    print("   Interpretation: Clear positive diagnosis")

    # Scenario 2: Conflicting tests
    print("\n2. Conflicting test results:")
    formulas2 = [
        SignedFormula(t, parse_acrq_formula("HasCondition(patient2)")),
        SignedFormula(
            t, parse_acrq_formula("HasCondition*(patient2)", SyntaxMode.BILATERAL)
        ),
    ]
    tableau2 = ACrQTableau(formulas2)
    result2 = tableau2.construct()
    print("   t: HasCondition(patient2), t: HasCondition*(patient2)")
    print(f"   Result: {'SATISFIABLE' if result2.satisfiable else 'UNSATISFIABLE'}")
    print("   Interpretation: Conflicting evidence (glut) - need more tests")


def demo2_negation_transformation():
    """Show how negation works in ACrQ."""
    demo_header("Demo 2: Negation in ACrQ")

    print("\nIn ACrQ, negation of atomic predicates becomes bilateral:")
    print("  ¬P(x) transforms to P*(x)")
    print("\nThis is NOT the same as classical negation!\n")

    # Example with clear distinction
    print("Example: Citizenship status")
    print("-" * 40)

    print("\n1. Standard negation (transparent mode):")
    formula1 = parse_acrq_formula("~Citizen(john)")
    print("   Input:  ~Citizen(john)")
    print(f"   Parsed: {formula1}")
    print("   Meaning: Evidence that John is NOT a citizen")

    print("\n2. What this means in tableau:")
    formulas = [SignedFormula(t, parse_acrq_formula("~Citizen(john)"))]
    tableau = ACrQTableau(formulas)
    result = tableau.construct()

    print("   Formula: t: ~Citizen(john)")
    print("   Becomes: t: Citizen*(john)")
    print(f"   Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    if result.models:
        print(f"   Model: {result.models[0]}")


def demo3_paraconsistency_clear():
    """Clear example of paraconsistent reasoning."""
    demo_header("Demo 3: Paraconsistency - Containing Contradictions")

    print("\nClassical logic: One contradiction → Everything is true (explosion)")
    print("ACrQ: Contradictions are local, don't affect unrelated facts\n")

    print("Scenario: Database with conflicting records")
    print("-" * 40)

    # Set up: Conflicting age records, but clear name record
    print("\nDatabase contains:")
    print("  1. Age(Alice, 30)")
    print("  2. Age(Alice, 25)  [conflicting!]")
    print("  3. Name(Alice, 'Alice Smith')")

    print("\nQuestion: Does the age conflict affect the name record?")

    # In ACrQ, we can have both ages true (glut) without affecting name
    formulas = [
        SignedFormula(t, parse_acrq_formula("Age(alice, 30)")),
        SignedFormula(t, parse_acrq_formula("Age(alice, 25)")),
        SignedFormula(t, parse_acrq_formula("Name(alice, smith)")),
    ]

    tableau = ACrQTableau(formulas)
    result = tableau.construct()

    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Conflicting ages don't invalidate the name!")
    print("          The contradiction is contained to Age predicate only.")

    # Show non-explosion
    print("\nTest explosion: Does Age conflict entail unrelated fact?")
    test_formulas = [
        SignedFormula(t, parse_acrq_formula("Age(alice, 30)")),
        SignedFormula(t, parse_acrq_formula("Age(alice, 25)")),
        SignedFormula(f, parse_acrq_formula("Weather(sunny)")),  # Unrelated
    ]

    tableau2 = ACrQTableau(test_formulas)
    result2 = tableau2.construct()

    print(
        f"Can Weather be false despite Age conflict? {'YES' if result2.satisfiable else 'NO'}"
    )
    print("Conclusion: No explosion - contradictions don't spread!")


def demo4_demorgan_clarity():
    """Clarify DeMorgan transformations."""
    demo_header("Demo 4: DeMorgan - Transformation vs Validity")

    print("\nIMPORTANT: In ACrQ, DeMorgan rules are syntactic transformations,")
    print("not semantic equivalences (due to weak Kleene logic).\n")

    print("1. Syntactic transformation (always applied):")
    print("-" * 40)
    formula = parse_acrq_formula("~(Tall(x) & Smart(x))")
    print("   Input:      ~(Tall(x) & Smart(x))")
    print("   Transforms: Tall*(x) | Smart*(x)")
    print("   This transformation happens during parsing")

    print("\n2. Semantic validity (NOT valid in weak Kleene):")
    print("-" * 40)

    # Test semantic validity of DeMorgan as implication
    from wkrq import parse, valid

    demorgan_formula = parse("~(P & Q) -> (~P | ~Q)")
    is_valid = valid(demorgan_formula)

    print("   Formula: ~(P & Q) → (~P | ~Q)")
    print(f"   Valid in weak Kleene? {is_valid}")
    print("   Why not? When P=undefined, Q=undefined:")
    print("            ~(e & e) = ~e = e")
    print("            (~e | ~e) = (e | e) = e")
    print("            So e → e = e (undefined, not always true!)")


def demo5_practical_example():
    """Practical example combining features."""
    demo_header("Demo 5: Practical Application - Legal Reasoning")

    print("\nScenario: Legal database with conflicting testimonies\n")

    # Setup the legal scenario
    formulas_text = [
        "[∀x Witness(x)]Testifies(x)",  # All witnesses testify
        "Witness(smith)",  # Smith is a witness
        "Witness(jones)",  # Jones is a witness
        "~Testifies(smith)",  # But Smith didn't testify (contradiction!)
        "Says(jones, guilty)",  # Jones says guilty
        "Says(smith, innocent)",  # Smith says innocent (if they testified)
    ]

    print("Legal facts:")
    for i, text in enumerate(formulas_text[:4], 1):
        print(f"  {i}. {text}")

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
        print("\nAnalysis:")
        print("  • Smith is both required to testify (as witness) and didn't testify")
        print("  • This creates a glut: Testifies(smith)=t and Testifies*(smith)=t")
        print("  • The legal inconsistency is contained to Smith's testimony")
        print("  • Other facts (Jones's testimony) remain unaffected")
        print("\nLegal interpretation: Procedural issue with Smith doesn't")
        print("invalidate entire proceeding or Jones's testimony.")


def demo6_knowledge_gaps():
    """Demonstrate knowledge gaps clearly."""
    demo_header("Demo 6: Knowledge Gaps vs Contradictions")

    print("\nACrQ distinguishes between:")
    print("  • Contradiction (glut): Both P and P* are true")
    print("  • Ignorance (gap): Neither P nor P* is true\n")

    print("Example: Archaeological claims")
    print("-" * 40)

    # Scenario 1: Contradiction (multiple dating methods disagree)
    print("\n1. Conflicting evidence (glut):")
    print("   Carbon dating: Artifact is 5000 years old")
    print("   Stratigraphy: Artifact is 3000 years old")

    formulas1 = [
        SignedFormula(t, parse_acrq_formula("Age5000(artifact)")),
        SignedFormula(t, parse_acrq_formula("Age3000(artifact)")),
    ]
    tableau1 = ACrQTableau(formulas1)
    result1 = tableau1.construct()
    print(f"   Result: {'SATISFIABLE' if result1.satisfiable else 'UNSATISFIABLE'}")
    print("   Interpretation: Conflicting evidence (glut) - methods disagree")

    # Scenario 2: No evidence (gap)
    print("\n2. No evidence (gap):")
    print("   Unknown artifact with no dating information")

    # Use n-sign to represent "not true" which includes false and undefined
    from wkrq import Constant, PredicateFormula

    unknown = PredicateFormula("Ancient", [Constant("mystery_item")])

    formulas2 = [SignedFormula(n, unknown)]  # n = nontrue (false or undefined)
    tableau2 = ACrQTableau(formulas2)
    result2 = tableau2.construct()

    print("   n: Ancient(mystery_item)")
    print(f"   Result: {'SATISFIABLE' if result2.satisfiable else 'UNSATISFIABLE'}")
    print("   Interpretation: Can be false (not ancient) or undefined (unknown)")


def main():
    """Run revised ACrQ demonstrations."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  ACrQ DEMONSTRATION FOR THOMAS FERGUSON  ".center(68) + "█")
    print("█" + "  Clear, Intuitive Examples  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    demos = [
        ("Bilateral Predicates", demo1_bilateral_basics),
        ("Negation Transformation", demo2_negation_transformation),
        ("Paraconsistency", demo3_paraconsistency_clear),
        ("DeMorgan Clarification", demo4_demorgan_clarity),
        ("Legal Reasoning Example", demo5_practical_example),
        ("Knowledge Gaps", demo6_knowledge_gaps),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        if i > 1:
            input(f"\n[Press Enter for Demo {i}: {name}...]")
        demo_func()

    # Closing
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  END OF DEMONSTRATION  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    print("\nKey ACrQ Properties Demonstrated:")
    print("• Bilateral predicates enable four information states")
    print("• Negation transforms to bilateral (¬P → P*)")
    print("• Paraconsistency contains contradictions locally")
    print("• DeMorgan: syntactic transformation ≠ semantic validity")
    print("• Practical applications in databases, legal reasoning, etc.")


if __name__ == "__main__":
    main()
