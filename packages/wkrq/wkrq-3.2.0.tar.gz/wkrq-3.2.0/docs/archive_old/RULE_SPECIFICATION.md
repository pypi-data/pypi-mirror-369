# Tableau Rule Specification Document

## Overview
This document provides a formal specification of each tableau rule in the wKrQ and ACrQ systems, based on Ferguson (2021). Each rule is documented with its formal definition, preconditions, transformations, and implementation details.

## Ferguson's Sign System
- `t`: true (definite truth value)
- `f`: false (definite truth value)  
- `e`: error/undefined (definite truth value)
- `m`: meaningful (branches to t or f)
- `n`: nontrue (branches to f or e)
- `v`: variable (meta-sign for any of t, f, e)

## Part I: wKrQ Rules (Ferguson Definition 9)

### 1. Conjunction Rules

#### Rule: t-conjunction
**Formal Notation**: 
```
t : (φ ∧ ψ)
─────────────
t : φ, t : ψ
```
**Precondition**: Node has sign `t` and formula is a conjunction
**Action**: Add both conjuncts with sign `t` to the same branch
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `t` and `ConjunctionFormula`

#### Rule: f-conjunction
**Formal Notation**:
```
f : (φ ∧ ψ)
───────────────────
f : φ | f : ψ | e : φ | e : ψ
     |      |      |
     |      └──────┘
     └─────────────┘
```
**Precondition**: Node has sign `f` and formula is a conjunction
**Action**: Create 3 branches
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `f` and `ConjunctionFormula`

#### Rule: e-conjunction
**Formal Notation**:
```
e : (φ ∧ ψ)
───────────
e : φ | e : ψ
```
**Precondition**: Node has sign `e` and formula is a conjunction
**Action**: Create 2 branches with error propagation
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `e` and `ConjunctionFormula`

#### Rule: m-conjunction
**Formal Notation**:
```
m : (φ ∧ ψ)
───────────
t : (φ ∧ ψ) | f : (φ ∧ ψ)
```
**Precondition**: Node has sign `m` and formula is a conjunction
**Action**: Branch on meaningful values
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `m` and `ConjunctionFormula`

#### Rule: n-conjunction
**Formal Notation**:
```
n : (φ ∧ ψ)
───────────
f : (φ ∧ ψ) | e : (φ ∧ ψ)
```
**Precondition**: Node has sign `n` and formula is a conjunction
**Action**: Branch on nontrue values
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `n` and `ConjunctionFormula`

### 2. Disjunction Rules

#### Rule: t-disjunction
**Formal Notation**:
```
t : (φ ∨ ψ)
───────────────────
t : φ | t : ψ | e : φ | e : ψ
     |      |      |
     |      └──────┘
     └─────────────┘
```
**Precondition**: Node has sign `t` and formula is a disjunction
**Action**: Create 3 branches
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `t` and `DisjunctionFormula`

#### Rule: f-disjunction
**Formal Notation**:
```
f : (φ ∨ ψ)
───────────
f : φ, f : ψ
```
**Precondition**: Node has sign `f` and formula is a disjunction
**Action**: Add both disjuncts with sign `f` to the same branch
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `f` and `DisjunctionFormula`

#### Rule: e-disjunction
**Formal Notation**:
```
e : (φ ∨ ψ)
───────────
e : φ | e : ψ
```
**Precondition**: Node has sign `e` and formula is a disjunction
**Action**: Create 2 branches with error propagation
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `e` and `DisjunctionFormula`

### 3. Implication Rules

#### Rule: t-implication
**Formal Notation**:
```
t : (φ → ψ)
───────────────────
f : φ | t : ψ | e : φ | e : ψ
     |      |      |
     |      └──────┘
     └─────────────┘
```
**Precondition**: Node has sign `t` and formula is an implication
**Action**: Create 3 branches
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `t` and `ImplicationFormula`

#### Rule: f-implication
**Formal Notation**:
```
f : (φ → ψ)
───────────
t : φ, f : ψ
```
**Precondition**: Node has sign `f` and formula is an implication
**Action**: Add antecedent with `t` and consequent with `f`
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `f` and `ImplicationFormula`

#### Rule: e-implication
**Formal Notation**:
```
e : (φ → ψ)
───────────
e : φ | e : ψ
```
**Precondition**: Node has sign `e` and formula is an implication
**Action**: Create 2 branches with error propagation
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `e` and `ImplicationFormula`

### 4. Negation Rules

#### Rule: t-negation
**Formal Notation**:
```
t : ¬φ
──────
f : φ
```
**Precondition**: Node has sign `t` and formula is a negation
**Action**: Add negated formula with opposite sign
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `t` and `NegationFormula`

#### Rule: f-negation
**Formal Notation**:
```
f : ¬φ
──────
t : φ
```
**Precondition**: Node has sign `f` and formula is a negation
**Action**: Add negated formula with opposite sign
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `f` and `NegationFormula`

#### Rule: e-negation
**Formal Notation**:
```
e : ¬φ
──────
e : φ
```
**Precondition**: Node has sign `e` and formula is a negation
**Action**: Propagate error through negation
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `e` and `NegationFormula`

#### Rule: v-negation (General Negation Elimination)
**Formal Notation**:
```
v : ¬φ
──────
¬v : φ
```
where `¬t = f`, `¬f = t`, `¬e = e`, `¬m = n`, `¬n = m`, `¬v = v`

**Precondition**: Node has any sign and formula is a negation
**Action**: Apply sign negation operation
**Type**: Non-branching (α-rule)
**Note**: This rule is NOT in ACrQ (Definition 18)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` general negation case

### 5. Restricted Quantification Rules

#### Rule: t-restricted-forall
**Formal Notation**:
```
t : [∀X P(X)]Q(X)
─────────────────────────
f : P(c) | t : Q(c)
```
where `c` is either an existing constant from the branch or a fresh constant

**Precondition**: Node has sign `t` and formula is a restricted universal
**Action**: Create 2 branches with instantiation
**Type**: Branching (β-rule)
**Special**: Can be reapplied with different constants
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedUniversalFormula`

#### Rule: f-restricted-forall
**Formal Notation**:
```
f : [∀X P(X)]Q(X)
─────────────────
t : P(c), f : Q(c)
```
where `c` is a fresh constant

**Precondition**: Node has sign `f` and formula is a restricted universal
**Action**: Add both formulas with specific signs
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedUniversalFormula`

#### Rule: e-restricted-forall
**Formal Notation**:
```
e : [∀X P(X)]Q(X)
─────────────────
e : P(c) | e : Q(c)
```
where `c` is a fresh constant

**Precondition**: Node has sign `e` and formula is a restricted universal
**Action**: Create 2 branches with error propagation
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedUniversalFormula`

#### Rule: t-restricted-exists
**Formal Notation**:
```
t : [∃X P(X)]Q(X)
─────────────────
t : P(c), t : Q(c)
```
where `c` is a fresh constant

**Precondition**: Node has sign `t` and formula is a restricted existential
**Action**: Add both formulas with sign `t`
**Type**: Non-branching (α-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedExistentialFormula`

#### Rule: f-restricted-exists
**Formal Notation**:
```
f : [∃X P(X)]Q(X)
─────────────────────────
f : P(c) | f : Q(c)
```
where `c` is either an existing constant from the branch or a fresh constant

**Precondition**: Node has sign `f` and formula is a restricted existential
**Action**: Create 2 branches
**Type**: Branching (β-rule)
**Special**: Can be reapplied with different constants
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedExistentialFormula`

#### Rule: e-restricted-exists
**Formal Notation**:
```
e : [∃X P(X)]Q(X)
─────────────────
e : P(c) | e : Q(c)
```
where `c` is a fresh constant

**Precondition**: Node has sign `e` and formula is a restricted existential
**Action**: Create 2 branches with error propagation
**Type**: Branching (β-rule)
**Implementation**: `wkrq_rules.py::get_wkrq_rule()` case for `RestrictedExistentialFormula`

## Part II: ACrQ Rules (Ferguson Definition 18)

ACrQ uses all the same rules as wKrQ EXCEPT:
1. **NO general negation elimination** (v-negation rule is removed)
2. **Bilateral predicate support** for handling R and R*

### Key Differences in ACrQ

#### Negation Handling
- Atomic negations are converted to bilateral predicates during parsing
- `¬P(x)` becomes `P*(x)` in transparent mode
- Compound negations follow standard rules without general elimination

#### Bilateral Predicates
**Formula Types**:
- `R(x)`: Positive evidence for predicate R
- `R*(x)`: Negative evidence for predicate R (dual)

**Information States**:
- `t: R(x), f: R*(x)`: Standard true
- `f: R(x), t: R*(x)`: Standard false
- `f: R(x), f: R*(x)`: Knowledge gap
- `t: R(x), t: R*(x)`: Glut (paraconsistent)

#### Branch Closure (Ferguson Lemma 5)
**wKrQ Closure**: Branch closes when distinct v, u ∈ {t,f,e} appear for same formula
**ACrQ Closure**: Modified to allow gluts - `t: R(x)` and `t: R*(x)` can coexist

### Implementation Files
- `acrq_rules.py`: ACrQ-specific rule implementations
- `wkrq_rules.py`: wKrQ rule implementations
- `tableau.py`: Core tableau engine
- `acrq_tableau.py`: ACrQ-specific tableau with bilateral support

## Part III: LLM Integration Rules

### Rule: llm-eval
**Formal Notation**:
```
v : P(x)  [where P is atomic]
────────────────────────────
LLM evaluation → signed formulas based on BilateralTruthValue
```

**Precondition**: Node has atomic formula and LLM evaluator is available
**Action**: Query LLM and add signed formulas based on response
**Type**: Non-branching or branching depending on LLM response
**Priority**: Lower than logical rules (priority 30)
**Implementation**: `tableau.py::_create_llm_evaluation_rule()`

**LLM Response Mapping**:
- `(TRUE, FALSE)` → `t: P(x)`
- `(FALSE, TRUE)` → `f: P(x)`
- `(TRUE, TRUE)` → `t: P(x), t: P*(x)` (glut)
- `(FALSE, FALSE)` → `f: P(x), f: P*(x)` (gap as explicit uncertainty)
- `(UNDEFINED, _)` or `(_, UNDEFINED)` → `e: P(x)`

## Testing Requirements

### For Each Rule
1. **Minimal Test**: Simplest formula that triggers the rule
2. **Non-Application Test**: Verify rule doesn't fire incorrectly
3. **Output Verification**: Check exact formulas produced
4. **Branch Structure Test**: For branching rules, verify branch creation
5. **Sign Propagation Test**: Verify signs are correctly applied

### Invariants to Maintain
1. No formula has contradictory signs on same branch (except ACrQ gluts)
2. Closed branches remain closed
3. Rules produce exactly the specified conclusions
4. Universal instantiation can be reapplied with different constants
5. Fresh constants are truly fresh (not already on branch)

## Validation Checklist
- [ ] Each rule has formal specification from Ferguson (2021)
- [ ] Each rule has comprehensive test coverage
- [ ] Rule interactions are tested
- [ ] Branch closure conditions are verified
- [ ] Sign operations are correct
- [ ] Quantifier instantiation is sound
- [ ] LLM integration preserves tableau properties