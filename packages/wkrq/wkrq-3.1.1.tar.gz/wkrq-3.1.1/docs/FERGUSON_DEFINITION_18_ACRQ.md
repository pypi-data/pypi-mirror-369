# Ferguson Definition 18: ACrQ Tableau Calculus

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 15

## Key Lemmas

### Lemma 3
For an AC interpretation I, **I(φ) = I(φ*)**.

### Lemma 4  
**Γ ⊨_AC φ iff Γ* ⊨_wK φ***

These lemmas establish that the bilateral translation preserves validity.

## Definition 18: ACrQ Tableau Rules

Let **wKrQ⁺** be the result of dropping the ~ rule from wKrQ. Then the tableau calculus **ACrQ** is defined by adding to wKrQ⁺:

### Atomic Bilateral Rules
```
v : ~R(c₀, ..., cₙ₋₁)     →    v : R*(c₀, ..., cₙ₋₁)
v : R*(c₀, ..., cₙ₋₁)     →    v : R(c₀, ..., cₙ₋₁)  
```

### Double Negation
```
v : ~~φ
───────
v : φ
```

### Negated Conjunction/Disjunction (DeMorgan Rules!)
```
v : ~(φ ∧ ψ)              v : ~(φ ∨ ψ)
─────────────             ─────────────
v : (~φ ∨ ~ψ)             v : (~φ ∧ ~ψ)
```

### Negated Quantifiers (Quantifier DeMorgan!)
```
v : ~[∀φ(x)]ψ(x)          v : ~[∃φ(x)]ψ(x)
─────────────────         ─────────────────
v : [∃φ(x)]~ψ(x)          v : [∀φ(x)]~ψ(x)
```

where v is any element of V₃.

## Critical Insights

### 1. No General Negation Elimination
ACrQ is wKrQ⁺ (wKrQ without the general ~ rule). This means:
- No general rule v : ~φ → ~v : φ
- Negation is handled through specific rules above

### 2. DeMorgan's Laws Are Rules!
The rules for ~(φ ∧ ψ) and ~(φ ∨ ψ) **directly implement** DeMorgan's laws:
- ~(φ ∧ ψ) becomes (~φ ∨ ~ψ)
- ~(φ ∨ ψ) becomes (~φ ∧ ~ψ)

### 3. Bilateral Predicates
- ~R(...) becomes R*(...)
- This implements the bilateral semantics

### 4. Quantifier Duality
- ~∀ becomes ∃~
- ~∃ becomes ∀~

## Lemma 5: Branch Closure

If u : φ and v : ψ, for distinct u and v, are on a branch of an ACrQ tableau such that **φ* = ψ***, then the branch will close.

### Key Point
The condition φ* = ψ* means that after bilateral translation, the formulas are identical. This is crucial for understanding closure in ACrQ.

## Lemma 6: Soundness and Completeness

**Γ ⊢_ACrQ φ if and only if Γ* ⊢_ACrQ φ***

This establishes that ACrQ is sound and complete with respect to AC semantics via the bilateral translation.

## Implementation Implications

Our ACrQ implementation should:

1. **NOT have general negation elimination** ✓ (We have this correct)
2. **Transform ~R to R*** ✓ (We have this for atomic predicates)
3. **Implement DeMorgan rules for compounds** ✗ (We're MISSING this!)
4. **Implement quantifier DeMorgan rules** ✗ (We're MISSING this!)

### What We're Missing

Our implementation doesn't have explicit rules for:
- v : ~(φ ∧ ψ) → v : (~φ ∨ ~ψ)
- v : ~(φ ∨ ψ) → v : (~φ ∧ ~ψ)
- v : ~[∀φ(x)]ψ(x) → v : [∃φ(x)]~ψ(x)
- v : ~[∃φ(x)]ψ(x) → v : [∀φ(x)]~ψ(x)

These should be added to `acrq_rules.py` to fully implement Definition 18.

## The DeMorgan Mystery Solved

Ferguson's Definition 18 shows that DeMorgan's laws are **tableau rules** in ACrQ, not valid inferences. When you have ~(P ∧ Q), the tableau rule transforms it to (~P ∨ ~Q) directly. This is how DeMorgan's laws are "reestablished" - as transformation rules, not as semantic validities!