# Ferguson Definition 17: Bilateral Predicate Translation

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 14

## Definition 16: Validity in S*_fde and AC
Let L be either S*_fde or AC. Then L validity is defined as truth preservation, i.e.

**Γ ⊨_L φ if for all L interpretations such that I₀[Γ] = {t}, I₀(φ) = t.**

## Definition 17: Bilateral Language Translation

For a language L, let L* be the language that includes for every predicate R a predicate of the same arity R*; for a sentence φ ∈ L, let φ* ∈ L* be:

### Translation Rules

1. **Atomic predicates**: 
   - R(t₀, ..., tₙ₋₁)* = R(t₀, ..., tₙ₋₁) 
   - (~R(t₀, ..., tₙ₋₁))* = R*(t₀, ..., tₙ₋₁)

2. **Double negation**: 
   - (~~φ)* = φ*

3. **Conjunction**: 
   - (φ ∧ ψ)* = (φ)* ∧ (ψ)*
   - (φ ∨ ψ)* = (φ)* ∨ (ψ)*

4. **Quantifiers**:
   - [∀xφ(x)]ψ(x))* = [∀x(φ(x))*](ψ(x))*
   - [∃xφ(x)]ψ(x))* = [∃x(φ(x))*](ψ(x))*

5. **Compound negations**:
   - (~(φ ∧ ψ))* = (~φ)* ∨ (~ψ)* 
   - (~(φ ∨ ψ))* = (~φ)* ∧ (~ψ)*

6. **Quantified negations**:
   - (~[∀xφ(x)]ψ(x))* = [∃x(φ(x))*](~ψ(x))*
   - (~[∃xφ(x)]ψ(x))* = [∀x(φ(x))*](~ψ(x))*

## Critical Insight: DeMorgan's Laws Built Into Translation!

Look at rules 5 and 6 - **the translation itself implements DeMorgan's laws**:
- ~(φ ∧ ψ) becomes (~φ)* ∨ (~ψ)*
- ~(φ ∨ ψ) becomes (~φ)* ∧ (~ψ)*
- ~∀ becomes ∃~
- ~∃ becomes ∀~

## This Explains Everything!

Ferguson's claim that "DeMorgan's laws are reestablished" makes sense now:
1. The **translation** from L to L* **builds in** DeMorgan's laws
2. When you translate ~(P ∧ Q), you get P* ∨ Q* (not ~P ∨ ~Q)
3. The bilateral system doesn't make the **inference** ~(P ∧ Q) ⊢ ~P ∨ ~Q valid
4. Instead, it **translates** ~(P ∧ Q) directly to the DeMorgan equivalent form

## Our Implementation

Our ACrQ parser appears to implement this:
- ~P(a) → P*(a) ✓
- But does it implement the compound negation rules?
- Does ~(P(a) ∧ Q(a)) → P*(a) ∨ Q*(a)?

## The Resolution

DeMorgan's laws are "reestablished" not as **valid inferences** but as **built-in translations**:
- In wK: ~(P ∧ Q) and (~P ∨ ~Q) are different formulas with different semantics
- In AC/S*_fde: ~(P ∧ Q) is **translated** to P* ∨ Q* automatically

This is why our inference tests fail - we're testing whether ~(P ∧ Q) ⊢ ~P ∨ ~Q, but the system translates the left side to P* ∨ Q* and the right side to P* ∨ Q*, so we're really testing whether P* ∨ Q* ⊢ P* ∨ Q*, which is trivially true!

## Footnote 4

"A reviewer has observed that alternative definitions could be considered, e.g., requiring preservation of non-refutability in the second coordinate. Whether such alternatives determine distinct consequence relations is an interesting question."

This footnote hints at the complexity of the bilateral approach and why different interpretations are possible.