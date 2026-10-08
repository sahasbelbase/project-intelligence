"""
Project Intelligence — MCP Proposed-Action Tools Tests
Verifies that mutating and execution tools enforce two-phase safety,
dry-run preview modes, DAG validation, gate prerequisites, atomic persistence,
human edit preservation, and command allowlisting.
Uses Python standard library with zero external dependencies.
"""

import unittest
from pathlib import Path
import sys
import json
import tempfile
import shutil

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from adapters.mcp.tools import ProjectIntelligenceTools


def _create_temp_workspace(pin_gate: str = "G0") -> Path:
    """Clones canonical core, contracts, and memory into an ephemeral test workspace.

    The copied execution state is pinned to `pin_gate` so transition tests do not
    depend on whichever gate the live repository memory currently records.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="pi_mcp_test_"))
    for d in ["core", "contracts", "memory", "instructions", "validation", "adapters"]:
        src = project_root / d
        if src.exists():
            shutil.copytree(src, temp_dir / d)
    state_file = temp_dir / "memory" / "execution-state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        state["currentGate"] = pin_gate
        state["activePhase"] = int(pin_gate[1:])
        state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return temp_dir


class TestMCPProposedActions(unittest.TestCase):
    def setUp(self):
        self.tools = ProjectIntelligenceTools(workspace_root=project_root)

    def test_create_work_plan_dry_run_and_dag_validation(self):
        """Ensure create_work_plan validates schemas and DAG acyclicity without writing during dry run."""
        phases = [
            {"phaseNumber": 1, "name": "Foundation", "goal": "Setup core structure"}
        ]
        tasks = [
            {
                "taskId": "TASK-001",
                "phaseNumber": 1,
                "title": "Build baseline adapter",
                "assignedAgent": "Implementation Agent",
                "dependencies": [],
                "allowedFiles": ["adapters/mcp/server.py"],
                "forbiddenFiles": ["core/lifecycle/engine.py"],
                "verificationCommand": "python3 -m unittest",
                "status": "PENDING",
            },
            {
                "taskId": "TASK-002",
                "phaseNumber": 1,
                "title": "Add integration tests",
                "assignedAgent": "Test Agent",
                "dependencies": ["TASK-001"],
                "allowedFiles": ["validation/mcp-tests/"],
                "forbiddenFiles": [],
                "verificationCommand": "python3 validation/test_runner.py",
                "status": "PENDING",
            },
        ]
        file_ownership = [
            {"pathPattern": "adapters/mcp/*", "exclusiveOwnerRole": "Implementation Agent"}
        ]

        # 1. Valid Dry Run
        res = self.tools.create_work_plan(
            workstream_id="WS-08",
            title="MCP Adapter Integration",
            assigned_agent_role="Implementation Agent",
            phases=phases,
            tasks=tasks,
            file_ownership=file_ownership,
            dry_run=True,
        )
        self.assertTrue(res["success"])
        self.assertTrue(res["dryRun"])
        self.assertEqual(res["tasksCount"], 2)
        self.assertIn("contractEnvelope", res)

        # 2. Circular dependency detection
        cyclic_tasks = [
            {
                "taskId": "TASK-001",
                "phaseNumber": 1,
                "title": "A",
                "assignedAgent": "Lead",
                "dependencies": ["TASK-002"],
                "allowedFiles": [],
                "forbiddenFiles": [],
                "verificationCommand": "true",
                "status": "PENDING",
            },
            {
                "taskId": "TASK-002",
                "phaseNumber": 1,
                "title": "B",
                "assignedAgent": "Lead",
                "dependencies": ["TASK-001"],
                "allowedFiles": [],
                "forbiddenFiles": [],
                "verificationCommand": "true",
                "status": "PENDING",
            },
        ]
        res_cyclic = self.tools.create_work_plan(
            workstream_id="WS-09",
            title="Cyclic Plan",
            assigned_agent_role="Implementation Agent",
            phases=phases,
            tasks=cyclic_tasks,
            file_ownership=file_ownership,
            dry_run=True,
        )
        self.assertFalse(res_cyclic["success"])
        self.assertTrue(any("Circular dependency" in err for err in res_cyclic["payloadErrors"]))

    def test_create_work_plan_persistence_in_temp_workspace(self):
        """Ensure create_work_plan atomically persists contract when dry_run=False."""
        temp_ws = _create_temp_workspace()
        try:
            temp_tools = ProjectIntelligenceTools(workspace_root=temp_ws)
            phases = [{"phaseNumber": 1, "name": "Phase 1", "goal": "Goal 1"}]
            tasks = [
                {
                    "taskId": "TASK-100",
                    "phaseNumber": 1,
                    "title": "Persist Test",
                    "assignedAgent": "Agent",
                    "dependencies": [],
                    "allowedFiles": [],
                    "forbiddenFiles": [],
                    "verificationCommand": "echo 1",
                    "status": "PENDING",
                }
            ]
            file_ownership = [{"pathPattern": "test/*", "exclusiveOwnerRole": "Agent"}]

            res = temp_tools.create_work_plan(
                workstream_id="WS-10",
                title="Persisted Plan",
                assigned_agent_role="Agent",
                phases=phases,
                tasks=tasks,
                file_ownership=file_ownership,
                dry_run=False,
            )
            self.assertTrue(res["success"])
            self.assertFalse(res["dryRun"])

            written_file = temp_ws / "contracts" / "implementation" / "contract.json"
            self.assertTrue(written_file.exists())
            with open(written_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved["contractId"], "plan-ws-10")
            self.assertEqual(saved["status"], "DRAFT")
        finally:
            shutil.rmtree(temp_ws, ignore_errors=True)

    def test_advance_lifecycle_gate_transitions_and_approvals(self):
        """Ensure advance_lifecycle_gate validates FSM transitions and human approval."""
        # Workspace pinned at G0, and contracts/project/contract.json is APPROVED.
        # Transition G0 -> G1 via G0_APPROVED requires human approval.
        temp_ws = _create_temp_workspace()
        self.addCleanup(shutil.rmtree, temp_ws, ignore_errors=True)
        tools = ProjectIntelligenceTools(workspace_root=temp_ws)

        # 1. Missing approval fails
        res_no_appr = tools.advance_lifecycle_gate(
            target_gate="G1",
            condition="G0_APPROVED",
            approved_by="",
            dry_run=True,
        )
        self.assertFalse(res_no_appr["success"])
        self.assertIn("explicit human approval", res_no_appr["error"].lower())

        # 2. With human approval passes in dry_run
        res_ok = tools.advance_lifecycle_gate(
            target_gate="G1",
            condition="G0_APPROVED",
            approved_by="Lead Architect",
            dry_run=True,
        )
        self.assertTrue(res_ok["success"])
        self.assertTrue(res_ok["dryRun"])
        self.assertEqual(res_ok["proposedGate"], "G1")

        # 3. Illegal gate skipping is blocked (G0 -> G4)
        res_skip = tools.advance_lifecycle_gate(
            target_gate="G4",
            condition="G0_APPROVED",
            approved_by="Lead Architect",
            dry_run=True,
        )
        self.assertFalse(res_skip["success"])
        self.assertIn("blocked", res_skip["error"].lower())

    def test_advance_lifecycle_gate_persistence_in_temp_workspace(self):
        """Ensure advance_lifecycle_gate atomically updates execution-state.json when dry_run=False."""
        temp_ws = _create_temp_workspace()
        try:
            temp_tools = ProjectIntelligenceTools(workspace_root=temp_ws)

            res = temp_tools.advance_lifecycle_gate(
                target_gate="G1",
                condition="G0_APPROVED",
                approved_by="Lead Architect",
                dry_run=False,
            )
            self.assertTrue(res["success"])
            self.assertFalse(res["dryRun"])
            self.assertEqual(res["currentGate"], "G1")

            # Check file on disk
            with open(temp_ws / "memory" / "execution-state.json", "r", encoding="utf-8") as f:
                updated_state = json.load(f)
            self.assertEqual(updated_state["currentGate"], "G1")
            self.assertEqual(updated_state["activePhase"], 1)
        finally:
            shutil.rmtree(temp_ws, ignore_errors=True)

    def test_reconcile_project_memory_preview_and_preservation(self):
        """Ensure reconcile_project_memory supports preview and preserves human edits on update."""
        temp_ws = _create_temp_workspace()
        try:
            temp_tools = ProjectIntelligenceTools(workspace_root=temp_ws)
            state_file = temp_ws / "memory" / "execution-state.json"

            # Inject human task
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            state_data["activeTasks"] = ["HUMAN-ACTIVE-TASK-999"]
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2)

            # 1. Preview mode (update_mode=False) does not change file
            rep_preview = temp_tools.reconcile_project_memory(update_mode=False)
            self.assertIn("reconciliation_status", rep_preview)

            with open(state_file, "r", encoding="utf-8") as f:
                reloaded = json.load(f)
            self.assertEqual(reloaded["activeTasks"], ["HUMAN-ACTIVE-TASK-999"])

            # 2. Update mode (update_mode=True) updates telemetry while preserving human tasks
            rep_update = temp_tools.reconcile_project_memory(update_mode=True)
            self.assertIn("reconciliation_status", rep_update)

            with open(state_file, "r", encoding="utf-8") as f:
                updated = json.load(f)
            self.assertEqual(updated["activeTasks"], ["HUMAN-ACTIVE-TASK-999"])
        finally:
            shutil.rmtree(temp_ws, ignore_errors=True)

    def test_run_project_checks_allowlist_and_execution(self):
        """Ensure run_project_checks only runs configured checks and captures output safely."""
        # 1. Valid schemas check
        res_schemas = self.tools.run_project_checks(check_type="schemas", timeout_seconds=15)
        self.assertEqual(res_schemas["checkId"], "schemas")
        self.assertEqual(res_schemas["status"], "PASSED")
        self.assertEqual(res_schemas["exitCode"], 0)
        self.assertGreater(res_schemas["durationSeconds"], 0.0)

        # 2. Valid quality check
        res_quality = self.tools.run_project_checks(check_type="quality", timeout_seconds=15)
        self.assertEqual(res_quality["checkId"], "quality")
        self.assertEqual(res_quality["status"], "PASSED")

        # 3. Unauthorized check is rejected
        with self.assertRaises(Exception):
            self.tools.run_project_checks(check_type="unauthorized_arbitrary_shell")


if __name__ == "__main__":
    unittest.main()
