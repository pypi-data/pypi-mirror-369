# Ferguson's Restricted Quantifier Definitions

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 7

## Key Definitions from the Paper

### Definition 3: Restricted Kleene Quantifiers

The restricted Kleene quantifiers are functions ∃̇ and ∀̇ mapping a nonempty sets X ⊆ V₃² to truth values from V₃ as follows:

#### Existential Quantifier ∃̇(X):
```
       { t   if ⟨t,t⟩ ∈ X
∃̇(X) = { e   if for all ⟨u,v⟩ ∈ X, either u = e or v = e  
       { f   if ⟨t,t⟩ ∉ X & for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
```

#### Universal Quantifier ∀̇(X):
```
       { t   if ⟨t,f⟩, ⟨t,e⟩ ∉ X & for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
∀̇(X) = { e   if for all ⟨u,v⟩ ∈ X, either u = e or v = e
       { f   if {⟨t,f⟩, ⟨t,e⟩} ∩ X ≠ ∅ & for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
```

### Definition 4: Predicate Weak Kleene Interpretation

A predicate weak Kleene interpretation I is a pair ⟨C^I, R^I⟩ where:
- C^I is a domain of individuals
- R^I is a collection of functions where I assigns:
  - every constant c an individual c^I ∈ C^I
  - every n-ary predicate R a function R^I : (C^I)^n → V₃

In order to simplify matters, it is assumed that every element of C^I is c^I for some constant c.

### Definition 5: Formula Evaluation

A predicate weak Kleene interpretation induces a map from L' to V₃ defined as in Definition 2 with the exception that for atomic formulae:

- I(R(c₀, ..., c_{n-1})) = R^I(c₀^I, ..., c_{n-1}^I)

and quantified formulae are evaluated as follows:

- I([∃xφ(x)]ψ(x)) = ∃̇({⟨I(φ(c)), I(ψ(c))⟩ | c ∈ C})
- I([∀xφ(x)]ψ(x)) = ∀̇({⟨I(φ(c)), I(ψ(c))⟩ | c ∈ C})

### Definition 6: Validity

Validity in weak Kleene logic is defined as truth preservation, i.e.

Γ ⊨_wK φ if for all wK interpretations such that I[Γ] = {t}, I(φ) = t

where I[Γ] = {I(φ) | φ ∈ Γ}.

## Key Insights

1. **Restricted Quantifiers**: The quantifiers evaluate pairs ⟨restriction, matrix⟩ rather than single formulas
2. **Error Propagation**: If all instances have error in either component, the quantifier evaluates to e
3. **Existential True**: Requires at least one instance where both restriction and matrix are true
4. **Universal False**: Has a counterexample where restriction is true but matrix is false or error
5. **Non-triviality Condition**: For f value, requires at least one non-error instance

## Implications for Implementation

### For [∃xP(x)]Q(x):
- **True**: Some x makes both P(x) and Q(x) true
- **Error**: All x have P(x)=e or Q(x)=e  
- **False**: No x makes both true, but some x is non-error

### For [∀xP(x)]Q(x):
- **True**: No counterexample (P true, Q false/error) and some non-error instance exists
- **Error**: All instances have error
- **False**: Counterexample exists (P true, Q false/error) and some non-error instance exists

## Note on DeMorgan's Laws

Ferguson notes: "although the above quantifiers align with reasonable intuitions about restricted quantifiers, DeMorgan's laws fail. Despite this, the quantifiers will satisfy DeMorgan's laws for S*_fde and AC, as we will see in subsequent sections."

This is important for understanding why certain classical equivalences don't hold in weak Kleene logic with these quantifiers.