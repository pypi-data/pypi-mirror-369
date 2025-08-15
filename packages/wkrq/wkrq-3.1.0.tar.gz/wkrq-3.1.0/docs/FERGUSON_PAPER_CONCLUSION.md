# Ferguson Paper: Concluding Remarks and Complete System Overview

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", p. 18

## Theorem 6: Completeness of SrQ
**If Γ ⊨_S*fde φ then Γ ⊢_SrQ φ**

The proof follows the same pattern as ACrQ completeness, using the lemmas to establish that branch models from SrQ tableaux belong to the appropriate class S.

## Section 4: Concluding Remarks

### Systems and Their Purpose

The deductive systems **wK**, **S*_fde**, and **AC** capture notions of validity and equivalence that are stricter than classical, Boolean logic. Given the interpretative and philosophical work on these systems, they are **plausible candidates for modest closure conditions for intentional contexts**, including collections of agents':
- Beliefs
- Knowledge  
- Goals

### The Contribution

This paper introduces **sufficient quantification theory** for these systems to support applications like **description logics**. The end results envisioned are description logics that can:
- Felicitously capture agents' intentional states
- Plausibly reason about these states
- Provide a formal foundation for applications

Future work includes:
- Determining the complexity of deductions in the tableau calculi
- Adapting them to calculi including the syntax of description logics (e.g., ALC or SROIQ)

### Complexity Note

Ferguson notes an important complexity result:
- Definition 17 translates both systems into a **positive logic**
- In the propositional case, this corresponds to classical validity with a **variable-inclusion property**
- Thus, validity in propositional S*_fde or AC is **polynomial-time reducible** to classical validity
- It's worth investigating whether a similar approach works for restricted quantification

## Complete System Hierarchy

### 1. wKrQ (Definition 9)
- **Logic**: Three-valued weak Kleene logic
- **Values**: t (true), f (false), e (error/undefined)
- **Key Feature**: General negation elimination (v : ~φ → ~v : φ)
- **Quantifiers**: Restricted quantification [∀xP(x)]Q(x), [∃xP(x)]Q(x)
- **Use Case**: Reasoning with undefined/error propagation

### 2. ACrQ (Definition 18)
- **Logic**: Paraconsistent bilateral logic (AC)
- **Base**: wKrQ⁺ (wKrQ without general negation elimination)
- **Key Features**:
  - Bilateral predicates (R and R*)
  - DeMorgan transformation rules
  - No general negation elimination
- **Use Case**: Reasoning with contradictory evidence without explosion

### 3. SrQ (Definition 19)
- **Logic**: Four-valued First Degree Entailment (S*_fde)
- **Base**: ACrQ plus special bilateral rules
- **Values**: Can represent gaps and gluts
- **Key Features**:
  - Couples error states of R and R*
  - Branching rules for meaningful (m) sign
  - At-most-once application constraint
- **Use Case**: Full four-valued reasoning with both gaps and gluts

## Implementation Status Summary

### What We Have
1. ✅ **wKrQ**: Fully implemented with Ferguson's 6-sign system
2. ⚠️ **ACrQ**: Partially implemented
   - ✅ Has bilateral predicates
   - ✅ No general negation elimination
   - ❌ Missing DeMorgan transformation rules
   - ❌ May have incorrect closure condition

### What We're Missing
1. **ACrQ Completion**:
   - DeMorgan rules for ~(φ ∧ ψ), ~(φ ∨ ψ)
   - Quantifier DeMorgan rules for ~[∀x...], ~[∃x...]
   - Verification of φ* = ψ* closure condition

2. **SrQ Implementation**:
   - Not implemented at all
   - Would require adding the four bilateral coupling rules
   - Need to handle the "at most once" constraint
   - Support for four-valued semantics

## Key Takeaways

1. **The systems form a hierarchy** where each builds on the previous, adding more sophisticated handling of contradictions and undefined values.

2. **DeMorgan's laws in ACrQ** are not semantic validities but **tableau transformation rules** - this explains why our tests show them as invalid (we're missing the transformation rules).

3. **The bilateral approach** allows reasoning about intentional contexts where agents might have contradictory beliefs without the system exploding into triviality.

4. **Complexity is manageable**: The translation to positive logic means these non-classical systems have polynomial-time reducibility to classical logic in the propositional case.

5. **Applications**: These systems are designed for **description logics** and reasoning about **agents' intentional states** (beliefs, knowledge, goals) where classical logic is too strict.

## References Cited

1. Angell, R.B.: Three systems of first degree entailment (1977)
2. Bochvar, D.A.: On a three-valued logical calculus (1938)
3. Carnielli et al.: Formal inconsistency and evolutionary databases (2000)
4. Carnielli, W.A.: Systematization of finite many-valued logics through tableaux (1987)

## Action Items for Full Compliance

1. **Immediate**: Implement missing DeMorgan transformation rules in ACrQ
2. **Short-term**: Verify closure condition uses bilateral equivalence
3. **Long-term**: Consider implementing SrQ for full four-valued reasoning
4. **Future**: Adapt to description logic syntax (ALC, SROIQ)