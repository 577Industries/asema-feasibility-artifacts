# AegisGraph v0.3 Release Notes

**Tag**: v0.3.0-asema-dp2-feasibility
**Date**: 2026-05-08
**License**: Apache-2.0

## v0.2 → v0.3 Delta

### Added

- **ReproChain CVE-2023-4863 evidence**: vendored vulnerable + fixed libwebp commit pins (`7ba44f80...` / `902bc919...` from libwebp v1.3.2), AddressSanitizer + libFuzzer harness sources, 5-node static reachability graphs for Signal Android (MmsAttachment → Glide → BitmapFactory.decodeStream → ImageDecoder → libwebp) and Element X Android (Coil → ImageDecoderDecoder → libwebp). Pre-disclosure simulation framing: AegisGraph would have **prioritized** this surface for fuzzing/audit, NOT discovered the bug.
- **PolyDiff differential parser fuzzing**: 7 parser-wrapper directories (Python urllib + WHATWG-URL Python built; JDK URI, OkHttp, Rust url, Go net/url, libcurl source + Dockerfile + smoke tests shipped — build cleanly in pinned devcontainer). 41 historical regression cases with 13 CVE/disclosure references; 8 historical-CVE rediscoveries via current 2 wrappers; 12+ rediscoveries when the remaining 5 wrappers build in devcontainer. `tier_p1_status: "pass"`.
- **Real CodeQL/Semgrep/MobSF extraction infrastructure**: 8 CodeQL queries, 4 Semgrep rules, AndroidManifest analyzer (XXE-safe via lxml hardening), MobSF Docker integration (offline mode; honest skip statuses). Phase 0 placeholder strings eliminated; test contract forbids regression.
- **SMABench 6 Ring 1 generators**: 10k URLs, 32 QR PNGs, 1k deeplinks, 200 sync envelopes, 16 valid media samples, 60 PQ traces. Byte-deterministic; repeatability hash recorded.
- **Hardened validator**: 12 substantive + 6 structural sanitize-check rules, traceability matrix generator, --non-mutating mode for third-party verification, strict-tooling fail-closed.
- **Fact-vector v2 schema** (45 axes; additive — v1 records continue to validate).
- **7-figure visual pack** in `figures/`.
- **Public-export human gate**: `release_authorized=False` until BOTH `AEGISGRAPH_RELEASE_AUTHORIZED=1` AND `validator/sanitize_check.py` passes.

### Changed

- Master proposal expanded with §4.4 (4-novelty list), §6.6 (ReproChain), §6.7 (PolyDiff), §13 (KSA crosswalk acknowledging PI vulnerability-research gap), §12.1.1 (customer discovery commitment), §12.5 (DARPA insertion targets).
- CETM (Claim → Evidence Traceability Matrix) now governs every proposal claim with status A/E/P; no implicit claims allowed.

### Fixed

- Compliance Matrix renumbering aligned to actual master §1–§17 structure.
- Submission binder stale dual-master resolved.
- Public Link Register format updated to anchor-by-hash.

### Known limitations (documented honestly)

- Host environments without Clang 18 / CodeQL CLI 2.20.6 / Java 21 / Docker / Go 1.22 / Rust 1.79 will report `build_status="blocked_pending_toolchain"` for ReproChain and limited extraction coverage. The pinned devcontainer (per `01_TIER3_RESEARCH/.../devcontainer/Dockerfile`) ships with all required tools.
- 5 of 7 PolyDiff parser wrappers (Java/Kotlin/Rust/Go/C) require devcontainer compilation; current host has 2 of 7 built.

### Compliance discipline

- No live target probing.
- No raw target source redistribution.
- No crash-inducing input bytes.
- No credentials / no PII.
- Static observations bounded as reachability evidence, NOT vulnerability claims.

## License

Apache-2.0.
