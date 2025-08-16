#!/usr/bin/env python3
"""
LLM Integration Example
Shows how to use the bilateral-truth package for real-world knowledge.

REQUIRES: pip install bilateral-truth
"""

from wkrq import ACrQTableau, SignedFormula, parse_acrq_formula, t, f
from wkrq.llm_integration import create_llm_tableau_evaluator


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    section("LLM Integration with ACrQ")
    
    print("This example demonstrates LLM integration via bilateral-truth.")
    print("The LLM evaluator provides real-world knowledge for predicates.")
    print()
    
    # Try to get an LLM evaluator
    try:
        # Try real LLM first (requires API key)
        for provider in ['openai', 'anthropic', 'google']:
            try:
                llm_evaluator = create_llm_tableau_evaluator(provider)
                if llm_evaluator:
                    print(f"✓ Using {provider} LLM evaluator")
                    break
            except:
                continue
        else:
            # Fall back to mock if no API keys available
            llm_evaluator = create_llm_tableau_evaluator('mock')
            print("✓ Using mock LLM evaluator (no API key found)")
            print("  Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY for real LLM")
    except ImportError:
        print("ERROR: bilateral-truth package not installed")
        print("Install with: pip install bilateral-truth")
        return
    except Exception as e:
        print(f"ERROR: Could not create LLM evaluator: {e}")
        return
    
    print()
    
    # 1. Basic LLM evaluation
    print("1. Basic LLM evaluation of predicates:")
    print()
    
    # The LLM will evaluate these based on real-world knowledge
    formulas = [
        "Planet(mars)",          # True - Mars is a planet
        "Planet(pluto)",         # Controversial - depends on definition
        "Orbits(earth, sun)",    # True - Earth orbits the Sun
        "Orbits(sun, earth)",    # False - Sun doesn't orbit Earth
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
    
    # 2. Handling conflicting information
    print("2. Combining formal reasoning with world knowledge:")
    print()
    
    # Formal assertion that conflicts with reality
    print("   Formal: Pluto is definitely a planet")
    print("   Reality: Pluto's status is controversial")
    print()
    
    # Formal assertion
    pluto_planet = parse_acrq_formula("Planet(pluto)")
    
    # Create tableau - LLM might provide nuanced evaluation
    signed_formulas = [SignedFormula(t, pluto_planet)]
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()
    
    print(f"   Result: {result.satisfiable}")
    if result.satisfiable and result.models:
        model = result.models[0]
        print(f"   Model: {model}")
    print()
    
    # 3. Complex reasoning with LLM
    print("3. Complex reasoning combining logic and world knowledge:")
    print()
    
    # Penguins are birds but don't fly - classic exception
    print("   Testing: Penguins are birds that don't fly")
    
    penguin_bird = parse_acrq_formula("Bird(penguin)")
    penguin_flies = parse_acrq_formula("Flies(penguin)")
    
    signed_formulas = [
        SignedFormula(t, penguin_bird),   # Assert: penguin is a bird
        SignedFormula(t, penguin_flies),  # Assert: penguin flies
    ]
    
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()
    
    print(f"   Can penguin fly according to LLM? {result.satisfiable}")
    print("   (LLM should recognize this conflicts with reality)")
    print()
    
    # 4. Bilateral evaluation
    print("4. Bilateral truth values from LLM:")
    print()
    
    print("   LLM can provide nuanced bilateral evaluations:")
    print("   - (t,f): Clearly true")
    print("   - (f,t): Clearly false")
    print("   - (f,f): Unknown/gap")
    print("   - (t,t): Conflicting evidence/glut")
    print()
    
    # Test something ambiguous
    ambiguous = parse_acrq_formula("Intelligent(dolphin)")
    signed = SignedFormula(t, ambiguous)
    
    tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator)
    result = tableau.construct()
    
    print(f"   'Dolphins are intelligent': {result.satisfiable}")
    print("   (Depends on definition of intelligence)")
    print()
    
    # 5. Practical application
    print("5. Practical application - Knowledge base validation:")
    print()
    
    print("   Checking a knowledge base for consistency with reality:")
    print()
    
    kb_assertions = [
        "Orbits(moon, earth)",      # True
        "Orbits(earth, sun)",        # True
        "Larger(sun, earth)",        # True
        "Larger(earth, jupiter)",    # False - should be caught
    ]
    
    all_consistent = True
    for assertion_str in kb_assertions:
        assertion = parse_acrq_formula(assertion_str)
        signed = SignedFormula(t, assertion)
        
        tableau = ACrQTableau([signed], llm_evaluator=llm_evaluator)
        result = tableau.construct()
        
        print(f"   {assertion_str}: ", end="")
        if result.satisfiable:
            print("✓")
        else:
            print("✗ Inconsistent with world knowledge!")
            all_consistent = False
    
    print()
    print(f"   Knowledge base {'is' if all_consistent else 'is NOT'} consistent with reality")
    print()
    
    # Note about mock evaluator
    if 'mock' in str(type(llm_evaluator)).lower():
        print("NOTE: Using mock evaluator - results are simulated.")
        print("      Install bilateral-truth and set an API key for real LLM evaluation.")


if __name__ == "__main__":
    main()