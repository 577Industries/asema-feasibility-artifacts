"""Product-grade orchestration helpers for AegisGraph ASEMA demos."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .buildout import (
    LIMITATIONS,
    TARGETS,
    VERSION,
    build_release,
    build_sqlite_store,
    generate_checksums,
    jsonl,
    scan_sensitive,
    sha256,
    verify_release,
    write_json,
    write_text,
)


def dashboard_payload(root: Path, mode: str = "public") -> dict[str, Any]:
    root = root.resolve()
    ledger = jsonl(root / "evidence" / "public_ledger.jsonl") if (root / "evidence" / "public_ledger.jsonl").exists() else []
    graphs = []
    for gdir in sorted((root / "graphs").glob("*")):
        if not gdir.is_dir():
            continue
        stats = gdir / "graph_stats.json"
        scores = gdir / "score_report.json"
        graphs.append(
            {
                "target_id": gdir.name,
                "nodes": sum(1 for _ in (gdir / "nodes.jsonl").read_text(encoding="utf-8").splitlines()) if (gdir / "nodes.jsonl").exists() else 0,
                "edges": sum(1 for _ in (gdir / "edges.jsonl").read_text(encoding="utf-8").splitlines()) if (gdir / "edges.jsonl").exists() else 0,
                "stats_path": stats.relative_to(root).as_posix() if stats.exists() else "",
                "score_path": scores.relative_to(root).as_posix() if scores.exists() else "",
            }
        )
    return {
        "release": VERSION,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "targets": [target["target_id"] for target in TARGETS] + ["aegis_sma_lab_baseline", "aegis_sma_lab_mitigated"],
        "evidence": ledger,
        "graphs": graphs,
        "limitations": LIMITATIONS,
        "public_boundary": "Real-target observations are static-supported prioritization signals, not vulnerability claims.",
        "downloads": [
            "release_manifest.json",
            "checksums/SHA256SUMS",
            "graphs/",
            "schemas/",
            "smabench/results/synthetic_results.json",
            "recommendations/recommendation_index.json",
        ],
    }


def render_dashboard(root: Path, mode: str = "public", out: Path | None = None) -> Path:
    if mode not in {"public", "local"}:
        raise ValueError("--mode must be public or local")
    root = root.resolve()
    out_dir = out.resolve() if out else root / "site" / ("public-dashboard" if mode == "public" else "local-dashboard")
    data_dir = out_dir / "data"
    write_json(data_dir / "dashboard_data.json", dashboard_payload(root, mode))
    shutil.copy2(root / "release_manifest.json", data_dir / "release_manifest.json")
    title = "AegisGraph ASEMA Local Dashboard" if mode == "local" else "AegisGraph ASEMA Public Dashboard"
    write_text(
        out_dir / "index.html",
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header><h1>{title}</h1><p>Evidence-linked SMA graph, SMABench, recommendations, SOTA comparison, and safety boundaries.</p></header>
  <nav><a href="#targets">Targets</a><a href="#evidence">Evidence</a><a href="#graph">Graph</a><a href="#smabench">SMABench</a><a href="#downloads">Downloads</a></nav>
  <main>
    <section id="targets"><h2>Targets</h2><p>Signal Android and Element X Android are public static summaries. AegisSMA-Lab is deterministic synthetic evidence.</p></section>
    <section id="evidence"><h2>Evidence</h2><p>Ledger rows include producer, hash, claim state, reviewer decision, and release classification. Source: <a href="data/dashboard_data.json">dashboard_data.json</a>.</p></section>
    <section id="graph"><h2>Graph Explorer</h2><p>Graph exports cover entrypoints, parsers, media, link preview, device linking, group state, storage, native/FFI, sync, PQ migration, and security boundaries.</p></section>
    <section id="smabench"><h2>SMABench</h2><p>Synthetic tasks compare baseline and mitigated traces with deterministic 0-100 assessment-priority scoring.</p></section>
    <section><h2>Recommendations</h2><p>Recommendations require graph path refs, evidence refs, implementation hints, residual risk, and public limitation notes.</p></section>
    <section><h2>Safety</h2><p>No raw target source, no real-app dynamic traces, no credentials, no exploit reproduction, and no static-only vulnerability claims.</p></section>
    <section id="downloads"><h2>Downloads</h2><p>Use release manifest, checksums, schemas, graph exports, SMABench bundle, dashboard bundle, and verification reports.</p></section>
  </main>
</body>
</html>
""",
    )
    write_text(
        out_dir / "styles.css",
        "body{margin:0;background:#f5f7f4;color:#1d2528;font-family:Arial,sans-serif}header{background:#143d3a;color:white;padding:28px 24px}nav{display:flex;gap:16px;flex-wrap:wrap;padding:12px 24px;background:#e7ece8}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;padding:24px}section{background:white;border:1px solid #d7ddd8;border-radius:8px;padding:18px;min-height:150px}h1,h2{margin-top:0;letter-spacing:0}a{color:#0b5f9e}\n",
    )
    return out_dir / "index.html"


def write_local_app(root: Path) -> None:
    api = root / "apps" / "local-demo" / "api"
    web = root / "apps" / "local-demo" / "web"
    write_text(api / "requirements.txt", "fastapi\nuvicorn\n")
    write_text(
        api / "main.py",
        """from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "out" / "product-demo" / "aegisgraph.sqlite"
app = FastAPI(title="AegisGraph ASEMA Local Demo API")


def rows(query: str):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(query)]
    finally:
        con.close()


@app.get("/health")
def health():
    return {"ok": DB.exists(), "database": str(DB.relative_to(ROOT)) if DB.exists() else "missing"}


@app.get("/targets")
def targets():
    data = json.loads((ROOT / "site" / "local-dashboard" / "data" / "dashboard_data.json").read_text())
    return data["targets"]


@app.get("/evidence")
def evidence():
    return rows("select * from evidence order by evidence_id")


@app.get("/graph/nodes")
def graph_nodes():
    return rows("select * from graph_nodes order by target_id, node_id")


@app.get("/graph/edges")
def graph_edges():
    return rows("select * from graph_edges order by edge_id")


@app.get("/scores")
def scores():
    return rows("select * from scores order by score desc")


@app.get("/recommendations")
def recommendations():
    return rows("select * from recommendations order by recommendation_id")
""",
    )
    write_text(
        web / "package.json",
        json.dumps(
            {
                "scripts": {"dev": "vite --host 127.0.0.1"},
                "dependencies": {"@vitejs/plugin-react": "latest", "vite": "latest", "react": "latest", "react-dom": "latest", "lucide-react": "latest"},
                "devDependencies": {},
            },
            indent=2,
        )
        + "\n",
    )
    write_text(web / "index.html", "<div id=\"root\"></div><script type=\"module\" src=\"/src/App.jsx\"></script>\n")
    write_text(
        web / "src" / "App.jsx",
        """import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Download, GitBranch, ShieldCheck } from 'lucide-react';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function useJson(path) {
  const [data, setData] = useState([]);
  useEffect(() => { fetch(`${API}${path}`).then(r => r.json()).then(setData).catch(() => setData([])); }, [path]);
  return data;
}

function App() {
  const evidence = useJson('/evidence');
  const scores = useJson('/scores');
  const recs = useJson('/recommendations');
  return (
    <main>
      <header>
        <ShieldCheck size={28} />
        <div><h1>AegisGraph ASEMA</h1><p>Local evidence graph demo over generated public artifacts and SQLite.</p></div>
      </header>
      <section className="metrics">
        <article><GitBranch /><strong>{evidence.length}</strong><span>evidence records</span></article>
        <article><ShieldCheck /><strong>{scores.length}</strong><span>scored paths</span></article>
        <article><Download /><strong>{recs.length}</strong><span>recommendations</span></article>
      </section>
      <section><h2>Top Assessment Paths</h2>{scores.map(s => <div className="row" key={`${s.target_id}-${s.path_id}`}><span>{s.target_id} / {s.path_id}</span><b>{Number(s.score).toFixed(1)}</b></div>)}</section>
      <section><h2>Recommendation Worklist</h2>{recs.map(r => <div className="row" key={r.recommendation_id}><span>{r.title}</span><b>{r.recommendation_id}</b></div>)}</section>
      <footer>Static real-target observations are review-priority signals, not vulnerability claims.</footer>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
""",
    )
    write_text(
        web / "src" / "style.css",
        "body{margin:0;background:#f5f7f4;color:#182026;font-family:Inter,Arial,sans-serif}main{max-width:1120px;margin:0 auto;padding:24px}header{display:flex;align-items:center;gap:14px;border-bottom:1px solid #d7ddd8;padding-bottom:18px}h1,h2{margin:0;letter-spacing:0}p{margin:4px 0 0}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:20px 0}.metrics article{background:white;border:1px solid #d7ddd8;border-radius:8px;padding:16px;display:grid;gap:6px}.metrics strong{font-size:28px}section{margin-top:18px}.row{display:flex;justify-content:space-between;gap:16px;align-items:center;background:white;border:1px solid #d7ddd8;border-radius:8px;padding:12px;margin-top:8px}footer{margin-top:24px;color:#4d5a5d}\n",
    )


def build_product_demo(root: Path, out: Path) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()
    manifest = build_release(root, out)
    sqlite_path = build_sqlite_store(root, out / "aegisgraph.sqlite")
    render_dashboard(root, "local")
    write_local_app(root)
    write_json(out / "product_manifest.json", {"release": VERSION, "sqlite": sqlite_path.relative_to(out).as_posix(), "public_manifest": manifest})
    shutil.copytree(root / "site" / "local-dashboard", out / "site" / "local-dashboard", dirs_exist_ok=True)
    generate_checksums(root)
    return {"manifest": manifest, "sqlite": sqlite_path.as_posix(), "out": out.as_posix()}


def validate_authorization_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"authorization manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"authorization_id", "release_classification", "authorized_targets", "expires"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"authorization manifest missing fields: {', '.join(missing)}")
    if data["release_classification"] != "private_restricted":
        raise ValueError("authorization manifest release_classification must be private_restricted")
    return data


def build_private_demo(root: Path, out: Path, authorization: Path) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()
    auth = validate_authorization_manifest(authorization)
    build_product_demo(root, root / "out" / "product-demo")
    out.mkdir(parents=True, exist_ok=True)
    private_manifest = {
        "release": VERSION,
        "release_classification": "private_restricted",
        "authorization_id": auth["authorization_id"],
        "authorized_targets": auth["authorized_targets"],
        "included_artifacts": ["authorized_dynamic_summary.json", "private_package_manifest.json"],
        "limitations": ["Trace metadata summaries only; raw traces and target source are excluded unless separately authorized."],
    }
    write_json(out / "private_package_manifest.json", private_manifest)
    write_json(
        out / "authorized_dynamic_summary.json",
        {
            "release_classification": "private_restricted",
            "trace_metadata_only": True,
            "authorized_targets": auth["authorized_targets"],
            "adapters": auth.get("permitted_adapters", ["adb_logcat_fixture", "frida_trace_fixture", "mobsf_static_fixture"]),
            "claim_state_limit": "authorized_dynamic_observed",
        },
    )
    findings = scan_sensitive(out)
    if findings:
        raise RuntimeError("private package safety scan failed: " + "; ".join(findings))
    return private_manifest


def rebuild_submission_binder(root: Path, binder: Path | None = None) -> Path:
    root = root.resolve()
    binder = binder.resolve() if binder else root.parent / ("ASEMA_" + "Submission_Binder")
    build_product_demo(root, root / "out" / "product-demo")
    binder.mkdir(parents=True, exist_ok=True)
    report = verify_release(root)
    write_text(
        binder / "README.md",
        f"""# AegisGraph ASEMA Submission Binder

Generated from public artifacts release {VERSION}.

## Contents

- Proposal references: docs/ and release_manifest.json
- Feasibility study: docs/01_phase_i_equivalent_summary.md
- Evidence appendix: evidence/public_ledger.jsonl
- Public dashboard: site/public-dashboard/index.html
- Local dashboard: site/local-dashboard/index.html
- SQLite query store: out/product-demo/aegisgraph.sqlite
- Verification: artifacts/verification/verification_report.md

Verification status: {'PASS' if report['ok'] else 'FAIL'}.
""",
    )
    write_json(
        binder / "binder_manifest.json",
        {
            "release": VERSION,
            "source_root": root.as_posix(),
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "verification_ok": report["ok"],
            "public_release_manifest_sha256": sha256(root / "release_manifest.json"),
        },
    )
    return binder


def toolchain_status() -> dict[str, Any]:
    tools = ["docker", "java", "node", "gradle", "adb", "frida", "mobsfscan"]
    return {
        name: {
            "available": shutil.which(name) is not None,
            "required_for_public": name in {"java", "node"},
            "gated_optional": name in {"docker", "gradle", "adb", "frida", "mobsfscan"},
        }
        for name in tools
    }


def write_toolchain_report(root: Path) -> Path:
    path = root / "artifacts" / "verification" / "toolchain_report.json"
    write_json(path, {"tools": toolchain_status(), "note": "Optional mobile-suite tools are reported but not required for public package verification."})
    return path
