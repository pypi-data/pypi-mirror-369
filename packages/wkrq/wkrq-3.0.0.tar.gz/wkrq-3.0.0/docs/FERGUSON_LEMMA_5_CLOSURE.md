# Ferguson Lemma 5: ACrQ Branch Closure

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 15

## Lemma 5: Modified Closure Condition for ACrQ

**If u : φ and v : ψ, for distinct u and v, are on a branch of an ACrQ tableau such that φ* = ψ*, then the branch will close.**

## Critical Insight

The closure condition is based on **φ* = ψ*** (equality after bilateral translation), not just φ = ψ.

## What This Means

### Example 1: Gluts Don't Close
- t : P(a) and t : P*(a) on same branch
- P(a)* = P(a) and P*(a)* = P(a) (wait, this seems wrong...)
- Actually, according to Definition 17: P*(a) is already in bilateral form
- These have different starred forms, so no closure
- This allows gluts (contradictory evidence)

### Example 2: Standard Contradictions Close  
- t : P(a) and f : P(a) on same branch
- Both have P(a)* = P(a)
- Different signs (t ≠ f) with same starred formula
- Branch closes

### Example 3: Bilateral Contradictions
- t : P*(a) and f : P*(a) on same branch
- Both translate to the same bilateral form
- Different signs with same starred formula
- Branch closes

## Implementation Question

Our current implementation checks for closure when:
```python
# Same formula, different signs from {t, f, e}
```

But according to Lemma 5, we should check:
```python
# Same formula after bilateral translation, different signs
```

This might affect how we handle:
1. Mixed predicates (P vs P*)
2. Compound formulas that should be transformed by DeMorgan rules
3. The relationship between regular and bilateral predicates

## The Proof Insight

The proof mentions: "the functionality of ∧ ensures that in any such branch, either u₀ ≠ v₀ or u₁ ≠ v₁. Because φᵢ* = ψᵢ* for each i, the induction hypothesis ensures that each branch will close."

This refers to the fact that when conjunction rules are applied, if the formulas have the same bilateral translation but different signs, at least one of the resulting branches will have a contradiction.

## Key Takeaway

The closure condition in ACrQ is more subtle than in wKrQ:
- It's based on equality after bilateral translation
- This allows certain apparent contradictions (gluts) to coexist
- But ensures genuine logical contradictions still cause closure

## Implementation Status

We need to verify if our closure checking correctly handles:
1. The φ* = ψ* condition (checking bilateral equivalence)
2. Allowing gluts (P and P* with same sign)
3. Closing on genuine contradictions

This is related to the missing DeMorgan rules - without them, formulas that should have the same bilateral translation might not be recognized as such.