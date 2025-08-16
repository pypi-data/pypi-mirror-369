#!/usr/bin/env python3
"""
Basic wKrQ Examples
Demonstrates fundamental weak Kleene logic operations and tableau construction.
"""

from wkrq import parse, solve, valid, entails, SignedFormula, WKrQTableau, t, f, e


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    section("Basic wKrQ Examples")
    
    # 1. Three-valued logic basics
    print("1. Three-valued logic:")
    
    # Excluded middle is NOT valid in weak Kleene
    p_or_not_p = parse("p | ~p")
    print(f"   p ∨ ¬p is valid? {valid(p_or_not_p)}")  # False - can be undefined
    
    # But it can't be false
    result = solve(p_or_not_p, f)
    print(f"   p ∨ ¬p can be false? {result.satisfiable}")  # False
    
    # It CAN be undefined
    result = solve(p_or_not_p, e)
    print(f"   p ∨ ¬p can be undefined? {result.satisfiable}")  # True
    print()
    
    # 2. Weak Kleene contagion
    print("2. Weak Kleene undefined contagion:")
    
    # If p is undefined, p ∧ q is undefined regardless of q
    conjunction = parse("p & q")
    signed_formulas = [
        SignedFormula(e, parse("p")),  # p is undefined
        SignedFormula(t, parse("q")),  # q is true
        SignedFormula(t, conjunction)  # Try to make p∧q true
    ]
    tableau = WKrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"   Can p∧q be true when p=e, q=t? {result.satisfiable}")  # False (semantic issue but tableau may say True due to incompleteness)
    
    # If either operand is undefined, disjunction is undefined
    disjunction = parse("p | q")
    signed_formulas = [
        SignedFormula(t, parse("p")),  # p is true
        SignedFormula(e, parse("q")),  # q is undefined
        SignedFormula(t, disjunction)  # Try to make p∨q true
    ]
    tableau = WKrQTableau(signed_formulas)
    result = tableau.construct()
    print(f"   Can p∨q be true when p=t, q=e? {result.satisfiable}")  # False semantically, but tableau may miss it
    print()
    
    # 3. Valid inferences in weak Kleene
    print("3. Valid inferences:")
    
    # Modus ponens
    p = parse("p")
    p_implies_q = parse("p -> q")
    q = parse("q")
    is_valid = entails([p, p_implies_q], q)
    print(f"   Modus ponens (p, p→q ⊢ q): {is_valid}")  # True
    
    # Modus tollens
    not_q = parse("~q")
    not_p = parse("~p")
    is_valid = entails([p_implies_q, not_q], not_p)
    print(f"   Modus tollens (p→q, ¬q ⊢ ¬p): {is_valid}")  # True
    
    # Disjunctive syllogism
    p_or_q = parse("p | q")
    is_valid = entails([p_or_q, not_p], q)
    print(f"   Disjunctive syllogism (p∨q, ¬p ⊢ q): {is_valid}")  # True
    
    # Double negation (both directions valid)
    double_neg_p = parse("~~p")
    is_valid = entails([double_neg_p], p)
    print(f"   Double negation elim (¬¬p ⊢ p): {is_valid}")  # True
    is_valid = entails([p], double_neg_p)
    print(f"   Double negation intro (p ⊢ ¬¬p): {is_valid}")  # True
    print()
    
    # 4. Invalid classical principles
    print("4. Classical principles that FAIL in weak Kleene:")
    
    # Self-implication fails
    p_implies_p = parse("p -> p")
    is_valid = valid(p_implies_p)
    print(f"   p → p is valid? {is_valid}")  # False (when p=e, e→e=e)
    
    # Addition fails
    is_valid = entails([p], p_or_q)
    print(f"   Addition (p ⊢ p∨q): {is_valid}")  # False (t∨e = e)
    
    # Hypothetical syllogism fails
    q_implies_r = parse("q -> r")
    p_implies_r = parse("p -> r")
    is_valid = entails([p_implies_q, q_implies_r], p_implies_r)
    print(f"   Hypothetical syllogism ((p→q)∧(q→r) ⊢ p→r): {is_valid}")  # False
    
    # DeMorgan laws fail
    not_p_and_q = parse("~(p & q)")
    not_p_or_not_q = parse("~p | ~q")
    is_valid = entails([not_p_and_q], not_p_or_not_q)
    print(f"   DeMorgan (¬(p∧q) ⊢ ¬p∨¬q): {is_valid}")  # False
    print()
    
    # 5. Models and countermodels
    print("5. Finding models:")
    
    formula = parse("p | q")
    result = solve(formula, t)
    print(f"   Models for t:(p∨q): {len(result.models)} found")
    if result.models:
        print(f"   First model: {result.models[0]}")
    
    # Find countermodel for invalid inference
    result = solve(p_implies_p, f)  # p→p can be false?
    print(f"   p→p can be false? {result.satisfiable}")
    result = solve(p_implies_p, e)  # p→p can be undefined?
    print(f"   p→p can be undefined? {result.satisfiable}")
    if result.models:
        print(f"   Countermodel: {result.models[0]}")


if __name__ == "__main__":
    main()