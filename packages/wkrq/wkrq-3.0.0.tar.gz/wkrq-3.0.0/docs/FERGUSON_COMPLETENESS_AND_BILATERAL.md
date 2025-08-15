# Ferguson Completeness Theorem and Bilateral Logics

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 11

## Theorem 2: Completeness of wKrQ

**If Γ ⊨_wK φ then Γ ⊢_wKrQ φ.**

### Proof Summary
The proof uses the contrapositive approach:
- Suppose Γ ⊬_wKrQ φ
- Then there exists an open branch on a tableau with initial nodes {t:γᵢ} for γᵢ ∈ Γ and either f:φ or e:φ
- By Lemma 1, I_B(γᵢ) = t for all γᵢ ∈ Γ but I_B(φ) ≠ t
- Therefore I_B serves as a counterexample witnessing that Γ ⊭_wK φ

### Combined with Theorem 1 (Soundness)
Together, Theorems 1 and 2 establish that:
**Γ ⊢_wKrQ φ if and only if Γ ⊨_wK φ**

This means the tableau system wKrQ is **sound and complete** with respect to weak Kleene semantics.

## Section 3: Bilateral Logics Related to Weak Kleene Logic

### Motivation
Ferguson notes: "Although we find the question of providing an intuitive quantification theory in the weak Kleene setting to be intriguing, weak Kleene logic seems to have little promise as a tool for e.g. semantic representation of intentional contexts."

This motivates examining two related systems that are "obviously good candidates":

### 1. Charles Daniels' S*_fde
- "First degree story logic" described in [6]
- Weaker than classical propositional logic
- Offered as a notion of validity under which weak, non-veridical theories can be closed

### 2. Richard Angell's AC
- Logic of analytic containment described in [1]
- Also weaker than classical logic
- Both Correia [5] and Fine [9] argue that AC preserves equivalence of facts
- Classes of e.g. desires are closed under AC consequence

### Key Properties
Both S*_fde and AC are:
- Intriguing foundations for applications like description logics
- Good candidates for handling intentional contexts
- Related to weak Kleene logic, allowing direct employment of wK results

### Important Note
Ferguson states: "presuming the details of restricted quantification are worked out."

This indicates that while the propositional fragments are well-understood, extending these systems with restricted quantification (as done for wK) requires additional work.

## Relationship to Our Implementation

Our codebase implements both:
1. **wKrQ**: The weak Kleene system with restricted quantification (Definition 9)
2. **ACrQ**: An adaptation for AC with restricted quantification (Definition 18)

The key differences:
- ACrQ uses **bilateral predicates** (R and R*)
- ACrQ drops general negation elimination
- ACrQ allows **gluts** (both R(a) and R*(a) can be true)

This bilateral approach addresses the limitations Ferguson identifies with pure weak Kleene logic for intentional contexts.

## Significance

This section explains **why** Ferguson develops ACrQ:
1. Pure weak Kleene has limitations for practical applications
2. AC and S*_fde are better suited for intentional contexts
3. The bilateral approach enables handling of paraconsistent scenarios
4. These systems can leverage the work done on wK

Our implementation's inclusion of both wKrQ and ACrQ follows Ferguson's motivation to provide practical tools for reasoning about beliefs, desires, and other intentional states that don't follow classical logic.