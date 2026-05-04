#!/usr/bin/env python3
"""Build the local product demo bundle, SQLite store, and app scaffolding."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.aegisgraph import build_product_demo, verify_release
from tools.aegisgraph.buildout import generate_checksums
from tools.aegisgraph.product import write_toolchain_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="out/product-demo")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    result = build_product_demo(ROOT, out)
    write_toolchain_report(ROOT)
    generate_checksums(ROOT)
    verification = verify_release(ROOT)
    if not verification["ok"]:
        for err in verification["errors"]:
            print(f"ERROR: {err}")
        raise SystemExit(1)
    print(f"wrote product demo bundle to {result['out']}")
    print(f"wrote SQLite query store to {result['sqlite']}")
    print("local API scaffold: apps/local-demo/api")
    print("local web scaffold: apps/local-demo/web")


if __name__ == "__main__":
    main()
