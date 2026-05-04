#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph import build_release, render_dashboard

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["public", "local"], default="public")
parser.add_argument("--out")
args = parser.parse_args()

build_release(ROOT, ROOT / "out" / "demo")
out = Path(args.out) if args.out else None
if out and not out.is_absolute():
    out = ROOT / out
path = render_dashboard(ROOT, args.mode, out)
print(f"dashboard rendered at {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
