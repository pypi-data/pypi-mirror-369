#!/usr/bin/env python3
"""
Simple demonstration of LLM evaluation with ACrQ tableau.
Shows how LLM knowledge can contradict formal assertions.
"""

from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t, SyntaxMode
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE
from wkrq.cli import TableauTreeRenderer

def create_simple_llm():
    """LLM that knows Tweety is a penguin and penguins don't fly."""
    def evaluate(formula):
        s = str(formula).lower()
        if 'penguin(tweety)' in s:
            return BilateralTruthValue(positive=TRUE, negative=FALSE)  # Tweety IS a penguin
        elif 'flies(tweety)' in s or 'fly(tweety)' in s:
            return BilateralTruthValue(positive=FALSE, negative=TRUE)  # Tweety does NOT fly
        elif 'bird(tweety)' in s:
            return BilateralTruthValue(positive=TRUE, negative=FALSE)  # Tweety IS a bird
        else:
            # Unknown - return knowledge gap
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
    return evaluate

def test_simple_contradiction():
    """Test: Assert Tweety flies, but LLM knows penguins don't fly."""
    print("=" * 70)
    print("TEST 1: Simple Contradiction")
    print("=" * 70)
    print("\nSetup:")
    print("  Formal assertion: t: Flies(tweety)")
    print("  LLM knowledge: Penguins don't fly")
    print("\nExpected: UNSATISFIABLE (contradiction)")
    print()
    
    # Create tableau with single assertion
    formula = parse_acrq_formula('Flies(tweety)', SyntaxMode.TRANSPARENT)
    signed = SignedFormula(t, formula)
    
    tableau = ACrQTableau([signed], llm_evaluator=create_simple_llm(), trace=True)
    result = tableau.construct()
    
    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")
    
    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")

def test_complex_reasoning():
    """Test: Formal rules + LLM knowledge."""
    print("\n" + "=" * 70)
    print("TEST 2: Formal Rules + LLM Knowledge")
    print("=" * 70)
    print("\nSetup:")
    print("  Rule: [∀X Penguin(X)]~Flies(X)  (penguins don't fly)")
    print("  Fact: Penguin(tweety)")
    print("  Claim: Flies(tweety)")
    print("  LLM: Confirms penguin facts")
    print("\nExpected: UNSATISFIABLE (multiple paths to contradiction)")
    print()
    
    # Create formulas
    rule = parse_acrq_formula('[∀X Penguin(X)]~Flies(X)', SyntaxMode.TRANSPARENT)
    fact = parse_acrq_formula('Penguin(tweety)', SyntaxMode.TRANSPARENT)
    claim = parse_acrq_formula('Flies(tweety)', SyntaxMode.TRANSPARENT)
    
    signed_formulas = [
        SignedFormula(t, rule),
        SignedFormula(t, fact),
        SignedFormula(t, claim)
    ]
    
    tableau = ACrQTableau(signed_formulas, llm_evaluator=create_simple_llm(), trace=True)
    result = tableau.construct()
    
    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")
    
    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")

def test_knowledge_gap():
    """Test: LLM has no knowledge about something."""
    print("\n" + "=" * 70)
    print("TEST 3: Knowledge Gap")
    print("=" * 70)
    print("\nSetup:")
    print("  Assertion: t: Flies(opus)")
    print("  LLM knowledge: No information about opus")
    print("\nExpected: Branch closes due to explicit uncertainty")
    print()
    
    formula = parse_acrq_formula('Flies(opus)', SyntaxMode.TRANSPARENT)
    signed = SignedFormula(t, formula)
    
    tableau = ACrQTableau([signed], llm_evaluator=create_simple_llm(), trace=True)
    result = tableau.construct()
    
    # Show the tableau tree
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")
    
    if tableau.construction_trace:
        print("\nTrace Summary:")
        for line in tableau.construction_trace.get_rule_summary():
            print(f"  {line}")
    
    print("\nNote: Gap produces f: Flies(opus) and f: Flies*(opus)")
    print("      This represents 'cannot verify' AND 'cannot refute'")

if __name__ == "__main__":
    test_simple_contradiction()
    test_complex_reasoning()
    test_knowledge_gap()