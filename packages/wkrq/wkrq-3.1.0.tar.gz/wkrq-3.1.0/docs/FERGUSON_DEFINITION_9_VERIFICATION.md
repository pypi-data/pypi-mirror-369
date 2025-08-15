# Ferguson Definition 9 Verification

## Source
Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic"

## Verification Status: COMPLETE ✓

This document verifies our implementation against Ferguson's Definition 9 from the original paper.

## Rule-by-Rule Verification

### Negation Rules

| Rule | Ferguson Definition 9 | Our Implementation | Status |
|------|----------------------|-------------------|---------|
| t:¬φ | f:φ | f:φ | ✓ CORRECT |
| f:¬φ | t:φ | t:φ | ✓ CORRECT |
| e:¬φ | e:φ | e:φ | ✓ CORRECT |
| m:¬φ | (f:φ) + (t:φ) | (f:φ) + (t:φ) | ✓ CORRECT |
| n:¬φ | (t:φ) + (e:φ) | (t:φ) + (e:φ) | ✓ CORRECT |

### Conjunction Rules

| Rule | Ferguson Definition 9 | Our Implementation | Status |
|------|----------------------|-------------------|---------|
| t:(φ ∧ ψ) | (t:φ, t:ψ) | (t:φ, t:ψ) | ✓ CORRECT |
| f:(φ ∧ ψ) | f:φ \| f:ψ \| (e:φ, e:ψ) | f:φ \| f:ψ \| (e:φ, e:ψ) | ✓ FIXED |
| e:(φ ∧ ψ) | e:φ \| e:ψ | e:φ \| e:ψ | ✓ CORRECT |
| m:(φ ∧ ψ) | (t:φ, t:ψ) \| f:φ \| f:ψ | (t:φ, t:ψ) \| f:φ \| f:ψ | ✓ CORRECT |
| n:(φ ∧ ψ) | f:φ \| f:ψ \| (e:φ, e:ψ) | f:φ \| f:ψ \| (e:φ, e:ψ) | ✓ FIXED |

### Disjunction Rules

| Rule | Ferguson Definition 9 | Our Implementation | Status |
|------|----------------------|-------------------|---------|
| t:(φ ∨ ψ) | t:φ \| t:ψ \| (e:φ, e:ψ) | t:φ \| t:ψ \| (e:φ, e:ψ) | ✓ FIXED |
| f:(φ ∨ ψ) | (f:φ, f:ψ) | (f:φ, f:ψ) | ✓ CORRECT |
| e:(φ ∨ ψ) | e:φ \| e:ψ | e:φ \| e:ψ | ✓ CORRECT |
| m:(φ ∨ ψ) | t:φ \| t:ψ \| (f:φ, f:ψ) | t:φ \| t:ψ \| (f:φ, f:ψ) | ✓ CORRECT |
| n:(φ ∨ ψ) | (f:φ, f:ψ) \| e:φ \| e:ψ | (f:φ, f:ψ) \| e:φ \| e:ψ | ✓ CORRECT |

### Implication Rules

| Rule | Ferguson Definition 9 | Our Implementation | Status |
|------|----------------------|-------------------|---------|
| t:(φ → ψ) | f:φ \| t:ψ \| (e:φ, e:ψ) | f:φ \| t:ψ \| (e:φ, e:ψ) | ✓ FIXED |
| f:(φ → ψ) | (t:φ, f:ψ) | (t:φ, f:ψ) | ✓ CORRECT |
| e:(φ → ψ) | e:φ \| e:ψ | e:φ \| e:ψ | ✓ CORRECT |
| m:(φ → ψ) | f:φ \| t:ψ \| (t:φ, f:ψ) | f:φ \| t:ψ \| (t:φ, f:ψ) | ✓ CORRECT |
| n:(φ → ψ) | (t:φ, f:ψ) \| e:φ \| e:ψ | (t:φ, f:ψ) \| e:φ \| e:ψ | ✓ CORRECT |

## Notation Key
- `|` = branching (different tableau branches)
- `,` = conjunction (formulas on same branch)
- `+` = branching (alternative notation)

## Critical Fixes Applied

1. **t-disjunction**: Added missing error branch (e:φ, e:ψ)
2. **t-implication**: Added missing error branch (e:φ, e:ψ)  
3. **f-conjunction**: Changed from 4 branches to 3 branches with combined error case
4. **n-conjunction**: Changed from 4 branches to 3 branches with combined error case

## Implementation Files
- Main rules: `src/wkrq/wkrq_rules.py`
- Tests: `tests/test_ferguson_compliance.py`
- Verification tests: `tests/test_rule_verification.py`

## Conclusion
After verification against Ferguson's Definition 9 from the original paper, our implementation now **exactly matches** the formal specification. All propositional connective rules have been verified and corrected where necessary.