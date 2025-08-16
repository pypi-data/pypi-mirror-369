# Ferguson Definition 19: SrQ Tableau Calculus

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", p. 17

## Definition 19: SrQ for S*_fde with Restricted Quantifiers

The tableau calculus **SrQ** for S*_fde with restricted quantifiers is captured by adding the following rules to **ACrQ** where v ∈ {t, f}:

### Bilateral Predicate Rules for Error (e) and Meaningful (m)

```
e : R(c₀, ..., cₙ₋₁)       e : R*(c₀, ..., cₙ₋₁)
────────────────────       ────────────────────
e : R*(c₀, ..., cₙ₋₁)      e : R(c₀, ..., cₙ₋₁)

v : R(c₀, ..., cₙ₋₁)       v : R*(c₀, ..., cₙ₋₁)  
────────────────────       ────────────────────
m : R*(c₀, ..., cₙ₋₁)      m : R(c₀, ..., cₙ₋₁)
```

**Important Proviso**: An above rule may be applied to a formula R(c₀, ..., cₙ₋₁) or R*(c₀, ..., cₙ₋₁) **at most once** on any branch.

## Key Insights

### 1. Building on ACrQ
SrQ extends ACrQ by adding special rules for handling the relationship between R and R* with error (e) and meaningful (m) signs.

### 2. The "Not e" Interpretation
Ferguson notes: "Thinking of the notation m as indicating 'not e' may aid in interpreting the above rules."
- If R(c₀, ..., cₙ₋₁) is assigned e.g. t, this establishes only that its mate R*(c₀, ..., cₙ₋₁) is **not e**
- This entails a branch on the two remaining values (t or f)

### 3. Application Constraint
The proviso that rules apply "at most once on any branch" prevents infinite loops and ensures termination.

### 4. Relationship to S*_fde
S*_fde is the four-valued First Degree Entailment logic with bilateral predicates. The system allows:
- Truth (t)
- Falsity (f)  
- Error/undefined (e)
- Both true and false (glut) - when R and R* are both t

## Supporting Lemmas

### Lemma 7
**Γ ⊨_S*fde φ iff Γ* ⊨_S φ***

Establishes the relationship between S*_fde validity and the bilateral translation.

### Lemma 8  
**Let I_B be a branch model defined on an open branch from an SrQ tableau. Then I_B ∈ S.**

Shows that branch models from SrQ tableaux belong to the appropriate class S of weak Kleene interpretations where:
- I(R(c₀, ..., cₙ₋₁)) = e if and only if I(R*(c₀, ..., cₙ₋₁)) = e

### Lemma 9
**Let wKrQ^S be the result of adding properly SrQ rules to wKrQ^+. Then wKrQ^S is sound with respect to S.**

The "properly SrQ rules" correspond precisely to the semantic conditions defining the class S.

## Soundness and Completeness

### Theorem 5 (Soundness of SrQ)
**If Γ ⊢_SrQ φ then Γ ⊨_S*fde φ**

## Implementation Notes

### What This Means for Our System

1. **SrQ is ACrQ plus additional rules**: The four rules above handle the special relationship between R and R* in the four-valued setting

2. **The e-rules establish coupling**: If one of R/R* has error, so does the other

3. **The v-rules establish branching**: If one of R/R* has a definite value (t or f), the other is meaningful (branches to t or f, but not e)

4. **Single application constraint**: Each rule can only be applied once per branch to prevent loops

### Current Implementation Status

Our implementation currently supports ACrQ but not SrQ. To add SrQ support would require:

1. Adding the four bilateral rules above to a new `srq_rules.py`
2. Implementing the "at most once" constraint with tracking
3. Supporting the meaningful (m) sign properly as a branching instruction
4. Adjusting the semantics to handle S*_fde's four-valued logic

### The System Hierarchy

1. **wKrQ**: Basic three-valued weak Kleene with restricted quantification
2. **ACrQ**: wKrQ without general negation, plus bilateral predicates for paraconsistent reasoning  
3. **SrQ**: ACrQ plus special bilateral rules for four-valued FDE logic

Each system builds on the previous, adding more sophisticated handling of contradictions and undefined values.