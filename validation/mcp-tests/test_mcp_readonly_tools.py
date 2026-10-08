"""
Project Intelligence — MCP Read-Only Tools Tests
Verifies that all 6 read-only tools retrieve verified data from the repository,
enforce strict read-only semantics, and never mutate filesystem or Git state.
Uses Python standard library with zero external dependencies.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

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


def _live_execution_state() -> dict:
    """Reads the repository's live execution state, which tools must report verbatim."""
    with open(project_root / "memory" / "execution-state.json", "r", encoding="utf-8") as f:
        return json.load(f)


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
        live_gate = _live_execution_state()["currentGate"]
        gate_info = self.tools.lifecycle_engine.get_gate(live_gate)
        self.assertEqual(lifecycle["currentGate"], live_gate)
        self.assertEqual(lifecycle["gateName"], gate_info["name"])
        self.assertEqual(lifecycle["requiredContractType"], gate_info["requiredContractType"])
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
        # Pin a copy of the workspace at G0 so the expected G0 -> G1 candidate is stable.
        temp_ws = Path(tempfile.mkdtemp(prefix="pi_mcp_next_"))
        self.addCleanup(shutil.rmtree, temp_ws, ignore_errors=True)
        for d in ["core", "contracts", "memory"]:
            shutil.copytree(project_root / d, temp_ws / d)
        state_file = temp_ws / "memory" / "execution-state.json"
        state = json.loads(state_file.read_text(encoding="utf-8"))
        state["currentGate"], state["activePhase"] = "G0", 0
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

        res = ProjectIntelligenceTools(workspace_root=temp_ws).get_next_action()
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
        self.assertEqual(exec_state["executionState"]["currentGate"], _live_execution_state()["currentGate"])

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

    def test_project_status_matches_reconciler_live_drift(self):
        """Ensure project_status gitAlignment dynamically matches reconcile_project_memory on live repo."""
        status_res = self.tools.project_status()
        reconcile_res = self.tools.reconcile_project_memory(update_mode=False)

        git_align = status_res["gitAlignment"]
        self.assertEqual(
            git_align["driftDetected"],
            reconcile_res["drift_detected"],
            "driftDetected must match reconcile_project_memory.drift_detected",
        )
        self.assertEqual(
            git_align["reconciliationStatus"],
            reconcile_res["reconciliation_status"],
            "reconciliationStatus must match reconcile_project_memory.reconciliation_status",
        )
        self.assertEqual(
            git_align["currentHead"],
            reconcile_res["current_head"][:8] if reconcile_res["current_head"] else "00000000",
            "currentHead must match first 8 chars of current_head",
        )
        self.assertEqual(
            git_align["lastReconciledCommit"],
            reconcile_res["last_reconciled_commit"][:8] if reconcile_res["last_reconciled_commit"] else "00000000",
            "lastReconciledCommit must match first 8 chars of last_reconciled_commit",
        )
        self.assertEqual(
            git_align["uncommittedChangesCount"],
            len(reconcile_res["uncommitted_files"]),
            "uncommittedChangesCount must match len(uncommitted_files)",
        )

    def test_project_status_read_only_invariance(self):
        """Ensure invoking project_status does not modify memory/execution-state.json or any persisted state."""
        state_path = project_root / "memory" / "execution-state.json"
        before_content = state_path.read_text(encoding="utf-8")
        before_mtime = state_path.stat().st_mtime_ns

        # Invoke project_status multiple times
        self.tools.project_status()
        self.tools.project_status()

        after_content = state_path.read_text(encoding="utf-8")
        after_mtime = state_path.stat().st_mtime_ns

        self.assertEqual(before_content, after_content)
        self.assertEqual(before_mtime, after_mtime)

    def test_reconciliation_consistency_deterministic_scenarios(self):
        """Verify project_status and reconciler consistency across clean, commit drift, and uncommitted changes in isolated fixture."""
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_root = Path(tmp_dir_str)

            # Copy essential framework configuration
            for sub in ["core/lifecycle", "core/quality", "contracts/project", "memory/templates"]:
                (tmp_root / sub).mkdir(parents=True, exist_ok=True)
            shutil.copy(project_root / "core/lifecycle/lifecycle-fsm.json", tmp_root / "core/lifecycle/lifecycle-fsm.json")
            shutil.copy(project_root / "core/quality/profiles.json", tmp_root / "core/quality/profiles.json")
            shutil.copy(project_root / "contracts/project/contract.json", tmp_root / "contracts/project/contract.json")
            shutil.copy(project_root / "memory/templates/execution-state.template.json", tmp_root / "memory/templates/execution-state.template.json")

            # Init Git repo in fixture
            def _run_git(args):
                subprocess.run(["git"] + args, cwd=tmp_root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            _run_git(["init"])
            _run_git(["config", "user.name", "Test Runner"])
            _run_git(["config", "user.email", "test@example.com"])
            _run_git(["add", "."])
            _run_git(["commit", "-m", "commit 1"])

            c1 = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_root, text=True).strip()
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=tmp_root, text=True).strip()

            fixture_tools = ProjectIntelligenceTools(workspace_root=tmp_root)

            # Scenario 1 Check: Clean & Reconciled
            # Reconcile in update mode to establish an initial synchronized baseline
            fixture_tools.reconcile_project_memory(update_mode=True)

            s1_status = fixture_tools.project_status()
            s1_rec = fixture_tools.reconcile_project_memory(update_mode=False)
            self.assertFalse(s1_status["gitAlignment"]["driftDetected"])
            self.assertEqual(s1_status["gitAlignment"]["reconciliationStatus"], "CLEAN")
            self.assertEqual(s1_status["gitAlignment"]["driftDetected"], s1_rec["drift_detected"])
            self.assertEqual(s1_status["gitAlignment"]["reconciliationStatus"], s1_rec["reconciliation_status"])

            # Scenario 2 Check: Newer commit than stored anchor (Commit Drift)
            dummy_file = tmp_root / "new_feature.txt"
            dummy_file.write_text("hello world")
            _run_git(["add", "new_feature.txt"])
            _run_git(["commit", "-m", "commit 2 (ahead of state anchor)"])

            s2_status = fixture_tools.project_status()
            s2_rec = fixture_tools.reconcile_project_memory(update_mode=False)
            self.assertTrue(s2_status["gitAlignment"]["driftDetected"])
            self.assertEqual(s2_status["gitAlignment"]["reconciliationStatus"], "COMMIT_DRIFT")
            self.assertEqual(s2_status["gitAlignment"]["driftDetected"], s2_rec["drift_detected"])
            self.assertEqual(s2_status["gitAlignment"]["reconciliationStatus"], s2_rec["reconciliation_status"])
            self.assertEqual(s2_status["gitAlignment"]["currentHead"], s2_rec["current_head"][:8])

            # Scenario 3 Check: Working tree modifications (Uncommitted Changes)
            # Fast-forward anchor in memory state to match commit 2
            fixture_tools.reconcile_project_memory(update_mode=True)

            # Modify a developer file without committing
            dummy_file.write_text("uncommitted developer modifications")

            s3_status = fixture_tools.project_status()
            s3_rec = fixture_tools.reconcile_project_memory(update_mode=False)
            self.assertTrue(s3_status["gitAlignment"]["driftDetected"])
            self.assertEqual(s3_status["gitAlignment"]["driftDetected"], s3_rec["drift_detected"])
            self.assertEqual(s3_status["gitAlignment"]["reconciliationStatus"], s3_rec["reconciliation_status"])
            self.assertGreaterEqual(s3_status["gitAlignment"]["uncommittedChangesCount"], 1)


if __name__ == "__main__":
    unittest.main()
