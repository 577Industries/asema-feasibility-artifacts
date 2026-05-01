# ASEMA Feasibility Artifacts

Public reproducibility artifacts for 577 Industries' AegisGraph approach to DARPA ASEMA: Assessing Security of Encrypted Messaging Applications.

This repository is an evaluator-facing evidence layer. It publishes sanitized feasibility artifacts, target manifests, pilot summaries, benchmark seeds, diagrams, citations, schemas, and reproducibility scripts. It does not publish the internal proposal binder, cloned target source trees, raw scanner JSON, proprietary drafts, or exploit material.

## Quick Links

- GitHub Pages: https://577-industries.github.io/asema-feasibility-artifacts/
- Public feasibility study: `artifacts/feasibility/ASEMA_Phase_I_Feasibility_Study_Public.md`
- Public evidence index: `artifacts/evidence_index_public.csv`
- SMABench pilot seed: `artifacts/benchmark/SMABench_pilot_seed_manifest.md`
- Verification script: `scripts/verify_public_package.py`

## Pilot Summary

The pilot uses public source repositories only:

| Target | Repository | Scope |
|---|---|---|
| Signal Android | https://github.com/signalapp/Signal-Android | Public-source static manifest/source-indicator analysis |
| Element X Android | https://github.com/element-hq/element-x-android | Public-source static manifest/source-indicator analysis |

Semgrep informational findings:

| Target | Findings | Exit Code |
|---|---:|---:|
| signal_android | 239 | 0 |
| element_x_android | 162 | 0 |

These are informational static-analysis findings, not vulnerability claims.

## Reproduce

```bash
python3 scripts/verify_public_package.py
python3 scripts/run_public_pilot.py --out /tmp/asema-public-pilot-output
```

## Related 577 Industries Prototype Components

- https://github.com/577-Industries/workflow-dag
- https://github.com/577-Industries/hashchain-audit
- https://github.com/577Industries/tool-guardrails
- https://github.com/577Industries/model-router
- https://github.com/577Industries/agent-memory

## Scope Discipline

- No exploit reproduction.
- No live app or server probing.
- No credentialed app interaction.
- No closed-source reverse engineering.
- No target source redistribution.
- No claim that static indicators are vulnerabilities.

## Licensing

Scripts and schemas are Apache-2.0. Documentation, diagrams, public evidence summaries, and data artifacts are CC-BY-4.0 unless noted otherwise.
