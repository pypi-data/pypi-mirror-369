# wKrQ/ACrQ Documentation

This directory contains the essential documentation for understanding and using the wKrQ/ACrQ tableau systems for weak Kleene logic with restricted quantification.

## Essential Documentation (Start Here)

### System Architecture & Implementation
1. **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** - Complete system architecture with diagrams and pseudo-code
2. **[SOUNDNESS_COMPLETENESS_UPDATE.md](SOUNDNESS_COMPLETENESS_UPDATE.md)** - Current soundness and completeness properties
3. **[IMPLEMENTATION_VERIFICATION.md](IMPLEMENTATION_VERIFICATION.md)** - Detailed rule-by-rule verification and known limitations

### Ferguson (2021) Paper Analysis
4. **[FERGUSON_DEFINITIONS.md](FERGUSON_DEFINITIONS.md)** - Consolidated definitions from the paper (Definitions 9, 10, 11, 17, 18, Lemma 5)
5. **[FERGUSON_QUANTIFIER_DEFINITIONS.md](FERGUSON_QUANTIFIER_DEFINITIONS.md)** - Detailed restricted quantifier semantics and rules
6. **[FERGUSON_DEFINITION_9_COMPLETE.md](FERGUSON_DEFINITION_9_COMPLETE.md)** - Complete wKrQ tableau rules with annotations
7. **[FERGUSON_THEOREMS_3_4_ACRQ.md](FERGUSON_THEOREMS_3_4_ACRQ.md)** - Soundness and completeness theorems

### Bilateral Logic & ACrQ
8. **[FERGUSON_DEFINITION_17_BILATERAL.md](FERGUSON_DEFINITION_17_BILATERAL.md)** - Bilateral translation rules
9. **[FERGUSON_DEFINITION_18_ACRQ.md](FERGUSON_DEFINITION_18_ACRQ.md)** - ACrQ as modified wKrQ
10. **[FERGUSON_LEMMA_5_CLOSURE.md](FERGUSON_LEMMA_5_CLOSURE.md)** - Bilateral closure conditions
11. **[BILATERAL_EQUIVALENCE_IMPLEMENTATION.md](BILATERAL_EQUIVALENCE_IMPLEMENTATION.md)** - Implementation details

### User Documentation
12. **[API.md](API.md)** - Python API reference
13. **[CLI.md](CLI.md)** - Command-line interface guide
14. **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and tutorials

### Specialized Topics
15. **[DEMORGAN_IMPLEMENTATION_COMPLETE.md](DEMORGAN_IMPLEMENTATION_COMPLETE.md)** - DeMorgan laws in ACrQ
16. **[LLM_RULE_FORMAL_SPECIFICATION.md](LLM_RULE_FORMAL_SPECIFICATION.md)** - LLM integration for predicate evaluation

## Quick Start Guide

### If you're new to the system:
1. Read [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) for the big picture
2. Review [EXAMPLES.md](EXAMPLES.md) for practical usage
3. Check [API.md](API.md) or [CLI.md](CLI.md) depending on your use case

### For theoretical understanding:
1. Start with [FERGUSON_DEFINITIONS.md](FERGUSON_DEFINITIONS.md) for core concepts
2. Read [SOUNDNESS_COMPLETENESS_UPDATE.md](SOUNDNESS_COMPLETENESS_UPDATE.md) for theoretical properties
3. Review [IMPLEMENTATION_VERIFICATION.md](IMPLEMENTATION_VERIFICATION.md) for implementation details

## System Overview

### wKrQ (Standard System)
- Three-valued logic: `t` (true), `f` (false), `e` (undefined/error)
- Weak Kleene semantics: any operation with undefined yields undefined
- No classical tautologies: `p ∨ ¬p` can be undefined
- Restricted quantification: `[∃x P(x)]Q(x)` and `[∀x P(x)]Q(x)`
- Ferguson's 6-sign tableau system: `t`, `f`, `e`, `m`, `n`, `v`

### ACrQ (Paraconsistent Extension)
- Bilateral predicates: each predicate R has dual R* for negative evidence
- Four information states: true, false, gap (no info), glut (conflicting info)
- Paraconsistent: handles contradictions without explosion
- Based on Ferguson Definition 18

## Key Features

1. **Unified Tableau Engine** - Single implementation for both wKrQ and ACrQ
2. **LLM Integration** - Optional LLM evaluation of atomic formulas
3. **Complete Ferguson Compliance** - Exact implementation of Ferguson (2021)
4. **Rich CLI** - Interactive mode, tree visualization, inference testing
5. **Python API** - Full programmatic access to all features

## Installation

```bash
# From PyPI
pip install wkrq

# Development install
git clone https://github.com/yourusername/wkrq.git
cd wkrq
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_wkrq_basic.py  # Run specific test
pytest --cov=wkrq        # With coverage
```

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed examples including:
- Basic propositional logic
- First-order logic with quantifiers
- ACrQ paraconsistent reasoning
- LLM integration
- Complex inference patterns

## References

Ferguson, T. M. (2021). *Weak Kleene Logics with Restricted Quantification*.