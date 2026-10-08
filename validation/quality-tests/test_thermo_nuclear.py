"""
Project Intelligence — Thermo-Nuclear Reviewer & Code Judo Test Suite
Verifies structural simplification, cyclomatic nesting depth checks,
trivial wrapper detection, and Baseline UI craftsmanship audits.
"""

import unittest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.quality.thermo_nuclear_reviewer import ThermoNuclearReviewer, ThermoNuclearReport
from core.quality.evaluator import QualityEvaluator


class TestThermoNuclearReviewer(unittest.TestCase):
    def setUp(self):
        self.reviewer = ThermoNuclearReviewer()
        self.evaluator = QualityEvaluator()

    def test_nesting_depth_flags_pyramids(self):
        """Ensure Code Judo Move 2 flags nesting depth exceeding threshold 3."""
        nested_pyramid = """
def process_data(user, data):
    if user:
        if user.is_authenticated:
            if data:
                if len(data) > 0:
                    for item in data:
                        if item.is_valid:
                            print(item)
"""
        findings = self.reviewer.analyze_python_ast("test_dummy.py", nested_pyramid)
        depth_findings = [f for f in findings if f.rule_id == "JUDO-001-NESTING-DEPTH"]
        self.assertGreaterEqual(len(depth_findings), 1)
        self.assertTrue(any("guard clauses" in f.judo_recommendation for f in depth_findings))

    def test_nesting_depth_passes_flat_guard_clauses(self):
        """Flat code with early return guard clauses must pass cleanly."""
        flat_code = """
def process_data(user, data):
    if not user or not user.is_authenticated:
        return
    if not data or len(data) == 0:
        return
    for item in data:
        if not item.is_valid:
            continue
        print(item)
"""
        findings = self.reviewer.analyze_python_ast("test_dummy.py", flat_code)
        depth_findings = [f for f in findings if f.rule_id == "JUDO-001-NESTING-DEPTH"]
        self.assertEqual(len(depth_findings), 0)

    def test_trivial_wrapper_detection(self):
        """Ensure Code Judo Move 1 flags trivial passthrough functions."""
        wrapper_code = """
def get_user_record(user_id, tenant_id):
    return fetch_user(user_id, tenant_id)
"""
        findings = self.reviewer.analyze_python_ast("test_dummy.py", wrapper_code)
        wrapper_findings = [f for f in findings if f.rule_id == "JUDO-002-TRIVIAL-WRAPPER"]
        self.assertEqual(len(wrapper_findings), 1)
        self.assertIn("Collapse wrapper 'get_user_record'", wrapper_findings[0].judo_recommendation)

    def test_file_bloat_ceiling_audit(self):
        """Ensure files exceeding 1000 lines trigger hard blocking defect."""
        bloated_code = "\n".join(["x = 1"] * 1050)
        findings = self.reviewer.analyze_file_metrics("bloated.py", bloated_code)
        bloat_limit = [f for f in findings if f.rule_id == "JUDO-003-FILE-BLOAT-LIMIT"]
        self.assertEqual(len(bloat_limit), 1)
        self.assertEqual(bloat_limit[0].severity, "BLOCKING")

    def test_baseline_ui_spacing_cadence(self):
        """Ensure non-multiple of 4 spacing declarations are caught."""
        sloppy_css = """
        .card {
            margin-top: 13px;
            padding: 7px;
            gap: 16px;
        }
        """
        findings = self.reviewer.analyze_baseline_ui_css("styles.css", sloppy_css)
        cadence_findings = [f for f in findings if f.rule_id == "BASE-001-SPACING-CADENCE"]
        self.assertEqual(len(cadence_findings), 2)
        messages = [f.message for f in cadence_findings]
        self.assertTrue(any("13px" in m for m in messages))
        self.assertTrue(any("7px" in m for m in messages))

    def test_baseline_ui_token_discipline(self):
        """Ensure raw hex colors outside root token blocks are flagged."""
        sloppy_css = """
        .button-primary {
            background-color: #3b82f6;
            color: #ffffff;
        }
        """
        findings = self.reviewer.analyze_baseline_ui_css("styles.css", sloppy_css)
        token_findings = [f for f in findings if f.rule_id == "BASE-002-TOKEN-DISCIPLINE"]
        self.assertEqual(len(token_findings), 2)
        self.assertIn("Replace raw hex with semantic CSS token", token_findings[0].judo_recommendation)

    def test_baseline_ui_motion_bounds(self):
        """Ensure sluggish transitions > 300ms are flagged."""
        sluggish_css = """
        .modal {
            transition: all 600ms ease;
        }
        """
        findings = self.reviewer.analyze_baseline_ui_css("styles.css", sluggish_css)
        motion_findings = [f for f in findings if f.rule_id == "BASE-004-MOTION-BOUNDS"]
        self.assertEqual(len(motion_findings), 1)
        self.assertIn("600ms", motion_findings[0].message)

    def test_baseline_ui_focus_ring(self):
        """Ensure suppression of outline without replacement is flagged as BLOCKING."""
        inaccessible_css = """
        button:focus {
            outline: none;
        }
        """
        findings = self.reviewer.analyze_baseline_ui_css("styles.css", inaccessible_css)
        focus_findings = [f for f in findings if f.rule_id == "BASE-005-FOCUS-RING"]
        self.assertEqual(len(focus_findings), 1)
        self.assertEqual(focus_findings[0].severity, "BLOCKING")

    def test_evaluator_integration_with_thermo_nuclear(self):
        """Verify QualityEvaluator.evaluate_thermo_nuclear executes cleanly."""
        report = self.evaluator.evaluate_thermo_nuclear(Path(__file__).resolve())
        self.assertIsInstance(report, ThermoNuclearReport)
        self.assertTrue(report.is_approved())
        self.assertGreaterEqual(report.overall_score, 80.0)


if __name__ == "__main__":
    unittest.main()
