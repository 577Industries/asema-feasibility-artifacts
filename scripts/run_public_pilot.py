#!/usr/bin/env python3
"""Regenerate public ASEMA pilot summaries from public source repositories."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

TARGETS = [
    ("signal_android", "Signal Android", "https://github.com/signalapp/Signal-Android.git", "main", "AGPL-3.0"),
    ("element_x_android", "Element X Android", "https://github.com/element-hq/element-x-android.git", "main", "Apache-2.0 style project licensing; verify exact repository license before redistribution."),
]

SKIP_DIRS = {".git", ".gradle", "build", ".idea", "node_modules", "target", ".github", ".m2"}
EXTENSIONS = {".kt", ".kts", ".java", ".xml", ".rs", ".proto", ".gradle", ".toml"}
PATTERNS = [
    ("deep_link_uri", re.compile(r"(Intent\.ACTION_VIEW|android\.intent\.action\.VIEW|android:scheme|deep.?link|Uri\.parse|NavDeepLink)", re.I)),
    ("qr_or_device_linking", re.compile(r"(qr.?code|barcode|link.?device|linked.?device|device.?link|scan.?qr|LoginToken|verification.?code)", re.I)),
    ("media_file_surface", re.compile(r"(Attachment|Media|ImageDecoder|BitmapFactory|ExifInterface|ContentResolver|FileProvider|mime.?type|thumbnail|OpenableColumns|DocumentFile|video|audio)", re.I)),
    ("crypto_session_surface", re.compile(r"(libsignal|SignalProtocol|SessionCipher|Ratchet|Olm|Megolm|CryptoStore|KeyBackup|matrix_sdk_crypto|MegolmV1|SecretStorage)", re.I)),
    ("native_ffi_boundary", re.compile(r"(System\.loadLibrary|JNI|jniLibs|uniffi|ffi|\.so\b|Rust|matrix_sdk|libsignal_client)", re.I)),
    ("storage_keystore", re.compile(r"(EncryptedSharedPreferences|KeyStore|AndroidKeyStore|RoomDatabase|SQLCipher|SharedPreferences|DataStore|SecureStorage|database|keystore)", re.I)),
    ("network_sync_surface", re.compile(r"(OkHttpClient|WebSocket|Retrofit|sync|SyncService|FirebaseMessagingService|FCM|push|notification|ClientServerApi|HTTP)", re.I)),
    ("webview_javascript", re.compile(r"(WebView|javaScriptEnabled|setJavaScriptEnabled|addJavascriptInterface|shouldOverrideUrlLoading)", re.I)),
]

def run(args, cwd=None, timeout=600):
    proc = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed:\n{proc.stdout}")
    return proc.stdout.strip()

def clone_with_retries(url, branch, repo, attempts=3):
    for attempt in range(1, attempts + 1):
        if repo.exists():
            shutil.rmtree(repo)
        args = [
            "git",
            "-c", "http.lowSpeedLimit=1000",
            "-c", "http.lowSpeedTime=120",
            "clone",
            "--depth", "1",
            "--single-branch",
            "--branch", branch,
            url,
            str(repo),
        ]
        try:
            return run(args, timeout=900)
        except Exception as exc:
            if attempt == attempts:
                raise
            print(f"clone attempt {attempt} failed for {url}: {exc}")

def walk_source(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in EXTENSIONS:
                yield path

def parse_manifests(repo):
    ns = "{http://schemas.android.com/apk/res/android}"
    rows = []
    for manifest in repo.rglob("AndroidManifest.xml"):
        if any(part in SKIP_DIRS for part in manifest.parts):
            continue
        try:
            tree = ET.parse(manifest)
        except Exception:
            continue
        root = tree.getroot()
        for perm in root.findall("uses-permission"):
            rows.append({"manifest": str(manifest.relative_to(repo)), "type": "uses-permission", "exported": "", "permission_declared": "no", "has_intent_action": "no", "has_scheme": "no", "has_host": "no", "has_mime_type": "no", "notes": "Permission declaration."})
        app = root.find("application")
        if app is None:
            continue
        for component_type in ["activity", "activity-alias", "service", "receiver", "provider"]:
            for comp in app.findall(component_type):
                actions = []
                schemes = []
                hosts = []
                mime_types = []
                for filt in comp.findall("intent-filter"):
                    actions.extend([a.attrib.get(ns + "name", "") for a in filt.findall("action")])
                    for data in filt.findall("data"):
                        schemes.append(data.attrib.get(ns + "scheme", ""))
                        hosts.append(data.attrib.get(ns + "host", ""))
                        mime_types.append(data.attrib.get(ns + "mimeType", ""))
                rows.append({
                    "manifest": str(manifest.relative_to(repo)),
                    "type": component_type,
                    "exported": comp.attrib.get(ns + "exported", ""),
                    "permission_declared": "yes" if comp.attrib.get(ns + "permission", "") else "no",
                    "has_intent_action": "yes" if any(actions) else "no",
                    "has_scheme": "yes" if any(schemes) else "no",
                    "has_host": "yes" if any(hosts) else "no",
                    "has_mime_type": "yes" if any(mime_types) else "no",
                    "notes": "Android application component.",
                })
    return rows

def scan_categories(repo):
    counts = {}
    example_files = {}
    category_cap = 160
    for path in walk_source(repo):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(path.relative_to(repo))
        for line in text.splitlines():
            for category, regex in PATTERNS:
                if counts.get(category, 0) >= category_cap:
                    continue
                if regex.search(line):
                    counts[category] = counts.get(category, 0) + 1
                    example_files.setdefault(category, set()).add(rel)
    return counts, example_files

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/pilot")
    parser.add_argument("--workdir", default="")
    args = parser.parse_args()
    out = Path(args.out)
    work = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="asema-public-pilot-"))
    work.mkdir(parents=True, exist_ok=True)

    all_components = []
    all_counts = []
    for target_id, name, url, branch, license_note in TARGETS:
        repo = work / target_id
        if not repo.exists():
            clone_with_retries(url, branch, repo)
        commit = run(["git", "-C", str(repo), "rev-parse", "HEAD"])
        source_files = list(walk_source(repo))
        extension_counts = {}
        for source_file in source_files:
            extension_counts[source_file.suffix.lower()] = extension_counts.get(source_file.suffix.lower(), 0) + 1
        components = parse_manifests(repo)
        counts, example_files = scan_categories(repo)

        manifest = {
            "target_id": target_id,
            "name": name,
            "repo_url": url,
            "branch": branch,
            "commit": commit,
            "commit_short": commit[:8],
            "license_note": license_note,
            "analysis_scope": "Public-source static analysis of Android manifests and source-code indicators. No exploit reproduction, live target probing, or credentialed app interaction.",
            "source_file_count": len(source_files),
            "extension_counts": extension_counts,
            "manifest_component_counts": {},
            "observation_category_counts": counts,
        }
        for row in components:
            manifest["manifest_component_counts"][row["type"]] = manifest["manifest_component_counts"].get(row["type"], 0) + 1
            row["target"] = target_id
            all_components.append(row)
        (out / "manifests").mkdir(parents=True, exist_ok=True)
        (out / "manifests" / f"{target_id}_target_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        for category, count in sorted(counts.items()):
            all_counts.append({
                "target": target_id,
                "category": category,
                "observation_count_capped": count,
                "cap_note": "Scanner caps each category at 160 examples per target.",
                "example_files": ";".join(sorted(example_files.get(category, set()))[:8]),
            })

    write_csv(out / "android_manifest_component_inventory_public.csv", all_components, ["target", "manifest", "type", "exported", "permission_declared", "has_intent_action", "has_scheme", "has_host", "has_mime_type", "notes"])
    write_csv(out / "attack_surface_category_counts.csv", all_counts, ["target", "category", "observation_count_capped", "cap_note", "example_files"])
    print(f"wrote public pilot artifacts to {out}")

if __name__ == "__main__":
    main()
