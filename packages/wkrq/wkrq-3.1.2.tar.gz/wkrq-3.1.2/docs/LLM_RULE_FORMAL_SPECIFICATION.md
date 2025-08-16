# Formal Specification: LLM Evaluation Rule in ACrQ-LLM System

## Executive Summary

The incorporation of LLM evaluation into ACrQ creates a new tableau system, which we formally designate as **ACrQ-LLM** (Analytic Containment with restricted Quantification and LLM evaluation). This document provides a formal specification of the LLM evaluation rule and analyzes its relationship to Ferguson's (2021) ACrQ system.

## 1. System Classification

### 1.1 Tableau System Hierarchy

```
wKrQ (Ferguson Definition 9)
  ├── ACrQ (Ferguson Definition 18)
  │     └── ACrQ-LLM (This specification)
  └── SRQ (Ferguson Definition 19)
```

**Key distinction**: ACrQ-LLM extends ACrQ with an additional **epistemic evaluation rule** that queries external knowledge sources during tableau construction.

### 1.2 Why This Is a Different System

ACrQ-LLM is technically a distinct tableau system from ACrQ because:

1. **New inference rule**: The LLM evaluation rule is not derivable from Ferguson's Definition 18
2. **External knowledge incorporation**: Violates the closed-world assumption of pure tableau calculi
3. **Non-deterministic behavior**: Results depend on LLM state at query time
4. **Epistemic semantics**: Introduces knowledge/belief operators implicitly

## 2. Formal Specification of the LLM Evaluation Rule

### 2.1 Rule Definition

Let `LLM` be an external evaluation function with signature:
```
LLM: Formula → BilateralTruthValue
```

Where `BilateralTruthValue = (u, v)` with `u, v ∈ {TRUE, FALSE, UNDEFINED}`.

The LLM evaluation rule is defined as:

```
                    LLM(P(a)) = (u, v)
    ───────────────────────────────────────────── (llm-eval)
    σ : P(a) ⊢ Γ_LLM(σ, P(a), u, v)
```

Where `Γ_LLM` generates conclusions based on the bilateral truth value:

### 2.2 Conclusion Generation Function

```
Γ_LLM(σ, φ, u, v) = 
  case (σ, u, v) of
    (t, TRUE, FALSE)  → {t : φ}                    // Confirmation
    (t, FALSE, TRUE)  → {f : φ}                    // Refutation (closes branch)
    (t, TRUE, TRUE)   → {t : φ, t : φ*}           // Glut
    (t, FALSE, FALSE) → {f : φ, f : φ*}           // Gap (closes branch)
    (f, TRUE, FALSE)  → {t : φ}                    // Contradiction (closes branch)
    (f, FALSE, TRUE)  → {f : φ}                    // Confirmation
    (f, TRUE, TRUE)   → {t : φ, t : φ*}           // Glut (closes branch)
    (f, FALSE, FALSE) → {f : φ, f : φ*}           // Gap
```

### 2.3 Application Conditions

The LLM evaluation rule applies when:

1. **Atomicity**: `φ` is atomic (predicate or propositional atom)
2. **Novelty**: Node has not been previously evaluated by LLM on this branch
3. **Availability**: LLM evaluator function is provided
4. **Priority**: Applied after all deterministic rules exhausted

### 2.4 Formal Properties

**Theorem 1 (Non-monotonicity)**: ACrQ-LLM is non-monotonic.

*Proof*: Let Γ ⊢_ACrQ-LLM φ at time t₁. If LLM knowledge changes at t₂, we may have Γ ⊬_ACrQ-LLM φ at t₂. □

**Theorem 2 (Soundness Relative to LLM)**: If Γ ⊢_ACrQ-LLM φ and LLM is consistent with reality, then φ follows from Γ and real-world facts.

*Proof sketch*: By induction on tableau construction, treating LLM as an oracle for ground truth. □

## 3. Integration with ACrQ Rules

### 3.1 Rule Priority Ordering

The complete rule priority for ACrQ-LLM:

```
Priority 1: Closure detection (contradictions)
Priority 2: Alpha rules (non-branching)
  - t-conjunction, f-disjunction, negation elimination, etc.
Priority 3: Beta rules (branching)  
  - t-disjunction, f-conjunction, t-implication, etc.
Priority 4: Gamma rules (quantifier instantiation)
  - Universal and existential quantifier rules
Priority 5: LLM evaluation (epistemic consultation)
  - Applied only to atomic formulas
```

### 3.2 Interaction with Bilateral Predicates

The LLM rule respects bilateral predicate semantics:

```
For predicate P(a):
  - LLM evaluates base predicate P(a)
  - Returns (u, v) representing positive/negative evidence
  
For bilateral predicate P*(a):
  - LLM evaluates base predicate P(a)  
  - Returns (u, v), then swaps components: (v, u)
```

### 3.3 Branch Closure Modification

ACrQ-LLM modifies ACrQ branch closure:

```
ACrQ closure (Lemma 5): 
  - t:P(a) and f:P(a) → closed
  - t:P(a) and t:P*(a) → open (glut allowed)

ACrQ-LLM closure:
  - Same as ACrQ for formal derivations
  - LLM gap (FALSE, FALSE) with t:P(a) → closed
  - LLM refutation with assertion → closed
```

## 4. Formal Rule Specification

### 4.1 LLM Evaluation Rule in Tableau Notation

```
Rule: llm-eval
Type: Non-branching (but may produce multiple conclusions)
Priority: 5 (lowest)

Premises: σ : P(a) where P is atomic
Side condition: P(a) not previously LLM-evaluated on branch

Action:
  1. Query LLM(P(a)) → (u, v)
  2. Generate conclusions per Γ_LLM(σ, P(a), u, v)
  3. Mark P(a) as LLM-evaluated on branch
  4. Check for contradictions with existing formulas
```

### 4.2 Formal Rule Schema

```latex
\infer[\text{llm-eval}]
  {Γ, σ : P(a), Γ_{\text{LLM}}(σ, P(a), u, v)}
  {Γ, σ : P(a) \quad \text{LLM}(P(a)) = (u, v)}
```

## 5. Comparison with Ferguson's Systems

### 5.1 Relationship to Definition 18 (ACrQ)

ACrQ-LLM extends ACrQ by:

| Aspect | ACrQ (Ferguson) | ACrQ-LLM |
|--------|-----------------|----------|
| Rules | Definition 18 rules | Definition 18 + llm-eval |
| Knowledge source | Formal axioms only | Axioms + LLM oracle |
| Determinism | Fully deterministic | Non-deterministic |
| Completeness | Complete for ACrQ semantics | Complete relative to LLM |
| Soundness | Sound for weak Kleene | Sound relative to LLM truth |

### 5.2 Theoretical Properties

**Preservation from ACrQ**:
- Bilateral predicate semantics
- Glut tolerance
- Paraconsistency
- Restricted quantification

**New in ACrQ-LLM**:
- Epistemic evaluation
- Time-dependent results
- Oracle-relative soundness
- Knowledge gap semantics

## 6. Implementation Validation

### 6.1 Rule Implementation Location

```python
# src/wkrq/tableau.py, lines 780-856

def _create_llm_evaluation_rule(
    self, node: TableauNode, branch: Branch
) -> Optional[RuleInfo]:
    """Create an LLM evaluation rule."""
    # Implementation of llm-eval rule
    bilateral_value = self.llm_evaluator(node.formula.formula)
    
    # Generate conclusions per Γ_LLM
    if bilateral_value.positive == TRUE and bilateral_value.negative == FALSE:
        # Clear positive evidence
        conclusion_set.append(SignedFormula(t, node.formula.formula))
    # ... etc per formal specification
```

### 6.2 Test Coverage

```python
# tests/test_llm_integration.py

class TestLLMEvaluationRule:
    def test_llm_positive_confirmation(self):
        """LLM(P(a)) = (TRUE, FALSE) with t:P(a) → satisfiable"""
        
    def test_llm_refutation(self):
        """LLM(P(a)) = (FALSE, TRUE) with t:P(a) → unsatisfiable"""
        
    def test_llm_glut(self):
        """LLM(P(a)) = (TRUE, TRUE) → both t:P(a) and t:P*(a)"""
        
    def test_llm_gap(self):
        """LLM(P(a)) = (FALSE, FALSE) → epistemic uncertainty"""
```

## 7. Documentation Requirements

### 7.1 Updates Needed

1. **FERGUSON_DEFINITION_18_ACRQ.md**: Add note about ACrQ-LLM extension
2. **README.md**: Clarify ACrQ vs ACrQ-LLM distinction
3. **API documentation**: Document llm_evaluator parameter
4. **Test suite**: Add LLM rule to rule verification tests

### 7.2 Ferguson Compliance Note

ACrQ-LLM should be documented as:

> An extension of Ferguson's ACrQ (Definition 18) that adds epistemic evaluation via LLM consultation. This creates a hybrid formal-epistemic reasoning system that combines tableau-based logical inference with real-world knowledge from language models.

## 8. Formal System Definition

### Definition: ACrQ-LLM Tableau System

**ACrQ-LLM** is defined as the tuple ⟨L, S, R, C⟩ where:

- **L**: The language of ACrQ with bilateral predicates
- **S**: Ferguson's six-sign system {t, f, e, m, n, v}
- **R**: Rules from Definition 18 ∪ {llm-eval}
- **C**: Closure conditions from Lemma 5 extended with LLM contradictions

### Inference Relation

Γ ⊢_ACrQ-LLM^E φ denotes that φ is derivable from Γ in ACrQ-LLM with epistemic oracle E (the LLM).

## 9. Soundness and Completeness

### 9.1 Relative Soundness

**Theorem 3**: ACrQ-LLM is sound relative to the conjunction of weak Kleene semantics and LLM knowledge.

*Proof*: By structural induction on tableau rules, treating LLM as a consistent knowledge base. The llm-eval rule preserves truth when LLM accurately reflects reality. □

### 9.2 Incompleteness

**Theorem 4**: ACrQ-LLM is incomplete.

*Proof*: There exist formulas derivable in classical logic that ACrQ-LLM cannot derive when LLM knowledge is incomplete. Example: If LLM lacks knowledge about P(a), the gap response prevents certain valid inferences. □

## 10. Practical Implications

### 10.1 Use Cases

ACrQ-LLM is suitable for:
- Hybrid formal-empirical reasoning
- Knowledge base validation
- Consistency checking with real-world facts
- Educational theorem proving with fact checking

### 10.2 Limitations

ACrQ-LLM should not be used when:
- Reproducibility is required
- Formal completeness is necessary
- LLM accuracy cannot be verified
- Time-invariant results are needed

## 11. Conclusion

The LLM evaluation rule transforms ACrQ into ACrQ-LLM, a hybrid formal-epistemic tableau system. While this violates the purity of Ferguson's formal system, it creates a powerful tool for combining logical reasoning with real-world knowledge. The formal specification provided here ensures that this extension is well-defined and its properties are understood.

## 12. References

1. Ferguson, T.M. (2021). "Tableaux for Restricted Quantification..." TABLEAUX 2021.
2. Allen, B.P. (2024). "bilateral-truth: LLM Factuality Assessment"
3. This specification document

## Appendix A: Rule Validation Tests

```python
def validate_llm_rule():
    """Validate that llm-eval rule meets formal specification."""
    
    # Test 1: Rule only applies to atomic formulas
    assert applies_to_atomic_only()
    
    # Test 2: Rule respects bilateral predicates
    assert handles_bilateral_correctly()
    
    # Test 3: Rule generates correct conclusions per Γ_LLM
    assert conclusions_match_specification()
    
    # Test 4: Rule has correct priority (after all other rules)
    assert has_lowest_priority()
    
    # Test 5: Rule marks formulas as evaluated
    assert prevents_duplicate_evaluation()
```

## Appendix B: Future Work

1. **Formal verification**: Coq/Isabelle proof of relative soundness
2. **Optimization**: Caching strategies for LLM queries
3. **Extensions**: Multiple LLM consensus mechanisms
4. **Analysis**: Complexity analysis of ACrQ-LLM
5. **Applications**: Domain-specific ACrQ-LLM variants