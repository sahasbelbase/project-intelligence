"""
Project Intelligence — Regression Tests: CLI and Lifecycle Invariants
Tests CLI argument parsing, status inspection, gate advance/rollback,
illegal backward transitions, illegal self-loops, and human approval flags.
"""

import subprocess
import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.lifecycle.engine import LifecycleEngine, LifecycleError


class TestLifecycleExtendedInvariants(unittest.TestCase):
    def setUp(self):
        self.engine = LifecycleEngine()

    def test_illegal_backward_jumps_blocked(self):
        """Ensure backward transitions other than G5->G4 are strictly blocked."""
        illegal_backwards = [
            ("G6", "G0"), ("G6", "G1"), ("G6", "G4"),
            ("G4", "G1"), ("G4", "G2"), ("G3", "G0"), ("G2", "G0")
        ]
        for src, dst in illegal_backwards:
            allowed, reason = self.engine.can_transition(src, dst, "ANY_CONDITION")
            self.assertFalse(allowed, f"Illegal backward jump {src} -> {dst} must be blocked: {reason}")

    def test_illegal_self_loops_blocked(self):
        """Ensure only G4 permits self-loop task retry; all other gates reject self-transitions."""
        non_retry_gates = ["G0", "G1", "G2", "G3", "G5", "G6"]
        for g in non_retry_gates:
            allowed, _ = self.engine.can_transition(g, g, "SELF_LOOP")
            self.assertFalse(allowed, f"Self-transition on gate {g} must be blocked")

    def test_invalid_transition_conditions_rejected(self):
        """Ensure valid gate pairs with incorrect or empty conditions are rejected."""
        allowed, reason = self.engine.can_transition("G0", "G1", "INVALID_CONDITION")
        self.assertFalse(allowed)
        self.assertIn("does not match allowed conditions", reason)

        allowed, _ = self.engine.can_transition("G0", "G1", "")
        self.assertFalse(allowed)

    def test_human_approval_gate_flags_declared(self):
        """Verify that FSM transitions requiring human approval declare requiresHumanApproval: true."""
        gates_requiring_human = [("G0", "G1"), ("G1", "G2"), ("G2", "G3"), ("G3", "G4"), ("G5", "G6")]
        for src, dst in gates_requiring_human:
            t = self.engine.get_transition(src, dst)
            self.assertIsNotNone(t, f"Missing transition {src} -> {dst}")
            self.assertTrue(
                t.get("requiresHumanApproval", False),
                f"Transition {src} -> {dst} must declare requiresHumanApproval: true"
            )


class TestCliExecution(unittest.TestCase):
    def test_engine_cli_help(self):
        """Ensure engine.py --help executes with exit code 0 and shows usage."""
        engine_script = PROJECT_ROOT / "core" / "lifecycle" / "engine.py"
        res = subprocess.run(
            [sys.executable, str(engine_script), "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Lifecycle State Machine CLI", res.stdout)
        self.assertIn("--advance", res.stdout)
        self.assertIn("--status", res.stdout)

    def test_engine_cli_verify(self):
        """Ensure engine.py --verify executes with exit code 0 and verifies all 7 gates."""
        engine_script = PROJECT_ROOT / "core" / "lifecycle" / "engine.py"
        res = subprocess.run(
            [sys.executable, str(engine_script), "--verify"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Lifecycle State Machine Verification: PASSED", res.stdout)
        self.assertIn("Gates Defined       : 7", res.stdout)

    def test_engine_cli_status(self):
        """Ensure engine.py --status executes with exit code 0."""
        engine_script = PROJECT_ROOT / "core" / "lifecycle" / "engine.py"
        res = subprocess.run(
            [sys.executable, str(engine_script), "--status"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("PROJECT INTELLIGENCE — LIFECYCLE STATUS", res.stdout)
        self.assertIn("Active Gate", res.stdout)

    def test_evaluator_cli_help(self):
        """Ensure evaluator.py --help executes with exit code 0."""
        eval_script = PROJECT_ROOT / "core" / "quality" / "evaluator.py"
        res = subprocess.run(
            [sys.executable, str(eval_script), "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Quality Profile Evaluator CLI", res.stdout)
        self.assertIn("--profile", res.stdout)

    def test_evaluator_cli_selftest(self):
        """Ensure evaluator.py --selftest executes with exit code 0."""
        eval_script = PROJECT_ROOT / "core" / "quality" / "evaluator.py"
        res = subprocess.run(
            [sys.executable, str(eval_script), "--selftest"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Quality Profile Evaluator Self-Test: PASSED", res.stdout)
        self.assertIn("Mandatory Baseline Rules: 7", res.stdout)

    def test_evaluator_cli_case_insensitive_profile(self):
        """Ensure evaluator.py handles lowercase and kebab-case profile arguments."""
        eval_script = PROJECT_ROOT / "core" / "quality" / "evaluator.py"
        for p in ["standard", "STANDARD", "production-ready", "PRODUCTION_READY", "prototype"]:
            res = subprocess.run(
                [sys.executable, str(eval_script), "--profile", p, "--target", str(PROJECT_ROOT / "core")],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 0, f"Profile {p} failed: {res.stderr}")
            self.assertIn("PROJECT INTELLIGENCE — QUALITY EVALUATION", res.stdout)


if __name__ == "__main__":
    unittest.main()
