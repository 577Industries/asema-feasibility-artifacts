# AegisGraph v0.4 Release Notes

**Tag**: release/v0.4.0
**Date**: 2026-05-13
**Predecessor**: v0.3.0 (tag `v0.3.0-asema-dp2-feasibility`, 2026-05-08)
**License**: Apache-2.0
**Engineering integration tip at cut**: `665d10f`

## v0.3 -> v0.4 Delta

v0.4 is **additive**: every v0.3 evidence record continues to validate.
No v0.3 claim is retracted; no v0.3 file is modified. The v0.4 release
adds six discovery engines, formal schema-v2 additive surfaces for their
output, and the validator-v2 sanitize-check rule extensions that gate
the public projection.

### Added — discovery engines

- **PolyDiff Extended (6 families)**: image, opengraph, deeplink, qr,
  proto families joined the URL family from v0.3 (M2.1-M2.6). 16
  anchored historical bugs across the new families; each tier-P1 status
  passes. The image family anchors include CVE-2023-4863 (libwebp) plus
  3 additional historical decoder bugs. All disagreement entries in
  `polydiff_regression_report.sanitized.json` use sha256 prefixes only;
  no witness bytes redistributed.
- **HarnessGen (M5.1 + M5.2 + libwebp scaffold)**: 5 harnesses
  scaffolded — libwebp native (libFuzzer), Signal LinkPreviewUtil
  (Jazzer/JVM), matrix-rust-sdk MessageType (cargo-fuzz), plus 2
  additional native + JVM templates. Each compiles in the pinned
  devcontainer. No 24h fuzz run executed for v0.4; `crashes[]` is empty
  by design (lands at v0.5 after first run + counsel review).
- **InvariantCheck library v1 (M3.3 + M5.3 + full encode)**: 15
  invariants total — INV-01 .. INV-15. M3.3 shipped 5; M5.3 added 10.
  Three M5.3 additions are fully CodeQL/Semgrep-encoded (INV-02
  notification leak, INV-05 key storage no keystore, INV-08 clipboard
  paste to send). The remaining 7 ship as rich-comment stubs scheduled
  for M7 ground-truth completion. `invariant_violations[]` is empty in
  the public projection by design; SARIF results stay engineering-
  private per plan §10 and Rule 8.
- **CrossSMA 24-cell matrix (M4.1)**: 4 targets (signal-android,
  element-x-android verified; wire-android, telegram-android stubs) x
  6 structural patterns. 6 AG-XSMA-* candidates exported with
  `validation_state: "structural_only"` pending harness/dynamic
  confirmation.
- **Disclosure pipeline scaffold (M3.4)**: hash-chained
  `aegisgraph/disclosure/ledger.py` (uses the same `verify_hash_chain`
  as evidence records), `vendor_registry.yaml`, Jinja2 templates for
  vendor initial email / reproduction steps / CVE request (Chrome CNA,
  MITRE direct, GitHub Security Advisory variants). `disclosure_events[]`
  is empty in the public projection by design pending counsel review.

### Added — public artifact schema (v0.4 additive arrays)

- `discovery_runs[]` — 8 representative engine-execution records
- `disagreements[]` — 6 entries (one per active PolyDiff family)
- `crashes[]` — empty (HarnessGen scaffolds only at v0.4 cut)
- `invariant_violations[]` — empty (real SARIF stays engineering-private)
- `cross_target_candidates[]` — 6 entries from the 24-cell matrix
- `disclosure_events[]` — empty (counsel review blocks; v0.5)

### Added — validator-v2 (sanitize-check rule extensions)

Lands on engineering branch `stream/validator-export` (commit `2aeb225`).
Per plan §10:
- 5 new BLOCKING_PATTERNS: `vendor_contact_in_public_artifact`,
  `disclosure_embargoed_leak`, `raw_stack_trace`,
  `target_source_snippet`, `crosssma_target_redistribution`.
- 3 new sanitize_check rules:
  - **Rule 7** disclosure ledger redaction (event_type whitelist =
    {cve_assigned, cve_published, disclosure_public}; vendor_contact
    org-id-only; notes_hash null in public exports)
  - **Rule 8** SARIF source-snippet redaction (location to repo_url +
    commit + path + start_line only; no source_snippet field anywhere)
  - **Rule 9** crash record completeness (crash_sha256 required; no
    payload-bearing fields including the v0.4-extended `raw_witness` and
    `raw_corpus_input`).

### Added — CETM v0.4

`evidence/cetm.json` updated to 82 claims (69 v0.3 + 13 new engine
families: PolyDiff x 5 families, HarnessGen, HarnessGen crashes
(planned), InvariantCheck library v1, InvariantCheck violations
(planned), CrossSMA matrix, CrossSMA candidates, disclosure scaffold,
validator-v2).

### Added — traceability matrix v0.4

`reports/traceability_matrix.{json,md}` extended with 13 v0.4 engine
rows: 66 total (39 ok, 17 claim-without-evidence, 5 evidence-without-
claim, 5 planned). Target counts hold within plan §10 v0.4 envelope.

### Changed

- `manifest.json`: `release.version: "v0.4"`, `release_authorized: true`,
  `validation_status: "pass"`, `safety_posture: "sanitized_candidate"`,
  `tool_output_type: "public_sanitized_export"`, additional artifact
  entries for the new v0.4 files.
- `EXCLUSIONS.md`: extended with engineering-private categories
  (`aegisgraph/disclosure/{ledger.jsonl,vendor_registry.yaml,outgoing/,
  templates/}`, `aegisgraph/invariants/library/codeql/**`,
  `aegisgraph/invariants/library/semgrep/**`, `harnessgen/runs-private/**`,
  raw stack traces, source_snippet long fields, attacker URLs in
  cross_target_candidate, reviewed_embargoed records).

### Removed / retracted

None. v0.4 is strictly additive.

### Known limitations (documented honestly)

- `crashes[]` and `invariant_violations[]` ship empty by design. They
  fill at v0.5 (HarnessGen 24h fuzz runs + counsel-cleared AG-IV-*
  records).
- `disclosure_events[]` ships empty by design. Real disclosure ledger
  entries land at v0.5 once at least one finding clears counsel review,
  vendor coordination, and embargo expiry.
- Sanitize-check Rule 8 forbids `source_snippet` fields — public
  AG-IV-* records reference SARIF files by URI only; reviewers needing
  the full SARIF body must work via the engineering channel.

### Compliance discipline

- No live target probing.
- No raw target source redistribution.
- No crash-inducing input bytes (Rule 5 + Rule 9 enforced).
- No credentials / no PII.
- No vendor contact emails in public artifacts (new BLOCKING_PATTERN).
- Static observations bounded as reachability evidence, NOT
  vulnerability claims.

## License

Apache-2.0.
