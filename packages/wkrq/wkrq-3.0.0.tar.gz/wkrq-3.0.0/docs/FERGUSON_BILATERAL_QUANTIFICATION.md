# Ferguson's Bilateral Quantification (Definition 15)

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 13

## Definition 14: S*_fde Interpretation
A propositional S*_fde interpretation I is an AC interpretation where atoms are mapped to the set V₃².

## Definition 15: Predicate AC (respectively, S*_fde) Interpretation

A predicate AC (respectively, S*_fde) interpretation is a function I from L' to V₃² (respectively, V₃²) evaluating connectives as in Definition 13 and respecting the following:

```
I([∃xφ(x)]ψ(x)) = ⟨∃̇({⟨I₀(φ(c)), I₀(ψ(c))⟩ | c ∈ C}), ∀̇({⟨I₀(φ(c)), I₁(ψ(c))⟩ | c ∈ C})⟩
I([∀xφ(x)]ψ(x)) = ⟨∀̇({⟨I₀(φ(c)), I₀(ψ(c))⟩ | c ∈ C}), ∃̇({⟨I₀(φ(c)), I₁(ψ(c))⟩ | c ∈ C})⟩
```

## Key Insights

### 1. Bilateral Truth Values
The restricted quantifiers are "perfectly harmonious with the bilateral, weak Kleene-based interpretation from [7]."

### 2. Two Types of Refutation

In the bilateral context, consider two notions—one weak, one strong—in which [∃xφ(x)]ψ(x) might be thought to be **false** in an interpretation:

#### Weak Refutation
- The sentence might be considered **refuted** whenever searches for a c satisfying both φ(x) and ψ(x) have **failed**
- i.e., one has not successfully **verified** the sentence
- Reflected by assignment of ⟨f,v⟩ to the sentence (no verification)

#### Strong Refutation  
- There is a **demonstration** that any c satisfying φ(x) **must falsify** ψ(x)
- Reflected by assignment of ⟨v,t⟩ to the sentence (positive falsification)

### 3. Interpretation of Coordinates

For a quantified sentence [∃xφ(x)]ψ(x), the bilateral value ⟨u,v⟩ ∈ V₃² represents:
- **u**: Status of **verification** of [∃xφ(x)]ψ(x)
- **v**: Status of **falsification** of [∃xφ(x)]ψ(x)

The weak notion of refutation may be codified by assignment of ⟨f,v⟩ (not verified).
The strong type of refutation is reflected in receipt of ⟨v,t⟩ (positively falsified).

### 4. DeMorgan's Laws Restored

"The reader can confirm that the bilateral approach in fact improves on the presentation for wK inasmuch as DeMorgan's laws are reestablished; as S*_fde and AC are our actual targets, this should relieve concerns about their failure in wK."

Ferguson notes: "One further observation is required, establishing that V₃² is in fact closed under the bilateral interpretation of the restricted quantifiers."

## Lemma 2
**V₃²—the collection of S*_fde truth values—is closed under the above interpretation of the restricted quantifiers.**

## Implementation Significance

This definition explains our ACrQ implementation's approach:

### Bilateral Predicates
- **R(a)**: Positive evidence/verification
- **R*(a)**: Negative evidence/falsification

### Quantifier Semantics
For [∃xP(x)]Q(x):
- **Verification coordinate**: Uses ∃̇ on ⟨P(c), Q(c)⟩ pairs
- **Falsification coordinate**: Uses ∀̇ on ⟨P(c), ¬Q(c)⟩ pairs

For [∀xP(x)]Q(x):
- **Verification coordinate**: Uses ∀̇ on ⟨P(c), Q(c)⟩ pairs  
- **Falsification coordinate**: Uses ∃̇ on ⟨P(c), ¬Q(c)⟩ pairs

### Four Information States
The bilateral approach yields four states for any formula:
1. **⟨t,f⟩**: Verified, not falsified (TRUE)
2. **⟨f,t⟩**: Not verified, falsified (FALSE)
3. **⟨f,f⟩**: Neither verified nor falsified (GAP)
4. **⟨t,t⟩**: Both verified and falsified (GLUT)

## Why This Matters

1. **Fixes DeMorgan's Laws**: The bilateral approach restores DeMorgan's laws that fail in pure wK
2. **Handles Contradictions**: Can represent contradictory evidence (gluts)
3. **Practical Reasoning**: Better suited for intentional contexts (beliefs, desires)
4. **Paraconsistent**: Contradictions don't cause explosion

This is the theoretical foundation for why ACrQ uses bilateral predicates (R/R*) and can handle paraconsistent reasoning scenarios.