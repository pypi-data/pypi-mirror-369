#!/usr/bin/env python3
"""
LLM Integration Example
Comprehensive demonstration of LLM integration with ACrQ tableau reasoning.

Shows:
- Basic LLM evaluation of predicates
- Tableau tree visualization with LLM rules
- Complex reasoning patterns
- Medical diagnosis applications
- Real-world knowledge validation

REQUIRES: pip install bilateral-truth
"""

from wkrq import ACrQTableau, SignedFormula, f, parse_acrq_formula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.llm_integration import create_llm_tableau_evaluator


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def get_llm_evaluator():
    """Get LLM evaluator with clear setup messages."""
    try:
        # Try real LLM first (requires API key)
        for provider in ["anthropic", "openai", "google"]:
            try:
                llm_evaluator = create_llm_tableau_evaluator(provider)
                if llm_evaluator:
                    print(f"✅ Using {provider} LLM evaluator")
                    return llm_evaluator
            except:
                continue

        # Fall back to mock if no API keys available
        llm_evaluator = create_llm_tableau_evaluator("mock")
        print("📝 Using mock LLM evaluator (no API key found)")
        print(
            "   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY for real LLM"
        )
        return llm_evaluator

    except ImportError:
        print("❌ bilateral-truth package not installed")
        print("   Install with: pip install bilateral-truth")
        return None
    except Exception as e:
        print(f"❌ Could not create LLM evaluator: {e}")
        return None


def demo_basic_llm_evaluation(llm_evaluator):
    """Demonstrate basic LLM evaluation of predicates."""
    section("1. Basic LLM Evaluation")

    print("Testing LLM evaluation of astronomical predicates:")
    print("The LLM evaluator provides real-world knowledge for predicates.")
    print()

    # The LLM will evaluate these based on real-world knowledge
    formulas = [
        "Planet(mars)",  # True - Mars is a planet
        "Planet(pluto)",  # Controversial - depends on definition
        "Orbits(earth, sun)",  # True - Earth orbits the Sun
        "Orbits(sun, earth)",  # False - Sun doesn't orbit Earth
    ]

    for formula_str in formulas:
        formula = parse_acrq_formula(formula_str)
        signed = SignedFormula(t, formula)

        # Create tableau with LLM evaluator
        tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        print(f"   {formula_str}: ", end="")
        if result.satisfiable:
            print("✓ Consistent with world knowledge")
        else:
            print("✗ Contradicts world knowledge")

    print()


def demo_tableau_tree_visualization(llm_evaluator):
    """Show LLM evaluation rules in tableau trees."""
    section("2. Tableau Tree Visualization with LLM Rules")

    print("Demonstrating visible LLM evaluation rules in tableau trees.")
    print("Look for [llm-eval(...)] annotations in the tree structure.")
    print()

    renderer = TableauTreeRenderer(show_rules=True, compact=False)

    # Simple atomic predicate evaluation
    print("2.1. Simple atomic predicate: Planet(pluto)")

    formula = parse_acrq_formula("Planet(pluto)")
    signed_formulas = [SignedFormula(t, formula)]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree:")
    print(tree)
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")

    # Check if LLM rule is visible
    if "llm-eval" in tree:
        print("✓ LLM evaluation rule is visible in tree!")
    else:
        print("Note: LLM evaluation may not be visible if it confirms the assertion")

    print()

    # Complex formula with multiple atomic predicates
    print("2.2. Complex formula: Planet(earth) & Planet(mars)")

    conjunction = parse_acrq_formula("Planet(earth) & Planet(mars)")
    signed_formulas = [SignedFormula(t, conjunction)]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree:")
    print(tree)
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")

    # Count LLM evaluations
    llm_eval_count = tree.count("llm-eval")
    print(f"LLM evaluations found: {llm_eval_count}")
    print()


def demo_universal_rule_with_llm(llm_evaluator):
    """Show universal rule derivation with LLM evaluation."""
    section("3. Universal Rule + LLM Evaluation")

    print("Universal rule: [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("Facts: OrbitsSun(pluto), Spherical(pluto)")
    print("Question: Is Pluto a planet according to formal rules + LLM knowledge?")
    print()

    renderer = TableauTreeRenderer(show_rules=True, compact=False)

    planet_rule = parse_acrq_formula("[forall X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse_acrq_formula("OrbitsSun(pluto)")
    spherical_fact = parse_acrq_formula("Spherical(pluto)")

    signed_formulas = [
        SignedFormula(t, planet_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree:")
    print(tree)
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")

    print("\nExplanation:")
    print(
        "1. Universal rule instantiates: OrbitsSun(pluto) & Spherical(pluto) → Planet(pluto)"
    )
    print("2. We have t:OrbitsSun(pluto) and t:Spherical(pluto)")
    print("3. So we derive t:Planet(pluto)")
    print("4. LLM evaluates Planet(pluto) based on real-world knowledge")
    print("5. ACrQ can handle conflicts between formal derivation and LLM knowledge")
    print()


def demo_bilateral_predicates(llm_evaluator):
    """Show bilateral predicate handling with LLM."""
    section("4. Bilateral Predicates + LLM")

    print("Testing conflicting evidence: Planet(pluto) vs ~Planet(pluto)")
    print("ACrQ can handle 'gluts' - both positive and negative evidence.")
    print()

    renderer = TableauTreeRenderer(show_rules=True, compact=False)

    planet_positive = parse_acrq_formula("Planet(pluto)")
    planet_negative = parse_acrq_formula("~Planet(pluto)")  # Becomes Planet*(pluto)

    signed_formulas = [
        SignedFormula(t, planet_positive),
        SignedFormula(t, planet_negative),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree for: t:Planet(pluto), t:Planet*(pluto)")
    print(tree)
    print(f"Result: {'✓ Glut handled' if result.satisfiable else '✗ Inconsistent'}")

    if result.satisfiable:
        print("\n✓ ACrQ successfully handles the conflicting evidence!")
        print("  - Planet(pluto) = true (positive evidence)")
        print("  - Planet*(pluto) = true (negative evidence)")
        print("  - This represents a 'glut' - conflicting evidence coexists")
    print()


def demo_medical_reasoning(llm_evaluator):
    """Demonstrate medical diagnosis with conflicting guidelines."""
    section("5. Medical Diagnosis with Conflicting Information")

    print("🏥 Medical Case: Patient with Hypertension and Drug Allergies")
    print()
    print("DISCLAIMER: This is a logical reasoning demonstration only.")
    print("Not intended as actual medical advice. Consult healthcare professionals.")
    print()

    renderer = TableauTreeRenderer(show_rules=True, compact=False)

    # Medical rules
    hypertension_rule = parse_acrq_formula(
        "[forall X Hypertensive(X)]RequiresBloodPressureMed(X)"
    )
    ace_rule = parse_acrq_formula(
        "[forall X RequiresBloodPressureMed(X) & ~AllergicToACE(X)]PrescribeACE(X)"
    )
    beta_rule = parse_acrq_formula(
        "[forall X RequiresBloodPressureMed(X) & AllergicToACE(X)]PrescribeBetaBlocker(X)"
    )

    # Patient facts
    patient_hypertensive = parse_acrq_formula("Hypertensive(patient1)")
    patient_ace_allergy = parse_acrq_formula("AllergicToACE(patient1)")

    signed_formulas = [
        SignedFormula(t, hypertension_rule),
        SignedFormula(t, ace_rule),
        SignedFormula(t, beta_rule),
        SignedFormula(t, patient_hypertensive),
        SignedFormula(t, patient_ace_allergy),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Medical reasoning tableau:")
    print(tree)
    print(
        f"Result: {'✓ Consistent treatment plan' if result.satisfiable else '✗ Inconsistent'}"
    )

    if result.satisfiable and result.models:
        model = result.models[0]
        print("\nDerived treatment plan:")
        relevant_predicates = [
            "RequiresBloodPressureMed(patient1)",
            "PrescribeACE(patient1)",
            "PrescribeBetaBlocker(patient1)",
        ]
        for pred in relevant_predicates:
            if pred in str(model):
                print(f"  ✓ {pred}")

    print("\n🎯 Medical AI Benefits:")
    print("  - Handles conflicting guidelines systematically")
    print("  - LLM provides real-world drug interaction knowledge")
    print("  - Paraconsistent logic prevents system collapse from conflicts")
    print()


def demo_complex_reasoning_patterns(llm_evaluator):
    """Show complex reasoning patterns with LLM evaluation."""
    section("6. Complex Reasoning Patterns")

    renderer = TableauTreeRenderer(show_rules=True, compact=False)

    # Force LLM evaluation to appear by testing satisfiability differently
    print("6.1. Contradiction Testing - Force LLM Evaluation Visibility")
    print("Testing if Planet(pluto) can be false when formal rules derive it as true")
    print()

    planet_rule = parse_acrq_formula("[forall X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse_acrq_formula("OrbitsSun(pluto)")
    spherical_fact = parse_acrq_formula("Spherical(pluto)")
    planet_false = parse_acrq_formula("Planet(pluto)")

    signed_formulas = [
        SignedFormula(t, planet_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact),
        SignedFormula(f, planet_false),  # Try to make Planet(pluto) false
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree:")
    print(tree)
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("This should show clear LLM evaluation because of the contradiction")
    print()

    # Multiple derivations
    print(
        "6.2. Chained Derivations: OrbitsSun(pluto) → Planet(pluto) → CelestialBody(pluto)"
    )

    rule1 = parse_acrq_formula("[forall X OrbitsSun(X)]Planet(X)")
    rule2 = parse_acrq_formula("[forall X Planet(X)]CelestialBody(X)")
    fact = parse_acrq_formula("OrbitsSun(pluto)")

    signed_formulas = [
        SignedFormula(t, rule1),
        SignedFormula(t, rule2),
        SignedFormula(t, fact),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()

    tree = renderer.render_ascii(result.tableau)
    print("Tableau tree:")
    print(tree)
    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Should show LLM evaluation on each derived predicate")
    print()


def demo_knowledge_base_validation(llm_evaluator):
    """Validate knowledge base against real-world knowledge."""
    section("7. Knowledge Base Validation")

    print("Checking astronomical knowledge base for consistency with reality:")
    print()

    kb_assertions = [
        ("Orbits(moon, earth)", "Moon orbits Earth"),
        ("Orbits(earth, sun)", "Earth orbits Sun"),
        ("Larger(sun, earth)", "Sun is larger than Earth"),
        ("Larger(earth, jupiter)", "Earth is larger than Jupiter"),  # Should fail
        ("Planet(mars)", "Mars is a planet"),
        ("Planet(pluto)", "Pluto is a planet"),  # Controversial
    ]

    all_consistent = True
    for assertion_str, description in kb_assertions:
        assertion = parse_acrq_formula(assertion_str)
        signed = SignedFormula(t, assertion)

        tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator)
        result = tableau.construct()

        print(f"   {description}: ", end="")
        if result.satisfiable:
            print("✓ Consistent")
        else:
            print("✗ Contradicts world knowledge")
            all_consistent = False

    print()
    print(
        f"   Knowledge base {'is' if all_consistent else 'has inconsistencies with'} world knowledge"
    )
    print()


def main():
    section("LLM Integration with ACrQ Tableau Reasoning")

    print(
        "This comprehensive example demonstrates LLM integration via bilateral-truth."
    )
    print("The LLM evaluator provides real-world knowledge for predicate evaluation.")
    print()

    llm_evaluator = get_llm_evaluator()
    if not llm_evaluator:
        return

    print()

    # Run all demonstrations
    demo_basic_llm_evaluation(llm_evaluator)
    demo_tableau_tree_visualization(llm_evaluator)
    demo_universal_rule_with_llm(llm_evaluator)
    demo_bilateral_predicates(llm_evaluator)
    demo_medical_reasoning(llm_evaluator)
    demo_complex_reasoning_patterns(llm_evaluator)
    demo_knowledge_base_validation(llm_evaluator)

    # Summary
    section("Summary: LLM Integration Benefits")

    print("🎯 Key Benefits of LLM Integration with ACrQ:")
    print()
    print("1. **Real-World Knowledge**: LLM provides up-to-date factual knowledge")
    print("   that can be integrated with formal logical reasoning.")
    print()
    print("2. **Visible Rule Applications**: [llm-eval(...)] annotations in tableau")
    print("   trees show exactly when and how LLM knowledge is applied.")
    print()
    print("3. **Conflict Handling**: ACrQ's paraconsistent nature allows formal")
    print("   derivations and LLM knowledge to coexist even when conflicting.")
    print()
    print("4. **Bilateral Truth Values**: LLM can provide nuanced evaluations:")
    print("   - (t,f): Clearly true")
    print("   - (f,t): Clearly false")
    print("   - (f,f): Unknown/gap")
    print("   - (t,t): Conflicting evidence/glut")
    print()
    print("5. **Practical Applications**: Medical diagnosis, knowledge validation,")
    print("   scientific reasoning, and other domains requiring both logic and")
    print("   real-world knowledge.")
    print()
    print("6. **Non-Monotonic Reasoning**: LLM knowledge can change over time,")
    print("   allowing the system to adapt to new information.")
    print()

    # Note about mock evaluator
    if "mock" in str(type(llm_evaluator)).lower():
        print("💡 NOTE: Using mock evaluator - results are simulated.")
        print("   Install bilateral-truth and set an API key for real LLM evaluation:")
        print("   - export ANTHROPIC_API_KEY='your-key'")
        print("   - export OPENAI_API_KEY='your-key'")
        print("   - export GOOGLE_API_KEY='your-key'")


if __name__ == "__main__":
    main()
