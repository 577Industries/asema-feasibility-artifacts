"""Sanitizing adapters for external static and dynamic tool summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .buildout import import_cyclonedx, import_sarif, write_json
from .product import validate_authorization_manifest


def import_mobsf_static_summary(path: Path, out: Path, target_id: str = "imported_target") -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = {
        "target_id": target_id,
        "source": path.name,
        "claim_state": "static_supported",
        "release_classification": "public_sanitized",
        "permissions": sorted(data.get("permissions", {}).keys())[:50] if isinstance(data.get("permissions"), dict) else [],
        "activities": len(data.get("activities", []) or []),
        "services": len(data.get("services", []) or []),
        "receivers": len(data.get("receivers", []) or []),
        "limitation": "Sanitized MobSF-style static summary only; no vulnerability claim.",
    }
    write_json(out, summary)
    return summary


def import_gradle_dependencies(path: Path, out: Path, target_id: str = "imported_target") -> dict[str, Any]:
    components = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = line.strip().lstrip("+-\\| ")
        if ":" in text and "project " not in text:
            parts = text.split(":")
            if len(parts) >= 2:
                components.append({"group": parts[0], "name": parts[1], "version": parts[2] if len(parts) > 2 else ""})
    result = {"snapshot_id": f"DEP-{target_id}-GRADLE", "target_id": target_id, "format": "gradle-dependencies-summary", "components": components[:500]}
    write_json(out, result)
    return result


def import_adb_logcat_trace(path: Path, out: Path, authorization: Path) -> dict[str, Any]:
    auth = validate_authorization_manifest(authorization)
    events = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()[:200]):
        events.append({"step": idx + 1, "event": "logcat_line", "summary": line[:160]})
    result = {
        "trace_id": f"TRACE-AUTH-LOGCAT-{auth['authorization_id']}",
        "release_classification": "private_restricted",
        "claim_state": "authorized_dynamic_observed",
        "events": events,
        "raw_trace_included": False,
    }
    write_json(out, result)
    return result


def import_frida_trace(path: Path, out: Path, authorization: Path) -> dict[str, Any]:
    auth = validate_authorization_manifest(authorization)
    calls = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()[:200]):
        calls.append({"step": idx + 1, "hook_summary": line[:160]})
    result = {
        "trace_id": f"TRACE-AUTH-FRIDA-{auth['authorization_id']}",
        "release_classification": "private_restricted",
        "claim_state": "authorized_dynamic_observed",
        "calls": calls,
        "raw_trace_included": False,
    }
    write_json(out, result)
    return result


__all__ = [
    "import_sarif",
    "import_cyclonedx",
    "import_mobsf_static_summary",
    "import_gradle_dependencies",
    "import_adb_logcat_trace",
    "import_frida_trace",
]
