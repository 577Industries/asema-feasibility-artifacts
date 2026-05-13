# AegisGraph v0.4 — ASEMA DP2 Sanitized Public Release

> 577 Industries' AegisGraph platform provides graph-based application-layer assessment evidence for Secure Messaging Applications (SMAs), addressing DARPA topic HR0011SB20254-12 ASEMA.

**v0.4 is additive: every v0.3 evidence record continues to validate.**
v0.4 = v0.3 + 6 discovery engines + schema-v2 additive arrays + validator-v2.

## What This Release Contains

### Carried forward from v0.3 (unchanged)

- **v0.3 evidence package** (`evidence/aegisgraph-v0.3-evidence.json`):
  12 evidence_refs, 6 graph_threads, 12 recommendations, 7-tool SOTA
  matrix, 2 pinned targets.
- **7-figure visual pack** (`figures/F1-F7`).
- **v0.3 polydiff regression** (URL family, 74 disagreement entries
  preserved in `polydiff_regression_report.sanitized.json`).
- **Apache-2.0 license**.

### New in v0.4 (additive)

- **v0.4 evidence package** (`evidence/aegisgraph-v0.4-evidence.json`):
  all v0.3 sections preserved + new top-level arrays
  `discovery_runs[]` (8 entries), `disagreements[]` (6 entries),
  `cross_target_candidates[]` (6 entries from the CrossSMA 24-cell
  matrix), `crashes[]` (empty pending v0.5 fuzz runs),
  `invariant_violations[]` (empty pending v0.5 ground-truthing),
  `disclosure_events[]` (empty pending counsel review).
- **CETM v0.4** (`evidence/cetm.json`): 82 claims (69 v0.3 + 13 new
  engine families).
- **Extended polydiff regression**: 16 additional v0.4-additive
  disagreement entries across 5 new families (image, opengraph,
  deeplink, qr, proto) — hashes only.
- **Extended traceability matrix** (`reports/traceability_matrix.{json,md}`):
  66 rows (53 v0.3 + 13 v0.4 engine rows).
- **Manifest** (`manifest.json`): `release.version: v0.4`,
  `release_authorized: true`, `safety_posture: sanitized_candidate`,
  `tool_output_type: public_sanitized_export`.
- **Exclusions** (`EXCLUSIONS.md`): extended with v0.4 engineering-
  private categories.
- **Release notes** (`RELEASE_NOTES.md`): full v0.3 -> v0.4 changelog.

## What This Release DOES NOT Contain (see `EXCLUSIONS.md`)

### Carried forward from v0.3
- Crash-triggering input bytes from ReproChain (only hashes + structure).
- Pre-disclosure findings outside disclosure-policy authorization.
- Raw target source code (Signal Android, Element X Android).
- Live target probes / production-app traces.
- Credentials, private paths, customer/partner names.

### New v0.4 exclusions (per plan §10 + validator-v2)
- `aegisgraph/disclosure/{ledger.jsonl, vendor_registry.yaml, outgoing/,
  templates/}` (engineering-private disclosure pipeline).
- `aegisgraph/invariants/library/codeql/**` + `library/semgrep/**`
  (queries and SARIF results stay engineering-private; only redacted
  AG-IV-* records would surface publicly).
- private fuzz corpora and 24h fuzz-run artifacts (`reprochain/`
  and `harnessgen/` private subtrees per `EXCLUSIONS.md`).
- Raw stack traces with line numbers (only `stack_trace_hash` +
  `stack_trace_summary` allowed).
- `source_snippet` fields longer than 256 chars.
- Pasted attacker URLs / payloads inside
  `cross_target_candidate.structural_description`.
- Records carrying `claim_state == "reviewed_embargoed"` in any
  sanitized_candidate document.

## Quick Verification

```
git clone <this-repo>
cd <this-repo>
python3 scripts/verify_public_package.py
# Expected: PUBLIC PACKAGE READY: all evaluator-visible checks passed.
sha256sum -c evidence/checksums.sha256
sha256sum -c checksums/SHA256SUMS
```

The release manifest's `safety_posture: sanitized_candidate` and
`release_authorized: true` are gated by the engineering-side
`validator/sanitize_check.py` v0.4 (Rules 7/8/9 + 5 new
BLOCKING_PATTERNS). The validator-v2 commit on engineering
`stream/validator-export` (commit `2aeb225`) is the reference
implementation; this tree was scanned and certified clean before tag.

## What Reviewers Should Note

- **Additive promise**: no v0.3 file modified; no v0.3 claim retracted.
  v0.4 strictly extends. Re-running the v0.3 verification flow against
  the v0.3 evidence subset still passes.
- **Honest empty arrays**: `crashes[]`, `invariant_violations[]`, and
  `disclosure_events[]` are empty by design. v0.4 ships the schemas and
  scaffolding; v0.5 ships the populated records once engineering output
  and counsel review land.
- **Static reachability != exploitation**: ReproChain reachability claims
  about CVE-2023-4863 are preserved from v0.3 without modification.
- **PolyDiff parser disagreements != vulnerabilities**: security-
  relevance is asserted only after the documented classifier rules
  in favor.
- **Score vectors are assessment-priority**, NOT vulnerability-severity:
  see `aegisgraph-v0.3-evidence.json#score_model` and master proposal
  §5.6.
- **CrossSMA structural_only**: every v0.4 AG-XSMA-* candidate carries
  `validation_state: "structural_only"`. Harness/dynamic confirmation
  lands at v0.5.
- **Engineering integration commit at v0.4 cut**: `665d10f` on
  `stream/integration`.

## v0.3 -> v0.4 Delta

See `RELEASE_NOTES.md` for the changelog.

## Changelog Appendix: v0.3 -> v0.4 Section Mapping

| v0.3 section | v0.4 section | Note |
|---|---|---|
| `release` | `release` (predecessor: "v0.3") | Adds `predecessor`, `engineering_integration_commit`, `additive_promise` |
| `score_model` | unchanged | preserved verbatim |
| `targets` | unchanged | preserved verbatim |
| `evidence_refs` | unchanged | 12 entries preserved |
| `graph_threads` | unchanged | 6 threads preserved |
| `recommendations` | unchanged | 12 entries preserved |
| `sota_matrix` | unchanged | preserved verbatim |
| `smabench` | unchanged | preserved verbatim |
| `external_validation` | unchanged | preserved verbatim |
| (new) | `discovery_runs[]` | 8 engine-execution records |
| (new) | `disagreements[]` | 6 PolyDiff family entries |
| (new) | `crashes[]` | empty by design (v0.5) |
| (new) | `invariant_violations[]` | empty by design (v0.5) |
| (new) | `cross_target_candidates[]` | 6 entries from 24-cell matrix |
| (new) | `disclosure_events[]` | empty by design (v0.5) |

Every v0.3 record continues to validate against
`evidence/aegisgraph-v0.3-evidence.json`. The v0.4 evidence file is a
superset that nests every v0.3 surface verbatim.

## License

Apache-2.0.

## Pointers

- AegisGraph engineering platform (open-source): https://github.com/577Industries/aegisgraph
- DARPA topic: HR0011SB20254-12 (Assessing Security of Encrypted Messaging Applications, ASEMA)
- Master proposal narrative: cited by hash in this release; full text in submission package
