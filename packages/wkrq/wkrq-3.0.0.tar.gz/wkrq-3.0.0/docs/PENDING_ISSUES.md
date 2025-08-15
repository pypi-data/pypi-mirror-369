# Pending Issues to Revisit

## 1. DeMorgan's Laws Discrepancy in ACrQ

### Issue
Ferguson's paper (p. 13) claims that DeMorgan's laws are "reestablished" in the bilateral systems (AC and S*_fde), but our ACrQ implementation shows they remain invalid.

### Current Status
- **wKrQ**: DeMorgan's laws invalid (expected per Ferguson)
- **ACrQ**: DeMorgan's laws invalid (unexpected - Ferguson says they should be restored)

### Test Results
```bash
# Both fail in ACrQ:
~(P(a) & Q(a)) ⊬ (~P(a) | ~Q(a))  # Invalid
~(P(a) | Q(a)) ⊬ (~P(a) & ~Q(a))  # Invalid

# Counterexample: P(a)=e, P*(a)=f, Q(a)=e, Q*(a)=f
```

### Ferguson's Claim (Definition 15, p. 13)
> "The reader can confirm that the bilateral approach in fact improves on the presentation for wK inasmuch as DeMorgan's laws are reestablished; as S*_fde and AC are our actual targets, this should relieve concerns about their failure in wK."

### Root Cause Identified
**Our implementation is incomplete!** Ferguson's Definition 17 specifies that the bilateral translation should implement DeMorgan's laws:
- ~(φ ∧ ψ) → (~φ)* ∨ (~ψ)*
- ~(φ ∨ ψ) → (~φ)* ∧ (~ψ)*
- ~[∀xφ(x)]ψ(x) → [∃x(φ(x))*](~ψ(x))*
- ~[∃xφ(x)]ψ(x) → [∀x(φ(x))*](~ψ(x))*

Our implementation only handles atomic negation (~P → P*) but NOT compound negation rules.

### Files to Review
- `src/wkrq/acrq_rules.py` - Check against Ferguson's Definition 18
- `src/wkrq/acrq_parser.py` - Verify bilateral translation
- `tests/test_ferguson_validation.py::TestACrQDeMorgansLaws`

### Solution Required
According to Ferguson's Definition 18, we need to add the following rules to `acrq_rules.py`:

1. **Negated Conjunction Rule**: v : ~(φ ∧ ψ) → v : (~φ ∨ ~ψ)
2. **Negated Disjunction Rule**: v : ~(φ ∨ ψ) → v : (~φ ∧ ~ψ)
3. **Negated Universal Rule**: v : ~[∀φ(x)]ψ(x) → v : [∃φ(x)]~ψ(x)
4. **Negated Existential Rule**: v : ~[∃φ(x)]ψ(x) → v : [∀φ(x)]~ψ(x)

These are not optional - they are core rules of the ACrQ system per Definition 18.

## 2. Quantifier Rule Simplifications

### Issue
Our implementation simplifies Ferguson's complex quantifier rules (Definition 9) by avoiding meta-signs and two-constant patterns.

### Current Status
- Tests pass and system appears sound
- But not exactly Ferguson-compliant
- Simplification documented in `QUANTIFIER_IMPLEMENTATION_ANALYSIS.md`

### Example
**Ferguson's t-universal**:
```
t:[∀xφ(x)]ψ(x) → m:φ(c) ○ m:ψ(c) ○ (n:φ(a) + t:ψ(a))
```

**Our implementation**:
```
t:[∀xφ(x)]ψ(x) → f:φ(c) | t:ψ(c)
```

### Question
Are these simplifications truly equivalent or do we lose something important?

## 3. Performance Issues with Complex Formulas

### Issue
Some complex formulas with nested quantifiers may cause performance problems.

### Status
- Not critical for current use cases
- May need optimization for larger problems

## 4. Documentation Inconsistencies

### Issue
Some documentation refers to old versions before Ferguson compliance fixes.

### Files to Update
- Examples in docs that might use old behavior
- README examples
- API documentation

## Notes

These issues are not critical for basic functionality but should be addressed for:
1. Full theoretical compliance with Ferguson's system
2. Publication or formal verification
3. Advanced use cases requiring DeMorgan's laws in paraconsistent reasoning

---
*Last updated after Ferguson paper review*