#!/usr/bin/env python3
"""Verify the public ASEMA v0.2 package."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.aegisgraph import build_release, verify_release


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    if not (root / "release_manifest.json").exists():
        build_release(root, root / "out" / "demo")
    result = verify_release(root)
    print("AegisGraph ASEMA public package verification")
    for check in result["checks"]:
        status = "PASS" if check["ok"] else "FAIL"
        print(f"{status:4} {check['name']} {check['detail']}")
    if not result["ok"]:
        print("PUBLIC PACKAGE NOT READY: evaluator-visible checks failed.")
        raise SystemExit(1)
    print("PUBLIC PACKAGE READY: all evaluator-visible checks passed.")


if __name__ == "__main__":
    main()
