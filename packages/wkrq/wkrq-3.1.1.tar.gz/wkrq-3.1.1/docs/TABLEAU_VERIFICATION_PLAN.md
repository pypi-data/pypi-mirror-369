# Tableau Verification Plan

## Overview
This document outlines a comprehensive plan to verify the correctness of the wKrQ/ACrQ tableau reasoning system. The goal is to provide systematic verification that would convince a skeptical logician that the implementation is correct.

## The Core Problem
We have a complex tableau system with ~477 tests, but:
- It's hard to tell if individual rules are correct
- Branch management and closure detection are opaque
- The relationship between our implementation and Ferguson's formal specification isn't clear
- We lack systematic verification that would convince a skeptical logician

## Phase 1: Systematic Rule Verification
**Goal**: Prove each rule is implemented correctly according to Ferguson's definitions

### 1.1 Create a Rule Specification Document
- For each rule in Ferguson's Definition 9 (wKrQ) and Definition 18 (ACrQ)
- Document the exact preconditions, transformations, and postconditions
- Include the formal notation from the paper

### 1.2 Rule-by-Rule Test Suite
For each rule, test:
- Minimal case (simplest formula that triggers the rule)
- Edge cases (empty conjunctions, single-element disjunctions, etc.)
- Non-application cases (verify rule doesn't fire when it shouldn't)
- Exact output verification (check produced formulas character-by-character)
- Branch structure verification (for branching rules)

### 1.3 Rule Isolation Testing
- Test each rule in isolation with mock tableaux
- Verify no unintended side effects
- Ensure rules don't interfere with each other

## Phase 2: Tableau Construction Invariants
**Goal**: Verify the tableau algorithm maintains critical properties

### 2.1 Invariant Monitoring
```python
class InvariantCheckingTableau(Tableau):
    def check_invariants(self):
        # After every rule application, verify:
        - No formula has multiple signs on same branch
        - Closed branches remain closed
        - Node parent-child relationships are consistent
        - Branch formula indices are accurate
        - Universal instantiation tracking is correct
```

### 2.2 Satisfiability Preservation
- Verify each rule preserves satisfiability equivalence
- If a branch was satisfiable before, the resulting branches preserve that

### 2.3 Termination Guarantees
- Verify the tableau terminates for propositional formulas
- Track that we don't re-apply the same rule infinitely

## Phase 3: Cross-Validation
**Goal**: Compare results with known-correct systems

### 3.1 Propositional Logic Validation
- Generate random propositional formulas
- Compare with Z3 SAT solver
- Compare with simple truth table enumeration for small formulas

### 3.2 First-Order Logic Validation
- Compare with established provers (Vampire, E, Prover9)
- Focus on decidable fragments where we can verify results

### 3.3 Three-Valued Logic Validation
- Implement a simple semantic evaluator for ground formulas
- Compare tableau results with semantic evaluation

## Phase 4: Literature Compliance
**Goal**: Reproduce exactly the examples from academic papers

### 4.1 Ferguson Paper Examples
- Every example tableau from Ferguson (2021)
- Character-by-character reproduction of the paper's tableaux
- Document any deviations and justify them

### 4.2 Standard Tableau Examples
- Examples from Smullyan's tableau books
- Examples from Fitting's modal logic tableaux
- Adapt for three-valued logic where needed

### 4.3 Known Problem Sets
- TPTP problem library (adapted for weak Kleene)
- Competition problems from automated reasoning contests

## Phase 5: Property-Based Testing
**Goal**: Verify logical properties hold across random inputs

### 5.1 Logical Properties
Properties to test:
- If ⊢ φ (valid), then ¬φ is unsatisfiable
- If φ ∧ ψ satisfiable, then φ and ψ are individually satisfiable
- If φ ∨ ψ unsatisfiable, then both φ and ψ are unsatisfiable
- Contrapositive: if φ → ψ valid, then ¬ψ → ¬φ valid

### 5.2 Tableau Properties
- Soundness: closed tableau implies unsatisfiable
- Completeness: unsatisfiable implies tableau closes
- Confluence: different rule orders lead to same result

## Phase 6: Formal Documentation
**Goal**: Create rigorous documentation a logician would trust

### 6.1 Correctness Proof Document
- Formal proof of soundness
- Formal proof of completeness
- Explicit mapping from implementation to formal system

### 6.2 Test Coverage Matrix
- Table showing which tests verify which rules
- Coverage percentages for each rule
- Gap analysis

### 6.3 Verification Report
- Executive summary of verification approach
- Detailed results from each phase
- Known limitations and assumptions

## Phase 7: Regression Prevention
**Goal**: Ensure bugs don't reappear

### 7.1 Bug Archive
- Every bug found gets a test case
- Document the bug, the fix, and why it occurred
- Regular regression runs

### 7.2 Mutation Testing
- Deliberately introduce bugs
- Verify tests catch them
- Identify weak spots in test coverage

## Implementation Priority

### Immediate (High Impact, Low Effort)
1. Rule specification document
2. Minimal test for each rule
3. Ferguson example reproduction

### Short Term (High Impact, Medium Effort)
1. Invariant checking
2. Property-based testing framework
3. Cross-validation with Z3

### Long Term (High Impact, High Effort)
1. Formal correctness proofs
2. Complete TPTP adaptation
3. Mutation testing framework

## Success Criteria
A logician should be able to:
1. See a clear mapping from Ferguson's formal system to our code
2. Verify that each rule is tested comprehensively
3. Reproduce any example from the literature
4. Understand exactly why we believe the system is sound and complete
5. Run validation against other trusted systems

## Tracking Progress
- [ ] Phase 1: Systematic Rule Verification
- [ ] Phase 2: Tableau Construction Invariants
- [ ] Phase 3: Cross-Validation
- [ ] Phase 4: Literature Compliance
- [ ] Phase 5: Property-Based Testing
- [ ] Phase 6: Formal Documentation
- [ ] Phase 7: Regression Prevention

## Conclusion
This plan transforms our test suite from "lots of tests" to "systematic verification of correctness." Each phase builds confidence in different aspects of the system, from individual rules to global properties, from theoretical correctness to practical reliability.