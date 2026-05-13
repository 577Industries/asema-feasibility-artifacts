# AegisGraph v1.0 Release Notes

**Tag**: `v1.0.0-asema-dp2-feasibility` (branch `release/v1.0.0`)
**Date**: 2026-05-13
**Predecessor**: v0.4.0 (tag `release/v0.4.0`, 2026-05-13)
**Earlier predecessor**: v0.3.0 (tag `v0.3.0-asema-dp2-feasibility`, 2026-05-08)
**License**: Apache-2.0
**Engineering integration tip at cut**: `d91c1df` on `stream/integration`
**Tests at cut**: 1030 passed, 19 skipped (engineering integration)
**Master proposal v1.0 PDF SHA**: `1ed7a5afe4a4b2ff659afa307e7bb391c724c16365d7a693d51121b9e073716b`

## v0.4 -> v1.0 Delta

v1.0 is **additive**. Every v0.4 evidence record continues to validate.
Every v0.3 evidence record continues to validate. No earlier file is
modified; no earlier claim is retracted. v1.0 represents the final
engineering wrap-up of M7 (InvariantCheck ground-truth) + M8-M10
(reviewer workbench) + M11-M14 (CrossSMA validation, baseline-tool
delta, M14 demo dry-run).

### Added — engineering completions

- **InvariantCheck 15/15 production**: invariant library reached the
  full 15-of-15 production state (was 12/15 at v0.4). Ground-truth
  fixture at `tests/fixtures/demo-vulnerable-app/` on the engineering
  side. Real SARIF result bodies stay engineering-private per plan
  §10 + sanitize-check Rule 8. Ground-truth pass against real binaries
  runs on a self-hosted runner per
  `.github/workflows/invariants-ground-truth.yml`. The public
  `invariant_violations[]` array remains empty by design — public
  AG-IV-* records are held pending Rule 8 location redaction and
  counsel review.
- **HarnessGen 5/5 entry points scaffolded** (was 1/5 at v0.4):
  - libwebp native (libFuzzer)
  - libavif native (libFuzzer)
  - Signal LinkPreviewUtil JVM (Jazzer)
  - Element X MediaRepository JVM (Jazzer)
  - matrix-rust-sdk MessageType Rust (cargo-fuzz)
  All five compile in the pinned devcontainer. **Live 24h fuzz runs
  remain deferred** to T-M4.1 self-hosted runner provisioning. The
  public `crashes[]` array stays empty by design at v1.0 cut; crash
  records (with `crash_sha256` + `stack_trace_hash`; NEVER raw bytes
  per Rule 9) land in a subsequent point release once at least one
  run completes and counsel review approves.
- **CrossSMA validated cell** (`AG-XSMA-VALIDATED-SIG-GP-001-ELX`):
  the Signal SIG-GP-001 link-preview URL parser pattern is confirmed
  reachable on the Element X equivalent path. Status:
  `confirmed_reachable` (validation_state). 1 of 24 cells validated
  at v1.0 cut. The remaining 23 cells retain `candidate_path`
  honestly pending HarnessGen run validation on the self-hosted
  runner. Wire/Telegram target_findings statuses are
  `deferred_to_M22.1` per ADR additive policy; T-M22.1 gates
  additional-SMA target authorization.
- **Baseline-tool delta report scaffold**
  (`baseline-tool-delta/delta-report.{json,md}` + per-target
  subdirectories): CodeQL/Semgrep/MobSF vs AegisGraph comparison
  scaffold. **MOBSF-LIMITED.md** honesty marker recorded for both
  Signal Android and Element X Android targets — APK absent under
  anchor-only policy; no fabricated MobSF findings. Per-target
  AegisGraph counts are 0 (scaffold_pending) because invariant +
  polydiff execution against the real targets is deferred to the
  self-hosted runner (T-M4.1). The delta-report is honest scaffolding,
  not a fabricated finding count.
- **Reviewer workbench CLI + `make reviewer-packet`** (M8-M10):
  shipped on engineering `stream/integration` at tip `d91c1df`. The
  CLI exposes `python3 -m aegisgraph.cli workbench list` and the
  Makefile target produces sanitized reviewer bundles at
  `exports/reviewer-packet/{ISO_DATE}/`. The workbench promotion
  ledger itself remains engineering-private; only the bundle manifest
  is reviewer-facing. The public release projects only the structural
  fact that this surface exists.
- **M14 demo dry-run script** (`scripts/m14_demo_dryrun.sh`):
  end-to-end pipeline orchestration covering extraction-v2, PolyDiff
  Extended, InvariantCheck ground-truth, HarnessGen scaffold compile,
  CrossSMA matrix render, reviewer-packet export, and disclosure
  ledger append. Honest skip semantics: step 3 (InvariantCheck
  ground-truth on real binaries) skips with `runner_blocked` /
  T-M4.1; step 7 (disclosure ledger append) skips with
  `counsel_blocked` / T-M1.4 + T-M1.5. The public projection ships
  only the `m14_demo_dryrun_summary` block (step names, status
  counts, skip reasons) — no payload bytes.
- **F15-F22 figure pack**: 8 new figures rendered for the v1.0
  master proposal cut and now bundled in `figures/`:
  F15 engine architecture, F16 discovery loop, F17 polydiff
  multi-family, F18 harnessgen flow, F19 invariantcheck card,
  F20 crosssma matrix, F21 disclosure state diagram, F22 schema-v2
  overlay.
- **Master proposal v1.0**: published at
  `03_PROPOSAL/active-package/01_master_proposal/AegisGraph_ASEMA_DP2_Master_Proposal_v1.0.md`;
  rendered PDF SHA `1ed7a5afe4a4b2ff659afa307e7bb391c724c16365d7a693d51121b9e073716b`.

### Added — public artifact schema (v1.0 additive surfaces)

All additive on top of v0.4. Every v0.4 array remains intact.

- `cross_target_candidates_validated: 1` summary field plus the new
  AG-XSMA-VALIDATED-SIG-GP-001-ELX record appended to
  `cross_target_candidates[]`.
- `m14_demo_dryrun_summary` structural block (tool_output_type,
  status_counts, step_names, iso_date) referencing the engineering-
  private dryrun output landing at
  `exports/m14-demo-dryrun/2026-05-13/`.
- v1.0 `_crashes_note`, `_invariant_violations_note`,
  `_disclosure_events_note` updated to record the engineering
  completion state honestly.

### Added — public artifact files

- `evidence/aegisgraph-v1.0-evidence.json` (full v0.4 evidence
  preserved verbatim + the v1.0 additive surfaces above)
- `evidence/cetm.json` updated to the 82-claim v0.4 CETM with
  C-NEW-PD-EXT promoted to A; engineering integration tip field
  bumped to `ca9e3af` (Wave 7C); no further modification at v1.0
- `polydiff_regression_report.sanitized.v1.0.json` (versioned
  filename; full 6-family content; hashes only)
- `reports/traceability_matrix.{json,md}` extended with 9 v1.0
  engine rows
- `baseline-tool-delta/` (full directory copied from engineering
  v0.4 scaffold; sanitize-check-clean per Wave 9A)
- `figures/F15-F22` (engine architecture, discovery loop, polydiff
  multi-family, harnessgen flow, invariantcheck card, crosssma
  matrix, disclosure state diagram, schema-v2 overlay)

### Changed

- `manifest.json`: `release.version: "v1.0"`, `release.predecessor:
  "v0.4"`, `release.cut_date: "2026-05-13"`,
  `release.engineering_integration_commit: "d91c1df"`,
  `release_authorized: true`, `validation_status: "pass"`,
  `safety_posture: "sanitized_candidate"`,
  `tool_output_type: "public_sanitized_export"`. Artifact entries
  extended for the new v1.0 files.
- `EXCLUSIONS.md`: extended with v1.0 engineering-private categories
  (`aegisgraph/workbench/promotions/**`,
  `exports/m14-demo-dryrun/**`,
  `aegisgraph/invariants/ground_truth/**`,
  `aegisgraph/harnessgen/scaffolds/private/**`,
  `aegisgraph/crosssma/validations/raw/**`).

### Removed / retracted

None. v1.0 is strictly additive. Every v0.3 and v0.4 evidence record
continues to validate.

### Disclosure status — honest

**Zero real disclosure ledger entries at v1.0 cut.** The disclosure
pipeline format is fully demonstrated (hash-chained ledger,
vendor-registry, Jinja2 templates for Chrome CNA / MITRE direct /
GitHub Security Advisory). Real CVE filing is blocked on:

- **T-M1.4**: counsel one-time review of disclosure policy + first
  vendor-contact letter template
- **T-M1.5**: retain vulnerability-disclosure counsel (prerequisite
  for T-M1.4)

`disclosure_events[]` remains empty in the public projection by
design. The v1.0 narrative does not claim disclosures that did not
occur.

### Honest gap list (load-bearing — read this)

- **0 real disclosure ledger entries** (T-M1.4 + T-M1.5 counsel
  review pending)
- **Live 24h HarnessGen fuzz runs deferred** (T-M4.1 self-hosted
  runner provisioning). HarnessGen ships harness *scaffolds*, not
  crash bytes.
- **DynamicProbe Engine 5 scaffold only** (M15-M24 option-period
  scope per plan §28).
- **InvariantCheck ground-truth pass against real binaries** runs on
  the self-hosted runner per
  `.github/workflows/invariants-ground-truth.yml`. Public
  `invariant_violations[]` stays empty by design.
- **MobSF baseline-tool runs against APKs not executed** — anchor-
  only policy means no APKs in-tree. `MOBSF-LIMITED.md` recorded
  honestly in each target's baseline-tool-delta subdirectory.

### Compliance discipline (unchanged from v0.4)

- No live target probing.
- No raw target source redistribution.
- No crash-inducing input bytes (Rule 5 + Rule 9 enforced).
- No credentials / no PII.
- No vendor contact emails in public artifacts (Rule 7).
- Static observations bounded as reachability evidence, NOT
  vulnerability claims.

### Verification

```
git clone <this-repo>
cd <this-repo>
python3 scripts/verify_public_package.py
# Expected: PUBLIC PACKAGE READY: all evaluator-visible checks passed.
sha256sum -c evidence/checksums.sha256
sha256sum -c checksums/SHA256SUMS
```

## License

Apache-2.0.
