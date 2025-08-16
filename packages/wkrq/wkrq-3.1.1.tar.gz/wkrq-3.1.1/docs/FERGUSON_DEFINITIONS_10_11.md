# Ferguson Definitions 10-11: Branch and Tableau Closure

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic", pp. 10

## Definition 10: Branch Closure

**A branch B of a tableau T closes if there is a sentence φ and distinct v, u ∈ V₃ such that both v : φ and u : φ appear on B.**

### Key Points:
- A branch closes when the SAME formula appears with DIFFERENT signs
- The signs must be from V₃ = {t, f, e} (the definite truth values)
- This is the standard closure condition for tableau systems

### Footnote 3:
"N.b. that the criterion for closure is that a formula appears signed with distinct truth values and not distinct signs. E.g., m : φ is merely a notational device for potential branching, so both m : φ and t : φ may harmoniously appear in an open branch."

This clarifies that:
- Meta-signs (m, n) don't cause closure when they appear with definite signs
- Only conflicts between definite truth values (t, f, e) cause closure

## Definition 11: Tableau Closure

**{φ₀, ..., φₙ₋₁} ⊢wKrQ φ when every branch of a tableau T with initial nodes {t : φ₀, ..., t : φₙ₋₁, n : φ} closes.**

### Explanation:
- To prove φ follows from premises {φ₀, ..., φₙ₋₁}
- Start tableau with all premises signed with t
- Add the negation of the conclusion signed with n (non-true)
- If all branches close, the inference is valid

### Why n : φ for the negated conclusion?
- n represents "non-true" (branches to f or e)
- This tests if φ can be false or undefined given true premises
- If all such attempts lead to contradiction, φ must be true

## Theorem 1: Soundness of wKrQ

**If Γ ⊢wKrQ φ then Γ ⊨wK φ.**

### Proof Outline:
The proof shows that each rule of wKrQ exhaustively characterizes the corresponding semantic conditions from Definitions 4 and 5. When every branch closes in a tableau proving Γ ⊢ φ, this shows that no model I exists for which I[Γ] = {t} and I(φ) ≠ t is possible, i.e., Γ ⊨wK φ.

## Additional Definitions from the Proof

### Definition 12: Branch Interpretation
Given a tableau with an open branch B, we define the branch interpretation I_B and domain C^I_B as follows:

- For all constants c appearing on the branch, c^I_B is a unique element of C^I_B
- For all relation symbols R and tuples c₀, ..., cₙ₋₁ appearing on the branch:
  ```
  R^I_B(c₀^I_B, ..., cₙ₋₁^I_B) = {
    v   if v : R(c₀, ..., cₙ₋₁) is on B
    e   otherwise
  }
  ```

### Lemma 1
**For all sentences φ and v ∈ V₃, if v : φ is on B, then I_B(φ) = v.**

This lemma shows that the branch interpretation respects all signed formulas on the branch.

## Implementation Notes

Our implementation in `tableau.py`:
1. Uses Definition 10 for branch closure detection
2. Implements Definition 11's proof procedure in the `prove()` method
3. Correctly handles meta-signs (m, n) as non-closing per Footnote 3

### Code References:
- Branch closure: `tableau.py::TableauBranch::is_closed()`
- Tableau proof: `tableau.py::Tableau::prove()`
- Sign conflicts: Only between t, f, e (not m, n)

## Importance

These definitions establish:
1. **When branches close**: Contradictory truth values for same formula
2. **How to prove validity**: All branches must close
3. **Soundness**: The tableau method is sound with respect to weak Kleene semantics
4. **Meta-signs don't close**: m and n can coexist with definite values