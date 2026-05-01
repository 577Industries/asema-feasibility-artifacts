# SMABench Pilot Seed Manifest

Created: 2026-05-01

This manifest upgrades the previous candidate benchmark concept into a bounded pilot evidence set. It records reproducible seed classes for secure messaging application implementation analysis without claiming exploit reproduction.

| Seed | Class | Evidence | Metric |
| --- | --- | --- | --- |
| SMA-SEED-001 | Android manifest entrypoint inventory | 05_Real_App_Analysis_Pilot/inventories/android_manifest_component_inventory.csv | Component counts, exported status, permissions, intent actions, schemes, hosts, MIME types. |
| SMA-SEED-002 | Source indicator attack-surface inventory | 05_Real_App_Analysis_Pilot/inventories/attack_surface_observations.csv | Categorized occurrences for media handling, deep links, QR/device linking, storage, crypto/session, native/FFI, network/sync, WebView. |
| SMA-SEED-003 | Static rule scan | 05_Real_App_Analysis_Pilot/semgrep/semgrep_results_summary.csv | Informational Semgrep findings from ASEMA-specific generic rules. |
| SMA-SEED-004 | Prototype infrastructure validation | 04_Feasibility_Evidence_Appendix/03_test_logs/support_repo_check_results.csv | Local test/build/lint status for supporting 577i prototype libraries. |

## Non-Goals

- No exploit reproduction.
- No live app or server probing.
- No claim that informational static indicators are vulnerabilities.
