#!/usr/bin/env python3
"""
Restricted Quantifier Examples
Demonstrates Ferguson's restricted quantification in wKrQ.
"""

from wkrq import SignedFormula, WKrQTableau, entails, n, parse, solve, t


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    section("Restricted Quantifier Examples")

    # 1. Basic restricted quantification
    print("1. Restricted quantifier syntax:")
    print("   [∃X P(X)]Q(X) means: There exists X such that P(X) AND Q(X)")
    print("   [∀X P(X)]Q(X) means: For all X, if P(X) then Q(X)")
    print()

    # 2. Valid quantifier inferences
    print("2. Valid quantifier inferences:")

    # Universal instantiation
    forall_human_mortal = parse("[forall X Human(X)]Mortal(X)")
    human_socrates = parse("Human(socrates)")
    mortal_socrates = parse("Mortal(socrates)")

    is_valid = entails([forall_human_mortal, human_socrates], mortal_socrates)
    print(f"   ∀X[Human(X)→Mortal(X)], Human(socrates) ⊢ Mortal(socrates): {is_valid}")

    # Existential generalization
    exists_human_mortal = parse("[exists X Human(X)]Mortal(X)")
    is_valid = entails([human_socrates, mortal_socrates], exists_human_mortal)
    print(f"   Human(socrates), Mortal(socrates) ⊢ ∃X[Human(X)∧Mortal(X)]: {is_valid}")
    print()

    # 3. Invalid quantifier inferences
    print("3. Invalid quantifier inferences (critical for soundness):")

    # Existential does NOT imply universal
    exists_a_b = parse("[exists X A(X)]B(X)")
    forall_a_b = parse("[forall Y A(Y)]B(Y)")

    is_valid = entails([exists_a_b], forall_a_b)
    print(f"   ∃X[A(X)∧B(X)] ⊢ ∀Y[A(Y)→B(Y)]: {is_valid}")  # Must be False!

    # This was a critical bug we fixed - n-sign universal must generate fresh constants
    print("   (This tests our fresh constant generation for n-universal)")
    print()

    # 4. Domain reasoning
    print("4. Domain-specific reasoning:")

    # All birds fly, Tweety is a bird, therefore Tweety flies
    all_birds_fly = parse("[forall X Bird(X)]Flies(X)")
    tweety_bird = parse("Bird(tweety)")
    tweety_flies = parse("Flies(tweety)")

    is_valid = entails([all_birds_fly, tweety_bird], tweety_flies)
    print(f"   Classic syllogism: {is_valid}")

    # But penguins are birds that don't fly (would need exception handling)
    all_penguins_birds = parse("[forall X Penguin(X)]Bird(X)")
    # Note: Negation within the consequent of restricted quantifier needs parentheses
    all_penguins_not_fly = parse("[forall X Penguin(X)](~Flies(X))")
    tweety_penguin = parse("Penguin(tweety)")

    # This creates a potential inconsistency in classical logic
    # but weak Kleene can handle it via undefined values
    premises = [all_birds_fly, all_penguins_birds, all_penguins_not_fly, tweety_penguin]
    is_valid = entails(premises, tweety_flies)
    print(f"   Tweety paradox (Tweety flies?): {is_valid}")

    not_flies = parse("~Flies(tweety)")
    is_valid = entails(premises, not_flies)
    print(f"   Tweety paradox (Tweety doesn't fly?): {is_valid}")
    print("   (Weak Kleene can handle this via undefined)")
    print()

    # 5. Testing Definition 11 implementation
    print("5. Ferguson Definition 11 (correct inference checking):")

    # Create a simple inference to test
    p = parse("P(a)")
    forall_p_q = parse("[forall X P(X)]Q(X)")
    q = parse("Q(a)")

    # Manual tableau construction using Definition 11
    signed_formulas = [
        SignedFormula(t, p),  # t: P(a) (premise)
        SignedFormula(t, forall_p_q),  # t: [∀X P(X)]Q(X) (premise)
        SignedFormula(n, q),  # n: Q(a) (negated conclusion)
    ]

    print("   Testing P(a), [∀X P(X)]Q(X) ⊢ Q(a)")
    print("   Initial tableau nodes:")
    print("     t: P(a)")
    print("     t: [∀X P(X)]Q(X)")
    print("     n: Q(a)  (using n-sign per Definition 11)")

    tableau = WKrQTableau(signed_formulas)
    result = tableau.construct()

    print(f"   All branches close? {not result.satisfiable}")
    print(
        f"   Therefore inference is: {'VALID' if not result.satisfiable else 'INVALID'}"
    )
    print()

    # 6. Multiple quantifiers in conjunction
    print("6. Multiple quantifiers (not nested):")

    # Multiple quantifiers can appear in conjunctions/disjunctions
    formula = parse("([exists X P(X)]Q(X)) & ([forall Y R(Y)]S(Y))")
    print("   Multiple: ([∃X P(X)]Q(X)) ∧ ([∀Y R(Y)]S(Y))")
    result = solve(formula, t)
    print(f"   Satisfiable under t: {result.satisfiable}")

    # Different variables in disjunction
    formula = parse("([exists X Human(X)]Wise(X)) | ([forall Y Bird(Y)]Flies(Y))")
    print("   Disjunction: ([∃X Human(X)]Wise(X)) ∨ ([∀Y Bird(Y)]Flies(Y))")
    result = solve(formula, t)
    print(f"   Satisfiable under t: {result.satisfiable}")


if __name__ == "__main__":
    main()
