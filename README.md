# AegisGraph v1.0 — ASEMA DP2 Sanitized Public Release

> 577 Industries' AegisGraph platform provides graph-driven automated
> vulnerability discovery evidence for Secure Messaging Applications
> (SMAs), addressing DARPA topic HR0011SB20254-12 ASEMA.

**v1.0 is additive: every v0.3 and v0.4 evidence record continues to validate.**
v1.0 = v0.4 + completed M7 (InvariantCheck ground-truth) + M8-M10
(reviewer workbench) + M11-M14 engineering deliverables.

## What This Release Contains

### Carried forward from v0.4 (unchanged)

- **v0.4 evidence package** (`evidence/aegisgraph-v0.4-evidence.json`):
  preserved verbatim. 8 discovery_runs, 6 disagreements, 6
  cross_target_candidates, empty crashes/invariant_violations/
  disclosure_events arrays by design.
- **v0.3 evidence package** (`evidence/aegisgraph-v0.3-evidence.json`):
  preserved verbatim. 12 evidence_refs, 6 graph_threads, 12
  recommendations, 7-tool SOTA matrix, 2 pinned targets.
- **14-figure visual pack** (`figures/F1-F14`).
- **v0.4 extended polydiff regression**
  (`polydiff_regression_report.sanitized.json`): 16 v0.4-additive
  disagreement entries across 5 new families. Preserved unchanged.
- **Apache-2.0 license**.

### New in v1.0 (additive)

- **v1.0 evidence package** (`evidence/aegisgraph-v1.0-evidence.json`):
  all v0.4 sections preserved + AG-XSMA-VALIDATED-SIG-GP-001-ELX
  appended to `cross_target_candidates[]`; new
  `cross_target_candidates_validated: 1` summary field; new
  `m14_demo_dryrun_summary` structural block.
- **CETM** (`evidence/cetm.json`): updated to the 82-claim v0.4 CETM
  with C-NEW-PD-EXT promoted to A and engineering integration tip
  bumped to `ca9e3af` (per Wave 7C).
- **Versioned polydiff sanitized report**
  (`polydiff_regression_report.sanitized.v1.0.json`): full 6-family
  content with v1.0 additions note; hashes only.
- **Extended traceability matrix**
  (`reports/traceability_matrix.{json,md}`): 75 rows total (66 v0.4
  rows + 9 v1.0 engine rows).
- **Baseline-tool delta report** (`baseline-tool-delta/`):
  CodeQL/Semgrep/MobSF vs AegisGraph comparison scaffold + per-target
  MOBSF-LIMITED.md honesty markers.
- **F15-F22 figure pack** (`figures/`): engine architecture, discovery
  loop, polydiff multi-family, harnessgen flow, invariantcheck card,
  crosssma matrix, disclosure state diagram, schema-v2 overlay.
- **Manifest** (`manifest.json`): `release.version: v1.0`,
  `release.predecessor: v0.4`, `release.cut_date: 2026-05-13`,
  `release.engineering_integration_commit: d91c1df`,
  `release_authorized: true`, `safety_posture: sanitized_candidate`,
  `tool_output_type: public_sanitized_export`.
- **Exclusions** (`EXCLUSIONS.md`): extended with v1.0 engineering-
  private categories.
- **Release notes** (`RELEASE_NOTES.md`): full v0.4 -> v1.0 changelog.

## What This Release DOES NOT Contain (see `EXCLUSIONS.md`)

### Carried forward from v0.3 + v0.4
- Crash-triggering input bytes from ReproChain or HarnessGen (only
  hashes + structure).
- Pre-disclosure findings outside disclosure-policy authorization.
- Raw target source code (Signal Android, Element X Android,
  matrix-rust-sdk).
- Live target probes / production-app traces.
- Credentials, private paths, customer/partner names.
- Engineering-private disclosure ledger, vendor registry, outbound
  letters, Jinja2 templates.
- Engineering-private CodeQL queries and Semgrep rules; SARIF result
  bodies stay engineering-private.
- Raw stack traces with line numbers.
- `source_snippet` fields longer than 256 chars.
- Attacker URLs / payloads inside cross_target_candidate.
- `claim_state == "reviewed_embargoed"` records.

### New v1.0 exclusions
- Engineering-private reviewer-workbench promotion ledger
  (`aegisgraph/workbench/promotions/**`) — only sanitized reviewer-
  packet manifest metadata surfaces publicly.
- Engineering-private M14 demo dry-run output bytes
  (`exports/m14-demo-dryrun/**`) — only the structural
  `m14_demo_dryrun_summary` block (step names, status counts, skip
  reasons) appears publicly.
- Engineering-private InvariantCheck ground-truth fixture outputs
  (`aegisgraph/invariants/ground_truth/**`).
- Engineering-private HarnessGen scaffold private inputs /
  corpus references (`aegisgraph/harnessgen/scaffolds/private/**`).
- Engineering-private CrossSMA validation working files
  (`aegisgraph/crosssma/validations/raw/**`).

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
BLOCKING_PATTERNS). The engineering integration tip at v1.0 cut is
`d91c1df` on `stream/integration` (1030 tests passed, 19 skipped).
This tree was scanned and certified clean before tag.

## What Reviewers Should Note

- **Additive promise**: every v0.3 and v0.4 evidence record continues
  to validate. No earlier file is modified; no earlier claim is
  retracted. v1.0 strictly extends.
- **Honest empty arrays**: `crashes[]`, `invariant_violations[]`,
  and `disclosure_events[]` remain empty by design at v1.0 cut.
  HarnessGen ships scaffolds; live 24h fuzz runs are deferred to
  the self-hosted runner. SARIF results stay engineering-private.
  Disclosure ledger entries remain blocked on counsel review
  (T-M1.4 + T-M1.5).
- **0 disclosures (counsel-blocked, honest)**: the disclosure
  pipeline format is fully demonstrated; entries are zero. We do
  not claim disclosures that did not occur.
- **MOBSF-LIMITED transparency**: APKs are absent under anchor-only
  policy. The baseline-tool-delta report records this honestly per
  target.
- **CrossSMA validated cell**: 1 of 24 cells validated
  (AG-XSMA-VALIDATED-SIG-GP-001-ELX, status `confirmed_reachable`).
  Remaining 23 cells stay `candidate_path` honestly pending
  HarnessGen run validation on the self-hosted runner; Wire and
  Telegram target_findings statuses are `deferred_to_M22.1` per
  ADR additive policy.
- **Static reachability != exploitation**: ReproChain reachability
  claims about CVE-2023-4863 are preserved from v0.3 without
  modification.
- **PolyDiff parser disagreements != vulnerabilities**: security-
  relevance is asserted only after the documented classifier rules
  in favor.
- **Score vectors are assessment-priority**, NOT vulnerability-
  severity.
- **Engineering integration commit at v1.0 cut**: `d91c1df` on
  `stream/integration`.
- **Master proposal v1.0 PDF SHA**:
  `1ed7a5afe4a4b2ff659afa307e7bb391c724c16365d7a693d51121b9e073716b`.

## v0.4 -> v1.0 Delta

See `RELEASE_NOTES.md` for the full changelog.

## Changelog Appendix: v0.4 -> v1.0 Section Mapping

| v0.4 section | v1.0 section | Note |
|---|---|---|
| `release.version: v0.4` | `release.version: v1.0` | predecessor: v0.4 |
| `release.engineering_integration_commit: 665d10f` | `release.engineering_integration_commit: d91c1df` | engineering tip advance |
| `cross_target_candidates[]` (6 entries) | `cross_target_candidates[]` (7 entries) | adds AG-XSMA-VALIDATED-SIG-GP-001-ELX; v0.4 entries with Wire/Telegram `unknown` updated to `deferred_to_M22.1` per ADR additive policy |
| (new) | `cross_target_candidates_validated: 1` | summary count |
| (new) | `m14_demo_dryrun_summary` | structural block, no payload bytes |
| `crashes[]: []` | `crashes[]: []` | still empty; HarnessGen 5/5 scaffolds shipped; live fuzz deferred to T-M4.1 |
| `invariant_violations[]: []` | `invariant_violations[]: []` | still empty in public; SARIF engineering-private; production invariants 12/15 -> 15/15 |
| `disclosure_events[]: []` | `disclosure_events[]: []` | still empty; counsel-blocked (T-M1.4/T-M1.5) |
| `discovery_runs[]` (8 entries) | `discovery_runs[]` (8 entries) | preserved unchanged at v1.0 |
| `disagreements[]` (6 entries) | `disagreements[]` (6 entries) | preserved unchanged at v1.0 |

Every v0.3 and v0.4 record continues to validate against
`evidence/aegisgraph-v0.3-evidence.json` and
`evidence/aegisgraph-v0.4-evidence.json`. The v1.0 evidence file is
a superset that nests every v0.4 surface verbatim.

## Pointers

- AegisGraph engineering platform (open-source): https://github.com/577Industries/aegisgraph
- DARPA topic: HR0011SB20254-12 (Assessing Security of Encrypted Messaging Applications, ASEMA)
- Master proposal narrative: PDF SHA `1ed7a5afe4a4b2ff659afa307e7bb391c724c16365d7a693d51121b9e073716b`; full text in submission package

## License

Apache-2.0.
