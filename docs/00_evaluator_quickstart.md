# 00 Evaluator Quickstart — AegisGraph ASEMA D2P2

**Tag:** `v1.0.0-asema-dp2-feasibility` · **License:** Apache-2.0 · **Reviewer reproduction target:** ≤ 5 minutes warm, ≤ 1 hour cold

## 1. Verify the release

```bash
git clone https://github.com/577-Industries/asema-feasibility-artifacts
cd asema-feasibility-artifacts
git checkout v1.0.0-asema-dp2-feasibility
sha256sum -c evidence/checksums.sha256              # all entries OK
node evidence/validate-evidence.mjs                  # safety_scan: passed
node evidence/validate-cetm.mjs evidence/cetm.json   # issues_count: 0, total_claims: 82
```

## 2. Reproduce the engineering platform (full reproduction)

```bash
git clone https://github.com/577Industries/aegisgraph
cd aegisgraph
git checkout v1.0.0-tier3-research                   # tag SHA: d91c1df6e9d6849060388949c6e0202f1aef1e5c
devcontainer up                                       # pinned: Python 3.11.9, Clang 18, JDK 21, CodeQL 2.20.6, Semgrep 1.86.0, Go 1.22.5, Rust 1.79.0, NDK r26d
make tooling-strict
python3 -m pytest -q                                 # expect 1030 passed, 19 skipped
python3 -m aegisgraph.cli validate                   # validate evidence records
python3 -m validator.cli sanitize-check exports/public-sanitized   # exit 0
```

## 3. What the artifacts cover

- `evidence/aegisgraph-v0.3-evidence.json` / `v0.4` / `v1.0` — release scope, score model, 2 pinned targets, 6 graph threads, 12 recommendations, 7-tool SOTA matrix, cross-target candidates (1 validated), m14 demo dryrun summary
- `evidence/cetm.json` — 82-claim CETM (53 A / 8 E / 21 P / 0 forbidden-I)
- `evidence/checksums.sha256` — SHA-256 integrity for every artifact in this release
- `figures/F1–F22` — 22 architecture, lifecycle, evidence-flow, SOTA, and engine-detail diagrams
- `polydiff_regression_report.sanitized.json` / `.v1.0.json` — 8 historical CVE rediscoveries across 6 parser families (v2.0 fact-vector schema envelope)
- `reports/traceability_matrix.{json,md}` — 75-row traceability matrix (66 v0.4 rows + 9 v1.0 engine rows)
- `baseline-tool-delta/` — honest CodeQL/Semgrep/MobSF vs AegisGraph capability comparison with `MOBSF-LIMITED.md` honesty markers
- `EXCLUSIONS.md` — what's intentionally NOT in the release (crash bytes, raw target source, engineering-private artifacts)
- `RELEASE_NOTES.md` — full v0.3 → v0.4 → v1.0 changelog
- `LICENSE` — Apache-2.0
- `manifest.json` — sanitized public-export manifest; `release.version: v1.0`, `release_authorized: true`, `safety_posture: sanitized_candidate`

## 4. What's NOT in this release (by design)

- Crash-triggering input bytes (only SHA-256 hashes + structure references)
- Pre-disclosure findings outside disclosure-policy authorization (disclosure ledger is currently empty pending counsel review T-M1.4 / T-M1.5)
- Raw target source code (Signal Android, Element X Android, matrix-rust-sdk — all public on their own GitHub repos)
- Live target probes or production-app traces
- Engineering-private CodeQL queries + Semgrep rules; SARIF result bodies stay engineering-side
- Embargoed disclosure records (`claim_state == "reviewed_embargoed"`)
- Source snippets longer than 256 chars; attacker URLs / payloads inside cross-target candidates

## 5. For reviewers verifying the ASEMA D2P2 proposal

- **Six-engine ensemble**: PolyDiff Extended, HarnessGen, InvariantCheck, CrossSMA, DynamicProbe (option period), Coordinated Disclosure — see `figures/F15-engine-architecture.png` and `figures/F16-discovery-loop.png`
- **Engine evidence anchored**: all six engines have evidence files in `evidence/aegisgraph-v1.0-evidence.json` and the corresponding CETM `C-ENG-*` / `C-NEW-*` claims
- **CETM claim verification**: every status-A claim has its `evidence_artifact` path resolve on disk; `validate-cetm.mjs` enforces
- **Engineering tip**: `stream/integration` at commit `d91c1df6` (= the v1.0.0-tier3-research tag), 1030 tests passing
- **Cross-target validated cell**: `AG-XSMA-VALIDATED-SIG-GP-001-ELX` is the 1 of 24 cells confirmed `confirmed_reachable`

## 6. Disclosure posture

- Coordinated-disclosure pipeline (Engine 6) is fully scaffolded; ledger is empty pending counsel review (T-M1.4 / T-M1.5)
- Recommended first-disclosure target: libwebp upstream via Chrome CNA (per ADR-0006 Option A)
- 90-day embargo policy (CERT/CC-style); day-7/14/30/60/90 boundary issues auto-fired by `.github/workflows/embargo-tick.yml` in the engineering repo

## 7. Questions / contact

- Engineering issues: https://github.com/577Industries/aegisgraph/issues
- Disclosure policy: see `aegisgraph/disclosure/policy.md` in the engineering repo
- Proposal evaluation: via DARPA SBIR ASEMA topic HR0011SB20254-12
