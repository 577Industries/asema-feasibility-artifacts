#!/usr/bin/env python3
"""Rebuild the generated submission binder index from current artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.aegisgraph import rebuild_submission_binder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    binder = Path(args.out) if args.out else None
    if binder and not binder.is_absolute():
        binder = ROOT / binder
    path = rebuild_submission_binder(ROOT, binder)
    print(f"rebuilt submission binder at {path}")


if __name__ == "__main__":
    main()
