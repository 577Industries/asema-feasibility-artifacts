#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph import build_release
from tools.aegisgraph.claims import validate_claim_states

build_release(ROOT, ROOT / "out" / "demo")
violations = validate_claim_states(ROOT)
for violation in violations:
    print(f"VIOLATION: {violation}")
if violations:
    raise SystemExit(1)
print("claim-state violations: 0")
