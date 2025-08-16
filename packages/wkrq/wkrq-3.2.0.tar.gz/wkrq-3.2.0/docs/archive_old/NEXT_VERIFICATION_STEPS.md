# Next Systematic Verification Steps

## Current Status Summary

### ✅ Completed
1. **Ferguson 2021 Analysis**: Complete understanding of the paper
2. **wKrQ Verification**: Fixed critical bugs (t-disjunction, t-implication, conjunction rules)
3. **Documentation**: Created comprehensive documentation of all definitions and theorems
4. **Gap Analysis**: Identified missing ACrQ components

### 📊 Test Suite Status
- **Current**: 502/527 tests passing (95.3% pass rate)
- **Before fixes**: 477/527 tests passing
- **Improvement**: +25 tests fixed

## Phase 1: Fix ACrQ Implementation (CRITICAL - Week 1)

### Step 1.1: Implement DeMorgan Transformation Rules
**File**: `src/wkrq/acrq_rules.py`
**Priority**: CRITICAL

Add these transformations to `get_acrq_negation_rule()`:
1. `v : ~(φ ∧ ψ) → v : (~φ ∨ ~ψ)`
2. `v : ~(φ ∨ ψ) → v : (~φ ∧ ~ψ)`
3. `v : ~[∀xP(x)]Q(x) → v : [∃xP(x)]~Q(x)`
4. `v : ~[∃xP(x)]Q(x) → v : [∀xP(x)]~Q(x)`

**Verification**:
- Create targeted tests for each transformation
- Verify DeMorgan's laws become valid in ACrQ
- Check that compound negations are properly handled

### Step 1.2: Verify Closure Condition
**File**: `src/wkrq/acrq_tableau.py`
**Priority**: HIGH

Ensure branch closure uses bilateral equivalence (φ* = ψ*):
1. Review current closure checking logic
2. Implement bilateral translation comparison if missing
3. Test with glut examples (t:P(a) and t:P*(a) should NOT close)

### Step 1.3: Create Comprehensive ACrQ Tests
**File**: `tests/test_acrq_demorgan.py` (new)
**Priority**: HIGH

Test cases:
```python
# DeMorgan's laws (should be valid after fix)
test_demorgan_conjunction: "~(P(a) & Q(a)) -> (~P(a) | ~Q(a))"
test_demorgan_disjunction: "~(P(a) | Q(a)) -> (~P(a) & ~Q(a))"
test_quantifier_demorgan_universal: "~[Ax P(x)]Q(x) -> [Ex P(x)]~Q(x)"
test_quantifier_demorgan_existential: "~[Ex P(x)]Q(x) -> [Ax P(x)]~Q(x)"

# Glut handling (should not close)
test_glut_coexistence: "P(a) & P*(a)" should be satisfiable
test_glut_inference: Test that gluts don't cause explosion
```

## Phase 2: Systematic Test Analysis (Week 1-2)

### Step 2.1: Categorize Remaining Test Failures
**Priority**: MEDIUM

1. Run full test suite after ACrQ fixes
2. Categorize the ~25 remaining failures:
   - Quantifier-related failures
   - Closure condition issues
   - Semantic evaluation problems
   - Parser/syntax issues

### Step 2.2: Create Failure Analysis Document
**File**: `docs/TEST_FAILURE_ANALYSIS.md`
**Priority**: MEDIUM

For each failure category:
- Root cause analysis
- Ferguson compliance check
- Proposed fix
- Impact assessment

## Phase 3: Quantifier Rule Verification (Week 2)

### Step 3.1: Systematic Quantifier Testing
**File**: `tests/test_quantifier_systematic.py` (new)
**Priority**: MEDIUM

Test matrix:
- All 6 signs × 2 quantifier types (universal/existential)
- Nested quantifiers
- Mixed quantifier-propositional formulas
- Domain restriction edge cases

### Step 3.2: Verify Ferguson's Complex Patterns
**Priority**: MEDIUM

Ferguson uses patterns like:
- `m:φ(c) ○ m:ψ(c)` (meaningful branching)
- `n:φ(a) + t:ψ(a)` (non-true combinations)

Verify our simplifications are sound:
1. Create tests comparing our rules to Ferguson's exact rules
2. Prove equivalence or identify discrepancies

## Phase 4: Branch Closure Verification (Week 2-3)

### Step 4.1: Closure Condition Tests
**File**: `tests/test_closure_conditions.py` (new)
**Priority**: HIGH

Test all closure scenarios:
- wKrQ: Standard closure (u:φ and v:φ where u ≠ v ∈ {t,f,e})
- ACrQ: Bilateral closure (φ* = ψ* condition)
- Edge cases with complex formulas

### Step 4.2: Trace Closure Decisions
**Priority**: MEDIUM

Use existing tracing infrastructure to:
1. Log all closure checks
2. Verify correct signs trigger closure
3. Ensure no premature closures

## Phase 5: Performance and Optimization (Week 3)

### Step 5.1: Benchmark Current Performance
**Priority**: LOW

1. Create benchmark suite with complex formulas
2. Profile tableau construction
3. Identify bottlenecks

### Step 5.2: Optimize Critical Paths
**Priority**: LOW

Based on profiling:
1. Optimize rule selection
2. Improve constant management
3. Cache bilateral translations

## Phase 6: Documentation and Examples (Week 3-4)

### Step 6.1: Update Documentation
**Priority**: MEDIUM

1. Update CLAUDE.md with ACrQ fixes
2. Create user guide for bilateral logic
3. Add examples demonstrating DeMorgan's laws

### Step 6.2: Literature Examples
**Priority**: LOW

Implement examples from:
- Ferguson's paper
- Carnielli's tableaux work
- Fine's intentional content examples

## Phase 7: Final Validation (Week 4)

### Step 7.1: Complete Test Suite Run
**Priority**: HIGH

Goal: Achieve 100% pass rate for intended functionality
1. Run all tests
2. Document any intentional deviations from Ferguson
3. Create acceptance criteria document

### Step 7.2: Cross-Reference Implementation
**Priority**: MEDIUM

Final check against Ferguson:
1. Every Definition implemented correctly
2. All Lemmas respected
3. Theorems (soundness/completeness) validated

## Success Criteria

### Immediate (Phase 1)
- [ ] DeMorgan transformation rules implemented
- [ ] ACrQ tests for DeMorgan's laws pass
- [ ] Test suite reaches >96% pass rate

### Short-term (Phases 2-4)
- [ ] All quantifier rules verified against Ferguson
- [ ] Closure conditions proven correct
- [ ] Remaining test failures understood and documented

### Long-term (Phases 5-7)
- [ ] 100% intended test pass rate
- [ ] Complete Ferguson compliance documented
- [ ] Performance acceptable for practical use

## Risk Mitigation

### High Risk Areas
1. **Quantifier simplifications**: May not be equivalent to Ferguson
   - Mitigation: Systematic comparison tests
   
2. **Bilateral closure**: Current implementation may be wrong
   - Mitigation: Direct implementation of φ* = ψ* check

3. **Parser interactions**: ACrQ parser modes may conflict with rules
   - Mitigation: Test all three parser modes thoroughly

## Next Immediate Action

**Start with Phase 1.1**: Implement DeMorgan transformation rules in `acrq_rules.py`. This is the most critical gap and will likely fix multiple test failures while bringing us into Ferguson compliance.