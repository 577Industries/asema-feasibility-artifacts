#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph import build_release

build_release(ROOT, ROOT / "out" / "demo")
print("SMABench synthetic results written to smabench/results/synthetic_results.json")
