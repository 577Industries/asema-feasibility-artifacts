import unittest
from pathlib import Path

from tools.aegisgraph import build_release, verify_release
from tools.aegisgraph.scoring import stable_score


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseTests(unittest.TestCase):
    def test_demo_build_and_verify(self):
        build_release(ROOT, ROOT / "out" / "test-demo")
        result = verify_release(ROOT, write_reports=False)
        self.assertTrue(result["ok"], result["errors"])
        self.assertGreaterEqual(result["graph_evidence_coverage"], 0.98)


    def test_scoring_deterministic(self):
        self.assertEqual(stable_score("parser"), stable_score("parser"))
        self.assertLess(stable_score("parser", mitigated=True), stable_score("parser"))


    def test_static_records_do_not_claim_vulnerabilities(self):
        build_release(ROOT, ROOT / "out" / "test-demo")
        ledger = (ROOT / "evidence" / "public_ledger.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("vulnerability_claim", ledger)


if __name__ == "__main__":
    unittest.main()
