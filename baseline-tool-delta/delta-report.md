# Baseline-tool delta report (AegisGraph vs CodeQL / Semgrep / MobSF)

_Generated at:_ `2026-05-05T00:00:00Z`
_Milestone:_ M14

## What this report measures

For each pinned Secure Messenger App (Signal Android, Element X Android), this report contrasts findings from three single-tool baselines (CodeQL alone, Semgrep alone, MobSF alone) against AegisGraph (15-invariant InvariantCheck library v3 + PolyDiff Extended regression). The headline metric is the **"added by AegisGraph"** column: findings present in AegisGraph output AND absent in (codeql ∪ semgrep ∪ mobsf) at the same `(category, location_hash)` coordinate. This is the M14 discovery-delta metric per Phase II plan §5.

## Per-target summary

### Element X Android

- target_id: `elementx_android@91d265e6`
- repo: https://github.com/element-hq/element-x-android
- commit: `91d265e6`

| Tool | Status | Findings | Tool version | Reason |
|---|---|---|---|---|
| codeql | `binary_missing` | 0 | `_n/a_` | codeql CLI not on PATH |
| semgrep | `failed` | 0 | `_n/a_` | source_root_missing: anchor-only source tree absent |
| mobsf | `apk_missing` | 0 | `_n/a_` | no APK available under anchor-only policy |
| aegisgraph | `scaffold_pending` | 0 | `invariants-v3 + polydiff-extended` | AegisGraph invariant + polydiff execution deferred to self-hosted runner (T-M4.1) |

**Added by AegisGraph (this target):** 0

### Signal Android

- target_id: `signal_android@1043851`
- repo: https://github.com/signalapp/Signal-Android
- commit: `1043851`

| Tool | Status | Findings | Tool version | Reason |
|---|---|---|---|---|
| codeql | `binary_missing` | 0 | `_n/a_` | codeql CLI not on PATH |
| semgrep | `failed` | 0 | `_n/a_` | source_root_missing: anchor-only source tree absent |
| mobsf | `apk_missing` | 0 | `_n/a_` | no APK available under anchor-only policy |
| aegisgraph | `scaffold_pending` | 0 | `invariants-v3 + polydiff-extended` | AegisGraph invariant + polydiff execution deferred to self-hosted runner (T-M4.1) |

**Added by AegisGraph (this target):** 0

## Overlap matrix (per-category)

Cells are `(category × tool)`. The 'shared' column lists how many `(category, location_hash)` coordinates have two or more tools reporting at the same spot — these are deduplicated overlaps, NOT independent findings.

## Added by AegisGraph (per-target, per-category)

Counts the `(target, category, location_hash)` coordinates where AegisGraph reports a finding AND none of CodeQL / Semgrep / MobSF report at the same coordinate. This is the discovery-delta column for the M14 demo.

## Constraints and caveats

- **Anchor-only**: target source trees are pinned by commit hash and not redistributed in this research repo. The self-hosted runner clones them at execution time per `extraction/targets/<target>/build_db.sh`.
- **MobSF transparency**: when no APK is available the `mobsf` row reports `apk_missing` and a sibling `MOBSF-LIMITED.md` records the limitation. No fabricated findings.
- **Sanitize-check Rule 7/8/9**: every emitted record passes through `aegisgraph.evidence.finalize_record` (for AG records) or the sanitization projection here (for baseline tools). Source snippets are NEVER carried into the report; only `location_hash` fingerprints are.
