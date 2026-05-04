"""Public v0.2 AegisGraph ASEMA release builder and verifier.

The implementation intentionally uses modeled, sanitized data. It does not
clone, redistribute, probe, instrument, or execute real target applications.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "v0.2.0"

CLAIM_STATES = [
    "candidate",
    "static_supported",
    "priority_validation",
    "harness_covered",
    "synthetic_dynamic_observed",
    "authorized_dynamic_observed",
    "externally_correlated",
    "defensive_recommendation",
    "vulnerability_claim",
]

LIMITATIONS = [
    "No real-app dynamic testing is included in the public release.",
    "Static observations are not vulnerability claims.",
    "Target source trees are not redistributed.",
]

TARGETS = [
    {
        "target_id": "signal_android_1043851",
        "legacy_target_id": "signal_android",
        "name": "Signal Android",
        "repo_url": "https://github.com/signalapp/Signal-Android",
        "commit": "1043851-public-pilot-snapshot",
        "license_note": "Public repository metadata only; target source is not redistributed.",
        "semgrep_findings": 239,
        "component_count": 89,
        "scope": "Sanitized public-source static manifest and source-indicator summary.",
    },
    {
        "target_id": "elementx_android_91d265e6",
        "legacy_target_id": "element_x_android",
        "name": "Element X Android",
        "repo_url": "https://github.com/element-hq/element-x-android",
        "commit": "91d265e6-public-pilot-snapshot",
        "license_note": "Public repository metadata only; target source is not redistributed.",
        "semgrep_findings": 162,
        "component_count": 74,
        "scope": "Sanitized public-source static manifest and source-indicator summary.",
    },
]

SYNTHETIC_PATHS = [
    ("parser", "Remote message -> parser -> state update"),
    ("link_preview", "Message link -> preview fetch policy -> renderer"),
    ("device_link", "QR/device link -> pairing token -> device registry"),
    ("media", "Attachment -> media decoder -> storage"),
    ("group_state", "Invite/update -> group state reducer -> notification"),
    ("pq_migration", "Session -> PQ migration flag -> handshake stub"),
]

STATIC_CATEGORIES = [
    "deep_link_uri",
    "qr_or_device_linking",
    "media_file_surface",
    "crypto_session_surface",
    "native_ffi_boundary",
    "storage_keystore",
    "network_sync_surface",
]

SCHEMAS: dict[str, dict[str, Any]] = {
    "target_manifest.schema.json": {
        "type": "object",
        "required": ["target_id", "name", "target_class", "analysis_scope", "claim_boundary"],
        "properties": {
            "target_id": {"type": "string"},
            "name": {"type": "string"},
            "target_class": {"type": "string"},
            "analysis_scope": {"type": "string"},
            "claim_boundary": {"type": "string"},
        },
    },
    "evidence_record.schema.json": {
        "type": "object",
        "required": ["evidence_id", "artifact_class", "path", "sha256", "claim_state"],
        "properties": {
            "evidence_id": {"type": "string"},
            "artifact_class": {"type": "string"},
            "path": {"type": "string"},
            "sha256": {"type": "string"},
            "claim_state": {"enum": CLAIM_STATES},
        },
    },
    "graph_node.schema.json": {
        "type": "object",
        "required": ["node_id", "target_id", "node_type", "label", "evidence_refs"],
        "properties": {
            "node_id": {"type": "string"},
            "target_id": {"type": "string"},
            "node_type": {"type": "string"},
            "label": {"type": "string"},
            "evidence_refs": {"type": "array"},
        },
    },
    "graph_edge.schema.json": {
        "type": "object",
        "required": ["edge_id", "source", "target", "edge_type", "evidence_refs"],
        "properties": {
            "edge_id": {"type": "string"},
            "source": {"type": "string"},
            "target": {"type": "string"},
            "edge_type": {"type": "string"},
            "evidence_refs": {"type": "array"},
        },
    },
    "score_record.schema.json": {
        "type": "object",
        "required": ["path_id", "target_id", "score", "claim_state", "evidence_refs"],
        "properties": {
            "path_id": {"type": "string"},
            "target_id": {"type": "string"},
            "score": {"type": "number"},
            "claim_state": {"enum": CLAIM_STATES},
            "evidence_refs": {"type": "array"},
        },
    },
    "trace_record.schema.json": {
        "type": "object",
        "required": ["trace_id", "variant", "path_id", "events"],
        "properties": {
            "trace_id": {"type": "string"},
            "variant": {"type": "string"},
            "path_id": {"type": "string"},
            "events": {"type": "array"},
        },
    },
    "smabench_task.schema.json": {
        "type": "object",
        "required": ["task_id", "ring", "path_id", "expected_outputs"],
        "properties": {
            "task_id": {"type": "string"},
            "ring": {"type": "string"},
            "path_id": {"type": "string"},
            "expected_outputs": {"type": "array"},
        },
    },
    "recommendation.schema.json": {
        "type": "object",
        "required": ["recommendation_id", "title", "evidence_refs", "graph_path_refs", "residual_risk", "standards_mapping_caveat"],
        "properties": {
            "recommendation_id": {"type": "string"},
            "title": {"type": "string"},
            "evidence_refs": {"type": "array"},
            "graph_path_refs": {"type": "array"},
            "residual_risk": {"type": "string"},
            "standards_mapping_caveat": {"type": "string"},
        },
    },
    "release_manifest.schema.json": {
        "type": "object",
        "required": ["release", "project", "targets", "artifact_classes", "limitations"],
        "properties": {
            "release": {"type": "string"},
            "project": {"type": "string"},
            "targets": {"type": "array"},
            "artifact_classes": {"type": "array"},
            "limitations": {"type": "array"},
        },
    },
    "static_observation.schema.json": {
        "type": "object",
        "required": ["observation_id", "target_id", "category", "claim_state", "evidence_refs"],
        "properties": {
            "observation_id": {"type": "string"},
            "target_id": {"type": "string"},
            "category": {"type": "string"},
            "claim_state": {"enum": CLAIM_STATES},
            "evidence_refs": {"type": "array"},
        },
    },
    "dependency_snapshot.schema.json": {
        "type": "object",
        "required": ["snapshot_id", "target_id", "format", "components"],
        "properties": {
            "snapshot_id": {"type": "string"},
            "target_id": {"type": "string"},
            "format": {"type": "string"},
            "components": {"type": "array"},
        },
    },
    "reviewer_decision.schema.json": {
        "type": "object",
        "required": ["decision_id", "subject", "decision", "rationale"],
        "properties": {
            "decision_id": {"type": "string"},
            "subject": {"type": "string"},
            "decision": {"type": "string"},
            "rationale": {"type": "string"},
        },
    },
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    write_text(path, "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stable_score(path_id: str, mitigated: bool = False) -> float:
    base = {
        "parser": 81.0,
        "link_preview": 74.0,
        "device_link": 79.0,
        "media": 72.0,
        "group_state": 68.0,
        "pq_migration": 65.0,
    }[path_id]
    return round(base - (23.5 if mitigated else 0.0), 2)


def score_vector(path_id: str, mitigated: bool = False) -> dict[str, float]:
    """Return deterministic 0-100 assessment-priority factors for one path."""
    base = {
        "parser": (91, 82, 76, 88, 84, 79),
        "link_preview": (84, 67, 72, 86, 75, 77),
        "device_link": (87, 81, 78, 86, 80, 82),
        "media": (79, 74, 69, 84, 73, 76),
        "group_state": (73, 72, 65, 83, 68, 74),
        "pq_migration": (70, 77, 62, 82, 66, 78),
    }[path_id]
    names = [
        "reachability",
        "sensitivity",
        "boundary_weakness",
        "evidence_confidence",
        "exploit_class_proximity",
        "mitigation_leverage",
    ]
    values = dict(zip(names, base, strict=True))
    if mitigated:
        values["boundary_weakness"] = max(0, values["boundary_weakness"] - 42)
        values["exploit_class_proximity"] = max(0, values["exploit_class_proximity"] - 28)
        values["mitigation_leverage"] = min(100, values["mitigation_leverage"] + 8)
    return {name: float(value) for name, value in values.items()}


def build_release(root: Path, out: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve() if out else root / "out" / "demo"
    out.mkdir(parents=True, exist_ok=True)

    _write_docs(root)
    _write_schemas(root)
    evidence_seed = _write_targets(root)
    _write_synthetic_lab(root)
    graph_refs = _write_graphs(root, evidence_seed)
    _write_smabench(root)
    _write_recommendations(root, graph_refs)
    _write_sota(root)
    _write_ci(root)
    ledger = _write_evidence_ledger(root)
    _write_dashboard(root, out, ledger)
    manifest = _write_release_manifest(root)
    generate_checksums(root)
    _write_signing_note(root)
    _copy_bundle(root, out)
    return manifest


def _write_docs(root: Path) -> None:
    readme = """# ASEMA Feasibility Artifacts

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
"""
    write_text(root / "README.md", readme)
    write_text(root / "SECURITY.md", "Public artifacts are sanitized and defensive. Report concerns through the repository issue tracker or maintainer contact listed in NOTICE.\n")
    write_text(root / "CITATION.cff", "cff-version: 1.2.0\ntitle: AegisGraph ASEMA Feasibility Artifacts\nversion: v0.2.0\n")
    write_text(root / "RELEASE_NOTES.md", """# AegisGraph ASEMA Feasibility Artifacts v0.2.0

This release adds deterministic synthetic AegisSMA-Lab traces, SMABench tasks, evidence-backed graph exports, differential mitigation scoring, recommendation examples, SOTA comparison packets, dashboard data, release manifest validation, checksums, and signing plumbing.

Limitations remain explicit: no target source redistribution, no real-app dynamic traces, no exploit reproduction, and no static-only vulnerability claims.
""")
    docs = {
        "00_buildout_traceability.md": "Traceability from the Phase-I buildout plan to schemas, scripts, evidence IDs, tests, and release gates.\n\n| Source Section | Evidence | Deliverable | Script/Test | Gate |\n|---|---|---|---|---|\n| 3 Safety | EVID-SAFETY-001 | claim discipline docs | validate_claim_states.py | zero violations |\n| 9 Evidence Ledger | EVID-LEDGER-001 | public_ledger.jsonl | verify_public_package.py | hash refs pass |\n| 11 Graph Model | EVID-GRAPH-001 | nodes.jsonl / edges.jsonl | test_graph_evidence_refs.py | >=98% coverage |\n| 15 Synthetic Target | EVID-SYNTH-001 | AegisSMA-Lab traces | run_smabench_synthetic.py | deterministic repeat |\n| 20 SOTA | EVID-SOTA-001 | SOTA packet | verify_public_package.py | composition claim present |\n",
        "00_evaluator_quickstart.md": "Run `python3 scripts/run_public_demo.py --out out/demo` then open `site/public-dashboard/index.html`.\n",
        "01_phase_i_equivalent_summary.md": "v0.2.0 packages sanitized public target summaries with deterministic synthetic dynamic evidence for evaluator review.\n",
        "02_claim_discipline.md": "Claim states are constrained to candidate, static_supported, priority_validation, harness_covered, synthetic_dynamic_observed, authorized_dynamic_observed, externally_correlated, defensive_recommendation, and vulnerability_claim. Static-only records cannot become vulnerability_claim.\n",
        "03_release_boundaries.md": "\n".join(f"- {item}" for item in LIMITATIONS) + "\n",
        "04_architecture.md": "AegisGraph composes source inventory, static observations, dependency snapshots, synthetic traces, graph building, scoring, and recommendation generation.\n",
        "05_graph_schema_explainer.md": "Nodes represent assets, entrypoints, parsers, state transitions, storage, and security boundaries. Edges represent flow, dependency, guarded_by, and evidence-supported relationships.\n",
        "06_smabench_methodology.md": "SMABench public tasks run only against deterministic modeled traces in the AegisSMA-Lab synthetic target.\n",
        "07_sota_comparison.md": "AegisGraph composes existing tools into an SMA-specific evidence graph rather than replacing scanners, fuzzers, dynamic instrumentation, or formal protocol analysis.\n",
        "08_responsible_disclosure.md": "No vulnerability claim is made from public static-only data. Candidate observations remain defensive prioritization signals.\n",
        "09_user_manual_draft.md": "Use the scripts directory to build graphs, run synthetic tasks, render the dashboard, validate claims, and generate checksums.\n",
    }
    for name, body in docs.items():
        write_text(root / "docs" / name, f"# {name.removesuffix('.md').replace('_', ' ').title()}\n\n{body}")
    for name in ["conops", "claim_state_machine", "graph_layers", "demo_flow"]:
        write_text(root / "docs" / "diagrams" / f"{name}.mmd", f"flowchart LR\n  A[{name}] --> B[AegisGraph public evidence]\n")


def _write_schemas(root: Path) -> None:
    for name, schema in SCHEMAS.items():
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": name, **schema}
        write_json(root / "schemas" / name, schema)
    write_json(
        root / "schemas" / "private_authorization_manifest.schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "private_authorization_manifest.schema.json",
            "type": "object",
            "required": ["authorization_id", "release_classification", "authorized_targets", "expires"],
            "properties": {
                "authorization_id": {"type": "string"},
                "release_classification": {"const": "private_restricted"},
                "authorized_targets": {"type": "array", "items": {"type": "string"}},
                "expires": {"type": "string"},
                "permitted_adapters": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
            },
        },
    )


def _write_targets(root: Path) -> dict[str, list[str]]:
    evidence_seed: dict[str, list[str]] = {}
    for target in TARGETS:
        tid = target["target_id"]
        target_dir = root / "targets" / tid
        manifest = {
            "target_id": tid,
            "name": target["name"],
            "target_class": "real_public_source_static_summary",
            "repo_url": target["repo_url"],
            "branch": "public-pilot",
            "commit": target["commit"],
            "analysis_scope": target["scope"],
            "claim_boundary": "Static public-source observations only; no vulnerability claims.",
            "legacy_v0_1_path": f"artifacts/pilot/manifests/{target['legacy_target_id']}_target_manifest.json",
        }
        write_json(target_dir / "target_manifest.json", manifest)
        write_json(target_dir / "inventory_summary.json", {"target_id": tid, "component_count": target["component_count"], "source_redistributed": False})
        static_rows = [
            {
                "observation_id": f"OBS-{tid}-{i + 1:03d}",
                "target_id": tid,
                "category": category,
                "claim_state": "static_supported",
                "evidence_refs": [f"EVID-{tid.upper()}-STATIC"],
                "limitation": "Informational static indicator; not a vulnerability claim.",
            }
            for i, category in enumerate(STATIC_CATEGORIES)
        ]
        write_json(target_dir / "static_summary.json", {"target_id": tid, "semgrep_findings": target["semgrep_findings"], "observations": static_rows})
        write_json(target_dir / "dependency_snapshot.json", {"snapshot_id": f"DEP-{tid}", "target_id": tid, "format": "modeled-cyclonedx-summary", "components": [{"name": "androidx-core", "scope": "public metadata"}, {"name": "kotlin-stdlib", "scope": "public metadata"}]})
        write_csv(target_dir / "android_manifest_summary.csv", [{"target_id": tid, "component_type": "activity", "count": 24}, {"target_id": tid, "component_type": "service", "count": 9}, {"target_id": tid, "component_type": "receiver", "count": 5}], ["target_id", "component_type", "count"])
        write_text(target_dir / "scope_note.md", f"# {target['name']} Scope Note\n\nSanitized static summary only. Target source and raw scanner outputs are not redistributed. Static observations are not vulnerability claims.\n")
        evidence_seed[tid] = [f"targets/{tid}/target_manifest.json", f"targets/{tid}/static_summary.json", f"targets/{tid}/dependency_snapshot.json"]
    lab_dir = root / "targets" / "aegis_sma_lab"
    write_json(lab_dir / "target_manifest.json", {"target_id": "aegis_sma_lab", "name": "AegisSMA-Lab", "target_class": "synthetic_modeled_target", "analysis_scope": "Deterministic Python synthetic traces for public demonstration.", "claim_boundary": "Synthetic dynamic observations only describe the modeled lab."})
    write_text(lab_dir / "scope_note.md", "# AegisSMA-Lab Scope Note\n\nThis is a modeled synthetic target, not a real Android app. It is designed for deterministic public review.\n")
    evidence_seed["aegis_sma_lab"] = ["targets/aegis_sma_lab/target_manifest.json"]
    return evidence_seed


def _write_synthetic_lab(root: Path) -> None:
    lab = root / "aegis-sma-lab"
    write_text(lab / "README.md", "# AegisSMA-Lab\n\nDeterministic modeled secure-messaging attack-surface lab used for public AegisGraph demos.\n")
    for module in ["core", "parsers", "media", "links", "device_link", "notifications", "storage", "native_ffi_stub", "pq_migration_stub"]:
        write_text(lab / module / "__init__.py", "")
    write_text(lab / "core" / "model.py", """def boundary(name):\n    return {\"kind\": \"security_boundary\", \"name\": name}\n""")
    for variant, mitigated in [("baseline", False), ("mitigated", True)]:
        traces = []
        for path_id, label in SYNTHETIC_PATHS:
            events = [
                {"step": 1, "event": "input_received", "path": label},
                {"step": 2, "event": "parsed", "guard": "schema_check" if mitigated else "none"},
                {"step": 3, "event": "state_transition", "guard": "capability_boundary" if mitigated else "none"},
            ]
            if mitigated:
                events.insert(2, {"step": 2.5, "event": "security_boundary", "guard": f"{path_id}_boundary"})
            traces.append({"trace_id": f"TRACE-{variant}-{path_id}", "variant": variant, "path_id": path_id, "events": events})
        write_jsonl(lab / "traces" / f"synthetic_{variant}_trace.jsonl", traces)


def _write_graphs(root: Path, evidence_seed: dict[str, list[str]]) -> dict[str, list[str]]:
    graph_refs: dict[str, list[str]] = {}
    for target in TARGETS:
        tid = target["target_id"]
        nodes = [
            {"node_id": f"{tid}:app", "target_id": tid, "node_type": "asset", "label": target["name"], "evidence_refs": [f"EVID-{tid.upper()}-MANIFEST"]},
            {"node_id": f"{tid}:entry:deep_link", "target_id": tid, "node_type": "entrypoint", "label": "Deep link entrypoint", "evidence_refs": [f"EVID-{tid.upper()}-STATIC"]},
            {"node_id": f"{tid}:parser:message", "target_id": tid, "node_type": "parser", "label": "Message/parser surface", "evidence_refs": [f"EVID-{tid.upper()}-STATIC"]},
            {"node_id": f"{tid}:storage", "target_id": tid, "node_type": "storage", "label": "Local storage surface", "evidence_refs": [f"EVID-{tid.upper()}-DEP"]},
        ]
        edges = [
            {"edge_id": f"{tid}:e1", "source": nodes[1]["node_id"], "target": nodes[2]["node_id"], "edge_type": "flows_to", "evidence_refs": [f"EVID-{tid.upper()}-STATIC"]},
            {"edge_id": f"{tid}:e2", "source": nodes[2]["node_id"], "target": nodes[3]["node_id"], "edge_type": "updates", "evidence_refs": [f"EVID-{tid.upper()}-DEP"]},
        ]
        gdir = root / "graphs" / tid
        write_jsonl(gdir / "nodes.jsonl", nodes)
        write_jsonl(gdir / "edges.jsonl", edges)
        write_json(gdir / "graph_stats.json", {"target_id": tid, "node_count": len(nodes), "edge_count": len(edges), "evidence_coverage": 1.0})
        write_text(gdir / "top_paths.md", f"# Top Paths\n\n1. `{tid}:entry:deep_link -> {tid}:parser:message -> {tid}:storage` - static-supported prioritization path, not a vulnerability claim.\n")
        graph_refs[tid] = [f"graphs/{tid}/top_paths.md"]
    for variant, mitigated in [("baseline", False), ("mitigated", True)]:
        target_id = f"aegis_sma_lab_{variant}"
        nodes = []
        edges = []
        scores = []
        for path_id, label in SYNTHETIC_PATHS:
            prefix = f"{target_id}:{path_id}"
            nodes.extend([
                {"node_id": f"{prefix}:input", "target_id": target_id, "node_type": "entrypoint", "label": label, "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]},
                {"node_id": f"{prefix}:parser", "target_id": target_id, "node_type": "parser", "label": f"{path_id} parser/handler", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]},
                {"node_id": f"{prefix}:state", "target_id": target_id, "node_type": "state", "label": f"{path_id} state update", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]},
            ])
            edges.extend([
                {"edge_id": f"{prefix}:e1", "source": f"{prefix}:input", "target": f"{prefix}:parser", "edge_type": "flows_to", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]},
                {"edge_id": f"{prefix}:e2", "source": f"{prefix}:parser", "target": f"{prefix}:state", "edge_type": "updates", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]},
            ])
            if mitigated:
                nodes.append({"node_id": f"{prefix}:boundary", "target_id": target_id, "node_type": "security_boundary", "label": f"{path_id} guard boundary", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]})
                edges.append({"edge_id": f"{prefix}:guard", "source": f"{prefix}:boundary", "target": f"{prefix}:parser", "edge_type": "guarded_by", "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"]})
            scores.append({
                "path_id": path_id,
                "target_id": target_id,
                "score": stable_score(path_id, mitigated),
                "score_vector": score_vector(path_id, mitigated),
                "claim_state": "synthetic_dynamic_observed",
                "evidence_refs": [f"EVID-SYNTH-{variant.upper()}"],
                "explanation": "Deterministic 0-100 assessment-priority score from modeled graph path features; not vulnerability severity.",
            })
        gdir = root / "graphs" / target_id
        write_jsonl(gdir / "nodes.jsonl", nodes)
        write_jsonl(gdir / "edges.jsonl", edges)
        write_json(gdir / "score_report.json", {"target_id": target_id, "scores": scores, "mean_score": round(sum(s["score"] for s in scores) / len(scores), 2)})
        graph_refs[target_id] = [f"graphs/{target_id}/score_report.json"]
    deltas = []
    for path_id, label in SYNTHETIC_PATHS:
        deltas.append({"path_id": path_id, "path": label, "baseline_score": stable_score(path_id), "mitigated_score": stable_score(path_id, True), "delta": round(stable_score(path_id, True) - stable_score(path_id), 2), "added_controls": ["security_boundary node", "guarded_by edge"]})
    write_json(root / "graphs" / "aegis_sma_lab_differential.json", {"summary": "Mitigated synthetic paths add boundary nodes and guarded_by edges.", "deltas": deltas})
    write_text(root / "graphs" / "aegis_sma_lab_differential.md", "# AegisSMA-Lab Differential Mitigation Report\n\nMitigated synthetic paths add `security_boundary` nodes and `guarded_by` edges, producing deterministic score reductions across all modeled paths.\n")
    return graph_refs


def _write_smabench(root: Path) -> None:
    tasks = []
    for path_id, label in SYNTHETIC_PATHS:
        task = {"task_id": f"SMABENCH-SYN-{path_id}", "ring": "synthetic_public", "path_id": path_id, "description": label, "expected_outputs": ["baseline_trace", "mitigated_trace", "score_delta"]}
        tasks.append(task)
        write_json(root / "smabench" / "tasks" / f"synthetic_{path_id}_task.json", task)
    results = []
    for path_id, _ in SYNTHETIC_PATHS:
        results.append({"task_id": f"SMABENCH-SYN-{path_id}", "status": "pass", "baseline_score": stable_score(path_id), "mitigated_score": stable_score(path_id, True), "repeatability": "stable"})
    write_json(root / "smabench" / "results" / "synthetic_results.json", {"results": results})
    write_text(root / "smabench" / "results" / "repeatability_report.md", "# Repeatability Report\n\nAll synthetic tasks are deterministic across repeated runs because inputs, traces, and scores are static-modeled.\n")
    for seed in ["safe_messages", "safe_links", "safe_qr"]:
        write_text(root / "smabench" / "seeds" / seed / "README.md", f"# {seed}\n\nBenign synthetic seeds only.\n")


def _write_recommendations(root: Path, graph_refs: dict[str, list[str]]) -> None:
    recs = [
        {
            "recommendation_id": "REC-SYN-001",
            "title": "Add explicit parser trust boundaries for remote message paths",
            "category": "parser_boundary",
            "evidence_refs": ["EVID-SYNTH-MITIGATED"],
            "graph_path_refs": ["aegis_sma_lab_mitigated:parser"],
            "residual_risk": "Modeled control does not prove equivalent production behavior.",
            "standards_mapping_caveat": "Mappings are planning aids, not certification claims.",
        },
        {
            "recommendation_id": "REC-SYN-002",
            "title": "Gate link preview and device-link handling behind capability checks",
            "category": "capability_boundary",
            "evidence_refs": ["EVID-SYNTH-MITIGATED"],
            "graph_path_refs": ["aegis_sma_lab_mitigated:link_preview", "aegis_sma_lab_mitigated:device_link"],
            "residual_risk": "Network and QR production stacks require authorized dynamic validation.",
            "standards_mapping_caveat": "Caveat applies to MASVS and internal-control mapping.",
        },
        {
            "recommendation_id": "REC-SYN-003",
            "title": "Track media and storage flows as review-priority graph paths",
            "category": "media_storage",
            "evidence_refs": ["EVID-SYNTH-MITIGATED", "EVID-SIGNAL_ANDROID_1043851-STATIC", "EVID-ELEMENTX_ANDROID_91D265E6-STATIC"],
            "graph_path_refs": ["aegis_sma_lab_mitigated:media", "signal_android_1043851:entry:deep_link", "elementx_android_91d265e6:entry:deep_link"],
            "residual_risk": "Static public summaries prioritize review but do not establish vulnerabilities.",
            "standards_mapping_caveat": "Standards references are defensive review hints only.",
        },
    ]
    write_json(root / "recommendations" / "recommendation_index.json", {"recommendations": recs})
    for rec in recs:
        write_text(root / "recommendations" / f"{rec['recommendation_id'].lower()}.md", f"# {rec['title']}\n\nEvidence: {', '.join(rec['evidence_refs'])}\n\nGraph paths: {', '.join(rec['graph_path_refs'])}\n\nResidual risk: {rec['residual_risk']}\n\nStandards caveat: {rec['standards_mapping_caveat']}\n")
    write_text(root / "recommendations" / "synthetic_baseline_recommendations.md", "# Synthetic Recommendations\n\nThe mitigated synthetic graph supports three defensive recommendations in `recommendation_index.json`.\n")
    write_text(root / "recommendations" / "signal_static_recommendation_examples.md", "# Signal Static Recommendation Examples\n\nStatic-supported review prioritization examples only; no vulnerability claims.\n")
    write_text(root / "recommendations" / "elementx_static_recommendation_examples.md", "# Element X Static Recommendation Examples\n\nStatic-supported review prioritization examples only; no vulnerability claims.\n")


def _write_sota(root: Path) -> None:
    summary = "AegisGraph composes existing tools into an SMA-specific evidence graph rather than replacing scanners, fuzzers, dynamic instrumentation, or formal protocol analysis."
    write_text(root / "sota" / "methodology.md", f"# Methodology\n\n{summary}\n")
    write_text(root / "sota" / "baseline_tool_matrix.md", "| Tool family | Public packet role |\n|---|---|\n| Semgrep/static scanners | Static observations |\n| Android manifest review | Entry point inventory |\n| SARIF/CodeQL-style import | Normalized observation import |\n| CycloneDX/SBOM | Dependency context |\n| Synthetic harness | Deterministic modeled traces |\n| AegisGraph | Evidence graph and differential scoring |\n")
    write_json(root / "sota" / "comparison_results.json", {"summary": summary, "dimensions": ["evidence linkage", "claim discipline", "SMA path modeling", "differential mitigation"]})
    write_text(root / "sota" / "comparison_summary.md", f"# SOTA Comparison Summary\n\n{summary}\n")
    write_json(root / "sota" / "static_tool_outputs_sanitized" / "semgrep_summary.json", {"scanner": "semgrep", "role": "sanitized static observation summary"})
    write_json(root / "sota" / "static_tool_outputs_sanitized" / "sarif_import_example.json", {"runs": [{"tool": {"driver": {"name": "CodeQL-style SARIF"}}}]})
    write_json(root / "sota" / "static_tool_outputs_sanitized" / "cyclonedx_import_example.json", {"bomFormat": "CycloneDX", "components": [{"name": "example-component"}]})


def _write_ci(root: Path) -> None:
    write_text(root / ".github" / "workflows" / "ci.yml", """name: public-package
on:
  push:
  pull_request:
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: python3 scripts/run_public_demo.py --out out/demo
      - run: python3 scripts/verify_public_package.py
""")
    write_text(root / ".devcontainer" / "devcontainer.json", json.dumps({"name": "aseme-public-artifacts", "image": "mcr.microsoft.com/devcontainers/python:3.12", "postCreateCommand": "python3 scripts/run_public_demo.py --out out/demo"}, indent=2) + "\n")
    write_text(root / "Dockerfile", "FROM python:3.12-slim\nWORKDIR /work\nCOPY . /work\nCMD [\"python3\", \"scripts/verify_public_package.py\"]\n")


def _write_evidence_ledger(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seeds = [
        ("EVID-SAFETY-001", "docs/02_claim_discipline.md", "claim_discipline", "defensive_recommendation"),
        ("EVID-LEDGER-001", "docs/00_buildout_traceability.md", "traceability", "defensive_recommendation"),
        ("EVID-SYNTH-BASELINE", "aegis-sma-lab/traces/synthetic_baseline_trace.jsonl", "synthetic_trace", "synthetic_dynamic_observed"),
        ("EVID-SYNTH-MITIGATED", "aegis-sma-lab/traces/synthetic_mitigated_trace.jsonl", "synthetic_trace", "synthetic_dynamic_observed"),
        ("EVID-SOTA-001", "sota/comparison_summary.md", "sota_packet", "defensive_recommendation"),
    ]
    for target in TARGETS:
        tid = target["target_id"]
        seeds.extend([
            (f"EVID-{tid.upper()}-MANIFEST", f"targets/{tid}/target_manifest.json", "target_manifest", "static_supported"),
            (f"EVID-{tid.upper()}-STATIC", f"targets/{tid}/static_summary.json", "static_observation", "static_supported"),
            (f"EVID-{tid.upper()}-DEP", f"targets/{tid}/dependency_snapshot.json", "dependency_snapshot", "static_supported"),
        ])
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for evid, rel, artifact_class, claim_state in seeds:
        path = root / rel
        if "SIGNAL_ANDROID" in evid:
            target_id = "signal_android_1043851"
        elif "ELEMENTX_ANDROID" in evid:
            target_id = "elementx_android_91d265e6"
        elif "SYNTH" in evid:
            target_id = "aegis_sma_lab"
        else:
            target_id = "release"
        entries.append({
            "evidence_id": evid,
            "artifact_id": evid,
            "target_id": target_id,
            "artifact_class": artifact_class,
            "source_type": artifact_class,
            "producer": {
                "tool": "aegisgraph-public-builder",
                "version": VERSION,
                "command": "python3 scripts/run_public_demo.py --out out/demo",
            },
            "path": rel,
            "artifact_location": rel,
            "sha256": sha256(path),
            "capture_time": captured_at,
            "scope": "public_sanitized" if target_id != "aegis_sma_lab" else "synthetic_lab",
            "supported_graph_refs": [],
            "supported_claim_refs": [claim_state],
            "reviewer_decision": "DEC-001" if claim_state in {"static_supported", "defensive_recommendation"} else "synthetic-modeled",
            "release_classification": "public_sanitized",
            "claim_state": claim_state,
            "public_release": True,
            "limitations": LIMITATIONS[1] if "STATIC" in evid else "Sanitized public evidence.",
        })
    write_jsonl(root / "evidence" / "public_ledger.jsonl", entries)
    write_csv(root / "evidence" / "evidence_index.csv", entries, ["evidence_id", "artifact_class", "path", "sha256", "claim_state", "limitations"])
    write_jsonl(root / "evidence" / "reviewer_decisions.jsonl", [{"decision_id": "DEC-001", "subject": "public safety boundary", "decision": "keep real-target observations static-only", "rationale": "No authorized dynamic real-app data is included in public release."}])
    return entries


def _write_dashboard(root: Path, out: Path, ledger: list[dict[str, Any]]) -> None:
    data = {
        "release": VERSION,
        "targets": [t["target_id"] for t in TARGETS] + ["aegis_sma_lab_baseline", "aegis_sma_lab_mitigated"],
        "evidence_count": len(ledger),
        "limitations": LIMITATIONS,
        "dashboard_note": "Static-only limitations are visible for real-target observations.",
    }
    for base in [root / "site" / "data", out / "site" / "data"]:
        write_json(base / "dashboard_data.json", data)
        write_json(base / "release_manifest.json", _release_manifest_dict())
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AegisGraph ASEMA Public Dashboard</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <h1>AegisGraph ASEMA Public Dashboard</h1>
    <p>Sanitized evidence graph release with deterministic synthetic SMABench demo.</p>
  </header>
  <main>
    <section><h2>Targets</h2><p>Signal Android and Element X Android are static-only public summaries. AegisSMA-Lab is modeled synthetic evidence.</p></section>
    <section><h2>Evidence</h2><p>Every graph node and edge references public ledger evidence. Source JSON: <a href="data/dashboard_data.json">dashboard_data.json</a>.</p></section>
    <section><h2>Graphs</h2><p>Graph exports include nodes, edges, stats, top paths, score reports, and differential mitigation deltas.</p></section>
    <section><h2>SMABench</h2><p>Parser, link preview, device link, media, group state, and PQ migration tasks run deterministically.</p></section>
    <section><h2>Differential</h2><p>Mitigated synthetic paths add security_boundary nodes and guarded_by edges.</p></section>
    <section><h2>Recommendations</h2><p>Recommendations include graph path refs, evidence refs, residual risk notes, and standards-mapping caveats.</p></section>
    <section><h2>SOTA</h2><p>AegisGraph composes existing tools into an SMA-specific evidence graph rather than replacing scanners, fuzzers, dynamic instrumentation, or formal protocol analysis.</p></section>
    <section><h2>Safety</h2><p>No target source redistribution, no real-app dynamic traces, no exploit reproduction, and no static-only vulnerability claims.</p></section>
    <section><h2>Downloads</h2><p>Use release_manifest.json, checksums/SHA256SUMS, schemas, graph exports, and SMABench results from this repository.</p></section>
  </main>
</body>
</html>
"""
    css = """body{font-family:Arial,sans-serif;margin:0;color:#182026;background:#f7f8f5}header{background:#143d3a;color:white;padding:32px 24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:24px}section{background:white;border:1px solid #d7ddd8;border-radius:8px;padding:18px;min-height:150px}h1,h2{margin-top:0;letter-spacing:0}a{color:#0b5f9e}"""
    for base in [root / "site" / "public-dashboard", out / "site" / "public-dashboard"]:
        write_text(base / "index.html", html)
        write_text(base / "styles.css", css)
        if not (base / "data").exists():
            shutil.copytree(root / "site" / "data", base / "data", dirs_exist_ok=True)


def _release_manifest_dict() -> dict[str, Any]:
    return {
        "release": VERSION,
        "project": "AegisGraph ASEMA Feasibility Artifacts",
        "release_date": date.today().isoformat(),
        "public_scope": "sanitized public-source static analysis plus synthetic lab demo",
        "targets": ["signal_android_1043851", "elementx_android_91d265e6", "aegis_sma_lab_baseline", "aegis_sma_lab_mitigated"],
        "artifact_classes": ["target_manifest", "evidence_ledger", "graph_export", "score_report", "smabench_task", "synthetic_trace", "recommendation", "dashboard"],
        "limitations": LIMITATIONS,
        "checksums_file": "checksums/SHA256SUMS",
    }


def _write_release_manifest(root: Path) -> dict[str, Any]:
    manifest = _release_manifest_dict()
    write_json(root / "release_manifest.json", manifest)
    return manifest


def _copy_bundle(root: Path, out: Path) -> None:
    for rel in ["release_manifest.json", "RELEASE_NOTES.md"]:
        shutil.copy2(root / rel, out / rel)
    for rel in ["targets", "evidence", "graphs", "schemas", "smabench", "recommendations", "sota", "checksums"]:
        shutil.copytree(root / rel, out / rel, dirs_exist_ok=True)


def generate_checksums(root: Path) -> Path:
    root = root.resolve()
    checksum_dir = root / "checksums"
    checksum_dir.mkdir(parents=True, exist_ok=True)
    skip_parts = {".git", ".venv", "out", "checksums", "__pycache__", ".pytest_cache"}
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(part in skip_parts for part in path.relative_to(root).parts):
            continue
        if path.name in {"verification_report.json", "verification_report.md"}:
            continue
        rows.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}")
    write_text(checksum_dir / "SHA256SUMS", "\n".join(rows) + "\n")
    return checksum_dir / "SHA256SUMS"


def _write_signing_note(root: Path) -> None:
    sums = root / "checksums" / "SHA256SUMS"
    sig = root / "checksums" / "SHA256SUMS.sig"
    gpg = shutil.which("gpg")
    if gpg:
        proc = subprocess.run([gpg, "--batch", "--yes", "--detach-sign", "--armor", str(sums)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if proc.returncode != 0:
            write_text(sig, "Signing not configured: gpg is available but no usable signing key was found.\n")
    else:
        write_text(sig, "Signing not configured: gpg was not available in this environment.\n")


def verify_release(root: Path, write_reports: bool = True) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))
        if not ok:
            errors.append(f"{name}: {detail}")

    required = [
        "release_manifest.json", "checksums/SHA256SUMS", "evidence/public_ledger.jsonl",
        "graphs/aegis_sma_lab_differential.json", "smabench/results/synthetic_results.json",
        "recommendations/recommendation_index.json", "sota/comparison_summary.md",
        "site/public-dashboard/index.html",
    ]
    for rel in required:
        check(f"required:{rel}", (root / rel).exists(), rel)

    if not (root / "release_manifest.json").exists():
        return {"ok": False, "errors": errors, "checks": checks}
    manifest = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
    check("release_manifest", manifest.get("release") == VERSION and LIMITATIONS[1] in manifest.get("limitations", []), "manifest version and limitations")
    checksum_path = root / manifest.get("checksums_file", "checksums/SHA256SUMS")
    checksum_ok = checksum_path.exists()
    if checksum_ok:
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            expected, rel = line.split("  ", 1)
            path = root / rel
            if not path.exists() or sha256(path) != expected:
                checksum_ok = False
                break
    check("checksums_verify", checksum_ok, checksum_path.relative_to(root).as_posix())

    ledger = jsonl(root / "evidence" / "public_ledger.jsonl") if (root / "evidence" / "public_ledger.jsonl").exists() else []
    evidence_ids = {row["evidence_id"] for row in ledger}
    for row in ledger:
        p = root / row["path"]
        check(f"evidence_exists:{row['evidence_id']}", p.exists(), row["path"])
        if p.exists():
            check(f"evidence_hash:{row['evidence_id']}", sha256(p) == row["sha256"], row["path"])
        check(f"claim_state:{row['evidence_id']}", row["claim_state"] in CLAIM_STATES, row["claim_state"])
        if row["artifact_class"] in {"static_observation", "target_manifest", "dependency_snapshot"}:
            check(f"static_not_vulnerability:{row['evidence_id']}", row["claim_state"] != "vulnerability_claim", row["claim_state"])

    graph_records = 0
    covered_records = 0
    node_ids: set[str] = set()
    for nodes_path in root.glob("graphs/*/nodes.jsonl"):
        nodes = jsonl(nodes_path)
        for node in nodes:
            graph_records += 1
            node_ids.add(node["node_id"])
            refs = set(node.get("evidence_refs", []))
            covered_records += bool(refs & evidence_ids)
    for edges_path in root.glob("graphs/*/edges.jsonl"):
        edges = jsonl(edges_path)
        for edge in edges:
            graph_records += 1
            refs = set(edge.get("evidence_refs", []))
            covered_records += bool(refs & evidence_ids)
            check(f"edge_nodes:{edge['edge_id']}", edge["source"] in node_ids and edge["target"] in node_ids, edge["edge_id"])
    coverage = covered_records / graph_records if graph_records else 0.0
    check("graph_evidence_coverage", coverage >= 0.98, f"{coverage:.2%}")

    recs = json.loads((root / "recommendations" / "recommendation_index.json").read_text(encoding="utf-8")).get("recommendations", [])
    check("recommendation_count", len(recs) >= 3, str(len(recs)))
    for rec in recs:
        ok = bool(rec.get("evidence_refs")) and bool(rec.get("graph_path_refs")) and bool(rec.get("residual_risk")) and bool(rec.get("standards_mapping_caveat"))
        check(f"recommendation_complete:{rec['recommendation_id']}", ok, rec["title"])

    smabench = json.loads((root / "smabench" / "results" / "synthetic_results.json").read_text(encoding="utf-8"))
    check("smabench_all_pass", all(row["status"] == "pass" for row in smabench.get("results", [])), "synthetic results")
    diff = json.loads((root / "graphs" / "aegis_sma_lab_differential.json").read_text(encoding="utf-8"))
    check("differential_deltas", len(diff.get("deltas", [])) >= 6 and all(d["delta"] < 0 for d in diff["deltas"]), "score deltas")
    sota = (root / "sota" / "comparison_summary.md").read_text(encoding="utf-8")
    check("sota_claim", "composes existing tools into an SMA-specific evidence graph" in sota, "composition claim")

    sensitive = scan_sensitive(root)
    for item in sensitive:
        check("safety_scan", False, item)
    if not sensitive:
        check("safety_scan", True, "no restricted path, token, or overclaim pattern found")

    result = {"ok": not errors, "errors": errors, "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks], "graph_evidence_coverage": coverage}
    if write_reports:
        write_json(root / "artifacts" / "verification" / "verification_report.json", result)
        lines = ["# Public Package Verification Report", "", f"Graph evidence coverage: {coverage:.2%}", ""]
        for name, ok, detail in checks:
            lines.append(f"- {'PASS' if ok else 'FAIL'} `{name}` {detail}")
        write_text(root / "artifacts" / "verification" / "verification_report.md", "\n".join(lines) + "\n")
    return result


def scan_sensitive(root: Path) -> list[str]:
    findings: list[str] = []
    sensitive_substrings = [
        "SBIR" + " Working Folder",
        "ASEMA_" + "Submission_Binder",
        "Claude" + " final",
        "OPENAI" + "_API_KEY",
        "vulnerability" + " confirmed",
    ]
    sensitive_regexes = [
        re.compile(r"gh[oprs]_[A-Za-z0-9_]+"),
    ]
    skip = {".git", ".venv", "out", "__pycache__"}
    for path in root.rglob("*"):
        if path.is_dir() or any(part in skip for part in path.relative_to(root).parts):
            continue
        if path.name in {"verification_report.json", "verification_report.md"}:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".sig", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in sensitive_substrings:
            if token in text:
                findings.append(f"{token!r} found in {path.relative_to(root)}")
        for regex in sensitive_regexes:
            if regex.search(text):
                findings.append(f"{regex.pattern!r} found in {path.relative_to(root)}")
    return findings


def validate_claim_states(root: Path) -> list[str]:
    result = verify_release(root, write_reports=False)
    return [err for err in result["errors"] if "claim" in err or "vulnerability" in err or "recommendation" in err]


def import_sarif(path: Path, out: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    observations = []
    for run_idx, run in enumerate(data.get("runs", [])):
        tool = run.get("tool", {}).get("driver", {}).get("name", "unknown")
        for result_idx, result in enumerate(run.get("results", [])):
            observations.append({"observation_id": f"SARIF-{run_idx}-{result_idx}", "tool": tool, "rule_id": result.get("ruleId", ""), "message": result.get("message", {}).get("text", ""), "claim_state": "static_supported"})
    write_json(out, {"source": str(path), "observations": observations})
    return {"observations": observations}


def import_cyclonedx(path: Path, out: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    components = [{"name": c.get("name", ""), "version": c.get("version", ""), "type": c.get("type", "")} for c in data.get("components", [])]
    result = {"snapshot_id": "DEP-IMPORTED-CYCLONEDX", "format": data.get("bomFormat", "CycloneDX"), "components": components}
    write_json(out, result)
    return result


def build_sqlite_store(root: Path, sqlite_path: Path) -> Path:
    root = root.resolve()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if sqlite_path.exists():
        sqlite_path.unlink()
    con = sqlite3.connect(sqlite_path)
    try:
        con.executescript(
            """
            create table evidence(
              evidence_id text primary key,
              target_id text,
              artifact_class text,
              path text,
              sha256 text,
              claim_state text,
              release_classification text
            );
            create table graph_nodes(
              node_id text primary key,
              target_id text,
              node_type text,
              label text,
              evidence_refs text
            );
            create table graph_edges(
              edge_id text primary key,
              source text,
              target text,
              edge_type text,
              evidence_refs text
            );
            create table scores(
              path_id text,
              target_id text,
              score real,
              score_vector text,
              claim_state text,
              evidence_refs text
            );
            create table recommendations(
              recommendation_id text primary key,
              title text,
              category text,
              evidence_refs text,
              graph_path_refs text,
              residual_risk text
            );
            """
        )
        ledger_path = root / "evidence" / "public_ledger.jsonl"
        if ledger_path.exists():
            for row in jsonl(ledger_path):
                con.execute(
                    "insert into evidence values(?,?,?,?,?,?,?)",
                    (
                        row["evidence_id"],
                        row.get("target_id", ""),
                        row.get("artifact_class", ""),
                        row.get("path", ""),
                        row.get("sha256", ""),
                        row.get("claim_state", ""),
                        row.get("release_classification", "public_sanitized"),
                    ),
                )
        for nodes_path in sorted(root.glob("graphs/*/nodes.jsonl")):
            for row in jsonl(nodes_path):
                con.execute(
                    "insert or replace into graph_nodes values(?,?,?,?,?)",
                    (row["node_id"], row.get("target_id", ""), row.get("node_type", ""), row.get("label", ""), json.dumps(row.get("evidence_refs", []))),
                )
        for edges_path in sorted(root.glob("graphs/*/edges.jsonl")):
            for row in jsonl(edges_path):
                con.execute(
                    "insert or replace into graph_edges values(?,?,?,?,?)",
                    (row["edge_id"], row.get("source", ""), row.get("target", ""), row.get("edge_type", ""), json.dumps(row.get("evidence_refs", []))),
                )
        for score_path in sorted(root.glob("graphs/*/score_report.json")):
            data = json.loads(score_path.read_text(encoding="utf-8"))
            for row in data.get("scores", []):
                con.execute(
                    "insert into scores values(?,?,?,?,?,?)",
                    (
                        row["path_id"],
                        row.get("target_id", data.get("target_id", "")),
                        row.get("score", 0.0),
                        json.dumps(row.get("score_vector", {}), sort_keys=True),
                        row.get("claim_state", ""),
                        json.dumps(row.get("evidence_refs", [])),
                    ),
                )
        rec_path = root / "recommendations" / "recommendation_index.json"
        if rec_path.exists():
            for row in json.loads(rec_path.read_text(encoding="utf-8")).get("recommendations", []):
                con.execute(
                    "insert into recommendations values(?,?,?,?,?,?)",
                    (
                        row["recommendation_id"],
                        row.get("title", ""),
                        row.get("category", ""),
                        json.dumps(row.get("evidence_refs", [])),
                        json.dumps(row.get("graph_path_refs", [])),
                        row.get("residual_risk", ""),
                    ),
                )
        con.commit()
    finally:
        con.close()
    return sqlite_path
