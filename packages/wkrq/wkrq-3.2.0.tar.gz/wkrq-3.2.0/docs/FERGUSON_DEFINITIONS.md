# Ferguson (2021) - Consolidated Definitions

This document consolidates all key definitions from Ferguson's "Tableaux for Systems Related to Weak Kleene Logic" (2021) that are implemented in this codebase.

## Core Definitions

### Definition 1: Weak Kleene Truth Tables
The three-valued weak Kleene logic uses truth values {t, f, e} with contagious undefined:
- Negation: ¬t = f, ¬f = t, ¬e = e
- Conjunction: t∧t = t, any operation with e yields e, otherwise f
- Disjunction: f∨f = f, any operation with e yields e, otherwise t
- Implication: Defined as ¬φ∨ψ

### Definition 3: Restricted Quantification
**Restricted Existential [∃xφ(x)]ψ(x):**
- t if ∃c: φ(c) = t AND ψ(c) = t
- e if ∀c: φ(c) = e OR ψ(c) = e
- f otherwise

**Restricted Universal [∀xφ(x)]ψ(x):**
- t if (∀c: φ(c) = t → ψ(c) = t) AND (∃c: φ(c) ≠ e AND ψ(c) ≠ e)
- e if ∀c: φ(c) = e OR ψ(c) = e
- f otherwise

### Definition 6: Validity
Γ ⊨wK φ if for all wK interpretations where I[Γ] = {t}, we have I(φ) = t

## wKrQ System (Definition 9)

### Tableau Rules
The wKrQ system uses six signs: t, f, e (truth values) and m, n, v (meta-signs).

**Negation Rules:**
- t:¬φ → f:φ
- f:¬φ → t:φ
- e:¬φ → e:φ
- m:¬φ → (f:φ)|(t:φ)
- n:¬φ → (t:φ)|(e:φ)

**Conjunction Rules:**
- t:(φ∧ψ) → t:φ, t:ψ
- f:(φ∧ψ) → (f:φ)|(f:ψ)|(e:φ,e:ψ)
- e:(φ∧ψ) → (e:φ)|(e:ψ)
- m:(φ∧ψ) → (t:φ,t:ψ)|(f:φ)|(f:ψ)
- n:(φ∧ψ) → (f:φ)|(f:ψ)|(e:φ,e:ψ)

**Disjunction Rules:**
- t:(φ∨ψ) → (t:φ)|(t:ψ)|(e:φ,e:ψ)
- f:(φ∨ψ) → f:φ, f:ψ
- e:(φ∨ψ) → (e:φ)|(e:ψ)
- m:(φ∨ψ) → (t:φ)|(t:ψ)|(f:φ,f:ψ)
- n:(φ∨ψ) → (f:φ,f:ψ)|(e:φ)|(e:ψ)

**Implication Rules (φ→ψ treated as ¬φ∨ψ):**
- t:(φ→ψ) → (f:φ)|(t:ψ)|(e:φ,e:ψ)
- f:(φ→ψ) → t:φ, f:ψ
- e:(φ→ψ) → (e:φ)|(e:ψ)
- m:(φ→ψ) → (f:φ)|(t:ψ)|(t:φ,f:ψ)
- n:(φ→ψ) → (t:φ,f:ψ)|(e:φ)|(e:ψ)

**Quantifier Rules:**
See FERGUSON_QUANTIFIER_DEFINITIONS.md for detailed rules.

**Critical Implementation Note:**
Meta-signs on atomic formulas must expand:
- m:p → (t:p)|(f:p)
- n:p → (f:p)|(e:p)

### Definition 10: Branch Closure
A branch closes when the same formula φ appears with distinct signs u, v ∈ {t, f, e}.
Meta-signs (m, n, v) do not cause closure.

### Definition 11: Inference
{φ₀, ..., φₙ₋₁} ⊢wKrQ φ when every branch of a tableau with initial nodes {t:φ₀, ..., t:φₙ₋₁, n:φ} closes.

**Critical:** Use n-sign for conclusion, not t:¬φ.

## ACrQ System

### Definition 17: Bilateral Translation
Converts standard formulas to bilateral form:
- ¬P(x) becomes P*(x)
- ¬¬φ becomes φ
- ¬(φ∧ψ) becomes ¬φ∨¬ψ (DeMorgan)
- ¬(φ∨ψ) becomes ¬φ∧¬ψ (DeMorgan)

### Definition 18: ACrQ Rules
ACrQ = wKrQ minus general negation elimination, plus:
- Bilateral predicate rules
- DeMorgan transformations for negated compounds
- No general rule v:¬φ → ¬v:φ for compound formulas

### Lemma 5: ACrQ Branch Closure
Branches close when u:φ and v:ψ appear with distinct signs where φ and ψ are bilaterally equivalent.

**Critical:** Gluts are allowed - t:R(a) and t:R*(a) can coexist without closing.

## Soundness and Completeness

### Theorem 1 (Soundness)
If Γ ⊢wKrQ φ, then Γ ⊨wK φ

### Theorem 2 (Completeness)
If Γ ⊨wK φ and the domain is finite, then Γ ⊢wKrQ φ

### Theorems 3 & 4
Similar soundness and completeness results hold for ACrQ.

## Known Implementation Limitation

**Semantic Incompleteness:** The tableau performs syntactic but not semantic contradiction checking. This means branches with semantic contradictions (e.g., t:(p∨q) with e:p and e:q) remain open, creating spurious models. The system remains sound but is semantically incomplete.