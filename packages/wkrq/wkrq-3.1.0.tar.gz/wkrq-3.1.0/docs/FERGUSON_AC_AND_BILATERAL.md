# Ferguson's AC and Bilateral Logic Framework

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 12

## AC Axioms (Angell's Logic of Analytic Containment)

### Basic Axioms
- **AC1a**: φ ⊢ ∼∼φ
- **AC1b**: ∼∼φ ⊢ φ
- **AC2**: φ ⊢ φ ∧ φ
- **AC3**: φ ∧ ψ ⊢ φ
- **AC4**: φ ∨ ψ ⊢ ψ ∨ φ
- **AC5a**: φ ∨ (ψ ∨ ξ) ⊢ (φ ∨ ψ) ∨ ξ
- **AC5b**: (φ ∨ ψ) ∨ ξ ⊢ φ ∨ (ψ ∨ ξ)
- **AC6a**: φ ∨ (ψ ∧ ξ) ⊢ (φ ∨ ψ) ∧ (φ ∨ ξ)
- **AC6b**: (φ ∨ ψ) ∧ (φ ∨ ξ) ⊢ φ ∨ (ψ ∧ ξ)

### Rules
- **AC7**: If φ ⊢ ψ and ψ ⊢ φ are derivable then ∼φ ⊢ ∼ψ is derivable
- **AC8**: If φ ⊢ ψ is derivable then φ ∨ ξ ⊢ ψ ∨ ξ is derivable
- **AC9**: If φ ⊢ ψ and ψ ⊢ ξ are derivable then φ ⊢ ξ is derivable

## S*_fde Axioms

S*_fde can be defined by adding to AC:
- **S1**: φ ⊢ φ ∨ ∼φ

For multiple-premise formulations with finite premises Γ, provability of Γ ⊢ φ can be understood as derivability of ⋀Γ ⊢ φ.

## Key Insight: Bilateral Nature

Ferguson states: "In [7], a tight connection between wK (on the one hand) and S*_fde and AC (on the other) is described. This connection can be summarized as the idea that these two logics are essentially **bilateral**—tracking distinct values for both truth and falsity—with the calculation of truth values and falsity values being performed by parallel positive weak Kleene interpretations."

## Definition 13: Propositional AC Interpretation

A propositional AC interpretation I is a function I : L → V₃ × V₃. Let I₀ and I₁ denote functions mapping formulae φ to the first and second coordinates of I(φ).

### Semantic Clauses
- I(∼φ) = ⟨I₁(φ), I₀(φ)⟩  [Negation toggles coordinates]
- I(φ ∧ ψ) = ⟨I₀(φ) ∧ I₀(ψ), I₁(φ) ∨̇ I₁(ψ)⟩
- I(φ ∨ ψ) = ⟨I₀(φ) ∨̇ I₀(ψ), I₁(φ) ∧ I₁(ψ)⟩

Note: ∧ is min operation, ∨̇ is max operation in weak Kleene

### Important Properties

1. **Toggle Negation**: Negation "clearly a 'toggle' negation in the sense of [13] as it simply exchanges the truth coordinate for the falsity coordinate."

2. **Duality Preserved**: "The duality between e.g. conjunction and disjunction is respected by defining the falsity of a conjunction as the disjunction of the falsity values of the conjuncts."

3. **Semantic Values**: S*_fde is yielded from AC by restricting available values to V₃² = {⟨t,t⟩, ⟨t,f⟩, ⟨f,t⟩, ⟨f,f⟩, ⟨e,e⟩}

## Interpretation of Semantic Values

A semantic value ⟨u,v⟩ with u,v ∈ V₃ can be read:
- First coordinate: indicator of **corroborating** evidence for a formula
- Second coordinate: indicator of **refuting** evidence

Examples:
- ⟨t,f⟩: "there exists evidence in favor of the truth of φ and no evidence refuting φ"
- ⟨f,f⟩: "there is no evidence either supporting or refuting φ"

## Four Information States

From the Halldén-Bochvar perspective, this yields:
1. **True**: ⟨t,f⟩ - Evidence for, none against
2. **False**: ⟨f,t⟩ - Evidence against, none for
3. **Gap**: ⟨f,f⟩ - No evidence either way
4. **Glut**: ⟨t,t⟩ - Evidence both for and against

## Implementation Connection

Our ACrQ implementation uses:
- **Bilateral predicates**: R for positive evidence, R* for negative evidence
- **Four states**: Corresponding to the semantic values above
- **Paraconsistent reasoning**: Handles gluts (contradictions) without explosion

This bilateral approach is why ACrQ can handle intentional contexts better than pure wKrQ - it tracks both supporting and refuting evidence separately.