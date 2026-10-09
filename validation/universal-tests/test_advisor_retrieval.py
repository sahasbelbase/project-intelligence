"""
Project Intelligence — Retrieval-Augmented Generation (RAG) Advisor Tests
Evaluates that the precomputed BM25 index matches repository capabilities and
achieves >= 90% Top-3 precision across canonical developer project scenarios.
Zero external dependencies (Python standard library only).
"""

import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has",
    "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
    "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over",
    "own", "same", "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str):
    if not text:
        return []
    clean = re.sub(r"[^a-z0-9_\-\s]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1 and t not in STOP_WORDS]


class TestAdvisorRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("node") is None:
            raise unittest.SkipTest("node is not installed")
        subprocess.run(["node", str(WEB / "build-data.js")], check=True, capture_output=True)
        text = (WEB / "data.js").read_text(encoding="utf-8")
        data = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
        cls.index = data.get("advisorIndex", {})
        cls.docs = cls.index.get("docs", [])
        cls.df = cls.index.get("df", {})
        cls.avg_doc_len = cls.index.get("avgDocLen", 30.0)
        cls.total_docs = cls.index.get("totalDocs", len(cls.docs))

    def test_advisor_index_structure(self):
        self.assertGreater(self.total_docs, 70, "Advisor index should contain skills, agents, councils, and gates")
        self.assertGreater(len(self.df), 100, "Inverted DF index should contain extensive vocabulary")

        for d in self.docs:
            self.assertIn("id", d)
            self.assertIn("kind", d)
            self.assertIn("name", d)
            self.assertIn("summary", d)
            self.assertIn("command", d)
            self.assertIn("tf", d)
            self.assertGreater(d.get("docLen", 0), 0)

    def bm25_search(self, query: str, top_k: int = 5):
        q_tokens = tokenize(query)
        k1 = 1.2
        b = 0.75
        n = self.total_docs
        avgdl = self.avg_doc_len or 30.0

        scores = []
        for doc in self.docs:
            score = 0.0
            tf = doc.get("tf", {})
            doc_len = doc.get("docLen", avgdl)

            for term in q_tokens:
                if term in tf:
                    term_df = self.df.get(term, 1)
                    idf = math.log((n - term_df + 0.5) / (term_df + 0.5) + 1.0)
                    f = tf[term]
                    num = f * (k1 + 1.0)
                    denom = f + k1 * (1.0 - b + b * (doc_len / avgdl))
                    score += idf * (num / denom)

            if score > 0:
                scores.append({"id": doc["id"], "kind": doc["kind"], "name": doc["name"], "score": score})

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

    def test_bm25_retrieval_benchmarks(self):
        scenarios = [
            (
                "We have an unmaintained legacy codebase with raw SQL and want to safely reverse engineer and document domain entities",
                ["legacy-codebase-knowledge-base", "existing-project-analysis", "safe-refactoring-and-migration"]
            ),
            (
                "We need to migrate our database schema without downtime, preserving data integrity and supporting rollback",
                ["database-migration-and-schema-evolution", "safe-refactoring-and-migration"]
            ),
            (
                "Build a design system with geometric tokens, typography scale, responsive layouts and WCAG AA contrast",
                ["design-system-engineering", "baseline-ui", "fixing-accessibility"]
            ),
            (
                "Synchronize OpenAPI contracts with server routes and prevent breaking API changes in pull requests",
                ["api-contract-and-openapi-spec"]
            ),
            (
                "We want to audit our repository for hardcoded secrets, injection vectors, and anti-slop violations",
                ["security-audit-and-hardening", "independent-review", "thermo-nuclear-review"]
            ),
            (
                "We have a raw feature idea and need to question assumptions and write a concrete PRD with tickets",
                ["idea-to-prd", "requirements-analysis"]
            ),
            (
                "Runtime profile flamegraph latency budget N+1 query memory leak profiling",
                ["runtime-performance-profiling"]
            ),
            (
                "Automate our CI/CD pipeline with GitHub Actions container build and quality gates",
                ["ci-cd-pipeline-engineering", "devops-automation-engineer"]
            ),
            (
                "Generate automated test cases, edge cases, and unit test assertions",
                ["test-case-generation", "testing-and-verification"]
            ),
            (
                "Conduct adversarial review of git diffs to detect code bloat, fake mocks, and slop",
                ["independent-review", "thermo-nuclear-review"]
            ),
            (
                "Translate skills and rules into Claude Code, Antigravity, and Copilot CLI adapters",
                ["cross-platform-adaptation"]
            ),
            (
                "Author a business case proposal with ROI valuation, cost-benefit trade-offs, and risks",
                ["business-case"]
            ),
            (
                "Feature prioritization scoring matrix and MVP scope boundary delineation",
                ["feature-prioritization"]
            ),
            (
                "Postmortem failure recovery analysis, root cause fix, and preventive guardrails",
                ["failure-recovery-and-improvement"]
            ),
            (
                "Phase planning work breakdown structure and task dependency mapping",
                ["phase-planning", "project-planning"]
            ),
        ]

        passed = 0
        total = len(scenarios)

        for query, expected_any in scenarios:
            with self.subTest(query=query[:40]):
                results = self.bm25_search(query, top_k=3)
                top_ids = [r["id"] for r in results]
                matched = any(exp in top_ids for exp in expected_any)
                if matched:
                    passed += 1
                self.assertTrue(
                    matched,
                    f"Query '{query}' expected one of {expected_any} in Top-3, but got {top_ids}"
                )

        precision = passed / total
        self.assertGreaterEqual(precision, 0.90, f"Benchmark precision was {precision:.1%}, required >= 90%")

    def test_advisor_deterministic_reproducibility(self):
        query = "Refactor database schema safely"
        run1 = self.bm25_search(query, top_k=5)
        run2 = self.bm25_search(query, top_k=5)
        self.assertEqual(run1, run2, "BM25 retrieval must be strictly deterministic across calls")


if __name__ == "__main__":
    unittest.main()
