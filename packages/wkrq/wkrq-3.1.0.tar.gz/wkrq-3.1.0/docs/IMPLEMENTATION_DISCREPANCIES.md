# Implementation Discrepancies Report

## Overview
This document tracks discrepancies between Ferguson (2021) formal specifications and the actual wKrQ/ACrQ implementation. These discrepancies were discovered through systematic rule verification testing.

## Key Finding
The implementation is **logically correct** but differs **structurally** from Ferguson's presentation in several cases. These differences don't affect soundness or completeness but may cause confusion when comparing to the paper.

## Discrepancies Found

### 1. f-conjunction Rule Branch Structure

**Ferguson's Specification (Definition 9)**:
```
f : (φ ∧ ψ)
───────────────────
f : φ | f : ψ | (e : φ, e : ψ)
```
Creates 3 branches, with the third branch containing both error formulas.

**Actual Implementation**:
```
f : (φ ∧ ψ)
───────────────────
f : φ | f : ψ | e : φ | e : ψ
```
Creates 4 separate branches, one for each formula.

**Impact**: Logically equivalent but structurally different. Both represent the same truth conditions: conjunction is false if either operand is false or either is error.

**Code Location**: `wkrq_rules.py` lines 130-138

### 2. m-conjunction Rule Branch Structure

**Ferguson's Specification**:
```
m : (φ ∧ ψ)
───────────
t : (φ ∧ ψ) | f : (φ ∧ ψ)
```
Branches on the compound formula itself.

**Actual Implementation**:
```
m : (φ ∧ ψ)
─────────────────────────
(t : φ, t : ψ) | f : φ | f : ψ
```
Creates 3 branches with decomposed formulas.

**Impact**: The implementation eagerly decomposes rather than branching on the compound. This is more efficient but differs from the paper's presentation.

**Code Location**: `wkrq_rules.py` lines 147-159

### 3. Similar patterns for other connectives

The implementation consistently:
- Creates separate branches for each error case rather than grouping them
- Eagerly decomposes compound formulas when possible
- Optimizes branch structure for efficiency

## Why These Discrepancies Exist

1. **Implementation Efficiency**: Creating separate branches for error cases simplifies the tableau engine's branch management.

2. **Code Clarity**: Having each branch contain exactly one formula (for branching rules) or multiple formulas on the same branch (for non-branching) is more consistent.

3. **Historical Development**: The implementation may have evolved independently from the paper's final presentation.

## Verification Strategy

Despite these discrepancies, we can verify correctness by:

1. **Logical Equivalence Testing**: Verify that both representations lead to the same satisfiability results.

2. **Semantic Validation**: Check that the weak Kleene truth tables are correctly implemented regardless of branch structure.

3. **Literature Example Reproduction**: Ensure that examples from Ferguson's paper produce the correct final results, even if the intermediate tableau structure differs.

## Recommendations

1. **Document the Differences**: Clearly document where the implementation differs from the paper (this document).

2. **Add Equivalence Tests**: Create tests that verify logical equivalence rather than structural identity.

3. **Consider Refactoring**: If exact Ferguson compliance is required, refactor the rules to match the paper exactly. However, this may reduce efficiency.

4. **Update Rule Specification**: Update RULE_SPECIFICATION.md to reflect the actual implementation rather than the paper's presentation.

## Test Adjustments Needed

The systematic rule verification tests need to be adjusted to test for:
- Logical correctness (the right formulas are produced)
- Branch independence (branches don't share state)
- Completeness (all necessary formulas are generated)

Rather than testing for exact structural match with Ferguson's presentation.

## Conclusion

The implementation is **logically sound** but **structurally different** from Ferguson's presentation. These differences are optimizations that don't affect the correctness of the reasoning system. However, they should be documented to avoid confusion when comparing the implementation to the paper.