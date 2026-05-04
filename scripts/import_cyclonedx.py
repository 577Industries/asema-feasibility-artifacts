#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph.buildout import import_cyclonedx

parser = argparse.ArgumentParser()
parser.add_argument("bom")
parser.add_argument("--out", default="sota/static_tool_outputs_sanitized/imported_cyclonedx_snapshot.json")
args = parser.parse_args()
out = Path(args.out)
if not out.is_absolute():
    out = ROOT / out
result = import_cyclonedx(Path(args.bom), out)
print(f"imported {len(result['components'])} CycloneDX components to {out}")
