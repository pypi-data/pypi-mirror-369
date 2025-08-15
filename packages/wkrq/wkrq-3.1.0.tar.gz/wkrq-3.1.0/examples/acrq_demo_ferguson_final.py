#!/usr/bin/env python3
"""
ACrQ Demonstration for Thomas Ferguson Call (Final Version)

Complete demonstration with tableau trees and rule sequences.
"""

from wkrq import (
    ACrQTableau,
    SignedFormula,
    SyntaxMode,
    parse_acrq_formula,
    t,
)
from wkrq.cli import TableauTreeRenderer


def demo_header(title):
    """Print a formatted demo header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show_tableau(result, title="Tableau Tree", limit_lines=None):
    """Display tableau tree with rules."""
    print(f"\n{title}:")
    print("-" * 40)
    renderer = TableauTreeRenderer(show_rules=True, compact=False)
    tree = renderer.render_ascii(result.tableau)
    lines = tree.split("\n")

    if limit_lines and len(lines) > limit_lines:
        for line in lines[:limit_lines]:
            print(line)
        print(f"... (showing first {limit_lines} lines of {len(lines)} total)")
    else:
        print(tree)

    # Show statistics
    print("\nTableau Statistics:")
    print(f"  Total nodes: {result.total_nodes}")
    print(f"  Open branches: {result.open_branches}")
    print(f"  Closed branches: {result.closed_branches}")
    print(f"  Satisfiable: {result.satisfiable}")


def demo1_bilateral_with_tableau():
    """Bilateral predicates with tableau visualization."""
    demo_header("Demo 1: Bilateral Predicates with Tableau Trees")

    print("\nBilateral predicates R and R* track positive/negative evidence.")
    print("Let's see how they work in tableau construction.\n")

    # Example 1: Simple glut
    print("Example 1: Glut (conflicting information)")
    print("-" * 40)
    print("Formulas: t: P(a), t: P*(a)")
    print("This represents conflicting evidence about P(a)\n")

    formulas1 = [
        SignedFormula(t, parse_acrq_formula("P(a)")),
        SignedFormula(t, parse_acrq_formula("P*(a)", SyntaxMode.BILATERAL)),
    ]

    tableau1 = ACrQTableau(formulas1, trace=True)
    result1 = tableau1.construct()

    show_tableau(result1, "Glut Tableau (both P and P* true)")

    if result1.models:
        print(f"\nModel: {result1.models[0]}")
        print("Interpretation: ACrQ allows gluts - both P(a) and P*(a) can be true")

    # Example 2: Negation becoming bilateral
    print("\n\nExample 2: Negation Transformation")
    print("-" * 40)
    print("Formula: t: ~P(b)")
    print("This transforms to: t: P*(b)\n")

    formulas2 = [SignedFormula(t, parse_acrq_formula("~P(b)"))]

    tableau2 = ACrQTableau(formulas2, trace=True)
    result2 = tableau2.construct()

    show_tableau(result2, "Negation to Bilateral Transformation")

    print("\nObserve: ~P(b) became P*(b) through transformation rule")


def demo2_demorgan_with_tableau():
    """DeMorgan transformation with tableau."""
    demo_header("Demo 2: DeMorgan Transformation in Tableau")

    print("\nDeMorgan in ACrQ is a syntactic transformation rule,")
    print("not a semantic equivalence. Let's see it in action.\n")

    # Show DeMorgan transformation
    print("Formula: t: ~(P(x) & Q(x))")
    print("Expected transformation: (~P(x) | ~Q(x)) → (P*(x) | Q*(x))\n")

    formula = parse_acrq_formula("~(P(x) & Q(x))")
    formulas = [SignedFormula(t, formula)]

    tableau = ACrQTableau(formulas, trace=True)
    result = tableau.construct()

    show_tableau(result, "DeMorgan Transformation Tableau", limit_lines=25)

    print("\nKey observations:")
    print("1. The negated conjunction triggers DeMorgan rule")
    print("2. This creates a disjunction of negations")
    print("3. Negations become bilateral predicates P* and Q*")
    print("4. The disjunction creates three branches (including error)")


def demo3_paraconsistency_tableau():
    """Paraconsistent reasoning with detailed tableau."""
    demo_header("Demo 3: Paraconsistency - Contradiction Containment")

    print("\nTest: Does a contradiction about P entail an unrelated Q?")
    print("In classical logic: YES (explosion)")
    print("In ACrQ: NO (paraconsistent)\n")

    print("Premises:")
    print("  1. P(a)     [P is true]")
    print("  2. ~P(a)    [P is false - contradiction!]")
    print("  3. ~Q(b)    [Q is false - unrelated]")
    print("\nIf the contradiction spreads, this should be unsatisfiable.\n")

    formulas = [
        SignedFormula(t, parse_acrq_formula("P(a)")),
        SignedFormula(t, parse_acrq_formula("~P(a)")),
        SignedFormula(t, parse_acrq_formula("~Q(b)")),
    ]

    tableau = ACrQTableau(formulas, trace=True)
    result = tableau.construct()

    show_tableau(result, "Paraconsistent Tableau")

    if result.satisfiable:
        print(f"\nModel: {result.models[0]}")
        print("\nConclusion: SATISFIABLE! The contradiction about P(a)")
        print("            doesn't affect Q(b). No explosion!")


def demo4_quantifier_demorgan_tableau():
    """Quantifier DeMorgan with tableau."""
    demo_header("Demo 4: Quantifier DeMorgan Rules")

    print("\nACrQ includes DeMorgan rules for quantifiers.")
    print("Let's see how negated quantifiers transform.\n")

    print("Formula: t: ~[∀x Human(x)]Mortal(x)")
    print("Expected: [∃x Human(x)]~Mortal(x) → [∃x Human(x)]Mortal*(x)\n")

    formula = parse_acrq_formula("~[∀x Human(x)]Mortal(x)")
    formulas = [SignedFormula(t, formula)]

    tableau = ACrQTableau(formulas, trace=True)
    result = tableau.construct()

    show_tableau(result, "Quantifier DeMorgan Tableau")

    print("\nRule sequence:")
    print("1. t-demorgan-universal: Negated ∀ becomes ∃ with negated matrix")
    print("2. t-restricted-exists: Instantiate with fresh constant")
    print("3. t-negated-to-bilateral: Convert ~Mortal to Mortal*")


def demo5_pluto_sedna_example():
    """The Pluto/Sedna planetary classification example."""
    demo_header("Demo 5: Pluto/Sedna - Formal Rules vs World Knowledge")

    print("\nScenario: Testing planetary classification with formal rules")
    print("and real-world knowledge (via LLM).\n")

    # Try to use bilateral-truth evaluator
    planetary_knowledge = None
    try:
        from dotenv import load_dotenv

        load_dotenv()  # Load API keys from .env file

        from wkrq.llm_integration import create_llm_tableau_evaluator

        # Use Claude 3.5 Sonnet for real-world knowledge
        planetary_knowledge = create_llm_tableau_evaluator(
            "anthropic", model="claude-3-5-sonnet-20241022"
        )

        if planetary_knowledge:
            print("✓ Using Claude 3.5 Sonnet for real planetary knowledge")
        else:
            print("Note: LLM not available, using formal logic only")
    except (ImportError, Exception) as e:
        print("Note: LLM not available, using formal logic only")
        print(f"      {e}")

    print("=" * 50)
    print("Part A: Classic Definition (pre-2006)")
    print("=" * 50)
    print("\nRule: [∀x OrbitsSun(x)]Planet(x)")
    print("      (Anything orbiting the sun is a planet)\n")

    print("Testing: Pluto")
    print("-" * 30)

    formulas_classic = [
        SignedFormula(t, parse_acrq_formula("[∀x OrbitsSun(x)]Planet(x)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto)")),
    ]

    tableau_classic = ACrQTableau(formulas_classic, llm_evaluator=planetary_knowledge)
    result_classic = tableau_classic.construct()

    show_tableau(result_classic, "Classic Definition Tableau", limit_lines=20)

    print("\nAnalysis: Formal logic derives Planet(pluto) from the rule,")
    print("          but LLM knows Pluto isn't a planet → CONTRADICTION")

    print("\n" + "=" * 50)
    print("Part B: Modern Definition (post-2006)")
    print("=" * 50)
    print("\nRule: [∀x OrbitsSun(x) & ClearedOrbit(x)]Planet(x)")
    print("      (Must orbit sun AND clear its orbit)\n")

    print("Testing: Pluto with modern definition")
    print("-" * 30)

    formulas_modern = [
        SignedFormula(
            t, parse_acrq_formula("[∀x OrbitsSun(x) & ClearedOrbit(x)]Planet(x)")
        ),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto)")),
        SignedFormula(t, parse_acrq_formula("~ClearedOrbit(pluto)")),
    ]

    tableau_modern = ACrQTableau(formulas_modern, llm_evaluator=planetary_knowledge)
    result_modern = tableau_modern.construct()

    show_tableau(result_modern, "Modern Definition Tableau", limit_lines=25)

    print("\nAnalysis: With the modern definition, Pluto correctly")
    print("          doesn't satisfy the requirements for planethood")

    print("\n" + "=" * 50)
    print("Part C: Unknown Object (Sedna)")
    print("=" * 50)
    print("\nTesting object with incomplete information\n")

    formulas_sedna = [
        SignedFormula(t, parse_acrq_formula("[∀x OrbitsSun(x)]Planet(x)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(sedna)")),
    ]

    tableau_sedna = ACrQTableau(formulas_sedna, llm_evaluator=planetary_knowledge)
    result_sedna = tableau_sedna.construct()

    show_tableau(result_sedna, "Sedna Classification Tableau", limit_lines=20)

    print("\nAnalysis: Formal logic derives Planet(sedna),")
    print("          but LLM has no knowledge (gap) → UNSATISFIABLE")
    print("          Knowledge gaps prevent conclusions")


def demo6_legal_reasoning_tableau():
    """Legal reasoning with full tableau."""
    demo_header("Demo 6: Legal Reasoning - Witness Testimony")

    print("\nScenario: Conflicting legal requirements\n")

    formulas_text = [
        "[∀x Witness(x)]Testifies(x)",  # All witnesses must testify
        "Witness(smith)",  # Smith is a witness
        "Witness(jones)",  # Jones is a witness
        "~Testifies(smith)",  # Smith didn't testify (violation!)
    ]

    print("Legal rules and facts:")
    for i, text in enumerate(formulas_text, 1):
        print(f"  {i}. {text}")

    print("\nQuestion: Is this situation legally consistent in ACrQ?")

    formulas = [SignedFormula(t, parse_acrq_formula(text)) for text in formulas_text]

    tableau = ACrQTableau(formulas, trace=True)
    result = tableau.construct()

    show_tableau(result, "Legal Reasoning Tableau", limit_lines=30)

    if result.satisfiable:
        print(f"\nModel: {result.models[0]}")
        print("\nLegal interpretation:")
        print("• Smith has both Testifies(smith)=t (required by rule)")
        print("  and Testifies*(smith)=t (from ~Testifies(smith))")
        print("• This is a glut - conflicting legal obligations")
        print("• Jones's testimony status is independent")
        print("• The inconsistency is localized to Smith")


def demo7_llm_integration_showcase():
    """Showcase real LLM integration with Claude."""
    demo_header("Demo 7: Real LLM Integration (ACrQ-LLM Extension)")

    print("\nACrQ-LLM extends ACrQ with epistemic evaluation via LLMs.")
    print("This creates a hybrid formal-empirical reasoning system.\n")

    # Load environment and create evaluator
    try:
        from dotenv import load_dotenv

        load_dotenv()

        from wkrq.llm_integration import create_llm_tableau_evaluator

        llm_evaluator = create_llm_tableau_evaluator(
            "anthropic", model="claude-3-5-sonnet-20241022"
        )

        if not llm_evaluator:
            print("LLM not available, skipping this demo")
            return

        print("✓ Using Claude 3.5 Sonnet for real-world knowledge\n")

    except Exception as e:
        print(f"Could not set up LLM: {e}")
        return

    # Test 1: Simple fact checking
    print("Test 1: Fact Checking")
    print("-" * 30)
    facts = [
        ("Earth is a planet", "Planet(earth)", True),
        ("Pluto is a planet", "Planet(pluto)", False),
        ("Penguins can fly", "CanFly(penguin)", False),
    ]

    for description, formula_text, should_be_true in facts:
        formula = parse_acrq_formula(formula_text)
        tableau = ACrQTableau([SignedFormula(t, formula)], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        expected = "SATISFIABLE" if should_be_true else "UNSATISFIABLE"
        actual = "SATISFIABLE" if result.satisfiable else "UNSATISFIABLE"
        status = "✓" if (result.satisfiable == should_be_true) else "✗"

        print(f"{status} {description}: {actual}")

    # Test 2: Formal rule conflicts with reality
    print("\n\nTest 2: Formal Rules vs Real-World Knowledge")
    print("-" * 30)
    print("Rule: All birds fly")
    print("Fact: Penguins are birds")
    print("LLM knows: Penguins don't fly")
    print()

    rule = parse_acrq_formula("[∀x Bird(x)]Flies(x)")
    fact = parse_acrq_formula("Bird(penguin)")

    formulas = [SignedFormula(t, rule), SignedFormula(t, fact)]
    tableau = ACrQTableau(formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("\nAnalysis: The formal rule derives Flies(penguin),")
    print("          but Claude knows penguins can't fly.")
    print("          This creates a contradiction!")

    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    tree = renderer.render_ascii(result.tableau)
    lines = tree.split("\n")[:10]
    print("\nTableau (first 10 lines):")
    for line in lines:
        print(f"  {line}")

    print("\n✓ LLM integration creates hybrid formal-empirical reasoning!")


def demo8_rule_sequence_analysis():
    """Analyze rule application sequences."""
    demo_header("Demo 8: Rule Application Sequence Analysis")

    print("\nLet's trace through a complex formula step by step.\n")

    formula_text = "(P(a) | Q(a)) & ~P(a)"
    print(f"Formula: t: {formula_text}")
    print("\nExpected rule sequence:")
    print("1. t-conjunction: Split into components")
    print("2. t-disjunction: Create branches for P|Q")
    print("3. Negation transformation: ~P becomes P*")
    print("4. Check for contradictions\n")

    formula = parse_acrq_formula(formula_text)
    formulas = [SignedFormula(t, formula)]

    tableau = ACrQTableau(formulas, trace=True)
    result = tableau.construct()

    show_tableau(result, "Rule Sequence Tableau")

    # Extract and show trace if available
    if hasattr(result, "trace") and result.trace:
        print("\nDetailed rule application sequence:")
        for i, step in enumerate(result.trace.steps[:10], 1):
            print(f"  Step {i}: {step.rule_name}")
            if step.conclusions:
                for conc in step.conclusions[:2]:
                    print(f"    → {conc}")


def main():
    """Run complete ACrQ demonstration."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  ACrQ DEMONSTRATION FOR THOMAS FERGUSON  ".center(68) + "█")
    print("█" + "  Complete with Tableau Trees and Rules  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    demos = [
        ("Bilateral Predicates with Tableaux", demo1_bilateral_with_tableau),
        ("DeMorgan Transformation Rules", demo2_demorgan_with_tableau),
        ("Paraconsistent Reasoning", demo3_paraconsistency_tableau),
        ("Quantifier DeMorgan", demo4_quantifier_demorgan_tableau),
        ("Pluto/Sedna Classification", demo5_pluto_sedna_example),
        ("Legal Reasoning", demo6_legal_reasoning_tableau),
        ("LLM Integration (ACrQ-LLM)", demo7_llm_integration_showcase),
        ("Rule Sequences", demo8_rule_sequence_analysis),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        if i > 1:
            response = input(
                f"\n[Press Enter for Demo {i}: {name}, or 'q' to quit...] "
            )
            if response.lower() == "q":
                break
        demo_func()

    # Summary
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  END OF DEMONSTRATION  ".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    print("\nKey ACrQ Features Demonstrated:")
    print("• Bilateral predicates (R/R*) with tableau trees")
    print("• DeMorgan as transformation rules (not semantic laws)")
    print("• Paraconsistent reasoning (contradictions contained)")
    print("• Quantifier DeMorgan transformations")
    print("• LLM integration for real-world knowledge")
    print("• Complete rule application sequences")
    print("\nThank you for your groundbreaking work on ACrQ, Thomas!")


if __name__ == "__main__":
    main()
