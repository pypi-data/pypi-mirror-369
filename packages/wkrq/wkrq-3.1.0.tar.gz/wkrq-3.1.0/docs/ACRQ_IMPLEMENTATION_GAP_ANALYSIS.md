# ACrQ Implementation Gap Analysis

## Executive Summary

Our ACrQ implementation is **incomplete** and does not fully comply with Ferguson's Definition 18. The implementation is missing critical DeMorgan transformation rules that are essential for the bilateral logic system to function correctly.

## Missing Components

### 1. DeMorgan Transformation Rules (CRITICAL)

According to Ferguson Definition 18 (p. 15), ACrQ must include:

#### Negated Conjunction Rule
```
v : ~(φ ∧ ψ)
─────────────
v : (~φ ∨ ~ψ)
```

#### Negated Disjunction Rule  
```
v : ~(φ ∨ ψ)
─────────────
v : (~φ ∧ ~ψ)
```

#### Negated Universal Quantifier Rule
```
v : ~[∀φ(x)]ψ(x)
─────────────────
v : [∃φ(x)]~ψ(x)
```

#### Negated Existential Quantifier Rule
```
v : ~[∃φ(x)]ψ(x)  
─────────────────
v : [∀φ(x)]~ψ(x)
```

**Current Status**: Our implementation at `src/wkrq/acrq_rules.py:106-108` explicitly returns `None` for compound negations, stating "we don't eliminate negation". This is incorrect - we should apply the specific transformation rules above.

### 2. Bilateral Equivalence Closure Check (UNCERTAIN)

According to Ferguson Lemma 5 (p. 15):
- Branches should close when `u : φ` and `v : ψ` with distinct signs appear where **φ* = ψ***
- This means formulas must be equivalent after bilateral translation

**Current Status**: Need to verify if our closure checking in `acrq_tableau.py` correctly implements the φ* = ψ* condition.

## Impact Analysis

### Why DeMorgan's Laws Appear Invalid

Our tests show DeMorgan's laws are invalid in ACrQ:
```python
~(P(a) & Q(a)) ⊬ (~P(a) | ~Q(a))  # Invalid
```

This is because:
1. Without the transformation rules, `~(P(a) & Q(a))` remains as-is
2. It doesn't get transformed to `(~P(a) | ~Q(a))` as it should
3. The tableau can't establish the entailment

### Ferguson's Claim Explained

Ferguson states (p. 13): "DeMorgan's laws are reestablished" in bilateral systems.

This works through:
1. **Translation rules** (Definition 17): Build DeMorgan's into the bilateral translation
2. **Tableau rules** (Definition 18): Apply DeMorgan's as transformation rules
3. **Not as semantic validity**: They're syntactic transformations, not semantic theorems

## Implementation Requirements

### Step 1: Add DeMorgan Transformation Rules

In `acrq_rules.py`, modify `get_acrq_negation_rule` to handle:

```python
# Check for negated conjunction: ~(φ ∧ ψ)
if isinstance(subformula, CompoundFormula):
    if subformula.connective == "&":
        # Transform to (~φ ∨ ~ψ)
        left_neg = CompoundFormula("~", [subformula.subformulas[0]])
        right_neg = CompoundFormula("~", [subformula.subformulas[1]])
        new_formula = CompoundFormula("|", [left_neg, right_neg])
        return FergusonRule(
            name=f"{sign.symbol}-demorgan-conjunction",
            premise=signed_formula,
            conclusions=[[SignedFormula(sign, new_formula)]]
        )
    elif subformula.connective == "|":
        # Transform to (~φ ∧ ~ψ)
        left_neg = CompoundFormula("~", [subformula.subformulas[0]])
        right_neg = CompoundFormula("~", [subformula.subformulas[1]])
        new_formula = CompoundFormula("&", [left_neg, right_neg])
        return FergusonRule(
            name=f"{sign.symbol}-demorgan-disjunction",
            premise=signed_formula,
            conclusions=[[SignedFormula(sign, new_formula)]]
        )
```

### Step 2: Add Quantifier DeMorgan Rules

Handle negated quantifiers similarly:

```python
if isinstance(subformula, RestrictedUniversalFormula):
    # ~[∀φ(x)]ψ(x) → [∃φ(x)]~ψ(x)
    neg_scope = CompoundFormula("~", [subformula.scope])
    new_formula = RestrictedExistentialFormula(
        variable=subformula.variable,
        restriction=subformula.restriction,
        scope=neg_scope
    )
    return FergusonRule(
        name=f"{sign.symbol}-demorgan-universal",
        premise=signed_formula,
        conclusions=[[SignedFormula(sign, new_formula)]]
    )
elif isinstance(subformula, RestrictedExistentialFormula):
    # ~[∃φ(x)]ψ(x) → [∀φ(x)]~ψ(x)
    neg_scope = CompoundFormula("~", [subformula.scope])
    new_formula = RestrictedUniversalFormula(
        variable=subformula.variable,
        restriction=subformula.restriction,
        scope=neg_scope
    )
    return FergusonRule(
        name=f"{sign.symbol}-demorgan-existential",
        premise=signed_formula,
        conclusions=[[SignedFormula(sign, new_formula)]]
    )
```

### Step 3: Verify Closure Condition

Check that `acrq_tableau.py` implements closure based on bilateral equivalence (φ* = ψ*).

## Test Cases to Add

After implementation, these should become valid:

```python
def test_acrq_demorgan_conjunction():
    # Should be valid after fix
    result = solve("~(P(a) & Q(a)) -> (~P(a) | ~Q(a))", mode="acrq")
    assert result["valid"] == True

def test_acrq_demorgan_disjunction():
    # Should be valid after fix
    result = solve("~(P(a) | Q(a)) -> (~P(a) & ~Q(a))", mode="acrq")
    assert result["valid"] == True

def test_acrq_quantifier_demorgan():
    # Should be valid after fix
    result = solve("~[Ax P(x)]Q(x) -> [Ex P(x)]~Q(x)", mode="acrq")
    assert result["valid"] == True
```

## Priority

**HIGH** - This is a fundamental correctness issue. Without these rules:
1. ACrQ doesn't match Ferguson's specification
2. DeMorgan's laws remain broken contrary to the paper's claims
3. The bilateral logic system is incomplete
4. Users cannot rely on expected logical equivalences

## Recommendation

Implement the missing DeMorgan transformation rules immediately to bring our ACrQ implementation into compliance with Ferguson's Definition 18. This will restore DeMorgan's laws as transformation rules (not semantic validities) and enable proper paraconsistent reasoning.