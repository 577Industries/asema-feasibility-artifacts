# AegisGraph v0.3 — ASEMA DP2 Sanitized Public Release

> 577 Industries' AegisGraph platform provides graph-based application-layer assessment evidence for Secure Messaging Applications (SMAs), addressing DARPA topic HR0011SB20254-12 ASEMA.

## What This Release Contains

- **Evidence package** (`evidence/`): the AegisGraph v0.3 evidence JSON (12 evidence_refs, 6 graph_threads, 12 recommendations, 7-tool SOTA matrix, 2 pinned targets), the CETM (Claim → Evidence Traceability Matrix; 69 claims, 0 implicit), and validators.
- **Reproducibility report** (`reports/traceability_matrix.{json,md}`): SPEC.md → DSIP requirement → on-disk evidence → proposal claim crosswalk; 53 rows.
- **Figures** (`figures/F*.png`): 7-figure visual pack (F1 architecture, F2 claim-state machine, F3 evidence flow, F4 graph path, F5 score vector, F6 SOTA matrix, F7 recommendation contract).
- **Sanitized polydiff regression** (`polydiff_regression_report.sanitized.json`): URL-parser disagreement evidence with `tier_p1_status: "pass"` and 8 historical-CVE rediscoveries.
- **Manifest** (`manifest.json`) and **exclusion documentation** (`EXCLUSIONS.md`).
- **License**: Apache-2.0.

## What This Release DOES NOT Contain (see `EXCLUSIONS.md`)

- Crash-triggering input bytes from ReproChain (only hashes + structure).
- Pre-disclosure findings outside disclosure-policy authorization.
- Raw target source code (Signal Android, Element X Android).
- Live target probes / production-app traces.
- Credentials, private paths, customer/partner names.

## Quick Verification

```
git clone <this-repo>
cd <this-repo>/release/v0.3.0
node evidence/validate-evidence.mjs   # safety_scan: passed
node evidence/validate-cetm.mjs evidence/cetm.json   # issues_count: 0
sha256sum -c evidence/checksums.sha256   # all OK
```

## What Reviewers Should Note

- **Honest scope discipline**: every claim in the v0.3 evidence is anchored (A) to a hashed artifact, expected (E) to be produced by Phase II evidence streams, or planned (P) for Phase II execution. NO implicit claims — the validator rejects any.
- **Static reachability ≠ exploitation**: where ReproChain reaches the libwebp CVE-2023-4863 surface in Signal Android and Element X Android, that is reachability evidence, NOT exploitation evidence.
- **PolyDiff parser disagreements ≠ vulnerabilities**: security-relevance is asserted only after the documented classifier rules in favor.
- **Score vectors are assessment-priority**, NOT vulnerability-severity: see `aegisgraph-v0.3-evidence.json#score_model` and master proposal §5.6.

## v0.2 → v0.3 Delta

See `RELEASE_NOTES.md` for the changelog.

## License

Apache-2.0.

## Pointers

- AegisGraph engineering platform (open-source): https://github.com/577Industries/aegisgraph
- DARPA topic: HR0011SB20254-12 (Assessing Security of Encrypted Messaging Applications, ASEMA)
- Master proposal narrative: cited by hash in this release; full text in submission package
