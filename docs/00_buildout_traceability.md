# 00 Buildout Traceability

Traceability from the Phase-I buildout plan to schemas, scripts, evidence IDs, tests, and release gates.

| Source Section | Evidence | Deliverable | Script/Test | Gate |
|---|---|---|---|---|
| 3 Safety | EVID-SAFETY-001 | claim discipline docs | validate_claim_states.py | zero violations |
| 9 Evidence Ledger | EVID-LEDGER-001 | public_ledger.jsonl | verify_public_package.py | hash refs pass |
| 11 Graph Model | EVID-GRAPH-001 | nodes.jsonl / edges.jsonl | test_graph_evidence_refs.py | >=98% coverage |
| 15 Synthetic Target | EVID-SYNTH-001 | AegisSMA-Lab traces | run_smabench_synthetic.py | deterministic repeat |
| 20 SOTA | EVID-SOTA-001 | SOTA packet | verify_public_package.py | composition claim present |
