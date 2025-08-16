#!/usr/bin/env python3
"""
ACrQ Bilateral Predicate Examples
Demonstrates paraconsistent reasoning with bilateral predicates.
"""

from wkrq import parse_acrq_formula, SyntaxMode, ACrQTableau, SignedFormula, t, f


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    section("ACrQ Bilateral Predicate Examples")
    
    # 1. Parsing modes
    print("1. Three parsing modes for bilateral predicates:")
    print()
    
    # Transparent mode (default)
    print("   Transparent mode (default):")
    formula = parse_acrq_formula("Human(alice) & ~Human(alice)")
    print(f"     Input: Human(alice) & ~Human(alice)")
    print(f"     Parsed as: Human(alice) & Human*(alice)")
    print(f"     (Negation automatically converted to dual)")
    print()
    
    # Bilateral mode
    print("   Bilateral mode (explicit):")
    formula = parse_acrq_formula("Human(alice) & Human*(alice)", SyntaxMode.BILATERAL)
    print(f"     Input: Human(alice) & Human*(alice)")
    print(f"     Parsed as: Human(alice) & Human*(alice)")
    print(f"     (Must use star syntax explicitly)")
    print()
    
    # Mixed mode
    print("   Mixed mode (both syntaxes):")
    formula = parse_acrq_formula("Human(alice) & ~Robot(alice)", SyntaxMode.MIXED)
    print(f"     Input: Human(alice) & ~Robot(alice)")
    print(f"     Can also write: Human(alice) & Robot*(alice)")
    print()
    
    # 2. Four information states
    print("2. Four possible information states with bilateral predicates:")
    print()
    
    # Clear positive
    print("   Clear positive (classical true):")
    signed_formulas = [
        SignedFormula(t, parse_acrq_formula("Human(alice)")),
        SignedFormula(f, parse_acrq_formula("Human*(alice)", SyntaxMode.BILATERAL))
    ]
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"     Human(alice)=t, Human*(alice)=f")
    print(f"     Interpretation: Clear positive evidence")
    print(f"     Satisfiable: {result.satisfiable}")
    print()
    
    # Clear negative
    print("   Clear negative (classical false):")
    signed_formulas = [
        SignedFormula(f, parse_acrq_formula("Human(alice)")),
        SignedFormula(t, parse_acrq_formula("Human*(alice)", SyntaxMode.BILATERAL))
    ]
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"     Human(alice)=f, Human*(alice)=t")
    print(f"     Interpretation: Clear negative evidence")
    print(f"     Satisfiable: {result.satisfiable}")
    print()
    
    # Knowledge gap
    print("   Knowledge gap (no information):")
    signed_formulas = [
        SignedFormula(f, parse_acrq_formula("Alien(alice)")),
        SignedFormula(f, parse_acrq_formula("Alien*(alice)", SyntaxMode.BILATERAL))
    ]
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"     Alien(alice)=f, Alien*(alice)=f")
    print(f"     Interpretation: No evidence either way")
    print(f"     Satisfiable: {result.satisfiable}")
    print()
    
    # Knowledge glut (THIS IS THE KEY DIFFERENCE FROM wKrQ!)
    print("   Knowledge glut (conflicting information):")
    signed_formulas = [
        SignedFormula(t, parse_acrq_formula("Robot(alice)")),
        SignedFormula(t, parse_acrq_formula("Robot*(alice)", SyntaxMode.BILATERAL))
    ]
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"     Robot(alice)=t, Robot*(alice)=t")
    print(f"     Interpretation: Conflicting evidence (glut)")
    print(f"     Satisfiable in ACrQ: {result.satisfiable}")  # TRUE - gluts allowed!
    print(f"     (This would close in wKrQ but not in ACrQ)")
    print()
    
    # 3. Paraconsistent reasoning
    print("3. Paraconsistent reasoning (contradictions don't explode):")
    print()
    
    # In classical/wKrQ logic, a contradiction implies everything
    print("   Classical explosion (p ∧ ¬p ⊢ q for any q):")
    print("   In ACrQ, this DOESN'T happen with bilateral predicates")
    print()
    
    # Create a glut
    glut = parse_acrq_formula("Human(alice) & ~Human(alice)")  # Becomes Human & Human*
    unrelated = parse_acrq_formula("Flies(alice)")
    
    # In classical logic, contradiction would imply anything
    # In ACrQ, the glut doesn't imply unrelated facts
    signed_formulas = [
        SignedFormula(t, glut),
        SignedFormula(f, unrelated)  # Can Flies(alice) be false despite the glut?
    ]
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"   Human(alice) ∧ Human*(alice) is true (glut)")
    print(f"   Does this force Flies(alice) to be true? {not result.satisfiable}")
    print(f"   (In ACrQ, gluts don't explode to unrelated predicates)")
    print()
    
    # 4. DeMorgan transformations in ACrQ
    print("4. DeMorgan laws work differently in ACrQ:")
    print()
    
    # Negated conjunction
    formula = parse_acrq_formula("~(Human(x) & Robot(x))")
    print(f"   Input: ~(Human(x) & Robot(x))")
    print(f"   Becomes: Human*(x) | Robot*(x)  (via DeMorgan)")
    
    signed = SignedFormula(t, formula)
    tableau = ACrQTableau([signed])
    result = tableau.construct()
    print(f"   Satisfiable: {result.satisfiable}")
    print()
    
    # 5. No general negation elimination
    print("5. ACrQ drops general negation elimination:")
    print()
    
    print("   wKrQ has: v:¬φ → ¬v:φ for all formulas")
    print("   ACrQ only has specific rules:")
    print("     - Double negation: ¬¬φ → φ")
    print("     - Negated predicates: ¬P(x) → P*(x)")
    print("     - DeMorgan for compounds")
    print()
    
    # This means compound negations behave differently
    formula = parse_acrq_formula("~(p | q)")  # Propositional, not predicate
    print(f"   Example: ~(p | q)")
    print(f"   In wKrQ: Would use general negation elimination")
    print(f"   In ACrQ: Uses DeMorgan to get ~p & ~q")
    print()
    
    # 6. Practical example: Belief revision
    print("6. Practical application - Belief revision:")
    print()
    
    print("   Agent believes: Tweety is a bird")
    print("   Agent believes: Birds fly")
    print("   Agent learns: Tweety is a penguin")
    print("   Agent learns: Penguins don't fly")
    print()
    
    bird_tweety = parse_acrq_formula("Bird(tweety)")
    flies_tweety = parse_acrq_formula("Flies(tweety)")
    not_flies_tweety = parse_acrq_formula("~Flies(tweety)")  # Becomes Flies*(tweety)
    
    # Create a glut about flying
    signed_formulas = [
        SignedFormula(t, bird_tweety),
        SignedFormula(t, flies_tweety),      # Positive evidence for flying
        SignedFormula(t, not_flies_tweety),  # Negative evidence for flying (Flies*)
    ]
    
    tableau = ACrQTableau(signed_formulas)
    result = tableau.construct()
    
    print(f"   Can maintain both beliefs? {result.satisfiable}")
    print(f"   (ACrQ allows conflicting evidence to coexist)")
    print(f"   This models uncertain/conflicting information")


if __name__ == "__main__":
    main()