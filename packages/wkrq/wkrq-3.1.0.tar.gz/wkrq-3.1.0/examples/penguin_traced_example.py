#!/usr/bin/env python3
"""
Traced Penguin Example: Step-by-Step Tableau Construction

This example demonstrates the classic "Tweety the Penguin" problem in
defeasible reasoning, showing exactly how the tableau develops step by step.

The problem:
- Birds typically fly
- Penguins are birds
- Penguins don't fly
- Tweety is a penguin
- Can Tweety fly?

This creates a conflict between the general rule (birds fly) and the
specific exception (penguins don't fly).
"""

from wkrq import (
    ACrQTableau,
    SignedFormula,
    SyntaxMode,
    parse_acrq_formula,
    t,
)
from wkrq.semantics import FALSE, TRUE, BilateralTruthValue


def create_mock_llm():
    """Create an LLM evaluator with knowledge about birds and penguins."""

    def evaluate_formula(formula_str: str) -> BilateralTruthValue:
        """Mock LLM that knows about birds and penguins."""
        formula = str(formula_str).lower()

        # Knowledge base
        if "bird(tweety)" in formula:
            # Tweety is a bird (penguins are birds)
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif "penguin(tweety)" in formula:
            # Tweety is specifically a penguin
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif "flies(tweety)" in formula or "fly(tweety)" in formula:
            # Penguins don't fly
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        elif "bird(opus)" in formula:
            # Opus is also a penguin character, hence a bird
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif "penguin(opus)" in formula:
            # Opus is a penguin
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif "flies(opus)" in formula or "fly(opus)" in formula:
            # Opus doesn't fly either
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        elif "bird(robin)" in formula:
            # A robin is a bird
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif "penguin(robin)" in formula:
            # A robin is not a penguin
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        elif "flies(robin)" in formula or "fly(robin)" in formula:
            # Robins can fly
            return BilateralTruthValue(positive=TRUE, negative=FALSE)

        # Unknown predicates
        return BilateralTruthValue(positive=FALSE, negative=FALSE)

    return evaluate_formula


def trace_penguin_problem():
    """Demonstrate the penguin problem with step-by-step tableau construction."""

    print("=" * 70)
    print("THE TWEETY PROBLEM: A Step-by-Step Tableau Construction")
    print("=" * 70)
    print()

    # Setup the formal rules
    print("FORMAL KNOWLEDGE:")
    print("-" * 40)
    print("1. General Rule: [∀X Bird(X)]Flies(X)")
    print("   'All birds fly' (default assumption)")
    print()
    print("2. Exception: [∀X Penguin(X)]~Flies(X)")
    print("   'All penguins don't fly' (specific exception)")
    print()
    print("3. Taxonomy: [∀X Penguin(X)]Bird(X)")
    print("   'All penguins are birds' (taxonomic fact)")
    print()
    print("4. Individual: Penguin(tweety)")
    print("   'Tweety is a penguin' (specific fact)")
    print()

    # The question
    print("QUESTION: Can Tweety fly?")
    print("-" * 40)
    print("We'll test whether Flies(tweety) is satisfiable.")
    print()

    # Create the formulas as separate signed formulas
    print("FORMULAS FOR SATISFIABILITY TEST:")
    print("-" * 40)
    print("  1. t: [∀X Bird(X)]Flies(X)")
    print("  2. t: [∀X Penguin(X)]~Flies(X)")
    print("  3. t: [∀X Penguin(X)]Bird(X)")
    print("  4. t: Penguin(tweety)")
    print("  5. t: Flies(tweety)")
    print()
    print("If UNSATISFIABLE: Tweety cannot fly (contradiction found)")
    print("If SATISFIABLE: Tweety could potentially fly")
    print()

    # Parse and create tableau with separate signed formulas
    bird_rule = parse_acrq_formula("[∀X Bird(X)]Flies(X)", SyntaxMode.TRANSPARENT)
    penguin_exception = parse_acrq_formula(
        "[∀X Penguin(X)]~Flies(X)", SyntaxMode.TRANSPARENT
    )
    taxonomy = parse_acrq_formula("[∀X Penguin(X)]Bird(X)", SyntaxMode.TRANSPARENT)
    penguin_fact = parse_acrq_formula("Penguin(tweety)", SyntaxMode.TRANSPARENT)
    flies_claim = parse_acrq_formula("Flies(tweety)", SyntaxMode.TRANSPARENT)

    signed_formulas = [
        SignedFormula(t, bird_rule),
        SignedFormula(t, penguin_exception),
        SignedFormula(t, taxonomy),
        SignedFormula(t, penguin_fact),
        SignedFormula(t, flies_claim),
    ]

    tableau = ACrQTableau(signed_formulas, llm_evaluator=create_mock_llm(), trace=True)

    print("=" * 70)
    print("TABLEAU CONSTRUCTION BEGINS")
    print("=" * 70)
    print()

    # Initial setup
    print("STEP 0: Initial Formula")
    print("-" * 40)
    print("We start with t: [entire conjunction]")
    print("The tableau will decompose this step by step.")
    print()

    # Step 1: Decompose main conjunction
    print("STEP 1: Decompose Main Conjunction [t-conjunction rule]")
    print("-" * 40)
    print("From: t: (F1 & F2 & F3 & F4 & F5)")
    print("Derive:")
    print("  0. t: [∀X Bird(X)]Flies(X)")
    print("  1. t: [∀X Penguin(X)]~Flies(X)")
    print("  2. t: [∀X Penguin(X)]Bird(X)")
    print("  3. t: Penguin(tweety)")
    print("  4. t: Flies(tweety)")
    print()
    print("Now we have 5 signed formulas to work with.")
    print()

    # Step 2: LLM evaluates Penguin(tweety)
    print("STEP 2: LLM Evaluates Penguin(tweety) [llm-eval rule]")
    print("-" * 40)
    print("The LLM is asked: Is Penguin(tweety) true?")
    print("LLM response: YES (Tweety is indeed a penguin)")
    print()
    print("From: 3. t: Penguin(tweety)")
    print("LLM confirms: t: Penguin(tweety) ✓")
    print("(No conflict - LLM agrees with formal assertion)")
    print()

    # Step 3: LLM evaluates Flies(tweety)
    print("STEP 3: LLM Evaluates Flies(tweety) [llm-eval rule]")
    print("-" * 40)
    print("The LLM is asked: Does Flies(tweety) hold?")
    print("LLM response: NO (Penguins don't fly)")
    print()
    print("From: 4. t: Flies(tweety)")
    print("LLM asserts: f: Flies(tweety)")
    print()
    print("⚡ CONFLICT DETECTED!")
    print("   We have both t: Flies(tweety) and f: Flies(tweety)")
    print("   This branch closes immediately! ×")
    print()

    # Step 4: Universal instantiation with tweety
    print("STEP 4: Universal Instantiations with 'tweety'")
    print("-" * 40)
    print()
    print("4a. From 2: t: [∀X Penguin(X)]Bird(X)")
    print("    Since we have Penguin(tweety), we can instantiate:")
    print("    ")
    print("    Rule creates two branches:")
    print("    Branch A: f: Penguin(tweety)")
    print("    Branch B: t: Bird(tweety)")
    print("    ")
    print("    Branch A closes: Conflicts with 3. t: Penguin(tweety) ×")
    print("    Continue on Branch B...")
    print()

    print("4b. From 1: t: [∀X Penguin(X)]~Flies(X)")
    print("    Since we have Penguin(tweety), we can instantiate:")
    print("    ")
    print("    Rule creates two branches:")
    print("    Branch B1: f: Penguin(tweety)")
    print("    Branch B2: t: ~Flies(tweety)")
    print("    ")
    print("    Branch B1 closes: Conflicts with 3. t: Penguin(tweety) ×")
    print("    ")
    print("    On Branch B2: t: ~Flies(tweety)")
    print("    In ACrQ transparent mode, this becomes: t: Flies*(tweety)")
    print("    (Negative evidence about flying)")
    print()

    print("4c. From 0: t: [∀X Bird(X)]Flies(X)")
    print("    We now have Bird(tweety) from step 4a, so we can instantiate:")
    print("    ")
    print("    Rule creates two branches:")
    print("    Branch B2-1: f: Bird(tweety)")
    print("    Branch B2-2: t: Flies(tweety)")
    print("    ")
    print("    Branch B2-1 closes: Conflicts with derived t: Bird(tweety) ×")
    print("    Branch B2-2 continues but we already have t: Flies(tweety)")
    print()

    # Final state
    print("=" * 70)
    print("FINAL TABLEAU STATE")
    print("=" * 70)
    print()
    print("All branches have closed:")
    print("  • Main branch: Closed by LLM conflict on Flies(tweety)")
    print("  • Branch A: Closed by conflict on Penguin(tweety)")
    print("  • Branch B1: Closed by conflict on Penguin(tweety)")
    print("  • Branch B2-1: Closed by conflict on Bird(tweety)")
    print()
    print("Result: UNSATISFIABLE")
    print()

    # Analysis
    print("=" * 70)
    print("ANALYSIS: What This Proves")
    print("=" * 70)
    print()
    print("1. FORMAL REASONING PATH:")
    print("   Penguin(tweety) → Bird(tweety) → Flies(tweety)")
    print("   [From taxonomy and general rule]")
    print()
    print("2. EXCEPTION PATH:")
    print("   Penguin(tweety) → ~Flies(tweety)")
    print("   [From specific exception rule]")
    print()
    print("3. LLM VALIDATION:")
    print("   The LLM confirms penguins don't fly")
    print("   Creating immediate conflict with formal derivation")
    print()
    print("4. CONCLUSION:")
    print("   Tweety CANNOT fly")
    print("   The specific exception (penguins don't fly) overrides")
    print("   the general rule (birds fly) in both formal and LLM reasoning")
    print()

    # Actually run it
    print("=" * 70)
    print("ACTUAL TABLEAU EXECUTION")
    print("=" * 70)
    print()

    result = tableau.construct()

    # Print the actual trace
    if tableau.construction_trace:
        print("ACTUAL TRACE OF RULE APPLICATIONS:")
        print("-" * 40)
        tableau.construction_trace.print_trace()
        print()

    print(
        f"Computed Result: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}"
    )
    print(f"Open Branches: {result.open_branches}")
    print(f"Closed Branches: {result.closed_branches}")
    print()

    if tableau.construction_trace:
        print("Rule Application Summary:")
        print("-" * 40)
        for line in tableau.construction_trace.get_rule_summary():
            print(line)

    print()
    print("=" * 70)
    print("END OF TRACED PENGUIN EXAMPLE")
    print("=" * 70)


def trace_robin_problem():
    """Show how the same rules work differently for a regular bird."""

    print("\n" + "=" * 70)
    print("BONUS: THE ROBIN PROBLEM (A Regular Bird)")
    print("=" * 70)
    print()

    print("Same rules, different individual:")
    print("  • Robin is a bird (not a penguin)")
    print("  • Testing: Can Robin fly?")
    print()

    formula_str = """
    [∀X Bird(X)]Flies(X) &
    [∀X Penguin(X)]~Flies(X) &
    [∀X Penguin(X)]Bird(X) &
    Bird(robin) &
    ~Penguin(robin) &
    Flies(robin)
    """

    print("FORMULA:")
    print("  [∀X Bird(X)]Flies(X) &")
    print("  [∀X Penguin(X)]~Flies(X) &")
    print("  [∀X Penguin(X)]Bird(X) &")
    print("  Bird(robin) &")
    print("  ~Penguin(robin) &")
    print("  Flies(robin)")
    print()

    formula = parse_acrq_formula(formula_str, SyntaxMode.TRANSPARENT)
    signed_formula = SignedFormula(t, formula)
    tableau = ACrQTableau([signed_formula], llm_evaluator=create_mock_llm(), trace=True)

    print("KEY DIFFERENCES FROM PENGUIN CASE:")
    print("-" * 40)
    print("1. Robin is NOT a penguin (explicitly stated)")
    print("2. Exception rule [∀X Penguin(X)]~Flies(X) won't trigger")
    print("3. General rule [∀X Bird(X)]Flies(X) applies without conflict")
    print("4. LLM confirms: Robins can fly")
    print()

    result = tableau.construct()

    print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print()
    print("Conclusion: Robin CAN fly")
    print("(No contradiction between formal rules and real-world knowledge)")
    print()


if __name__ == "__main__":
    trace_penguin_problem()
    trace_robin_problem()
