# Benchmark Validation Plan

Created: 2026-05-01

The ASEMA Phase II benchmark should evolve the pilot into repeatable task suites. The pilot validates that source retrieval, target pinning, manifest extraction, indicator categorization, static rule execution, logging, and evidence indexing can be performed on real public SMA codebases.

## Validation Levels

1. Source availability: pin target commit, license note, and retrieval date.
2. Structural inventory: extract Android components, permissions, intent filters, schemes, and MIME declarations.
3. Source indicator inventory: categorize code references into ASEMA-relevant attack-surface classes.
4. Rule scan: run informational static rules and store machine-readable JSON.
5. Evidence linkage: connect every pilot result to the feasibility study and proposal claim IDs.

## Phase II Expansion

- Add buildable harnesses for parser and state-machine boundaries identified in the pilot.
- Add differential conformance checks across platform implementations when lawful and technically feasible.
- Add dynamic instrumentation only in controlled lab environments and only for owned devices or authorized testbeds.
- Treat every novel issue as responsible-disclosure material, not as proposal-marketing copy.
