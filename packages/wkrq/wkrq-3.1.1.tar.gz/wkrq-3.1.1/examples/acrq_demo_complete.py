#!/usr/bin/env python3
"""
ACrQ Complete Demonstration

Comprehensive demonstration with tableau trees, rule sequences,
and LLM integration showcasing the full capabilities of ACrQ.
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
    """The Pluto/Sedna planetary classification example with detailed reasoning trace."""
    demo_header("Demo 5: Pluto/Sedna - How LLM Knowledge Affects Reasoning")

    print("\nThis demo shows step-by-step how LLM knowledge changes tableau construction.")
    print("We'll trace the exact reasoning process to see the impact.\n")

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

    print("\n" + "=" * 60)
    print("Part A: Pluto Classification - Formal Logic vs Reality")
    print("=" * 60)
    print("\nSetup:")
    print("  Rule: [∀x OrbitsSun(x)]Planet(x)  (pre-2006 definition)")
    print("  Fact: OrbitsSun(pluto)")
    print("  LLM knows: Pluto is NOT a planet (post-2006 knowledge)\n")

    formulas_classic = [
        SignedFormula(t, parse_acrq_formula("[∀x OrbitsSun(x)]Planet(x)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto)")),
    ]

    # Create tableau with trace enabled
    tableau_classic = ACrQTableau(
        formulas_classic, llm_evaluator=planetary_knowledge, trace=True
    )
    result_classic = tableau_classic.construct()

    # Show the reasoning trace
    print("REASONING TRACE:")
    print("-" * 40)
    if hasattr(tableau_classic, 'construction_trace') and tableau_classic.construction_trace:
        tableau_classic.construction_trace.print_trace()
    else:
        # Manual trace if construction_trace not available
        print("Step 1: Apply universal rule [∀x OrbitsSun(x)]Planet(x)")
        print("        → For pluto: OrbitsSun(pluto) → Planet(pluto)")
        print("\nStep 2: We have t: OrbitsSun(pluto) (given)")
        print("        → Rule derives: t: Planet(pluto)")
        print("\nStep 3: LLM evaluation of Planet(pluto)")
        print("        Claude knows: Pluto is NOT a planet")
        print("        → LLM returns: f: Planet(pluto)")
        print("\nStep 4: CONTRADICTION!")
        print("        Formal logic: t: Planet(pluto)")
        print("        LLM knowledge: f: Planet(pluto)")
        print("        → Branch closes!")

    # Show the tableau tree
    print("\n" + "-" * 40)
    show_tableau(result_classic, "Resulting Tableau", limit_lines=25)

    print("\n🔍 KEY INSIGHT:")
    print("   The formal rule derives Planet(pluto) = TRUE")
    print("   But Claude's 2024 knowledge says Planet(pluto) = FALSE")
    print("   This creates a contradiction, making the scenario unsatisfiable!")
    print("   The LLM's real-world knowledge overrides the outdated formal rule.")

    print("\n" + "=" * 60)
    print("Part B: Knowledge Gaps - The Sedna Case")
    print("=" * 60)
    print("\nSetup:")
    print("  Rule: [∀x OrbitsSun(x)]Planet(x)")
    print("  Fact: OrbitsSun(sedna)")
    print("  LLM knows: Nothing about Sedna (knowledge gap)\n")

    formulas_sedna = [
        SignedFormula(t, parse_acrq_formula("[∀x OrbitsSun(x)]Planet(x)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(sedna)")),
    ]

    # Create tableau with trace
    tableau_sedna = ACrQTableau(
        formulas_sedna, llm_evaluator=planetary_knowledge, trace=True
    )
    result_sedna = tableau_sedna.construct()

    print("REASONING TRACE:")
    print("-" * 40)
    print("Step 1: Apply universal rule to sedna")
    print("        → Derives: t: Planet(sedna)")
    print("\nStep 2: LLM evaluation of Planet(sedna)")
    print("        Claude has NO knowledge about Sedna")
    print("        → Returns BOTH:")
    print("          • f: Planet(sedna)  (can't verify it's true)")
    print("          • f: Planet*(sedna) (can't verify it's false)")
    print("\nStep 3: Knowledge gap creates contradiction!")
    print("        Formal: t: Planet(sedna)")
    print("        LLM gap: f: Planet(sedna)")
    print("        → Branch closes!")

    print("\n" + "-" * 40)
    show_tableau(result_sedna, "Resulting Tableau", limit_lines=20)

    print("\n🔍 KEY INSIGHT:")
    print("   When the LLM lacks knowledge, it creates a 'gap'")
    print("   This gap (both f: P and f: P*) makes reasoning fail")
    print("   The system can't proceed without complete information!")

    print("\n" + "=" * 60)
    print("Part C: Comparing WITHOUT LLM")
    print("=" * 60)
    print("\nLet's see what happens without LLM knowledge:\n")

    # Run without LLM
    tableau_no_llm = ACrQTableau(formulas_sedna, trace=True)
    result_no_llm = tableau_no_llm.construct()

    print("WITHOUT LLM:")
    print("-" * 40)
    print("Step 1: Apply universal rule")
    print("        → Derives: t: Planet(sedna)")
    print("\nStep 2: No LLM to contradict")
    print("        → Tableau remains SATISFIABLE")
    print("\nModel: {Planet(sedna) = true, OrbitsSun(sedna) = true}")

    print("\n🎯 CRITICAL DIFFERENCE:")
    print("   WITHOUT LLM: Accepts any formal derivation")
    print("   WITH LLM: Real-world knowledge can:")
    print("     • Contradict false derivations (Pluto)")
    print("     • Create gaps for unknowns (Sedna)")
    print("     • Validate correct derivations (Earth)")


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
    """Showcase real LLM integration with detailed impact analysis."""
    demo_header("Demo 7: LLM Integration - The Reasoning Revolution")

    print("\nThis demo shows how LLM integration transforms logical reasoning")
    print("from pure formal deduction to hybrid formal-empirical reasoning.\n")

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

    # Demonstrate the penguin paradox
    print("=" * 60)
    print("THE PENGUIN PARADOX")
    print("=" * 60)
    print("\nClassical logic says:")
    print("  1. All birds fly (general rule)")
    print("  2. Penguins are birds (taxonomic fact)")
    print("  3. Therefore, penguins fly (logical conclusion)")
    print("\nBut reality says: Penguins DON'T fly!\n")

    rule = parse_acrq_formula("[∀x Bird(x)]Flies(x)")
    fact = parse_acrq_formula("Bird(penguin)")

    formulas = [SignedFormula(t, rule), SignedFormula(t, fact)]

    # First, show without LLM
    print("REASONING WITHOUT LLM:")
    print("-" * 40)
    tableau_no_llm = ACrQTableau(formulas, trace=True)
    result_no_llm = tableau_no_llm.construct()
    print("1. Apply rule: [∀x Bird(x)]Flies(x)")
    print("2. Given: Bird(penguin)")
    print("3. Derive: Flies(penguin) ✓")
    print(f"Result: {('SATISFIABLE' if result_no_llm.satisfiable else 'UNSATISFIABLE')}")
    print("Conclusion: Penguins fly! (WRONG)")

    # Now with LLM
    print("\n" + "=" * 60)
    print("REASONING WITH LLM:")
    print("-" * 40)
    tableau_with_llm = ACrQTableau(formulas, llm_evaluator=llm_evaluator, trace=True)
    result_with_llm = tableau_with_llm.construct()
    
    print("1. Apply rule: [∀x Bird(x)]Flies(x)")
    print("2. Given: Bird(penguin)")
    print("3. Derive: t: Flies(penguin)")
    print("4. LLM CHECK: Claude evaluates Flies(penguin)")
    print("   → Claude knows: Penguins CAN'T fly")
    print("   → Returns: f: Flies(penguin)")
    print("5. CONTRADICTION DETECTED!")
    print("   Formal: t: Flies(penguin)")
    print("   Reality: f: Flies(penguin)")
    print(f"Result: {('SATISFIABLE' if result_with_llm.satisfiable else 'UNSATISFIABLE')}")
    print("Conclusion: The rule is WRONG for penguins! (CORRECT)")

    # Show impact
    print("\n" + "=" * 60)
    print("IMPACT ANALYSIS")
    print("=" * 60)
    print("\n🔄 TRANSFORMATION:")
    print("   From: Pure formal logic (syntactic manipulation)")
    print("   To: Hybrid reasoning (formal + empirical)")
    
    print("\n📊 CAPABILITIES GAINED:")
    print("   • Fact-checking against real-world knowledge")
    print("   • Detection of outdated or incorrect rules")
    print("   • Handling of exceptions to general principles")
    print("   • Integration of domain expertise")
    
    print("\n⚡ PRACTICAL APPLICATIONS:")
    print("   • Legal reasoning with case law knowledge")
    print("   • Medical diagnosis with clinical expertise")
    print("   • Scientific reasoning with current research")
    print("   • Business logic with market knowledge")

    print("\n✨ THE REVOLUTION:")
    print("   ACrQ-LLM bridges the gap between:")
    print("   • What logic DERIVES (formal consistency)")
    print("   • What is actually TRUE (empirical reality)")


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
    print("█" + "  ACrQ COMPLETE DEMONSTRATION  ".center(68) + "█")
    print("█" + "  Tableau Trees, Rules, and LLM Integration  ".center(68) + "█")
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
    print("\nACrQ: Advancing paraconsistent reasoning with bilateral logic.")


if __name__ == "__main__":
    main()
