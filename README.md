# ASEMA Feasibility Artifacts

Public reproducibility artifacts for 577 Industries' AegisGraph approach to DARPA ASEMA: Assessing Security of Encrypted Messaging Applications.

This repository is an evaluator-facing evidence layer. It publishes sanitized feasibility artifacts, target manifests, pilot summaries, benchmark seeds, diagrams, citations, schemas, deterministic synthetic traces, graph exports, recommendations, and reproducibility scripts. It does not publish internal proposal binders, cloned target source trees, raw scanner JSON, proprietary drafts, exploit material, or real-app dynamic traces.

## v0.2 Quickstart

```bash
python3 scripts/run_public_demo.py --out out/demo
python3 scripts/verify_public_package.py
```

The demo produces target manifests, a public evidence ledger, graph JSONL, score reports, SMABench synthetic results, a differential report, recommendations, SOTA comparison outputs, a dashboard at `site/public-dashboard/index.html`, checksums, and verification reports.

## Scope Discipline

- No exploit reproduction.
- No live app or server probing.
- No credentialed app interaction.
- No closed-source reverse engineering.
- No target source redistribution.
- Static observations are not vulnerability claims.

## Legacy v0.1 Artifacts

The `artifacts/` directory is retained for compatibility with the v0.1 public package. Canonical v0.2 data lives in `targets/`, `evidence/`, `graphs/`, `smabench/`, `recommendations/`, `sota/`, `site/`, and `checksums/`.
