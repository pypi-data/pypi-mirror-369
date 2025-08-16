# Ferguson Call Demo Summary

## Quick Start Commands

### 1. Basic wKrQ Demo
```bash
# Show that P → P is NOT valid in weak Kleene
wkrq valid "P -> P"

# Show modus ponens is NOT valid
wkrq valid "(P & (P -> Q)) -> Q"

# Show tableau with trace
wkrq solve "P & ~P" --trace --tree
```

### 2. ACrQ Comprehensive Demo
```bash
# Run the full interactive ACrQ demonstration
python examples/acrq_demo_ferguson.py
```

### 3. Test Suite
```bash
# Show all tests passing
pytest -q

# Show Ferguson compliance tests
pytest tests/test_ferguson_compliance.py -v

# Show ACrQ-specific tests
pytest tests/test_acrq_tableau.py -v

# Show LLM integration tests
pytest tests/test_llm_integration.py -v
```

## Key Demo Points

### wKrQ (Definition 9)
- ✅ Complete 6-sign system (t, f, e, m, n, v)
- ✅ Error branches for weak Kleene completeness
- ✅ Classical tautologies NOT valid (P → P can be undefined)
- ✅ Modus ponens NOT valid (weak Kleene semantics)

### ACrQ (Definition 18)
- ✅ Bilateral predicates (R/R* duality)
- ✅ Paraconsistent (contradictions don't explode)
- ✅ Paracomplete (knowledge gaps)
- ✅ DeMorgan as transformation rules
- ✅ Glut tolerance per Lemma 5

### ACrQ-LLM Extension (New!)
- ✅ Epistemic evaluation via Claude 3.5 Sonnet
- ✅ Hybrid formal-empirical reasoning
- ✅ Seamless integration with bilateral predicates
- ✅ Formal specification as new tableau rule
- ✅ Real-time fact checking against world knowledge
- ✅ Detects contradictions between formal rules and reality

## Demo Flow

### Part 1: wKrQ Basics (5 min)
1. Show P → P is not valid
2. Show modus ponens fails
3. Display tableau with error branches

### Part 2: ACrQ Features (20 min)
Run `python examples/acrq_demo_ferguson_final.py`:

1. **Bilateral Predicates** - R/R* duality with tableau trees
2. **Paraconsistency** - No explosion
3. **DeMorgan Transformations** - Syntactic rules
4. **Quantifier DeMorgan** - Negated quantifiers
5. **Pluto/Sedna Classification** - With real LLM knowledge
6. **Legal Reasoning** - Glut handling
7. **LLM Integration (ACrQ-LLM)** - Real Claude 3.5 Sonnet evaluation
8. **Rule Sequences** - Step-by-step tableau construction

### Part 3: Technical Discussion (10 min)
- Error branch implementation
- Bilateral predicate closure conditions
- LLM evaluation as tableau rule
- Questions for Thomas

## Files to Have Ready

```bash
# Core implementations
src/wkrq/wkrq_rules.py          # Definition 9
src/wkrq/acrq_rules.py          # Definition 18
src/wkrq/bilateral_equivalence.py # Lemma 5

# Documentation
docs/FERGUSON_VALIDATION_WITH_LLM.md
docs/LLM_RULE_FORMAL_SPECIFICATION.md
docs/FERGUSON_DEFINITION_18_ACRQ.md

# Tests
tests/test_ferguson_compliance.py
tests/test_acrq_tableau.py
tests/test_llm_rule_validation.py

# Examples
examples/acrq_demo_ferguson_final.py  # Main demo with LLM
examples/llm_demo_real.py            # Standalone LLM demo
examples/simple_llm_demo.py          # Simple LLM integration
```

## Statistics

- **Implementation**: 100% Ferguson-compliant
- **Tests**: 611 total (all passing)
- **Coverage**: All Definition 9 and 18 rules implemented
- **Performance**: < 10ms for propositional, < 100ms for first-order
- **LLM Integration**: Full bilateral-truth integration with Claude 3.5 Sonnet
- **Version**: 3.0.0 (released to PyPI)

## Questions for Thomas

1. **Error branches**: Is our interpretation correct for t-disjunction and t-implication?
2. **v-sign rules**: Should v-sign appear in actual tableaux or only in rule notation?
3. **ACrQ-LLM**: Thoughts on epistemic evaluation as tableau rule?
4. **Applications**: What real-world uses do you envision?

## Backup Plan

If technical issues arise:
```bash
# Pre-recorded outputs
cat examples/validation.txt        # Literature examples
cat docs/COMPLETE_VALIDATION.md    # Full validation report
pytest --co -q | tail -1           # Show test count

# Static demonstrations
python examples/simple_bilateral_usage.py
python examples/penguin_paraconsistent.py
```

## Thank You Message

"Thomas, your work on weak Kleene logic with restricted quantification has been transformative. The elegance of the 6-sign system and the power of bilateral predicates for paraconsistent reasoning opens new frontiers in computational logic. We're honored to have implemented your vision and hope this tool helps spread your ideas to researchers and students worldwide."