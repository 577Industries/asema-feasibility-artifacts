#!/usr/bin/env python3
"""Verify the public ASEMA artifact package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

SENSITIVE_SUBSTRINGS = [
    "SBIR" + " Working Folder",
    "ASEMA_" + "Submission_Binder",
    "98_" + "Archive_Originals",
    "Claude" + " final",
    "OPENAI" + "_API_KEY",
]

SENSITIVE_REGEXES = [
    re.compile(r"(?<![A-Za-z0-9._-])/home/[A-Za-z0-9._-]+"),
    re.compile(r"gh[oprs]_[A-Za-z0-9_]+"),
]

REQUIRED = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "docs/LICENSE-DOCS.md",
    "docs/index.html",
    "artifacts/feasibility/ASEMA_Phase_I_Feasibility_Study_Public.md",
    "artifacts/evidence_index_public.csv",
    "artifacts/pilot/manifests/signal_android_target_manifest.json",
    "artifacts/pilot/manifests/element_x_android_target_manifest.json",
    "artifacts/pilot/android_manifest_component_inventory_public.csv",
    "artifacts/pilot/attack_surface_category_counts.csv",
    "artifacts/pilot/semgrep_results_summary.csv",
    "artifacts/benchmark/SMABench_pilot_seed_manifest.md",
    "artifacts/citations/source_citations.md",
    "artifacts/verification/support_repo_check_summary.csv",
    "schemas/evidence_index.schema.json",
    "schemas/target_manifest.schema.json",
    "schemas/pilot_summary.schema.json",
    "scripts/run_public_pilot.py",
]

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    errors = []
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    for path in root.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in SENSITIVE_SUBSTRINGS:
            if token in text:
                errors.append(f"sensitive token {token!r} found in {path.relative_to(root)}")
        for regex in SENSITIVE_REGEXES:
            if regex.search(text):
                errors.append(f"sensitive pattern {regex.pattern!r} found in {path.relative_to(root)}")

    with (root / "artifacts/evidence_index_public.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        errors.append("public evidence index is empty")
    for row in rows:
        p = root / row["public_path"]
        if not p.exists():
            errors.append(f"evidence path missing: {row['public_path']}")
        elif row.get("sha256") and sha256(p) != row["sha256"]:
            errors.append(f"sha mismatch: {row['public_path']}")

    for rel in ["artifacts/pilot/manifests/signal_android_target_manifest.json", "artifacts/pilot/manifests/element_x_android_target_manifest.json"]:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
        for key in ["target_id", "name", "repo_url", "branch", "commit", "analysis_scope"]:
            if key not in data:
                errors.append(f"{rel} missing {key}")

    if errors:
        print("verification failed:")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    print("public package verification passed")

if __name__ == "__main__":
    main()
