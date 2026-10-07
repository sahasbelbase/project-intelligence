"""
Project Intelligence — MCP Read-Only Tools Tests
Verifies that all 6 read-only tools retrieve verified data from the repository,
enforce strict read-only semantics, and never mutate filesystem or Git state.
Uses Python standard library with zero external dependencies.
"""

import unittest
from pathlib import Path
import sys
import os

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from adapters.mcp.tools import ProjectIntelligenceTools


def _take_fs_snapshot(directory: Path) -> dict:
    """Takes a lightweight mtime and size snapshot of a directory."""
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        # Skip pycache and git internals
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for f in files:
            p = Path(root) / f
            try:
                stat = p.stat()
                snapshot[str(p.relative_to(directory))] = (stat.st_mtime_ns, stat.st_size)
            except OSError:
                pass
    return snapshot


class TestMCPReadOnlyTools(unittest.TestCase):
    def setUp(self):
        self.tools = ProjectIntelligenceTools(workspace_root=project_root)

    def test_project_status_returns_verified_data(self):
        """Ensure project_status returns lifecycle gate, tasks, blockers, and git alignment."""
        res = self.tools.project_status()
        self.assertIn("lifecycle", res)
        self.assertIn("tasks", res)
        self.assertIn("gitAlignment", res)

        lifecycle = res["lifecycle"]
        self.assertEqual(lifecycle["currentGate"], "G0")
        self.assertEqual(lifecycle["gateName"], "Discovery")
        self.assertEqual(lifecycle["requiredContractType"], "project")
        self.assertEqual(lifecycle["contractStatus"], "APPROVED")

        tasks = res["tasks"]
        self.assertIn("activeTasks", tasks)
        self.assertIn("completedTasks", tasks)
        self.assertIsInstance(tasks["blockedTasks"], list)

        git_align = res["gitAlignment"]
        self.assertTrue(git_align["isGitRepo"])
        self.assertIn(git_align["reconciliationStatus"], ["CLEAN", "COMMIT_DRIFT", "UNCOMMITTED_CHANGES"])

    def test_inspect_project_bounded_summary(self):
        """Ensure inspect_project returns bounded layout and counts without dumping entire tree."""
        res = self.tools.inspect_project()
        self.assertIn("standingInstructions", res)
        self.assertIn("counts", res)
        self.assertIn("topLevelLayout", res)
        self.assertIn("gitState", res)

        counts = res["counts"]
        self.assertGreater(counts["skills"], 0)
        self.assertGreater(counts["agents"], 0)
        self.assertGreaterEqual(counts["contracts"], 7)

        # Ensure top-level layout does not contain .git internals
        layout_names = [item["name"] for item in res["topLevelLayout"]]
        self.assertNotIn(".git", layout_names)
        self.assertIn("core", layout_names)
        self.assertIn("contracts", layout_names)

    def test_get_next_action_evaluates_fsm(self):
        """Ensure get_next_action identifies correct next step from lifecycle engine."""
        res = self.tools.get_next_action()
        self.assertEqual(res["currentGate"], "G0")
        self.assertIn("nextAction", res)
        self.assertIn("candidateTransitions", res)

        next_action = res["nextAction"]
        self.assertIn("action", next_action)
        self.assertIn("details", next_action)
        self.assertIsInstance(next_action["prerequisites"], list)

        transitions = res["candidateTransitions"]
        self.assertTrue(len(transitions) > 0)
        # Should have candidate transition from G0 to G1
        to_gates = [t["targetGate"] for t in transitions]
        self.assertIn("G1", to_gates)

    def test_validate_contract_real_and_synthetic(self):
        """Ensure validate_contract validates concrete files and catches synthetic errors."""
        # 1. Valid real project contract
        res_real = self.tools.validate_contract(contract_path="contracts/project/contract.json")
        self.assertTrue(res_real["valid"])
        self.assertEqual(res_real["contractType"], "project")
        self.assertEqual(res_real["envelopeErrors"], [])
        self.assertEqual(res_real["payloadErrors"], [])

        # 2. Corrupted in-memory contract (missing envelope fields)
        corrupted = {
            "schemaVersion": "1.0.0",
            "contractId": "bad-contract",
            # missing title, status, lifecycleGate, author, data
        }
        res_bad = self.tools.validate_contract(contract_data=corrupted)
        self.assertFalse(res_bad["valid"])
        self.assertGreater(len(res_bad["envelopeErrors"]), 0)

        # 3. Invalid status and illegal gate
        bad_gate = {
            "schemaVersion": "1.0.0",
            "contractId": "bad-gate-contract",
            "contractType": "project",
            "title": "Bad Gate Contract",
            "status": "NON_STANDARD_STATUS",
            "lifecycleGate": "G99",
            "createdAt": "2026-10-07T00:00:00Z",
            "updatedAt": "2026-10-07T00:00:00Z",
            "author": {"role": "Architect", "identifier": "lead"},
            "data": {},
        }
        res_gate = self.tools.validate_contract(contract_data=bad_gate)
        self.assertFalse(res_gate["valid"])
        err_str = " ".join(res_gate["envelopeErrors"])
        self.assertIn("NON_STANDARD_STATUS", err_str)
        self.assertIn("G99", err_str)

    def test_evaluate_quality_anti_slop_and_honesty(self):
        """Ensure evaluate_quality catches placeholders and emojis while passing clean code."""
        # 1. Clean code -> PASSED
        clean_code = "def calculate_hash(data: bytes) -> str:\n    import hashlib\n    return hashlib.sha256(data).hexdigest()\n"
        res_clean = self.tools.evaluate_quality(content=clean_code, profile_name="STANDARD")
        self.assertEqual(res_clean["overallStatus"], "PASSED")
        self.assertTrue(res_clean["antiSlopCheck"]["passed"])
        self.assertEqual(res_clean["antiSlopCheck"]["violations"], [])

        # 2. Slop code -> FAILED
        slop_code = "def run():\n    # TODO: implement later\n    print('🚀 Complete!')\n"
        res_slop = self.tools.evaluate_quality(content=slop_code, profile_name="STANDARD")
        self.assertEqual(res_slop["overallStatus"], "FAILED")
        self.assertFalse(res_slop["antiSlopCheck"]["passed"])
        self.assertGreaterEqual(len(res_slop["antiSlopCheck"]["violations"]), 2)

        # 3. Verification honesty check
        dishonest_suites = [
            {"suiteName": "Security Audit", "mandatory": True, "status": "SKIPPED"}
        ]
        res_dishonest = self.tools.evaluate_quality(
            content=clean_code, verification_suites=dishonest_suites
        )
        self.assertEqual(res_dishonest["overallStatus"], "FAILED")
        self.assertFalse(res_dishonest["verificationHonestyCheck"]["passed"])

    def test_get_project_memory_bounded_retrieval(self):
        """Ensure get_project_memory provides bounded retrieval for all tiers."""
        # Summary
        summary = self.tools.get_project_memory(section="summary", max_items=2)
        self.assertIn("goals", summary)
        self.assertLessEqual(len(summary["goals"]), 2)
        self.assertIn("currentGate", summary)

        # Durable knowledge
        durable = self.tools.get_project_memory(section="durable_knowledge")
        self.assertIn("durableKnowledge", durable)
        self.assertIn("goals", durable["durableKnowledge"])
        self.assertIn("architecturalDecisions", durable["durableKnowledge"])

        # Execution state
        exec_state = self.tools.get_project_memory(section="execution_state")
        self.assertIn("executionState", exec_state)
        self.assertEqual(exec_state["executionState"]["currentGate"], "G0")

        # Backlog
        backlog = self.tools.get_project_memory(section="backlog")
        self.assertIn("backlog", backlog)
        self.assertIn("bugs", backlog["backlog"])

    def test_read_only_filesystem_invariance(self):
        """Verify that invoking all read-only tools leaves the repository completely unchanged."""
        before_snapshot = _take_fs_snapshot(project_root)

        # Invoke all read-only tools
        self.tools.project_status()
        self.tools.inspect_project()
        self.tools.get_next_action()
        self.tools.validate_contract(contract_path="contracts/project/contract.json")
        self.tools.evaluate_quality(content="print('pure read test')")
        self.tools.get_project_memory(section="summary")

        after_snapshot = _take_fs_snapshot(project_root)
        self.assertEqual(
            before_snapshot,
            after_snapshot,
            "Read-only tools must not modify, add, or delete any files in the workspace",
        )


if __name__ == "__main__":
    unittest.main()
