# Ferguson's Rejected Quantifier Approaches

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 8

## Why Standard Quantifiers Were Rejected

Ferguson explicitly discusses and **rejects** both strong and weak Kleene quantifiers for his system. This page provides crucial context for understanding why restricted quantification was necessary.

## Definition 7: Strong Kleene Quantifiers (REJECTED)

The strong Kleene quantifiers are defined as:

```
∃(X) = {
  t   if t ∈ X
  e   if e ∈ X and t ∉ X
  f   if X = {f}
}

∀(X) = {
  t   if X = {t}
  e   if e ∈ X and f ∉ X  
  f   if f ∈ X
}
```

Comparing Definition 7 to the strong Kleene tables of [14] makes clear that e.g., strong Kleene existential quantification is essentially infinitary strong Kleene disjunction (and mutatis mutandis for universal quantification).

## Definition 8: Weak Kleene Quantifiers (REJECTED)

The weak Kleene quantifiers are defined as:

```
∃(X) = {
  t   if t ∈ X and e ∉ X
  e   if e ∈ X
  f   if X = {f}
}

∀(X) = {
  t   if X = {t}
  e   if e ∈ X
  f   if f ∈ X and e ∉ X
}
```

## Ferguson's Critique

From the text:
"By applying this algebra to weak Kleene quantifiers, we can define weak Kleene quantifiers in a manner that carries over the hallmark features. The weak quantifiers are then defined as follows..."

"Upon examination, each set of quantifiers has properties that conflict with our intuitive understanding of the above first-order formulae, making neither account entirely suitable for our purposes."

## Key Issues with Standard Approaches

1. **Strong Kleene Quantifiers**: 
   - Treat quantification as infinitary disjunction/conjunction
   - Don't properly handle domain restrictions
   - Malinowski describes them as "not frequently encountered in the literature" [15]

2. **Weak Kleene Quantifiers**:
   - Error is too contagious (any e makes the whole quantifier e)
   - Don't align with intuitive understanding of restricted domains
   - Insufficient for modeling intentional contexts

## The Solution: Restricted Quantifiers

Ferguson's innovation is to use **restricted quantifiers** (Definition 3) that:
- Evaluate pairs ⟨restriction, matrix⟩ rather than single values
- Better handle domain restrictions in practical applications
- Support reasoning about beliefs, goals, and other intentional contexts
- More closely align with natural language expressions like "all dogs are mammals"

## Important Quote

"If we look to universally quantified statements, the strong Kleene quantifiers should be considered true if it holds that whenever φ(c) is evaluated as t, also ψ(c) is evaluated as t, and false if ψ(c) is evaluated as f, for c for which either φ(c) or ψ(c) is evaluated as e. In such a case, φ(c) → ψ(c) will be evaluated as e, and ∀x(φ(x) → ψ(x)) will also be evaluated as e. As an example, the fact that Höhle gives a definite truth condition for this is given, though every thing that is a dog is a mammal, the fact that 'the number two is a dog' is meaningless is sufficient to render 'all dogs are mammals' meaningless."

This example illustrates why Ferguson needed a different approach - the standard quantifiers make sensible statements meaningless due to error propagation.

## Implementation Note

Our implementation uses `RestrictedExistentialFormula` and `RestrictedUniversalFormula` classes specifically to implement Ferguson's Definition 3 restricted quantifiers, NOT the standard strong/weak Kleene quantifiers shown here.