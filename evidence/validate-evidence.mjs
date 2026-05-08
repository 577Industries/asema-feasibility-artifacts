#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const PACKAGE_DIR = join(SCRIPT_DIR, "..");
const EVIDENCE_PATH = join(PACKAGE_DIR, "04_evidence/v0.3/aegisgraph-v0.3-evidence.json");
const CHECKSUM_PATH = join(PACKAGE_DIR, "04_evidence/v0.3/checksums.sha256");
const SAFETY_SCAN_DIRS = [
  "01_master_proposal",
  "02_figures_and_storyboard",
  "03_validation_commercialization_compliance",
  "04_evidence",
];

const REQUIRED_SCORE_KEYS = {
  remote_reachability: 15,
  attacker_controllability: 12,
  parser_media_link_device_complexity: 12,
  sensitive_boundary_crossing: 14,
  state_session_group_pq_sensitivity: 10,
  evidence_strength: 10,
  unvalidated_dynamic_gap: 8,
  dependency_exposure: 6,
  mitigation_leverage: 8,
  reproducibility_confidence: 5,
};

const REQUIRED_TOOLS = [
  "Semgrep",
  "Android manifest review",
  "SBOM/dependency snapshot",
  "CodeQL/SARIF",
  "MobSF/mobsfscan",
  "Manual review",
  "AegisGraph",
];

const REQUIRED_RECOMMENDATION_FIELDS = [
  "id",
  "category",
  "graph_refs",
  "evidence_refs",
  "source_file_anchors",
  "implementation_hint",
  "expected_effect",
  "residual_risk",
  "effort_estimate",
  "standards_mapping_caveat",
];

const FORBIDDEN_PATTERNS = [
  { name: "private local path", regex: /\/home\/[A-Za-z0-9._-]+\// },
  { name: "OpenAI-style secret", regex: /\bsk-[A-Za-z0-9_-]{20,}\b/ },
  { name: "private key block", regex: /BEGIN [A-Z ]*PRIVATE KEY/ },
  { name: "credential assignment", regex: /\b(password|passwd|secret|token)\s*=\s*['"][^'"]{8,}/i },
  { name: "raw source redistribution marker", regex: /BEGIN TARGET SOURCE|RAW TARGET SOURCE:/i },
  { name: "static-only vulnerability claim", regex: /confirmed vulnerability|exploitable vulnerability|exploit reproduced/i },
  { name: "live target probing claim", regex: /performed live service probing|production probing completed|real user data collected/i },
];

function fail(message) {
  throw new Error(message);
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function walkFiles(dir) {
  const files = [];
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      files.push(...walkFiles(path));
    } else {
      files.push(path);
    }
  }
  return files;
}

function validateScores(evidence) {
  const requiredKeys = Object.keys(REQUIRED_SCORE_KEYS);

  for (const thread of evidence.graph_threads) {
    const vector = thread.score_vector;
    if (!vector || typeof vector !== "object") {
      fail(`${thread.id} has no score_vector`);
    }

    const actualKeys = Object.keys(vector).sort();
    const expectedKeys = [...requiredKeys].sort();
    if (actualKeys.join(",") !== expectedKeys.join(",")) {
      fail(`${thread.id} score_vector keys differ from required score model`);
    }

    const total = requiredKeys.reduce((sum, key) => {
      const value = vector[key];
      const max = REQUIRED_SCORE_KEYS[key];
      if (!Number.isFinite(value) || value < 0 || value > max) {
        fail(`${thread.id} score_vector.${key}=${value} outside 0..${max}`);
      }
      return sum + value;
    }, 0);

    if (thread.score_total !== total) {
      fail(`${thread.id} score_total ${thread.score_total} does not equal vector sum ${total}`);
    }
  }
}

function validateTargets(evidence) {
  const targets = evidence.targets || [];
  if (targets.length < 2) {
    fail("Expected at least two real public-source targets");
  }

  for (const target of targets) {
    if (!target.commit || !/^[a-f0-9]{40}$/.test(target.commit)) {
      fail(`${target.id} has no pinned 40-character commit`);
    }
    if (!Array.isArray(target.path_classes) || target.path_classes.length < 6) {
      fail(`${target.id} has fewer than six ASEMA path classes`);
    }
    const threadCount = evidence.graph_threads.filter((thread) => thread.target_id === target.id).length;
    if (threadCount < 3) {
      fail(`${target.id} has fewer than three concrete graph path threads`);
    }
  }
}

function validateRecommendations(evidence) {
  if (!Array.isArray(evidence.recommendations) || evidence.recommendations.length !== 12) {
    fail("Expected exactly 12 recommendation records");
  }

  for (const recommendation of evidence.recommendations) {
    for (const field of REQUIRED_RECOMMENDATION_FIELDS) {
      if (!(field in recommendation)) {
        fail(`${recommendation.id || "recommendation"} missing ${field}`);
      }
    }
    if (!Array.isArray(recommendation.graph_refs) || recommendation.graph_refs.length === 0) {
      fail(`${recommendation.id} has no graph_refs`);
    }
    if (!Array.isArray(recommendation.evidence_refs) || recommendation.evidence_refs.length === 0) {
      fail(`${recommendation.id} has no evidence_refs`);
    }
    if (!Array.isArray(recommendation.source_file_anchors) || recommendation.source_file_anchors.length === 0) {
      fail(`${recommendation.id} has no source_file_anchors`);
    }
  }
}

function validateSota(evidence) {
  const toolNames = new Set((evidence.sota_matrix || []).map((entry) => entry.tool));
  for (const tool of REQUIRED_TOOLS) {
    if (!toolNames.has(tool)) {
      fail(`SOTA matrix missing ${tool}`);
    }
  }
}

function validateSafety() {
  const files = SAFETY_SCAN_DIRS.flatMap((dir) => walkFiles(join(PACKAGE_DIR, dir)))
    .filter((path) => !path.endsWith("checksums.sha256"));
  const violations = [];

  for (const file of files) {
    const rel = relative(PACKAGE_DIR, file);
    const text = readFileSync(file, "utf8");
    for (const pattern of FORBIDDEN_PATTERNS) {
      if (pattern.regex.test(text)) {
        violations.push(`${rel}: ${pattern.name}`);
      }
    }
  }

  if (violations.length > 0) {
    fail(`Safety scan failed:\n${violations.join("\n")}`);
  }
}

function checksums() {
  return walkFiles(PACKAGE_DIR)
    .filter((path) => !path.endsWith("checksums.sha256"))
    .sort()
    .map((path) => {
      const rel = relative(PACKAGE_DIR, path);
      const digest = createHash("sha256").update(readFileSync(path)).digest("hex");
      return `${digest}  ${rel}`;
    })
    .join("\n") + "\n";
}

function main() {
  const writeChecksums = process.argv.includes("--write-checksums");
  const evidence = readJson(EVIDENCE_PATH);

  if (evidence.release?.version !== "v0.3") {
    fail("Evidence release is not v0.3");
  }

  validateTargets(evidence);
  validateScores(evidence);
  validateRecommendations(evidence);
  validateSota(evidence);
  validateSafety();

  if (writeChecksums) {
    writeFileSync(CHECKSUM_PATH, checksums());
  }

  const summary = {
    release: evidence.release.version,
    targets: evidence.targets.length,
    graph_threads: evidence.graph_threads.length,
    recommendations: evidence.recommendations.length,
    sota_tools: evidence.sota_matrix.length,
    safety_scan: "passed",
    checksums_written: writeChecksums,
  };

  console.log(JSON.stringify(summary, null, 2));
}

main();
