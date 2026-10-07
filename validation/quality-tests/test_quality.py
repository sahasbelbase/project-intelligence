"""
Project Intelligence — Quality Evaluator Tests
Tests anti-slop detection, mandatory baseline enforcement, quality profiles, and verification honesty.
"""

import unittest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.quality.evaluator import QualityEvaluator, QualityError


class TestQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = QualityEvaluator()

    def test_mandatory_baseline_rules_declared(self):
        """Ensure all 7 mandatory baseline rules are defined."""
        rules = self.evaluator.mandatory_baseline.get("rules", [])
        self.assertEqual(len(rules), 7)
        rule_ids = [r["ruleId"] for r in rules]
        for expected_id in ["BL-001", "BL-002", "BL-003", "BL-004", "BL-005", "BL-006", "BL-007"]:
            self.assertIn(expected_id, rule_ids)

    def test_anti_slop_detects_forbidden_placeholders(self):
        """Ensure evaluator catches lazy AI placeholders."""
        slop_code = """
        def fetch_user_data(user_id):
            # TODO: implement later
            return fake_production_data
        """
        violations = self.evaluator.evaluate_anti_slop(slop_code)
        self.assertGreaterEqual(len(violations), 2)
        violation_text = " ".join(violations).lower()
        self.assertIn("todo: implement later", violation_text)
        self.assertIn("fake_production_data", violation_text)

    def test_anti_slop_detects_decorative_emoji(self):
        """Ensure evaluator catches decorative emojis in technical artifacts."""
        emoji_code = 'print("🚀 Starting the rocket ship! ✨ Great job! 🎉")'
        violations = self.evaluator.evaluate_anti_slop(emoji_code)
        self.assertTrue(any("decorative emoji" in v for v in violations))

    def test_anti_slop_passes_clean_code(self):
        """Clean professional code without placeholders or emojis must pass."""
        clean_code = """
        class UserService:
            def __init__(self, db_client):
                self.db_client = db_client
                
            def get_user(self, user_id: str) -> dict:
                if not user_id:
                    raise ValueError("user_id cannot be empty")
                return self.db_client.query({"id": user_id})
        """
        violations = self.evaluator.evaluate_anti_slop(clean_code)
        self.assertEqual(len(violations), 0)

    def test_quality_profiles_available(self):
        """Ensure all 5 specialized profiles exist with valid thresholds."""
        expected_profiles = ["PROTOTYPE", "STANDARD", "PRODUCTION_READY", "SECURITY_SENSITIVE", "DESIGN_INTENSIVE"]
        for p_name in expected_profiles:
            profile = self.evaluator.get_profile(p_name)
            self.assertIn("minCoveragePercent", profile)
            self.assertIn("requiresIndependentReview", profile)
            self.assertTrue(profile["requiresIndependentReview"])

    def test_verification_honesty_validation(self):
        """Ensure dishonest or failing verification statuses are caught."""
        # Honest passing suites
        valid_suites = [
            {"suiteName": "Unit Tests", "command": "pytest", "mandatory": True, "status": "PASSED"},
            {"suiteName": "Linter", "command": "flake8", "mandatory": True, "status": "PASSED"}
        ]
        ok, issues = self.evaluator.evaluate_verification_honesty(valid_suites)
        self.assertTrue(ok)
        self.assertEqual(len(issues), 0)

        # Mandatory suite SKIPPED -> Must fail evaluation
        dishonest_suites = [
            {"suiteName": "Security Audit", "command": "bandit", "mandatory": True, "status": "SKIPPED"}
        ]
        ok, issues = self.evaluator.evaluate_verification_honesty(dishonest_suites)
        self.assertFalse(ok)
        self.assertIn("non-passing status", issues[0])

        # Invalid status string
        corrupt_suites = [
            {"suiteName": "Bad Check", "command": "check", "mandatory": False, "status": "SORTA_PASSED"}
        ]
        ok, issues = self.evaluator.evaluate_verification_honesty(corrupt_suites)
        self.assertFalse(ok)
        self.assertIn("Invalid verification status", issues[0])


if __name__ == "__main__":
    unittest.main()
