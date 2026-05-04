#!/usr/bin/env python3
"""Build the deterministic public v0.2 demo bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.aegisgraph import build_release, verify_release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="out/demo")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    build_release(ROOT, out)
    result = verify_release(ROOT)
    if not result["ok"]:
        for err in result["errors"]:
            print(f"ERROR: {err}")
        raise SystemExit(1)
    print(f"wrote public demo bundle to {out}")
    print("rendered dashboard at site/public-dashboard/index.html")


if __name__ == "__main__":
    main()
