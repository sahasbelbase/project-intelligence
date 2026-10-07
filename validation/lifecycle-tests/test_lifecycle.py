"""
Project Intelligence — Lifecycle State Machine Tests
Tests legal transitions, gate skipping prevention, design exemptions, and defect rollbacks.
"""

import unittest
from pathlib import Path
import sys

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.lifecycle.engine import LifecycleEngine, LifecycleError


class TestLifecycleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LifecycleEngine()

    def test_all_seven_gates_present(self):
        """Verify gates G0 through G6 exist."""
        expected_gates = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
        for g in expected_gates:
            gate_data = self.engine.get_gate(g)
            self.assertEqual(gate_data["gateId"], g)
            self.assertTrue(len(gate_data["entryCriteria"]) > 0)
            self.assertTrue(len(gate_data["exitCriteria"]) > 0)

    def test_legal_sequential_transitions(self):
        """Verify normal linear flow passes validation."""
        self.assertTrue(self.engine.validate_transition("G0", "G1", "G0_APPROVED"))
        self.assertTrue(self.engine.validate_transition("G1", "G2", "G1_APPROVED"))
        self.assertTrue(self.engine.validate_transition("G2", "G3", "G2_APPROVED_OR_EXEMPTED"))
        self.assertTrue(self.engine.validate_transition("G3", "G4", "G3_APPROVED"))
        self.assertTrue(self.engine.validate_transition("G4", "G5", "G4_VERIFIED"))
        self.assertTrue(self.engine.validate_transition("G5", "G6", "G5_PASSED"))

    def test_illegal_gate_skipping_blocked(self):
        """Verify skipping required gates raises LifecycleError."""
        # Cannot skip from G0 directly to G4
        with self.assertRaises(LifecycleError) as ctx:
            self.engine.validate_transition("G0", "G4", "G0_APPROVED")
        self.assertIn("blocked", str(ctx.exception).lower())

        # Cannot skip from G1 directly to G5
        with self.assertRaises(LifecycleError) as ctx:
            self.engine.validate_transition("G1", "G5", "G1_APPROVED")
        self.assertIn("blocked", str(ctx.exception).lower())

        # Cannot skip from G3 directly to G6
        with self.assertRaises(LifecycleError) as ctx:
            self.engine.validate_transition("G3", "G6", "G3_APPROVED")
        self.assertIn("blocked", str(ctx.exception).lower())

    def test_design_exemption_handling(self):
        """Verify G2 (Design) exemption handling."""
        # G1 -> G3 with valid exemption rationale succeeds
        allowed, reason = self.engine.can_transition(
            "G1", "G3", "G2_EXEMPT",
            is_exempt=True,
            exemption_justification="Pure backend CLI engine with headless API; no graphical UI."
        )
        self.assertTrue(allowed, reason)

        # G1 -> G3 with empty justification fails
        allowed, reason = self.engine.can_transition(
            "G1", "G3", "G2_EXEMPT",
            is_exempt=True,
            exemption_justification=""
        )
        self.assertFalse(allowed)
        self.assertIn("explicit justification", reason)

        # G1 -> G3 without is_exempt fails
        allowed, reason = self.engine.can_transition(
            "G1", "G3", "G2_EXEMPT",
            is_exempt=False
        )
        self.assertFalse(allowed)

    def test_review_defect_rollback(self):
        """Verify defect found during review rolls back G5 to G4."""
        allowed, reason = self.engine.can_transition("G5", "G4", "REVIEW_DEFECTS_FOUND")
        self.assertTrue(allowed, reason)

    def test_task_retry_in_implementation(self):
        """Verify task retry loop in G4 is legal."""
        allowed, reason = self.engine.can_transition("G4", "G4", "TASK_RETRY")
        self.assertTrue(allowed, reason)

    def test_unknown_gate_rejected(self):
        """Verify invalid gate strings raise LifecycleError."""
        with self.assertRaises(LifecycleError):
            self.engine.get_gate("G99")
        allowed, _ = self.engine.can_transition("G0", "G99", "FOO")
        self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
