#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegisgraph.buildout import generate_checksums

path = generate_checksums(ROOT)
print(f"wrote {path.relative_to(ROOT)}")
