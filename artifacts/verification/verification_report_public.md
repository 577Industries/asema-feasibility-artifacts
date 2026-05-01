# ASEMA Binder Verification Report

Created: 2026-05-01

## Build Results

- Binder build script completed successfully: `99_Build_Tools/build_binder.py`.
- Support repository checks: 15 of 15 `npm test`, `npm run build`, and `npm run lint` commands exited with code 0.
- Real-app targets cloned and pinned:
  - Signal Android: `1043851`
  - Element X Android: `91d265e6`
- Static pilot artifacts generated:
  - `05_Real_App_Analysis_Pilot/inventories/android_manifest_component_inventory.csv`
  - `05_Real_App_Analysis_Pilot/inventories/attack_surface_observations.csv`
  - `05_Real_App_Analysis_Pilot/semgrep/semgrep_results_summary.csv`
- Semgrep informational findings:
  - Signal Android: 239
  - Element X Android: 162

## PDF Checks

- `02_Final_Proposal/ASEMA_DP2_Deep_Technical_Proposal.pdf`: rendered to PNG, 7 pages, text extraction verified.
- `03_Phase_I_Feasibility_Study/ASEMA_Phase_I_Feasibility_Study.pdf`: rendered to PNG, 7 pages, text extraction verified.
- `04_Feasibility_Evidence_Appendix/ASEMA_DP2_Feasibility_Evidence_Appendix.pdf`: rendered to PNG, 3 pages, text extraction verified.

Representative rendered pages were visually inspected from `tmp/rendered_pages/`; headings, tables, body text, and footer/page numbering were readable with no obvious clipping or overlap.

## Known Limits

- The pilot is public-source static analysis only.
- Static indicators are informational and are not vulnerability findings.
- The package does not perform exploit reproduction, live service probing, or closed-source reverse engineering.
- OpenAI image generation was not used in this public package; diagrams are reproducible SVG/Mermaid assets instead.


## Public Verification Boundary

This public report summarizes reproducible evidence checks. It intentionally excludes raw local logs, absolute filesystem paths, internal proposal drafts, and cloned target source trees.
