#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph.buildout import import_sarif

parser = argparse.ArgumentParser()
parser.add_argument("sarif")
parser.add_argument("--out", default="sota/static_tool_outputs_sanitized/imported_sarif_observations.json")
args = parser.parse_args()
out = Path(args.out)
if not out.is_absolute():
    out = ROOT / out
result = import_sarif(Path(args.sarif), out)
print(f"imported {len(result['observations'])} SARIF observations to {out}")
