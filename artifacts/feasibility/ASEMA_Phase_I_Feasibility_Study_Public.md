# ASEMA Phase I-Equivalent Feasibility Study

## AegisGraph Secure Messaging Application Assessment Framework

Prepared for 577 Industries

Created: 2026-05-01

## 1. Executive Findings

This feasibility study packages Phase I-equivalent evidence for the ASEMA Direct-to-Phase-II proposal. The evidence shows that 577 Industries can organize a reproducible secure messaging application assessment workflow, preserve provenance, run controlled source-level pilots on real applications, and connect those results to an evidence-indexed proposal.

The pilot is intentionally bounded. It uses public source repositories for Signal Android and Element X Android; extracts Android manifest, component, source-indicator, and static-rule evidence; and records every artifact in the binder. It does not perform exploit reproduction, credentialed app interaction, live service probing, reverse engineering of closed-source binaries, or cryptographic protocol proof work. That boundary is important because the ASEMA topic asks for approaches that model SMA security risks and recommend defensive measures; it does not require, and should not be answered with, speculative exploitation claims.

The evidence supports four feasibility conclusions:

- AegisGraph can ingest real SMA codebases and convert their application, OS, parser, storage, sync, and E2EE implementation surfaces into structured assessment evidence.
- 577 Industries already has prototype support libraries for workflow orchestration, tamper-evident evidence provenance, tool guardrails, model routing, and agent memory.
- A practical SMABench-style benchmark can be bootstrapped from real-app inventories before adding heavier dynamic harnessing in Phase II.
- The proposal can make deeper claims than a checklist scanner while staying honest about what has been proven, what is pilot evidence, and what remains Phase II work.

## 2. Evidentiary Standard and ASEMA Fit

DARPA's ASEMA opportunity, HR0011SB20254-12, seeks novel approaches for defending secure messaging applications by modeling their security risks and recommending defensive measures. The official page identifies the topic as SBIR: ASEMA, published September 23, 2025, with a May 13, 2026 deadline. The feasibility evidence in this binder is organized to meet the Direct-to-Phase-II expectation for Phase I-like technical reports, prototype evidence, test/measurement data, benchmark artifacts, and comparisons with state-of-the-art practice.

This study uses a conservative interpretation of feasibility. A claim is included as completed evidence only when an artifact exists in the binder. Future capabilities are described as Phase II work. Informational static-analysis findings are not labeled vulnerabilities. This posture makes the package more credible for evaluators because it gives them a clean path from claim to artifact.

## 3. Pilot Methodology

The real-app pilot used two public-source Android secure messaging applications:

| Target | Commit | Source Files | Manifest Rows | Indicator Rows |
| --- | --- | --- | --- | --- |
| Signal Android | 1043851 | 8105 | 284 | 1280 |
| Element X Android | 91d265e6 | 6473 | 35 | 1280 |

The pilot workflow performed the following actions:

- Pinned each target repository to a local commit and wrote a target manifest.
- Parsed Android manifest files for permissions, components, exported status, intent-filter actions, deep-link schemes, hosts, and MIME declarations.
- Scanned source files for ASEMA-relevant implementation indicators: media/file handling, QR and device-linking flows, deep links, push/sync boundaries, storage/keystore use, native/FFI boundaries, WebView surfaces, and E2EE/session implementation code.
- Ran an informational Semgrep rule set focused on exported components, deep links, FileProvider/ContentResolver surfaces, native boundaries, and WebView bridge indicators.
- Wrote machine-readable CSV/JSON artifacts for evaluator inspection.

Semgrep summary:

| Target | Findings | Status | JSON |
| --- | --- | --- | --- |
| signal_android | 239 | Pass | 05_Real_App_Analysis_Pilot/semgrep/signal_android_semgrep.json |
| element_x_android | 162 | Pass | 05_Real_App_Analysis_Pilot/semgrep/element_x_android_semgrep.json |

The outputs are stored under `05_Real_App_Analysis_Pilot/`. They are evidence of workflow feasibility and target-structure extraction, not an assertion that either target contains an exploitable flaw.

## 4. Feasibility Claim Model

The study uses three evidence tiers. Tier 1 evidence is directly executed or generated in this binder: repository check logs, target manifests, inventories, Semgrep outputs, diagrams, PDFs, source citation tables, and checksums. Tier 2 evidence is prior internal work copied into the archive or appendix, including FORGE QBit material and earlier ASEMA proposal drafts. Tier 3 evidence is external context from official topic pages, vendor advisories, government guidance, standards, and public threat research. The proposal may rely on Tier 1 and Tier 2 as feasibility evidence; Tier 3 should be used for motivation, state-of-the-art comparison, and threat examples.

The resulting feasibility claim is narrow but strong: AegisGraph can already perform the first reproducible step in an SMA assessment pipeline. It can select targets, pin source snapshots, extract structured implementation surfaces, preserve logs, create benchmark seeds, and tie proposal claims to evidence. Phase II funds the expansion from structural pilot to deeper analysis, not the invention of the entire workflow from scratch.

## 5. ASEMA Problem Model

AegisGraph models an SMA as a layered implementation system. The graph planes used in this study are:

- Application entrypoints: activities, services, receivers, providers, intent filters, schemes, hosts, MIME declarations, and exported component markers.
- Content and parser surfaces: attachments, images, video, audio, previews, content resolvers, file providers, thumbnails, document APIs, and MIME handling.
- Identity and device surfaces: QR flows, device linking, login tokens, verification codes, session setup, and account-recovery or backup flows.
- Protocol implementation surfaces: E2EE session code, ratchet-related modules, key backup, Matrix/Signal crypto bindings, and post-quantum migration touchpoints.
- Native and FFI boundaries: JNI, Rust/Uniffi, native libraries, and language-runtime crossing points where memory-safety and marshaling assumptions matter.
- Storage and key material: Android Keystore, encrypted preferences, databases, room stores, SQLCipher-like storage, DataStore, and secure-storage abstractions.
- Network, push, and sync: OkHttp/Retrofit/WebSocket use, push-message services, notification handling, app foreground/background sync, and server-mediated update paths.
- Evidence and provenance: logs, manifests, source inventories, Semgrep JSON, benchmark seed definitions, diagrams, and checksums.

This model keeps the work inside ASEMA's assessment and modeling scope. It also avoids confusing app-implementation analysis with cryptographic protocol analysis. Protocol knowledge remains necessary because it tells the assessor where state and key material can influence application behavior, but the proposed work evaluates code, boundaries, harnesses, and evidence.

## 6. Real-App Pilot Results

The pilot produced a structured, repeatable view of two independently implemented secure messaging apps. This directly supports the AegisGraph thesis: the practical SMA attack surface is not one monolithic cryptographic protocol. It is a layered system of Android components, account and device flows, media/rendering surfaces, storage boundaries, push and sync services, native libraries, and E2EE implementation code.

### Signal Android Indicator Counts

| Category | Count |
| --- | --- |
| crypto_session_surface | 160 |
| deep_link_uri | 160 |
| media_file_surface | 160 |
| native_ffi_boundary | 160 |
| network_sync_surface | 160 |
| qr_or_device_linking | 160 |
| storage_keystore | 160 |
| webview_javascript | 160 |
### Element X Android Indicator Counts

| Category | Count |
| --- | --- |
| crypto_session_surface | 160 |
| deep_link_uri | 160 |
| media_file_surface | 160 |
| native_ffi_boundary | 160 |
| network_sync_surface | 160 |
| qr_or_device_linking | 160 |
| storage_keystore | 160 |
| webview_javascript | 160 |

The source-indicator counts are capped per category by the pilot scanner, so a count of 160 means the category was abundant enough to reach the cap. It should be interpreted as breadth evidence, not as a full count of every occurrence in the repository. This cap keeps the pilot auditable and keeps CSVs small enough for an evaluator to inspect.

The component inventory is useful because it gives Phase II a starting graph: app components and external entrypoints are nodes; intent filters, schemes, MIME declarations, and permission-gated interactions are edges; source indicators add weighted annotations for parser, storage, session, and native boundaries. That graph can be compared across SMAs and over time.

### Signal Android Interpretation

Signal Android provides a high-complexity pilot target: a large public Android codebase with many application components, messaging features, media surfaces, native boundaries, and Signal-specific protocol implementation dependencies. The pilot does not judge this complexity as bad; mature messaging apps are necessarily complex. The feasibility point is that the pipeline can reduce that complexity into a reviewable evidence set that supports later graph scoring, harness selection, and regression tracking.

The Signal results are especially useful for proving that AegisGraph can handle a mature production repository rather than a toy benchmark. A Phase II extension can focus on high-value boundaries suggested by the structural pilot: media receive paths, custom URI schemes, native/JNI file and crypto boundaries, notification and sync services, and account/device flows.

### Element X Android Interpretation

Element X Android provides a complementary target because it represents the Matrix ecosystem and uses a different architecture, including the Matrix Rust SDK. That makes it valuable for cross-SMA comparison. It gives the benchmark a second implementation family and helps avoid overfitting the graph schema to Signal's design.

The Element X pilot also demonstrates why native/FFI modeling matters. Modern Android secure messaging apps increasingly rely on Rust, generated bindings, SDK layers, and modular build systems. An assessment framework that only reads Android manifests or only applies generic mobile checklists will miss the structure of those language and SDK boundaries.

### What the Pilot Proves

The pilot proves that AegisGraph can produce the following artifact classes from real code:

- Target manifest with repository URL, branch, commit, license note, retrieval date, and scope.
- Android component inventory with permission and intent-filter metadata.
- Source observation inventory grouped by ASEMA-relevant attack-surface class.
- Static rule logs and machine-readable Semgrep JSON.
- Benchmark seed manifest that can be reused in regression tests.
- Evidence index entries with paths and checksums.

### What the Pilot Does Not Prove

The pilot does not prove exploitability, dynamic reachability, code coverage, server-side behavior, or vulnerability presence. Those require Phase II harnessing, instrumentation, and responsible-disclosure workflows. Keeping this distinction visible is a strength of the package because it prevents feasibility evidence from becoming overclaiming.

## 7. Prior Technical Work

The prior reports and prototype repositories support the feasibility case from the platform side:

- `forge-qbit.pdf` is treated as a prior internal technical report supporting the team's experience with post-quantum security, identity, provenance, and graph-oriented security infrastructure. It is not presented as a public DARPA award.
- `workflow-dag` provides a workflow compiler that can turn repeatable assessment plans into executable DAGs and dependency-checked task graphs.
- `hashchain-audit` provides tamper-evident event logging suitable for preserving evidence provenance across automated assessment runs.
- `tool-guardrails` supports controlled execution, approvals, and bounded tool use, which is necessary when an autonomous security workflow can invoke scanners, build tools, or dynamic harnesses.
- `model-router` and `agent-memory` provide supporting infrastructure for multi-model analysis and persistent analyst context.

Local support-repository checks:

| Repository | Command | Status | Exit | Log |
| --- | --- | --- | --- | --- |
| workflow-dag | npm test | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/workflow-dag_npm_test_2026-05-01.log |
| workflow-dag | npm run build | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/workflow-dag_npm_build_2026-05-01.log |
| workflow-dag | npm run lint | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/workflow-dag_npm_lint_2026-05-01.log |
| hashchain-audit | npm test | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/hashchain-audit_npm_test_2026-05-01.log |
| hashchain-audit | npm run build | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/hashchain-audit_npm_build_2026-05-01.log |
| hashchain-audit | npm run lint | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/hashchain-audit_npm_lint_2026-05-01.log |
| tool-guardrails | npm test | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/tool-guardrails_npm_test_2026-05-01.log |
| tool-guardrails | npm run build | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/tool-guardrails_npm_build_2026-05-01.log |
| tool-guardrails | npm run lint | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/tool-guardrails_npm_lint_2026-05-01.log |
| model-router | npm test | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/model-router_npm_test_2026-05-01.log |
| model-router | npm run build | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/model-router_npm_build_2026-05-01.log |
| model-router | npm run lint | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/model-router_npm_lint_2026-05-01.log |
| agent-memory | npm test | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/agent-memory_npm_test_2026-05-01.log |
| agent-memory | npm run build | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/agent-memory_npm_build_2026-05-01.log |
| agent-memory | npm run lint | Pass | 0 | 04_Feasibility_Evidence_Appendix/03_test_logs/agent-memory_npm_lint_2026-05-01.log |

Every support command is preserved as a raw log. Passing tests and builds do not prove the final ASEMA system exists; they prove that the underlying prototype components are executable and can be checked in a reproducible way. That is the right level of evidence for DP2 feasibility: it shows prior engineering work, software skill, and a credible path for integrating those components into a Phase II prototype.

## 8. SMABench Feasibility

The previous appendix contained candidate benchmark artifacts. This study upgrades that concept with pilot evidence from real public codebases. The first SMABench slice is structural rather than exploit-driven: it asks whether the system can reliably retrieve a target, pin it, extract relevant attack-surface fields, categorize source indicators, run static rules, and package results with provenance.

This is the correct first benchmark because a Phase II system cannot responsibly fuzz or dynamically instrument an SMA until it knows which components, formats, entrypoints, and code boundaries matter. The pilot establishes those primitives and creates seed classes that can later support parser harnessing, state-machine testing, differential conformance checks, and responsible-disclosure workflows.

The Phase II benchmark should expand in four rings. Ring 1 is structural inventory, now demonstrated. Ring 2 is harness selection and seed-corpus construction for message, attachment, link, and device-flow boundaries. Ring 3 is controlled dynamic instrumentation for authorized targets. Ring 4 is cross-version and cross-implementation comparison, where the same graph and benchmark tasks are applied to multiple releases or multiple SMA families.

## 9. State-of-the-Art Comparison

General mobile security tooling, OWASP MASVS-style checklists, dependency scanners, and mobile taint-analysis systems are valuable baselines. They are not sufficient by themselves for ASEMA because the topic is not simply "find generic Android bugs." The relevant attack surface includes E2EE implementation state, linked-device workflows, post-quantum migration surfaces, media receive paths, group and invite behavior, sync boundaries, and the interface between app logic and mobile operating system services.

AegisGraph's feasibility evidence shows an approach that can incorporate those baselines without being limited by them. The graph model can ingest checklist findings, Semgrep results, dependency metadata, and dynamic traces, but it organizes them around SMA-specific entities and flows. That is the beyond-SOTA claim the proposal can safely make: not that existing tools are obsolete, but that they need a messaging-aware assessment layer to become useful for ASEMA.

## 10. DP2 Crosswalk

| DP2 Evidence Need | Binder Evidence | Status |
| --- | --- | --- |
| Technical report / feasibility study | 03_Phase_I_Feasibility_Study/ASEMA_Phase_I_Feasibility_Study.md and .pdf | Completed |
| Prototype design or model | 06_Diagrams_and_Figures/rendered/*.svg; 02_Final_Proposal/ASEMA_DP2_Deep_Technical_Proposal.md | Completed |
| Test and measurement data | 04_Feasibility_Evidence_Appendix/03_test_logs/*.log | Completed for support libraries |
| Benchmark artifacts | 04_Feasibility_Evidence_Appendix/04_benchmark_artifacts/SMABench_pilot_seed_manifest.* | Completed pilot seed |
| Real-world target evidence | 05_Real_App_Analysis_Pilot/manifests, inventories, semgrep logs | Completed public-source pilot |
| SOTA and threat citations | 04_Feasibility_Evidence_Appendix/06_source_citations/source_citations.* | Completed citation set |

## 11. Phase II Acceptance Criteria

A Phase II implementation should be judged by measurable outputs:

- Ingest at least two real-world SMAs and generate reproducible manifests, component inventories, source observations, and evidence indexes.
- Produce an attack-surface graph with documented schema, confidence scores, and traceable source artifacts.
- Demonstrate at least one controlled harness or dynamic trace for an authorized parser, link, device, sync, or media boundary.
- Run SMABench tasks repeatedly and show that results are stable across clean rebuilds.
- Generate defensive recommendations that map from evidence to mitigation, not generic checklist advice.
- Preserve all raw logs, tool versions, target commits, and checksums.

## 12. Limitations and Non-Claims

This study does not claim to have found novel vulnerabilities in Signal or Element X. It does not claim dynamic coverage, exploitability, or server-side access. It does not use closed-source WhatsApp code. It does not perform cryptographic protocol analysis. It treats public advisories about WhatsApp, Apple, Signal, and other threat examples as context for why app-layer implementation assessment matters.

The Phase II proposal should build from this base by adding controlled dynamic instrumentation, parser harnesses, stateful fuzzing, differential conformance tests, graph metrics, and responsible disclosure protocols.

## 13. Conclusion

The feasibility evidence is sufficient to support a credible Direct-to-Phase-II posture: 577 Industries has prototype infrastructure, can run and preserve repeatable technical evidence, can analyze public SMA source at the implementation layer, and can map the resulting artifacts to ASEMA evaluation needs. The strongest proposal narrative is therefore not that AegisGraph has already solved SMA security. It is that AegisGraph has a practical, evidence-backed starting point for measuring and improving understanding of SMA security against real-world app-layer attacks.


## Public Artifact Note

This public version is a sanitized reproducibility artifact. It omits internal proposal drafts, archived originals, cloned target source trees, raw scanner JSON, and local filesystem paths. The authoritative submission binder remains internal to 577 Industries; this repository provides public evidence that selected feasibility artifacts can be inspected and regenerated.
