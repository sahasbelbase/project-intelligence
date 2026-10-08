"""
Project Intelligence — Evidence Classifier & Honesty Validation Tests
Tests epistemic categorization, honesty auditing, and fact-vs-assumption separation.
Zero external dependencies (Python standard library only).
"""

import unittest
from pathlib import Path
import json

from core.decision.evidence import (
    EvidenceCategory,
    EvidenceItem,
    classify_statement,
    validate_evidence_honesty,
    separate_facts_and_assumptions,
    format_evidence_report,
    check_deliverable_evidence_separation
)


class TestEvidenceClassifier(unittest.TestCase):

    def test_evidence_category_enum(self):
        """Verify all 6 canonical epistemic categories exist and have valid string representations."""
        expected = {
            "VERIFIED_FACT",
            "ASSUMPTION",
            "ESTIMATE",
            "UNKNOWN",
            "RECOMMENDATION",
            "RISK"
        }
        actual = {c.value for c in EvidenceCategory}
        self.assertEqual(expected, actual)

    def test_evidence_item_dataclass_and_serialization(self):
        """Test EvidenceItem instantiation, serialization, deserialization, and verification status."""
        item = EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement="All 67 tests passing with exit code 0",
            source="validation/test_runner.py",
            confidence=1.0,
            basis="Empirical test execution log"
        )
        self.assertTrue(item.is_verified())

        data = item.to_dict()
        self.assertEqual(data["category"], "VERIFIED_FACT")
        self.assertEqual(data["statement"], "All 67 tests passing with exit code 0")
        self.assertEqual(data["source"], "validation/test_runner.py")
        self.assertEqual(data["confidence"], 1.0)

        # Roundtrip from dict
        reconstructed = EvidenceItem.from_dict(data)
        self.assertEqual(reconstructed.category, EvidenceCategory.VERIFIED_FACT)
        self.assertEqual(reconstructed.statement, item.statement)
        self.assertEqual(reconstructed.source, item.source)
        self.assertEqual(reconstructed.confidence, item.confidence)
        self.assertTrue(reconstructed.is_verified())

    def test_unverified_fact_without_source(self):
        """A VERIFIED_FACT item without a valid source must fail is_verified()."""
        item = EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement="Performance improved by 50%",
            source="",  # Missing source
            confidence=1.0
        )
        self.assertFalse(item.is_verified())

    def test_classify_statement_explicit_tags(self):
        """Test classification with explicit tag markers."""
        item_fact = classify_statement("[VERIFIED_FACT] Commit hash is e033682f", source="git rev-parse HEAD")
        self.assertEqual(item_fact.category, EvidenceCategory.VERIFIED_FACT)
        self.assertIn("Commit hash", item_fact.statement)

        item_shorthand = classify_statement("FACT: Repository root is clean", source="git status")
        self.assertEqual(item_shorthand.category, EvidenceCategory.VERIFIED_FACT)

        item_assumption = classify_statement("[ASSUMPTION] Users will prefer CLI over GUI")
        self.assertEqual(item_assumption.category, EvidenceCategory.ASSUMPTION)

        item_estimate = classify_statement("[ESTIMATE] Migration will take 4-6 hours")
        self.assertEqual(item_estimate.category, EvidenceCategory.ESTIMATE)

        item_unknown = classify_statement("[UNKNOWN] Peak concurrent memory consumption")
        self.assertEqual(item_unknown.category, EvidenceCategory.UNKNOWN)

        item_tbd = classify_statement("[TBD] Production database endpoint")
        self.assertEqual(item_tbd.category, EvidenceCategory.UNKNOWN)

        item_rec = classify_statement("[RECOMMENDATION] Adopt SQLite for local durable storage")
        self.assertEqual(item_rec.category, EvidenceCategory.RECOMMENDATION)

        item_risk = classify_statement("[RISK] Potential deadlocks during simultaneous subagent writes")
        self.assertEqual(item_risk.category, EvidenceCategory.RISK)

    def test_classify_statement_natural_heuristics(self):
        """Test classification based on semantic markers and linguistic cues."""
        fact = classify_statement("Executed tests with exit code 0", source="test_runner.py")
        self.assertEqual(fact.category, EvidenceCategory.VERIFIED_FACT)

        assumption = classify_statement("We assume developer machines have at least 16GB RAM")
        self.assertEqual(assumption.category, EvidenceCategory.ASSUMPTION)

        likely = classify_statement("The system is likely to experience high latency during peak")
        self.assertEqual(likely.category, EvidenceCategory.ASSUMPTION)

        estimate = classify_statement("Execution duration is approximately 25ms per check")
        self.assertEqual(estimate.category, EvidenceCategory.ESTIMATE)

        unknown = classify_statement("Target deployment environment is unclear and to be determined")
        self.assertEqual(unknown.category, EvidenceCategory.UNKNOWN)

        recommendation = classify_statement("We should enforce strict schema validation on all contracts")
        self.assertEqual(recommendation.category, EvidenceCategory.RECOMMENDATION)

        risk = classify_statement("There is a severe risk of data loss if broad deletes are run")
        self.assertEqual(risk.category, EvidenceCategory.RISK)

    def test_validate_evidence_honesty_compliant(self):
        """Honest evidence items pass validation with zero violations."""
        items = [
            EvidenceItem(
                category=EvidenceCategory.VERIFIED_FACT,
                statement="Schema validation suite passed",
                source="validation/schema-tests/test_schemas.py",
                confidence=1.0
            ),
            EvidenceItem(
                category=EvidenceCategory.ASSUMPTION,
                statement="Repository size is under 1GB",
                confidence=0.7
            ),
            EvidenceItem(
                category=EvidenceCategory.UNKNOWN,
                statement="Customer peak request distribution",
                confidence=0.1
            )
        ]
        is_honest, violations = validate_evidence_honesty(items)
        self.assertTrue(is_honest)
        self.assertEqual(len(violations), 0)

    def test_validate_evidence_honesty_violations(self):
        """Validate detection of dishonest evidence claims."""
        # 1. Fact without source
        dishonest_fact = EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement="System handles 10,000 req/s",
            source="",  # Empty source
            confidence=1.0
        )
        is_honest, violations = validate_evidence_honesty([dishonest_fact])
        self.assertFalse(is_honest)
        self.assertTrue(any("lacks reproducible source" in v for v in violations))

        # 2. Speculation masquerading as fact
        masquerading_fact = EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement="Users will probably never encounter this corner case",
            source="spec.md",
            confidence=1.0
        )
        is_honest, violations = validate_evidence_honesty([masquerading_fact])
        self.assertFalse(is_honest)
        self.assertTrue(any("Speculative language masquerading as VERIFIED_FACT" in v for v in violations))

        # 3. Overconfident unknown
        overconfident_unknown = EvidenceItem(
            category=EvidenceCategory.UNKNOWN,
            statement="Future cloud hosting costs",
            confidence=0.9  # Excessive confidence on unknown
        )
        is_honest, violations = validate_evidence_honesty([overconfident_unknown])
        self.assertFalse(is_honest)
        self.assertTrue(any("excessive confidence" in v for v in violations))

        # 4. Overconfident assumption
        overconfident_assumption = EvidenceItem(
            category=EvidenceCategory.ASSUMPTION,
            statement="All platforms implement identical POSIX signals",
            confidence=1.0  # Cannot claim 1.0 without empirical proof
        )
        is_honest, violations = validate_evidence_honesty([overconfident_assumption])
        self.assertFalse(is_honest)
        self.assertTrue(any("ASSUMPTION item claims 100% confidence" in v for v in violations))

    def test_separate_facts_and_assumptions(self):
        """Ensure partitioning into distinct buckets works reliably."""
        items = [
            EvidenceItem(category=EvidenceCategory.VERIFIED_FACT, statement="Fact 1", source="src"),
            EvidenceItem(category=EvidenceCategory.ASSUMPTION, statement="Assumption 1"),
            EvidenceItem(category=EvidenceCategory.ESTIMATE, statement="Estimate 1"),
            EvidenceItem(category=EvidenceCategory.UNKNOWN, statement="Unknown 1"),
            EvidenceItem(category=EvidenceCategory.RISK, statement="Risk 1"),
            EvidenceItem(category=EvidenceCategory.RECOMMENDATION, statement="Rec 1"),
        ]
        buckets = separate_facts_and_assumptions(items)
        self.assertEqual(len(buckets["facts"]), 1)
        self.assertEqual(len(buckets["assumptions"]), 1)
        self.assertEqual(len(buckets["estimates"]), 1)
        self.assertEqual(len(buckets["unknowns"]), 1)
        self.assertEqual(len(buckets["risks"]), 1)
        self.assertEqual(len(buckets["recommendations"]), 1)

    def test_format_evidence_report(self):
        """Test formatting of evidence report adhering to BL-001 (no decorative emoji)."""
        items = [
            EvidenceItem(category=EvidenceCategory.VERIFIED_FACT, statement="Fact A", source="log.txt"),
            EvidenceItem(category=EvidenceCategory.ASSUMPTION, statement="Assumption B", confidence=0.6)
        ]
        report = format_evidence_report(items, title="Test Audit Report")
        self.assertIn("# Test Audit Report", report)
        self.assertIn("## 1. Verified Facts (Empirical Evidence)", report)
        self.assertIn("## 2. Documented Assumptions", report)
        self.assertIn("- Fact A [Source: log.txt]", report)
        self.assertIn("- Assumption B (Confidence: 0.60)", report)
        # Ensure zero decorative emoji in formatted report
        forbidden_codepoints = [chr(0x1F680), chr(0x2728), chr(0x1F389), chr(0x1F9E0), chr(0x1F916), chr(0x1F4A1), chr(0x1F525)]
        for emoji in forbidden_codepoints:
            self.assertNotIn(emoji, report)

    def test_check_deliverable_evidence_separation(self):
        """Test auditing deliverable text for clear separation of facts and assumptions."""
        compliant_doc = """
# System Verification Report

## 1. Verified Facts
- [FACT] Process exited with exit code 0.
- [FACT] 12 schemas validated against Draft-07.

## 2. Documented Assumptions
- [ASSUMPTION] System runs on macOS and Linux.
"""
        audit_res = check_deliverable_evidence_separation(compliant_doc)
        self.assertTrue(audit_res["has_separated_sections"])
        self.assertTrue(audit_res["is_compliant"])

        non_compliant_doc = """
# Feature Summary
The feature is working great. We assume users will love it. Probably no performance issues.
"""
        audit_res_fail = check_deliverable_evidence_separation(non_compliant_doc)
        self.assertFalse(audit_res_fail["has_separated_sections"])
        self.assertFalse(audit_res_fail["is_compliant"])


if __name__ == "__main__":
    unittest.main()
