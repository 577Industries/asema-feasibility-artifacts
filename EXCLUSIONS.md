# What's Excluded From This Sanitized Release

The following are intentionally NOT in this public-sanitized export:

## v0.3 baseline exclusions
- `exports/private-submission/**`
- `reprochain/corpora-private/**`
- undisclosed findings
- raw target source
- raw scanner dumps
- credentials
- live dynamic traces

## v0.4 additions (per plan §10 + sanitize-check v0.4 rules)
- `aegisgraph/disclosure/ledger.jsonl` (engineering-private hash-chained
  disclosure ledger; only v0.5+ public projection events ever appear in
  `disclosure_events[]`)
- `aegisgraph/disclosure/vendor_registry.yaml` (vendor security contact
  routing table; blocked by `vendor_contact_in_public_artifact` rule)
- `aegisgraph/disclosure/outgoing/` (rendered outbound vendor letters,
  CVE request drafts — engineering-private)
- `aegisgraph/disclosure/templates/` (Jinja2 source templates remain on
  engineering side; only sanitized renders ever reach a public artifact)
- `aegisgraph/invariants/library/codeql/**` and `library/semgrep/**`
  (queries themselves stay engineering-private; SARIF result bodies stay
  engineering-private — only AG-IV-* records would surface publicly,
  with locations limited to repo_url + commit + path + start_line per
  sanitize-check Rule 8)
- `reprochain/corpora-private/**` (private fuzz corpora; sanitize-check
  blocks any leak of `bytes_b64`, `payload`, `raw_bytes`, `raw_witness`,
  `raw_corpus_input`, `raw_reproducer`)
- `harnessgen/runs-private/**` (24h fuzz run artifacts; crash bytes
  redacted to hashes via Rule 9; raw inputs blocked by Rule 5)
- raw stack traces with line numbers (blocked by `raw_stack_trace`
  pattern; only `stack_trace_hash` + `stack_trace_summary` allowed)
- `source_snippet` fields longer than 256 chars (blocked by
  `target_source_snippet` pattern; SARIF location bodies use uri +
  startLine only)
- pasted attacker URLs or attack payloads inside
  `cross_target_candidate.structural_description` (blocked by
  `crosssma_target_redistribution`; witness-hash refs only)
- records carrying `claim_state == "reviewed_embargoed"` in any
  sanitized_candidate document (blocked by `disclosure_embargoed_leak`)

## v1.0 additions (per plan §10 + reviewer-workbench + M14 demo dry-run)
- `aegisgraph/workbench/promotions/**` (engineering-private reviewer
  workbench promotion records; only sanitized reviewer-packet manifest
  metadata appears publicly via `make reviewer-packet`, never the
  raw promotion ledger or reviewer notes)
- `exports/m14-demo-dryrun/**` (engineering-private M14 demo dry-run
  outputs; only the structural `m14_demo_dryrun_summary` block —
  step names, status counts, skip reasons — appears in this public
  projection. No payload bytes, no raw stack traces, no source
  snippets, no reviewer notes redistributed)
- `aegisgraph/invariants/ground_truth/**` (engineering-private
  ground-truth fixture outputs from M7; demo-vulnerable-app SARIF
  bodies remain engineering-private; only the InvariantCheck
  production count surfaces publicly)
- `aegisgraph/harnessgen/scaffolds/private/**` (engineering-private
  HarnessGen scaffold private inputs / corpus references; only
  `discovery_runs[]` summaries appear publicly per Rule 5 + Rule 9)
- `aegisgraph/crosssma/validations/raw/**` (engineering-private
  CrossSMA validation working files; only the validated cell record
  AG-XSMA-VALIDATED-SIG-GP-001-ELX with structural metadata appears
  publicly per the `crosssma_target_redistribution` rule)
