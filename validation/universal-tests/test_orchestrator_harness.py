"""
Project Intelligence — Orchestrator Harness Automated Test Suite
Validates the execution harness, step simulation, telemetry tracing,
lifecycle gate verification, and failure recovery.
Zero external dependencies (Python 3.10+ standard library only).
"""

import json
from pathlib import Path
import tempfile
import unittest

from core.orchestrator.harness import (
    ExecutionStatus,
    HarnessTrace,
    OrchestratorHarness,
    StepExecutionRecord,
)
from core.orchestrator.router import IntentCategory, route_request


class TestOrchestratorHarness(unittest.TestCase):

    def setUp(self):
        self.harness = OrchestratorHarness()

    def test_single_persona_execution(self):
        """Single-persona tasks execute through the harness with a single completed step."""
        trace = self.harness.execute_plan("Fix typo in calculate_tax docstring")

        self.assertIsInstance(trace, HarnessTrace)
        self.assertEqual(trace.status, ExecutionStatus.COMPLETED)
        self.assertEqual(trace.route_type, "direct")
        self.assertEqual(len(trace.steps), 1)

        step = trace.steps[0]
        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.persona, "implementation")
        self.assertEqual(step.status, ExecutionStatus.COMPLETED)
        self.assertGreater(step.duration_ms, 0.0)
        self.assertIn("artifactsGenerated", step.output)

        trace_dict = trace.to_dict()
        self.assertIn("traceId", trace_dict)
        self.assertEqual(trace_dict["status"], "COMPLETED")

    def test_sequential_workflow_execution(self):
        """Sequential workflows execute all lifecycle phases with state tracking."""
        query = "Implement new notification feature from scratch through all lifecycle gates"
        trace = self.harness.execute_plan(query)

        self.assertEqual(trace.status, ExecutionStatus.COMPLETED)
        self.assertEqual(trace.route_type, "workflow")
        self.assertGreaterEqual(len(trace.steps), 3)

        # Verify all steps completed in order
        personas = [s.persona for s in trace.steps]
        self.assertIn("discovery", personas)
        self.assertIn("implementation", personas)
        self.assertIn("verification", personas)

        for s in trace.steps:
            self.assertEqual(s.status, ExecutionStatus.COMPLETED)
            self.assertTrue(len(s.evidence) > 0)

    def test_failure_injection_and_fast_fail_recovery(self):
        """Simulated step failure stops subsequent steps and records recovery actions."""
        query = "Implement user authentication end-to-end"
        trace = self.harness.execute_plan(query, fail_step_number=2)

        self.assertEqual(trace.status, ExecutionStatus.FAILED)
        self.assertEqual(trace.steps[0].status, ExecutionStatus.COMPLETED)
        self.assertEqual(trace.steps[1].status, ExecutionStatus.FAILED)
        self.assertIn("Simulated execution failure in step 2", trace.steps[1].error)

        # Remaining steps should be marked SKIPPED due to fail_fast=True
        for remaining in trace.steps[2:]:
            self.assertEqual(remaining.status, ExecutionStatus.SKIPPED)

        # Recovery log recorded
        self.assertTrue(len(trace.recovery_log) > 0)
        self.assertIn("Triggering recovery strategy", trace.recovery_log[0])

    def test_custom_step_executor_and_mocking(self):
        """Custom step executor can supply mock domain outputs."""
        custom_called = []

        def custom_executor(step_rec: StepExecutionRecord, mock_data: dict) -> dict:
            custom_called.append(step_rec.step_number)
            return {
                "output": {"customResult": f"Done by {step_rec.persona}", **mock_data},
                "evidence": [f"Custom empirical test evidence for step {step_rec.step_number}"]
            }

        custom_harness = OrchestratorHarness(custom_step_executor=custom_executor)
        mocks = {1: {"mockKey": "mockVal"}}
        trace = custom_harness.execute_plan("Run the test suite and verify all exit codes are 0", mock_outputs=mocks)

        self.assertEqual(trace.status, ExecutionStatus.COMPLETED)
        self.assertIn(1, custom_called)
        self.assertEqual(trace.steps[0].output.get("mockKey"), "mockVal")
        self.assertEqual(trace.steps[0].output.get("customResult"), "Done by verification")

    def test_lifecycle_gate_compliance(self):
        """Harness can query gate transition feasibility through the lifecycle engine."""
        # Valid progression
        is_ok, reason = self.harness.verify_gate_compliance("G0", "G1")
        self.assertTrue(is_ok)

        # Illegal skipping
        is_invalid, err_reason = self.harness.verify_gate_compliance("G0", "G4")
        self.assertFalse(is_invalid)

    def test_trace_export_to_disk(self):
        """Trace can be exported to JSON and read back accurately."""
        trace = self.harness.execute_plan("Fix typo in README.md")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "test_trace.json"
            exported_path = self.harness.export_trace_log(trace, tmp_path)
            self.assertTrue(exported_path.exists())

            loaded = json.loads(exported_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["traceId"], trace.trace_id)
            self.assertEqual(loaded["status"], "COMPLETED")
            self.assertEqual(loaded["stepCount"], 1)


if __name__ == "__main__":
    unittest.main()
