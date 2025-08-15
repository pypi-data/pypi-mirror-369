# Ferguson Definition 9 - Complete Tableau Calculus

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 9

## Complete Definition 9

The tableau calculus **wKrQ** for weak Kleene with restricted quantifiers is captured by the following rules:

### Negation Rules
```
v : ~φ        m : φ           n : φ
------      ---------      -----------
~v : φ      t : φ + f : φ   f : φ + e : φ
```

### Conjunction Rules  
```
v : φ ∧ ψ
---------
+ {v₀ : φ ○ v₁ : ψ} for all v₀ ∧ v₁ = v
```

### Disjunction Rules
```
v : φ ∨ ψ
---------
+ {v₀ : φ ○ v₁ : ψ} for all v₀ ∨ v₁ = v
```

### Existential Quantifier Rules

#### t : [∃φ(x)]ψ(x)
```
t : φ(c) ○ t : ψ(c)
```
Single branch with fresh constant c, both must be true.

#### f : [∃φ(x)]ψ(x)
```
m : φ(c) ○ m : ψ(c) ○ (n : φ(a) + n : ψ(a))
```
Complex rule with two constants:
- Fresh constant c with m signs (meaningful)
- Arbitrary constant a with n signs (non-true), branching

#### e : [∃φ(x)]ψ(x)
```
e : φ(a) + e : ψ(a)
```
Branches for error propagation with arbitrary constant a.

### Universal Quantifier Rules

#### t : [∀φ(x)]ψ(x)
```
m : φ(c) ○ m : ψ(c) ○ (n : φ(a) + t : ψ(a))
```
Complex rule with two constants:
- Fresh constant c with m signs
- Arbitrary constant a with n for restriction or t for matrix

#### f : [∀φ(x)]ψ(x)
```
t : φ(c) ○ f : ψ(c)
```
Counterexample with fresh constant c.

#### e : [∀φ(x)]ψ(x)
```
e : φ(a) + e : ψ(a)
```
Branches for error propagation with arbitrary constant a.

## Notation

- `○` means "and" (formulas on same branch)
- `+` means "or" (different branches)
- `c` denotes a fresh constant
- `a` denotes an arbitrary (possibly existing) constant
- `~v` means the negation of sign v where:
  - ~t = f
  - ~f = t  
  - ~e = e
  - ~m = n
  - ~n = m
  - ~v = v (variable stays variable)

## Important Notes

1. **Two-constant pattern**: Many quantifier rules use TWO constants:
   - A fresh constant c for the "witness"
   - An arbitrary constant a for additional constraints

2. **Meta-signs in quantifier rules**: The quantifier rules make heavy use of m and n signs, not just t, f, e.

3. **Complexity**: The quantifier rules are significantly more complex than standard first-order tableau rules.

## Footnote 2

"One qualification is in order, namely, that the critique emphasizes the semantic interpretations. Recent work by Andreas Fjellstad in [10] provides a very elegant proof-theoretic analysis but explicitly declines to 'engage in the discussion' of interpretation."

## Implementation Implications

Our current implementation **simplifies** some of these rules, particularly:
1. The t-universal rule is simplified to branching rather than using m/n signs
2. We don't always use the two-constant pattern explicitly
3. Some meta-sign usage is converted to direct branching

These simplifications may be logically equivalent but don't match Ferguson's specification exactly.