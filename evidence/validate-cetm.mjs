#!/usr/bin/env node

// validate-cetm.mjs — validates the Claim → Evidence Traceability Matrix (CETM)
// at 04_evidence/v0.3/cetm.json. Every claim row must carry a status of A, E,
// or P (anchored / engineering-stream-pending / planned). Status I (implicit /
// unanchored) is forbidden. Evidence-artifact paths that begin with a known
// in-package directory must resolve to a file on disk; missing paths are
// reported but do not always fail the run (status E rows are allowed to
// reference engineering-stream artifacts that don't exist yet — those are
// reported as "pending E").

import { readFileSync, existsSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, normalize, relative } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const PACKAGE_DIR = join(SCRIPT_DIR, "..");
const DEFAULT_CETM_PATH = join(PACKAGE_DIR, "04_evidence/v0.3/cetm.json");

// In-package directories where a relative evidence_artifact path is expected
// to resolve. If the path doesn't begin with one of these prefixes, we treat
// it as an external/engineering-stream reference and skip the on-disk check.
const IN_PACKAGE_PREFIXES = [
  "01_master_proposal/",
  "02_figures_and_storyboard/",
  "03_validation_commercialization_compliance/",
  "04_evidence/",
  "05_verification/",
  "06_rendered_outputs/",
];

const VALID_STATUSES = new Set(["A", "E", "P"]);

function fail(message) {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

// Strip JSON-pointer fragments (#foo), query params (?foo), and the trailing
// line-range or section markers (`:121-132`, `:§14`, `:§12.5.1`) used to
// pinpoint a specific span inside a markdown file. Also trims any
// parenthetical commentary that humans tend to inline (e.g.
// "evidence.json (per-thread structure)").
function cleanArtifactPath(raw) {
  let p = String(raw).split("#")[0].split("?")[0];
  // Drop everything from the first " (" onwards (parenthetical commentary).
  const parenIdx = p.indexOf(" (");
  if (parenIdx !== -1) p = p.slice(0, parenIdx);
  // Drop trailing :LINE-LINE, :LINE, :§..., :§...n.m, :§...-... markers.
  // Anything after the LAST `:` that does NOT itself contain `/` is a
  // line/section marker.
  const lastColon = p.lastIndexOf(":");
  if (lastColon !== -1) {
    const tail = p.slice(lastColon + 1);
    if (!tail.includes("/")) {
      // Confirm the tail looks like a line range or section anchor.
      if (/^(?:\d+(?:-\d+)?|§[\w.\-]+)/u.test(tail)) {
        p = p.slice(0, lastColon);
      }
    }
  }
  return p.trim();
}

function isInPackagePath(p) {
  if (!p) return false;
  if (isAbsolute(p)) return false;
  return IN_PACKAGE_PREFIXES.some((prefix) => p.startsWith(prefix));
}

function pathExists(p) {
  // Glob suffixes (e.g. "04_evidence/v0.3/*") are treated as references to
  // their parent directory.
  let cleaned = p;
  if (cleaned.endsWith("/*") || cleaned.endsWith("/")) {
    cleaned = cleaned.replace(/\/?\*?$/, "");
  }
  if (!cleaned) return false;
  const abs = isAbsolute(cleaned) ? cleaned : join(PACKAGE_DIR, cleaned);
  try {
    statSync(abs);
    return true;
  } catch {
    return false;
  }
}

function main() {
  const cetmPath = process.argv[2] || DEFAULT_CETM_PATH;

  if (!existsSync(cetmPath)) {
    fail(`CETM file not found at ${cetmPath}`);
  }

  let cetm;
  try {
    cetm = readJson(cetmPath);
  } catch (err) {
    fail(`Could not parse CETM JSON at ${cetmPath}: ${err.message}`);
  }

  if (!Array.isArray(cetm.claims)) {
    fail("CETM JSON missing top-level 'claims' array");
  }

  const issues = [];
  const counts = { A: 0, E: 0, P: 0, other: 0 };
  const ePending = [];
  const pPlanned = [];
  const missingPaths = [];

  for (const row of cetm.claims) {
    const id = row.claim_id || "<no claim_id>";

    if (!row.claim_id) {
      issues.push(`Row missing claim_id: ${JSON.stringify(row).slice(0, 120)}`);
      continue;
    }
    if (!row.source_location) {
      issues.push(`${id} missing source_location`);
    }
    if (!row.claim_text) {
      issues.push(`${id} missing claim_text`);
    }
    if (!row.status) {
      issues.push(`${id} missing status`);
      counts.other += 1;
      continue;
    }
    if (!VALID_STATUSES.has(row.status)) {
      // The forbidden case: status "I" or any other value.
      issues.push(
        `${id} has status="${row.status}" — must be one of A, E, P (status I or unspecified is forbidden)`,
      );
      counts.other += 1;
      continue;
    }

    counts[row.status] += 1;

    if (row.status === "E") {
      ePending.push({
        id,
        owner: row.owner_stream || "<unknown stream>",
        artifact: row.evidence_artifact,
      });
    } else if (row.status === "P") {
      pPlanned.push({
        id,
        owner: row.owner_stream || "<unknown stream>",
      });
    }

    // verification_command rule: if present, must be a non-empty string.
    if ("verification_command" in row && row.verification_command !== null) {
      if (
        typeof row.verification_command !== "string" ||
        row.verification_command.trim().length === 0
      ) {
        issues.push(
          `${id} has empty verification_command (must be null or non-empty string)`,
        );
      }
    }

    // evidence_artifact rule: if present, status A rows that point to an
    // in-package path must resolve on disk. Status E + P rows are allowed to
    // reference paths that don't exist yet, but if their evidence_artifact
    // points to an in-package path we still report the missing file as a
    // soft warning.
    if (row.evidence_artifact) {
      // Multi-path values (separated by " + " or "+") get exploded.
      const parts = String(row.evidence_artifact)
        .split(/\s*\+\s*/)
        .map((s) => cleanArtifactPath(s))
        .filter(Boolean);
      for (const part of parts) {
        if (isInPackagePath(part) && !pathExists(part)) {
          if (row.status === "A") {
            issues.push(
              `${id} status=A but evidence_artifact path '${part}' does not exist on disk`,
            );
          } else {
            missingPaths.push({ id, status: row.status, path: part });
          }
        }
      }
    }
  }

  // Emit a structured summary regardless of pass/fail.
  const summary = {
    cetm_path: relative(PACKAGE_DIR, cetmPath),
    total_claims: cetm.claims.length,
    counts,
    e_pending: ePending,
    p_planned: pPlanned,
    in_package_missing_paths_for_E_or_P_rows: missingPaths,
    issues_count: issues.length,
  };

  console.log(JSON.stringify(summary, null, 2));

  if (issues.length > 0) {
    console.error(`\nValidation issues (${issues.length}):`);
    for (const i of issues) console.error(`  - ${i}`);
    process.exit(1);
  }

  if (counts.other > 0) {
    process.exit(1);
  }

  // success
}

main();
