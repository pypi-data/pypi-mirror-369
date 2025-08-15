# Ferguson Theorems 3-4: ACrQ Soundness and Completeness

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 16

## Theorem 3: Soundness of ACrQ

**If Γ ⊢_ACrQ φ then Γ ⊨_AC φ.**

### Proof Summary
The proof works by:
1. Taking an ACrQ tableau T demonstrating Γ ⊢_ACrQ φ
2. Using Lemma 6 to show there's a closed ACrQ tableau for Γ* ⊢_ACrQ φ*
3. Noting this involves no properly ACrQ rules—it's thus a wKrQ⁺ tableau (and a fortiori a wKrQ tableau)
4. Therefore Γ* ⊢_wKrQ φ* and by Theorem 1, Γ* ⊨_wK φ*
5. Finally, by Lemma 4, we conclude Γ ⊨_AC φ

### Key Insight
The soundness proof relies on the relationship between ACrQ and wKrQ through the bilateral translation.

## Theorem 4: Completeness of ACrQ

**If Γ ⊨_AC φ then Γ ⊢_ACrQ φ**

### Proof Summary
Using the contrapositive:
1. Suppose Γ ⊬_ACrQ φ
2. By Lemma 6, Γ* ⊬_ACrQ φ*
3. As negation is essentially eliminated, Γ* ⊬_wKrQ φ*
4. Therefore there exists a wKrQ tableau with an open branch B
5. Definition 12 yields a weak Kleene branch model I_B for which I_B[Γ] = {t} and I_B(φ) ≠ t
6. I_B induces an AC interpretation I_B^⊠ that preserves the interpretation of constants while bilaterally interpreting n-ary predicates
7. The semantic clauses ensure that I_B^⊠ verifies all of Γ* while failing to verify φ*
8. By Lemma 3, this lifts to Γ and φ, hence Γ ⊭_AC φ

## Critical Implementation Insight

The proof reveals how ACrQ works:

### Transformation Process
1. **Input**: AC formulas with regular predicates
2. **Translation**: Apply Definition 17 to get bilateral formulas (*)
3. **Tableau**: Apply ACrQ rules (which are wKrQ⁺ plus special rules)
4. **Closure**: Check using Lemma 5 (φ* = ψ* condition)

### What "No Properly ACrQ Rules" Means
The proof mentions that the translated tableau "involves no properly ACrQ rules." This means:
- Once formulas are in bilateral form (after * translation)
- The actual tableau construction uses wKrQ⁺ rules
- The special ACrQ rules (DeMorgan transformations) are part of the translation

## Implementation Status

Our implementation:
1. ✓ Has wKrQ⁺ (wKrQ without general negation)
2. ✓ Handles atomic bilateral predicates (P/P*)
3. ✗ Missing DeMorgan transformation rules
4. ✗ May not correctly implement φ* = ψ* closure condition

## The Complete Picture

ACrQ achieves paraconsistent reasoning by:
1. **Bilateral predicates**: Track positive and negative evidence separately
2. **Translation rules**: Build DeMorgan's laws into the translation
3. **Modified closure**: Only close when formulas are equivalent after translation
4. **No general negation**: Avoid explosive contradictions

The system is **sound and complete** for AC semantics, providing a paraconsistent logic suitable for reasoning about intentional contexts where contradictory evidence can coexist.

## Practical Implication

For our implementation to be truly Ferguson-compliant ACrQ:
1. Must add DeMorgan transformation rules from Definition 18
2. Should verify closure condition uses bilateral equivalence
3. Need to ensure translation rules are consistently applied

Without these, we have a partial implementation that handles basic cases but misses the full power of Ferguson's bilateral approach.