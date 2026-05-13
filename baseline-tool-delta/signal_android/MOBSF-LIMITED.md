# MobSF run NOT executed for signal_android@1043851

**Reason:** `apk_missing`

**Generated at:** 2026-05-05T00:00:00Z

## Target

| Field | Value |
|---|---|
| target_id | `signal_android@1043851` |
| repo_url | https://github.com/signalapp/Signal-Android |
| commit | `1043851` |
| apk_path | _(not available)_ |

## Why MobSF did not run

MobSF requires an APK to analyze. AegisGraph operates under an
**anchor-only** source policy (see `extraction/targets/<target>/target.json`):
target binaries are NOT redistributed inside this research repo, and APKs
are acquired only at execution time on the self-hosted runner (see
`extraction/mobsf/README.md` "APK acquisition asymmetry" section).

The current invocation environment is missing the APK file (`apk_missing`)
or the docker binary required to run the MobSF container (`binary_missing`).
Per Wave 9A policy, the runner does **not** fabricate findings — it
records this state transparently and the delta report renders the cell as
"MOBSF-LIMITED" with zero findings counted.

## Operational note

To produce a real MobSF row in the baseline-delta report:

1. Acquire the APK on the self-hosted runner per
   `extraction/mobsf/README.md` (signed authorization required for
   any binary not publicly distributed).
2. Re-run `python3 -m aegisgraph.baseline_delta.runner --target signal`
   with `--apk-path` set.

## Status envelope

This file is the human-readable companion to the structured envelope:

```json
{
  "tool": "mobsf",
  "target_id": "signal_android@1043851",
  "status": "apk_missing",
  "findings_count": 0,
  "mobsf_limited_md": "MOBSF-LIMITED.md"
}
```
