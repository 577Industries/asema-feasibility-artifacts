#!/usr/bin/env python3
"""Build an authorization-gated private demo package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.aegisgraph import build_private_demo


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--authorization", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    authorization = Path(args.authorization)
    if not authorization.is_absolute():
        authorization = ROOT / authorization
    manifest = build_private_demo(ROOT, out, authorization)
    print(f"wrote private restricted demo package to {out}")
    print(f"authorization: {manifest['authorization_id']}")


if __name__ == "__main__":
    main()
