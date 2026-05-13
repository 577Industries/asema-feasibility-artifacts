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
