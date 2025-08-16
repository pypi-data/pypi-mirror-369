# wKrQ/ACrQ Architecture Overview

## System Overview

This codebase implements Ferguson's (2021) tableau calculus for three-valued weak Kleene logic with restricted quantification. It provides two closely related systems:
- **wKrQ**: Full weak Kleene logic with restricted quantification (Definition 9)
- **ACrQ**: Paraconsistent variant without general negation elimination (Definition 18)

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Interface Layer                          │
├──────────────────┬────────────────────┬─────────────────────────────────┤
│     CLI.py       │      API.py        │         LLM Integration        │
│  (Interactive)   │  (Programmatic)    │    (create_llm_evaluator)      │
└──────────────────┴────────────────────┴─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Parsing Layer                                 │
├──────────────────────────┬──────────────────────────────────────────────┤
│      parser.py           │           acrq_parser.py                     │
│  (Standard syntax)       │   (Mode-aware: Transparent/Bilateral/Mixed) │
└──────────────────────────┴──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Formula Representation                           │
├─────────────────────────────────────────────────────────────────────────┤
│                            formula.py                                   │
│  ┌──────────────────────────────────────────────────────┐              │
│  │ Formula (abstract)                                   │              │
│  ├──────────────────────────────────────────────────────┤              │
│  │ ├─ AtomicFormula                                     │              │
│  │ ├─ Variable(name)                                    │              │
│  │ ├─ Constant(name)                                    │              │
│  │ ├─ PredicateFormula(predicate, terms)               │              │
│  │ ├─ BilateralPredicateFormula(pos_name, terms, neg)  │              │
│  │ ├─ CompoundFormula(connective, subformulas)         │              │
│  │ ├─ RestrictedUniversalFormula(var, restriction,     │              │
│  │ │                              matrix)               │              │
│  │ └─ RestrictedExistentialFormula(var, restriction,   │              │
│  │                                  matrix)             │              │
│  └──────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Sign System                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                            signs.py                                     │
│  ┌────────────────────┐    ┌──────────────────────────┐               │
│  │ Truth Value Signs  │    │    Meta-Signs            │               │
│  ├────────────────────┤    ├──────────────────────────┤               │
│  │ t: true            │    │ m: meaningful (t|f)      │               │
│  │ f: false           │    │ n: nontrue (f|e)         │               │
│  │ e: error/undefined │    │ v: variable (any)        │               │
│  └────────────────────┘    └──────────────────────────┘               │
│                                                                         │
│              SignedFormula(sign: Sign, formula: Formula)               │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    wKrQ Rule System      │    │    ACrQ Rule System      │
├──────────────────────────┤    ├──────────────────────────┤
│    wkrq_rules.py         │    │    acrq_rules.py         │
│                          │    │                          │
│ • Full negation elim     │    │ • No general neg elim    │
│ • Standard predicates    │    │ • Bilateral predicates   │
│ • Ferguson Def. 9        │    │ • DeMorgan transforms    │
│ • Meta-sign expansion    │    │ • Ferguson Def. 18       │
└──────────────────────────┘    └──────────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Unified Tableau Engine                             │
├─────────────────────────────────────────────────────────────────────────┤
│                           tableau.py                                    │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐         │
│  │  TableauNode    │  │     Branch      │  │     Model      │         │
│  ├─────────────────┤  ├─────────────────┤  ├────────────────┤         │
│  │ • id            │  │ • node_ids      │  │ • valuations   │         │
│  │ • formula       │  │ • is_closed     │  │ • constants    │         │
│  │ • parent/child  │  │ • formula_index │  └────────────────┘         │
│  │ • branch_ids    │  │ • ground_terms  │                             │
│  └─────────────────┘  │ • instantiations│                             │
│                       └─────────────────┘                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │              Tableau (base class)                    │              │
│  ├──────────────────────────────────────────────────────┤              │
│  │ • construct(): Main loop                             │              │
│  │ • _get_applicable_rule(): Rule selection             │              │
│  │ • apply_rule(): Rule application                     │              │
│  │ • _check_contradiction(): Closure detection          │              │
│  │ • _extract_model(): Model from open branches         │              │
│  └──────────────────────────────────────────────────────┘              │
│           ▲                              ▲                              │
│           │                              │                              │
│  ┌────────┴──────────┐        ┌─────────┴──────────┐                  │
│  │   WKrQTableau     │        │   ACrQTableau       │                  │
│  ├───────────────────┤        ├────────────────────┤                  │
│  │ • wKrQ rules      │        │ • ACrQ rules       │                  │
│  │ • No gluts        │        │ • Allows gluts     │                  │
│  └───────────────────┘        │ • LLM evaluator    │                  │
│                               └────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Semantic Layer                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                          semantics.py                                   │
│                                                                         │
│  • TruthValue: {TRUE, FALSE, UNDEFINED}                                │
│  • BilateralTruthValue: (positive, negative) pairs                     │
│  • Weak Kleene operations (contagious undefined)                       │
│  • Model evaluation and satisfaction checking                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Tableau Construction Process - Pseudo-code

### wKrQ Tableau Algorithm

```python
ALGORITHM wKrQ_Tableau(formulas: List[SignedFormula]):
    # Initialize
    tableau = new Tableau()
    initial_branch = new Branch()
    
    # Add initial formulas
    for signed_formula in formulas:
        node = new Node(signed_formula)
        add_to_branch(node, initial_branch)
        if check_contradiction(node, initial_branch):
            mark_closed(initial_branch)
            return UNSATISFIABLE
    
    # Main construction loop
    while has_open_branches(tableau) and not is_complete(tableau):
        branch = select_open_branch(tableau)
        
        # Find applicable rules
        for node in unprocessed_nodes(branch):
            rule = get_applicable_wkrq_rule(node, branch)
            
            if rule is not None:
                apply_rule(rule, node, branch, tableau)
                break  # Process one rule at a time
    
    # Extract results
    if has_open_branches(tableau):
        models = extract_models_from_open_branches(tableau)
        return SATISFIABLE(models)
    else:
        return UNSATISFIABLE

FUNCTION get_applicable_wkrq_rule(node: Node, branch: Branch):
    formula = node.formula
    sign = node.sign
    
    # Check compound formula rules
    if is_compound(formula):
        switch formula.connective:
            case '~': return get_negation_rule(sign, formula)
            case '&': return get_conjunction_rule(sign, formula)
            case '|': return get_disjunction_rule(sign, formula)
            case '->': return get_implication_rule(sign, formula)
    
    # Check quantifier rules
    elif is_universal(formula):
        constants = get_ground_terms(branch)
        
        # Special handling for n-sign: generate fresh constant
        if sign == 'n' and not already_processed(node, branch):
            fresh = generate_fresh_constant()
            return get_universal_rule(sign, formula, constants + [fresh])
        else:
            return get_universal_rule(sign, formula, constants)
    
    elif is_existential(formula):
        fresh = generate_fresh_constant()
        return get_existential_rule(sign, formula, fresh)
    
    # CRITICAL: Meta-sign expansion for atomic formulas
    elif is_atomic(formula):
        if sign == 'm':
            return Rule('m-atomic', 
                       branches=[[t:formula], [f:formula]])
        elif sign == 'n':
            return Rule('n-atomic',
                       branches=[[f:formula], [e:formula]])
    
    return None

FUNCTION apply_rule(rule: Rule, node: Node, branch: Branch, tableau: Tableau):
    mark_processed(node, branch)
    
    if rule.is_branching():
        # Remove current branch from open branches
        remove_from_open(branch)
        
        # Create new branches
        for conclusion_set in rule.conclusions:
            new_branch = copy_branch(branch)
            
            for signed_formula in conclusion_set:
                new_node = new Node(signed_formula)
                add_to_branch(new_node, new_branch)
                
                if check_contradiction(new_node, new_branch):
                    mark_closed(new_branch)
                    break
            
            if not is_closed(new_branch):
                add_to_open(new_branch)
    else:
        # Non-branching rule
        for signed_formula in rule.conclusions[0]:
            new_node = new Node(signed_formula)
            add_to_branch(new_node, branch)
            
            if check_contradiction(new_node, branch):
                mark_closed(branch)
                remove_from_open(branch)
                return

FUNCTION check_contradiction(node: Node, branch: Branch):
    # Ferguson Definition 10: Branch closes when same formula
    # appears with distinct truth value signs (t, f, e)
    
    formula = node.formula
    sign = node.sign
    
    # Only truth value signs cause closure (not m, n, v)
    if sign not in ['t', 'f', 'e']:
        return False
    
    # Check for contradicting signs
    for other_sign in ['t', 'f', 'e']:
        if other_sign != sign:
            if has_formula_with_sign(branch, formula, other_sign):
                return True
    
    return False
```

### ACrQ Tableau Algorithm

```python
ALGORITHM ACrQ_Tableau(formulas: List[SignedFormula], llm_evaluator=None):
    # Initialize (similar to wKrQ)
    tableau = new Tableau()
    initial_branch = new Branch()
    bilateral_pairs = extract_bilateral_pairs(formulas)
    
    # ... initialization similar to wKrQ ...
    
    # Main loop is same structure, but uses ACrQ rules
    
FUNCTION get_applicable_acrq_rule(node: Node, branch: Branch):
    formula = node.formula
    sign = node.sign
    
    # Check for bilateral predicate negation FIRST
    if is_negation(formula) and is_predicate(formula.subformula):
        # ACrQ: ¬P(x) becomes P*(x) - no general negation elimination
        return convert_to_bilateral_rule(sign, formula)
    
    # Check compound formula rules
    if is_compound(formula):
        switch formula.connective:
            case '~':
                # Apply DeMorgan transformations for compound negations
                if is_compound(formula.subformula):
                    return get_demorgan_rule(sign, formula)
                else:
                    # Only atomic negation gets eliminated
                    return get_negation_rule(sign, formula)
            
            case '&', '|', '->':
                # Same as wKrQ
                return get_standard_rule(sign, formula)
    
    # Quantifiers: Same as wKrQ
    # Meta-signs: Same as wKrQ
    
    # LLM evaluation for atomic formulas (if available)
    if is_atomic(formula) and llm_evaluator and not processed(node):
        bilateral_value = llm_evaluator(formula)
        return create_llm_rule(bilateral_value, formula)
    
    return None

FUNCTION check_acrq_contradiction(node: Node, branch: Branch):
    # Ferguson Lemma 5: Modified closure for bilateral predicates
    
    formula = node.formula
    sign = node.sign
    
    # Check if this creates a glut (allowed in ACrQ)
    if is_bilateral_glut(node, branch):
        return False  # Gluts don't close branches
    
    # Check bilateral equivalence
    for other_node in branch.nodes:
        if check_bilateral_closure(sign, formula, 
                                 other_node.sign, other_node.formula):
            return True
    
    return False

FUNCTION check_bilateral_closure(sign1, formula1, sign2, formula2):
    # Only truth value signs can cause closure
    if sign1 not in ['t', 'f', 'e'] or sign2 not in ['t', 'f', 'e']:
        return False
    
    # Check if formulas are bilaterally equivalent
    if not bilateral_equivalent(formula1, formula2):
        return False
    
    # Different signs on equivalent formulas cause closure
    return sign1 != sign2

FUNCTION is_bilateral_glut(node: Node, branch: Branch):
    # Glut: Both t:R(a) and t:R*(a) present
    # This is ALLOWED in ACrQ (paraconsistent)
    
    if node.sign != 't':
        return False
    
    formula = node.formula
    if is_bilateral_predicate(formula):
        dual = get_dual_predicate(formula)
        if has_formula_with_sign(branch, dual, 't'):
            return True  # This is a glut - don't close
    
    return False
```

## Key Differences in Tableau Processes

### wKrQ Process Characteristics
1. **Full negation elimination**: `v:¬φ → ¬v:φ` for all formulas
2. **Standard contradiction**: Any formula with different truth signs closes
3. **Meta-sign expansion**: Critical for atomic formulas (m→t|f, n→f|e)
4. **Fresh constant generation**: n-universal generates fresh for counterexamples

### ACrQ Process Characteristics
1. **Limited negation elimination**: Only for atomic formulas, not compounds
2. **Bilateral predicates**: `¬P(x)` becomes `P*(x)`
3. **DeMorgan transformations**: For negated compound formulas
4. **Glut tolerance**: `t:R(a)` and `t:R*(a)` can coexist
5. **Bilateral equivalence checking**: For branch closure
6. **Optional LLM evaluation**: For atomic predicates

## Critical Implementation Details

### Meta-Sign Expansion (Both Systems)
```python
# CRITICAL: Without this, modus ponens fails!
if is_atomic(formula):
    if sign == 'm':
        # m:p must branch to (t:p) | (f:p)
        return branching_rule([[t:p], [f:p]])
    elif sign == 'n':
        # n:p must branch to (f:p) | (e:p)
        return branching_rule([[f:p], [e:p]])
```

### Fresh Constant Generation for n-Universal
```python
# CRITICAL: Without fresh constants, quantifier completeness fails!
if sign == 'n' and is_universal(formula):
    if not already_processed_with_fresh(node):
        existing = get_existing_constants(branch)
        fresh = generate_fresh_constant()
        # Try BOTH existing and fresh constants
        return create_branches_for_both(existing, fresh)
```

### Ferguson Definition 11 Implementation
```python
def check_inference(premises: List[Formula], conclusion: Formula):
    # CRITICAL: Must use n-sign for conclusion, not ~conclusion!
    signed_formulas = []
    
    # All premises get t-sign
    for premise in premises:
        signed_formulas.append(SignedFormula('t', premise))
    
    # Conclusion gets n-sign (not t:~conclusion!)
    signed_formulas.append(SignedFormula('n', conclusion))
    
    # Valid if all branches close
    tableau = construct_tableau(signed_formulas)
    return all_branches_closed(tableau)
```

## Known Limitation: Semantic Incompleteness

The tableau performs syntactic but not semantic contradiction checking:

```python
# This SHOULD close but doesn't:
t:(p ∨ q)  # Requires p∨q = t
e:p        # p = e
e:q        # q = e
# Semantic contradiction: e∨e = e ≠ t
# But tableau only checks syntactic identity, not semantic evaluation
```

**Impact**: Creates spurious models but maintains soundness (won't prove false things).

**Potential Fix**: Add semantic evaluation after each rule application, but computationally expensive.

## Core Architecture Principles

1. **Unified Tableau Engine**: Single tableau implementation (`tableau.py`) with system-specific rule selection
2. **Ferguson's 6-Sign System**: Uses signs t, f, e (truth values) and m, n, v (meta-signs)
3. **Weak Kleene Semantics**: Contagious undefined propagation
4. **Restricted Quantification**: Domain-aware quantifiers [∀X P(X)]Q(X) and [∃X P(X)]Q(X)

## File Structure and Key Classes

### Core Formula Representation (`src/wkrq/formula.py`)

**Classes:**
- `Formula` (abstract base class)
  - `AtomicFormula`: Base for atoms
  - `Variable`: Variable symbols (uppercase by convention)
  - `Constant`: Ground terms
  - `PredicateFormula`: Standard predicates P(x)
  - `BilateralPredicateFormula`: Bilateral predicates with positive/negative forms
  - `CompoundFormula`: Logical connectives (~, &, |, ->)
  - `RestrictedUniversalFormula`: [∀X P(X)]Q(X)
  - `RestrictedExistentialFormula`: [∃X P(X)]Q(X)

**Key Methods:**
- `substitute_term()`: Variable substitution for quantifier instantiation
- `get_atoms()`: Extract atomic formulas for model building
- `is_atomic()`: Check if formula is atomic (for meta-sign expansion)

### Semantic Evaluation (`src/wkrq/semantics.py`)

**Classes:**
- `TruthValue`: Enum with TRUE, FALSE, UNDEFINED
- `BilateralTruthValue`: Pairs (positive, negative) for ACrQ
- `Interpretation`: Maps atoms to truth values
- `ACrQInterpretation`: Extended with bilateral predicate support
- `Evaluator`: Standard weak Kleene evaluation
- `ACrQEvaluator`: Bilateral-aware evaluation

**Key Operations:**
- Weak Kleene conjunction: `t∧e = e`, `f∧e = f`
- Weak Kleene disjunction: `t∨e = e`, `f∨e = e`
- Weak Kleene implication: Treated as `¬φ∨ψ`
- Bilateral evaluation: Separate positive/negative evidence

### Sign System (`src/wkrq/signs.py`)

**Classes:**
- `Sign`: Type alias for sign strings
- `SignedFormula`: Pairs a sign with a formula
  - Attributes: `sign: Sign`, `formula: Formula`

**Sign Constants:**
- `t`: True (definite)
- `f`: False (definite)
- `e`: Error/undefined (definite)
- `m`: Meaningful (branches to t|f)
- `n`: Nontrue (branches to f|e)
- `v`: Variable (meta-sign for any truth value)

### Tableau Rules

#### wKrQ Rules (`src/wkrq/wkrq_rules.py`)

**Classes:**
- `FergusonRule`: Rule representation
  - `name`: Rule identifier
  - `premise`: SignedFormula that triggers rule
  - `conclusions`: List of branches, each containing SignedFormulas
  - `instantiation_constant`: For tracking universal instantiations

**Key Functions:**
- `get_negation_rule()`: Negation rules for all signs
- `get_conjunction_rule()`: Conjunction rules including branches
- `get_disjunction_rule()`: Includes critical (e,e) branch for t-sign
- `get_implication_rule()`: Treats implication as ¬φ∨ψ
- `get_restricted_universal_rule()`: Handles [∀X P(X)]Q(X)
  - Special n-sign handling: generates fresh constants for counterexamples
- `get_restricted_existential_rule()`: Handles [∃X P(X)]Q(X)
- `get_applicable_rule()`: Main dispatcher, includes meta-sign expansion for atomics

**Critical Implementation Details:**
- Meta-sign expansion for atomic formulas (lines 742-758)
- Fresh constant generation for n-universal (lines 713-726)
- (e,e) branches in t-disjunction/implication per Definition 9

#### ACrQ Rules (`src/wkrq/acrq_rules.py`)

**Key Differences from wKrQ:**
- No general negation elimination for compound formulas
- Bilateral predicate negation: `¬P(x)` becomes `P*(x)`
- DeMorgan transformations for negated compounds
- Same quantifier rules as wKrQ

**Functions:**
- `get_acrq_rule()`: Dispatcher that filters negation elimination
- `apply_bilateral_negation()`: Convert ¬P to P*
- `apply_demorgan_transformation()`: DeMorgan for compounds

### Unified Tableau Engine (`src/wkrq/tableau.py`)

**Core Classes:**

1. **`TableauNode`**
   - `id`: Unique identifier
   - `formula`: SignedFormula
   - `parent/children`: Tree structure
   - `branch_ids`: Set of branches containing this node
   - `causes_closure`: Tracks if node causes contradiction

2. **`Branch`**
   - `id`: Unique identifier
   - `node_ids`: Set of nodes in branch
   - `is_closed`: Closure status
   - `formula_index`: Maps (formula_str, sign) → node_ids for O(1) contradiction checking
   - `ground_terms`: Constants for quantifier instantiation
   - `universal_instantiations`: Tracks which constants used for which universals

3. **`Model`**
   - `valuations`: Maps atoms to TruthValues
   - `constants`: Domain elements and their properties

4. **`TableauResult`**
   - `satisfiable`: Whether formula has models
   - `models`: List of extracted models
   - `closed_branches`: Count of closed branches
   - `total_nodes`: Size of tableau

5. **`Tableau`** (base class)
   - `construct()`: Main tableau construction loop
   - `_check_contradiction()`: Branch closure checking
   - `_get_applicable_rule()`: Rule selection (overridden by subclasses)
   - `apply_rule()`: Rule application with branch management
   - `_extract_model()`: Model extraction from open branches

6. **`WKrQTableau`** (subclass)
   - Uses wKrQ rules
   - Standard contradiction checking (no gluts)

7. **`ACrQTableau`** (subclass)
   - Uses ACrQ rules
   - Bilateral-aware contradiction checking
   - Allows gluts (t:R and t:R* can coexist)
   - Optional LLM evaluator integration

**Key Algorithms:**
- Systematic rule application with priority ordering
- Branch independence and parallel exploration
- Universal quantifier reprocessing for new constants
- Model extraction from open branches

### Parsing System

#### Base Parser (`src/wkrq/parser.py`)
- `Parser`: Recursive descent parser for standard logical syntax
- `parse()`: Main entry point
- Supports: propositions, predicates, quantifiers, connectives

#### ACrQ Parser (`src/wkrq/acrq_parser.py`)
**Classes:**
- `SyntaxMode`: Enum with TRANSPARENT, BILATERAL, MIXED
- `ACrQParser`: Extended parser with mode-aware parsing

**Parsing Modes:**
1. **Transparent** (default): `¬P(x)` → `P*(x)` automatically
2. **Bilateral**: Explicit P/P* syntax, no negation of predicates
3. **Mixed**: Accepts both syntaxes

### API Layer (`src/wkrq/api.py`)

**Core Functions:**
- `solve(formula, sign)`: Check satisfiability with given sign
- `valid(formula)`: Check if formula is valid (always true)
- `entails(premises, conclusion)`: Check inference using Definition 11
- `check_inference(premises, conclusion)`: Alternative inference API

**Ferguson Definition 11 Implementation:**
```python
def entails(premises: list[Formula], conclusion: Formula) -> bool:
    # Create tableau with t:premises and n:conclusion
    signed_formulas = [SignedFormula(t, p) for p in premises]
    signed_formulas.append(SignedFormula(n, conclusion))
    
    tableau = WKrQTableau(signed_formulas)
    result = tableau.construct()
    
    # Valid if all branches close
    return not result.satisfiable
```

### CLI Interface (`src/wkrq/cli.py`)

**Key Components:**
- `main()`: Entry point with argument parsing
- `--mode`: Select wKrQ or ACrQ
- `--sign`: Specify sign for formula
- `--tree`: Display tableau structure
- `--models`: Show counter-models
- `--json`: Machine-readable output

### Auxiliary Modules

#### Bilateral Equivalence (`src/wkrq/bilateral_equivalence.py`)
- `get_bilateral_transform()`: Convert ¬φ to bilateral form
- `check_bilateral_equivalence()`: Test if formulas are equivalent
- `check_acrq_closure()`: Lemma 5 closure conditions

#### LLM Integration (`src/wkrq/llm_integration.py`)
- `create_llm_tableau_evaluator()`: Factory for LLM evaluators
- Wraps bilateral-truth package
- Converts between GeneralizedTruthValue and BilateralTruthValue

#### Tableau Tracing (`src/wkrq/tableau_trace.py`)
- `TableauConstructionTrace`: Records construction steps
- `RuleApplicationTrace`: Details of each rule application
- Used for debugging and visualization

## Data Flow

1. **Input**: Formula string or Formula object
2. **Parsing**: Convert string to Formula tree
3. **Tableau Setup**: Create initial SignedFormulas
4. **Construction Loop**:
   - Select applicable rules
   - Apply rules (may create branches)
   - Check for contradictions
   - Repeat until complete or saturated
5. **Model Extraction**: From open branches
6. **Output**: TableauResult with models or proof of unsatisfiability

## Key Implementation Insights

### Soundness
- All tableau rules preserve semantic validity
- Branch closure only on genuine contradictions
- Meta-signs properly expanded for atomic formulas

### Completeness (Practical)
- Systematic exploration of all truth values
- Fresh constant generation for quantifier counterexamples
- Universal reprocessing for new constants
- Terminates for finite domains

### Critical Fixes Applied
1. **Definition 11**: Correct implementation with `t:premises, n:conclusion`
2. **Meta-sign expansion**: Added for atomic formulas (essential for completeness)
3. **Fresh constants**: n-universal generates fresh constants for counterexamples

## Testing Architecture

### Test Organization (`tests/`)
- `test_soundness_completeness_proofs.py`: Systematic proof verification
- `test_ferguson_*.py`: Ferguson compliance tests
- `test_acrq_*.py`: ACrQ-specific functionality
- `test_quantifier_*.py`: Quantifier reasoning
- `test_critical_bugs.py`: Regression tests for major fixes

### Test Count: 633 tests
- 626 passing
- 4 skipped (intentional)
- 3 xfailed (known limitations)

## Performance Characteristics

- **Complexity**: Exponential in worst case (branching rules)
- **Optimizations**:
  - O(1) contradiction checking via formula indexing
  - Universal instantiation tracking prevents redundant work
  - Branch independence allows parallel exploration
- **Practical limits**: ~1000 nodes typical maximum

## Future Extension Points

1. **Semantic contradiction detection**: Add semantic evaluation after rule application
2. **Parallel tableau construction**: Exploit branch independence
3. **Incremental solving**: Reuse partial tableaux
4. **Alternative quantifier strategies**: Different instantiation orders
5. **Proof extraction**: Generate natural deduction proofs from closed tableaux