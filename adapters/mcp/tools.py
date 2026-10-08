"""
Project Intelligence — MCP Tools Implementation Module
Implements the 10 canonical tools bridging MCP protocol requests to core framework capabilities.
6 Read-Only Tools + 4 Proposed-Action Tools.
Conformance: Python 3.10+ standard library only.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from adapters.mcp.security import (
    FileBoundaryError,
    PathSecurityValidator,
    PathTraversalError,
    ProjectCheckType,
    SafeFileSystemAdapter,
    SafeGitAdapter,
    SafeSubprocessRunner,
    SecretLeakageAlert,
    SecretScrubber,
    SecurityError,
    SubprocessSecurityError,
)
from adapters.mcp.validator import ContractValidator


def _load_reconciler_module(workspace_root: pathlib.Path):
    """Loads reconciler module dynamically avoiding directory hyphen import issues."""
    if "reconciler" in sys.modules:
        return sys.modules["reconciler"]
    reconciler_path = workspace_root / "memory" / "reconciliation-rules" / "reconciler.py"
    if not reconciler_path.exists():
        reconciler_path = pathlib.Path(__file__).resolve().parents[2] / "memory" / "reconciliation-rules" / "reconciler.py"
    spec = importlib.util.spec_from_file_location("reconciler", reconciler_path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load reconciler from {reconciler_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["reconciler"] = module
    spec.loader.exec_module(module)
    return module


class ProjectIntelligenceTools:
    """Core adapter hosting the 11 Project Intelligence MCP tools."""

    def __init__(self, workspace_root: Optional[pathlib.Path] = None):
        if workspace_root is None:
            # Default to repo root
            workspace_root = pathlib.Path(__file__).resolve().parents[2]
        self.workspace_root = workspace_root.resolve(strict=True)

        # Core engines
        from core.lifecycle.engine import LifecycleEngine
        from core.quality.evaluator import QualityEvaluator

        self.lifecycle_engine = LifecycleEngine(self.workspace_root / "core" / "lifecycle" / "lifecycle-fsm.json")
        self.quality_evaluator = QualityEvaluator(self.workspace_root / "core" / "quality" / "profiles.json")

        # Security & filesystem adapters
        self.path_validator = PathSecurityValidator(self.workspace_root)
        self.fs_adapter = SafeFileSystemAdapter(self.workspace_root)
        self.git_adapter = SafeGitAdapter(self.workspace_root)
        self.subprocess_runner = SafeSubprocessRunner(self.workspace_root)

        # Reconciler module
        self.reconciler_mod = _load_reconciler_module(self.workspace_root)

    # ========================================================================
    # READ-ONLY TOOL: plan_task (orchestrator entry point for MCP clients)
    # ========================================================================
    def plan_task(self, task: str) -> Dict[str, Any]:
        """
        Plan how the orchestrator handles a request: tier, specialist or councils,
        convened personas, their skills, and the next commands. Reads framework
        files only; writes nothing.
        """
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task must be a non-empty description of what you want done")
        if len(task) > 2000:
            raise ValueError("task is limited to 2000 characters")
        from core.orchestrator.dispatch import dispatch, render_text

        result = dispatch(task, self.workspace_root)
        result["summary"] = render_text(result)
        return result

    # ========================================================================
    # 1. READ-ONLY TOOL: project_status
    # ========================================================================
    def project_status(self) -> Dict[str, Any]:
        """
        Return the verified lifecycle gate, task state, blockers, and available
        next actions using actual repository data.
        """
        state_file = self.workspace_root / "memory" / "execution-state.json"
        template_file = self.workspace_root / "memory" / "templates" / "execution-state.template.json"

        state_data, initialized_from_template, load_err = self.reconciler_mod.load_execution_state(
            state_file, template_file
        )

        current_gate_id = state_data.get("currentGate", "G0")
        gate_info = self.lifecycle_engine.get_gate(current_gate_id)

        # Compute live reconciliation alignment using canonical StateReconciler (read-only)
        reconciler = self.reconciler_mod.StateReconciler(
            repo_root=self.workspace_root,
            state_file=state_file,
            template_file=template_file,
        )
        rec_report = reconciler.reconcile(update_mode=False)

        # Contract for current gate
        req_contract_type = gate_info.get("requiredContractType", "project")
        contract_path = self.workspace_root / "contracts" / req_contract_type / "contract.json"
        contract_exists = contract_path.exists()
        contract_status = "MISSING"
        contract_id = None
        if contract_exists:
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                    contract_status = c_data.get("status", "UNKNOWN")
                    contract_id = c_data.get("contractId")
            except Exception:
                contract_status = "CORRUPTED"

        # Candidate next gates
        possible_transitions = []
        for trans in self.lifecycle_engine.transitions:
            if trans["fromGate"] == current_gate_id:
                possible_transitions.append({
                    "toGate": trans["toGate"],
                    "condition": trans["condition"],
                    "requiresHumanApproval": trans.get("requiresHumanApproval", False),
                })

        return {
            "lifecycle": {
                "currentGate": current_gate_id,
                "gateName": gate_info.get("name"),
                "description": gate_info.get("description"),
                "requiredContractType": req_contract_type,
                "contractFile": f"contracts/{req_contract_type}/contract.json",
                "contractStatus": contract_status,
                "contractId": contract_id,
                "allowedExemption": gate_info.get("allowedExemption", False),
                "entryCriteria": gate_info.get("entryCriteria", []),
                "exitCriteria": gate_info.get("exitCriteria", []),
                "possibleTransitions": possible_transitions,
            },
            "tasks": {
                "activePhase": state_data.get("activePhase", 0),
                "activeTasks": state_data.get("activeTasks", []),
                "completedTasksCount": len(state_data.get("completedTasks", [])),
                "completedTasks": state_data.get("completedTasks", []),
                "blockedTasks": state_data.get("blockedTasks", []),
            },
            "gitAlignment": {
                "isGitRepo": rec_report.is_git_repo,
                "currentBranch": rec_report.current_branch,
                "currentHead": rec_report.current_head[:8] if rec_report.current_head else "00000000",
                "lastReconciledCommit": rec_report.last_reconciled_commit[:8] if rec_report.last_reconciled_commit else "00000000",
                "driftDetected": rec_report.drift_detected,
                "reconciliationStatus": rec_report.reconciliation_status.value,
                "uncommittedChangesCount": len(rec_report.uncommitted_files),
            },
            "initializedFromTemplate": initialized_from_template,
            "stateLoadError": load_err,
        }

    # ========================================================================
    # 2. READ-ONLY TOOL: inspect_project
    # ========================================================================
    def inspect_project(
        self,
        project_root: Optional[str] = None,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        """
        Inspect a caller-specified project root within an explicitly authorized workspace boundary.
        Return a bounded summary of relevant repository structure, project instructions, and Git state.
        Do not dump the entire source tree or secrets.
        """
        target_root = self.workspace_root
        if project_root:
            target_path = pathlib.Path(project_root)
            if not target_path.is_absolute():
                target_path = (self.workspace_root / target_path).resolve()
            else:
                target_path = target_path.resolve()

            if not target_path.is_relative_to(self.workspace_root):
                raise PathTraversalError(
                    f"Authorized workspace violation: '{project_root}' escapes authorized root '{self.workspace_root}'"
                )
            target_root = target_path

        # Bounded depth
        bounded_depth = max(1, min(max_depth, 4))

        # Check standing instructions
        instructions_found = []
        for candidate_name in ["CLAUDE.md", "README.md", "CONTRIBUTING.md", "instructions/universal/core-rules.md"]:
            p = target_root / candidate_name
            if p.exists():
                instructions_found.append({
                    "path": candidate_name,
                    "sizeBytes": p.stat().st_size,
                })

        # List profiles
        profiles_dir = target_root / "instructions" / "profiles"
        available_profiles = []
        if profiles_dir.exists():
            for prof in sorted(profiles_dir.glob("*.md")):
                available_profiles.append(prof.stem)

        # Count skills & agents
        skills_dir = target_root / "skills"
        skills_count = len([d for d in skills_dir.iterdir() if d.is_dir()]) if skills_dir.exists() else 0

        agents_dir = target_root / "agents"
        agents_count = len([d for d in agents_dir.iterdir() if d.is_dir()]) if agents_dir.exists() else 0

        # Contracts count
        contracts_dir = target_root / "contracts"
        contracts_count = len(list(contracts_dir.glob("**/contract.json"))) if contracts_dir.exists() else 0

        # Top-level directory layout (bounded)
        top_level_layout = []
        for item in sorted(target_root.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
            if item.name.startswith(".") or item.name in ("__pycache__", "node_modules", ".git"):
                continue
            top_level_layout.append({
                "name": item.name,
                "isDirectory": item.is_dir(),
                "sizeBytes": item.stat().st_size if item.is_file() else None,
            })

        # Git status
        git_info = self.reconciler_mod.inspect_git_repository(target_root)
        uncommitted_files_preview = [
            {"file": u.file_path, "status": u.status_code, "isMemory": u.is_memory_file}
            for u in git_info.get("uncommitted_files", [])[:15]
        ]

        return {
            "authorizedWorkspaceRoot": str(self.workspace_root),
            "inspectedPath": str(target_root),
            "standingInstructions": instructions_found,
            "availableProfiles": available_profiles,
            "counts": {
                "skills": skills_count,
                "agents": agents_count,
                "contracts": contracts_count,
            },
            "topLevelLayout": top_level_layout,
            "gitState": {
                "isGitRepo": git_info["is_git_repo"],
                "currentBranch": git_info["current_branch"],
                "currentHead": git_info["current_head"][:8] if git_info["current_head"] else "00000000",
                "uncommittedFilesCount": len(git_info.get("uncommitted_files", [])),
                "uncommittedFilesSample": uncommitted_files_preview,
            },
        }

    # ========================================================================
    # 3. READ-ONLY TOOL: get_next_action
    # ========================================================================
    def get_next_action(self) -> Dict[str, Any]:
        """
        Use the actual lifecycle engine and contract state to identify the next
        valid action, its prerequisites, and required approvals.
        """
        state_file = self.workspace_root / "memory" / "execution-state.json"
        state_data, _, _ = self.reconciler_mod.load_execution_state(state_file)

        current_gate = state_data.get("currentGate", "G0")
        gate_info = self.lifecycle_engine.get_gate(current_gate)
        req_contract_type = gate_info.get("requiredContractType", "project")
        contract_path = self.workspace_root / "contracts" / req_contract_type / "contract.json"

        contract_status = "MISSING"
        if contract_path.exists():
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    contract_status = c.get("status", "UNKNOWN")
            except Exception:
                contract_status = "CORRUPTED"

        blocked_tasks = state_data.get("blockedTasks", [])

        # Candidate transitions
        transitions_evaluated = []
        for trans in self.lifecycle_engine.transitions:
            if trans["fromGate"] == current_gate:
                allowed, reason = self.lifecycle_engine.can_transition(
                    current_gate=current_gate,
                    target_gate=trans["toGate"],
                    condition=trans["condition"],
                )
                transitions_evaluated.append({
                    "targetGate": trans["toGate"],
                    "condition": trans["condition"],
                    "allowedByFsm": allowed,
                    "reason": reason,
                    "requiresHumanApproval": trans.get("requiresHumanApproval", False),
                })

        # Determine next action recommendation
        prerequisites = []
        required_approvals = []
        action_name = ""
        action_detail = ""

        if blocked_tasks:
            action_name = "UNBLOCK_TASKS"
            action_detail = f"There are {len(blocked_tasks)} blocked task(s) in execution state. Resolve blockers before advancing."
            prerequisites.append("Resolve blocked task dependencies in memory/execution-state.json")
        elif contract_status != "APPROVED":
            action_name = f"DRAFT_OR_APPROVE_CONTRACT"
            action_detail = (
                f"Gate {current_gate} requires an APPROVED '{req_contract_type}' contract. "
                f"Current file 'contracts/{req_contract_type}/contract.json' has status '{contract_status}'."
            )
            prerequisites.append(f"Create or review contracts/{req_contract_type}/contract.json")
            required_approvals.append(f"Approval for {req_contract_type} contract (status -> APPROVED)")
        elif current_gate == "G4":
            action_name = "RUN_VERIFICATION_SUITES"
            action_detail = "Gate G4 implementation requires executing automated test suites before advancing to review (G5)."
            prerequisites.append("Pass all mandatory verification checks via run_project_checks tool")
        else:
            # Ready to advance gate
            next_trans = next((t for t in transitions_evaluated if t["allowedByFsm"]), None)
            if next_trans:
                action_name = "ADVANCE_LIFECYCLE_GATE"
                action_detail = f"Prerequisites met. Ready to advance from {current_gate} to {next_trans['targetGate']} under condition '{next_trans['condition']}'."
                if next_trans["requiresHumanApproval"]:
                    required_approvals.append(f"Human sign-off required for transition to {next_trans['targetGate']}")
            else:
                action_name = "AWAIT_GATE_TRANSITION_CRITERIA"
                action_detail = f"Review exit criteria for gate {current_gate}."

        return {
            "currentGate": current_gate,
            "gateName": gate_info.get("name"),
            "requiredContract": {
                "type": req_contract_type,
                "path": f"contracts/{req_contract_type}/contract.json",
                "status": contract_status,
                "isApproved": contract_status == "APPROVED",
            },
            "nextAction": {
                "action": action_name,
                "details": action_detail,
                "prerequisites": prerequisites,
                "requiredApprovals": required_approvals,
            },
            "candidateTransitions": transitions_evaluated,
        }

    # ========================================================================
    # 4. READ-ONLY TOOL: validate_contract
    # ========================================================================
    def validate_contract(
        self,
        contract_path: Optional[str] = None,
        contract_type: Optional[str] = None,
        contract_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate a specified contract using the existing schemas and validation logic.
        Return structured errors and the actual validation result.
        """
        if contract_data is not None:
            is_valid, env_errs, pay_errs, warns = ContractValidator.validate_contract(contract_data)
            return {
                "valid": is_valid,
                "source": "in-memory payload",
                "contractId": contract_data.get("contractId"),
                "contractType": contract_data.get("contractType"),
                "lifecycleGate": contract_data.get("lifecycleGate"),
                "status": contract_data.get("status"),
                "envelopeErrors": env_errs,
                "payloadErrors": pay_errs,
                "warnings": warns,
            }

        # Resolve path
        if not contract_path and contract_type:
            contract_path = f"contracts/{contract_type}/contract.json"

        if not contract_path:
            raise ValueError("Must specify either contract_path, contract_type, or contract_data")

        resolved_path = self.path_validator.validate_read_path(contract_path)
        is_valid, data, env_errs, pay_errs, warns = ContractValidator.validate_file(resolved_path)

        return {
            "valid": is_valid,
            "source": str(resolved_path.relative_to(self.workspace_root)),
            "contractId": data.get("contractId") if data else None,
            "contractType": data.get("contractType") if data else None,
            "lifecycleGate": data.get("lifecycleGate") if data else None,
            "status": data.get("status") if data else None,
            "envelopeErrors": env_errs,
            "payloadErrors": pay_errs,
            "warnings": warns,
        }

    # ========================================================================
    # 5. READ-ONLY TOOL: evaluate_quality
    # ========================================================================
    def evaluate_quality(
        self,
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        profile_name: Optional[str] = None,
        verification_suites: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke the existing quality evaluator where supported.
        Return the selected profile, checks performed, check statuses, and evidence.
        If a check cannot run, mark it unavailable or blocked.
        """
        selected_profile = profile_name or "STANDARD"
        profile_info = self.quality_evaluator.get_profile(selected_profile)

        # Anti-slop checks
        anti_slop_violations: List[str] = []
        content_scanned = False

        if content:
            anti_slop_violations = self.quality_evaluator.evaluate_anti_slop(content)
            content_scanned = True
        elif file_path:
            resolved = self.path_validator.validate_read_path(file_path)
            with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                file_text = f.read()
            anti_slop_violations = self.quality_evaluator.evaluate_anti_slop(file_text)
            content_scanned = True

        # Verification honesty check
        honesty_passed = True
        honesty_issues: List[str] = []

        if verification_suites is not None:
            honesty_passed, honesty_issues = self.quality_evaluator.evaluate_verification_honesty(
                verification_suites
            )
        else:
            # Default to checking quality contract suites if present
            qc_file = self.workspace_root / "contracts" / "quality" / "contract.json"
            if qc_file.exists():
                try:
                    with open(qc_file, "r", encoding="utf-8") as f:
                        qc_data = json.load(f)
                    default_suites = qc_data.get("data", {}).get("verificationSuites", [])
                    if default_suites:
                        honesty_passed, honesty_issues = self.quality_evaluator.evaluate_verification_honesty(
                            default_suites
                        )
                except Exception:
                    pass

        # Determine overall quality status
        overall_status = "PASSED"
        if anti_slop_violations or not honesty_passed:
            overall_status = "FAILED"

        return {
            "profile": {
                "profileName": selected_profile,
                "description": profile_info.get("description"),
                "minCoveragePercent": profile_info.get("minCoveragePercent"),
                "requiresIndependentReview": profile_info.get("requiresIndependentReview"),
                "rulesEnforced": profile_info.get("rulesEnforced", []),
            },
            "antiSlopCheck": {
                "performed": content_scanned,
                "passed": len(anti_slop_violations) == 0,
                "violations": anti_slop_violations,
            },
            "verificationHonestyCheck": {
                "performed": verification_suites is not None,
                "passed": honesty_passed,
                "issues": honesty_issues,
            },
            "overallStatus": overall_status,
        }

    # ========================================================================
    # 6. READ-ONLY TOOL: get_project_memory
    # ========================================================================
    def get_project_memory(
        self,
        section: str = "summary",
        max_items: int = 10,
    ) -> Dict[str, Any]:
        """
        Read selected durable knowledge, execution state, and backlog records.
        Support bounded retrieval rather than unrestricted dumping of all memory.
        """
        memory_dir = self.workspace_root / "memory"
        durable_path = memory_dir / "durable-knowledge.json"
        execution_path = memory_dir / "execution-state.json"
        backlog_path = memory_dir / "backlog.json"

        max_items = max(1, min(max_items, 50))

        result: Dict[str, Any] = {"section": section}

        if section in ("summary", "all", "durable_knowledge"):
            if durable_path.exists():
                with open(durable_path, "r", encoding="utf-8") as f:
                    durable = json.load(f)
                if section == "durable_knowledge" or section == "all":
                    result["durableKnowledge"] = durable
                else:
                    # Bounded summary
                    result["goals"] = durable.get("goals", [])[:max_items]
                    result["architecturalDecisions"] = [
                        {"id": ad.get("decisionId"), "title": ad.get("title")}
                        for ad in durable.get("architecturalDecisions", [])[:max_items]
                    ]
                    result["codingConventionsCount"] = len(durable.get("codingConventions", []))

        if section in ("summary", "all", "execution_state"):
            if execution_path.exists():
                with open(execution_path, "r", encoding="utf-8") as f:
                    exec_state = json.load(f)
                if section == "execution_state" or section == "all":
                    result["executionState"] = exec_state
                else:
                    result["currentGate"] = exec_state.get("currentGate")
                    result["activePhase"] = exec_state.get("activePhase")
                    result["activeTasks"] = exec_state.get("activeTasks", [])[:max_items]
                    result["completedTasksCount"] = len(exec_state.get("completedTasks", []))
                    result["blockedTasksCount"] = len(exec_state.get("blockedTasks", []))
                    result["reconciliationStatus"] = exec_state.get("reconciliationStatus")

        if section in ("summary", "all", "backlog"):
            if backlog_path.exists():
                with open(backlog_path, "r", encoding="utf-8") as f:
                    backlog = json.load(f)
                if section == "backlog" or section == "all":
                    result["backlog"] = backlog
                else:
                    result["bugs"] = backlog.get("bugs", [])[:max_items]
                    result["technicalDebtCount"] = len(backlog.get("technicalDebt", []))
                    result["deferredItemsCount"] = len(backlog.get("deferredItems", []))

        # Redact any accidental secrets
        raw_json = json.dumps(result, ensure_ascii=False)
        scrubbed_json = SecretScrubber.redact_secrets(raw_json)
        return json.loads(scrubbed_json)

    # ========================================================================
    # 7. PROPOSED-ACTION TOOL: create_work_plan
    # ========================================================================
    def create_work_plan(
        self,
        workstream_id: str,
        title: str,
        assigned_agent_role: str,
        phases: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        file_ownership: List[Dict[str, Any]],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a proposed plan based on approved requirements and the existing contracts.
        Keep the result in draft form unless explicitly authorizing persistence.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        contract_payload = {
            "workstreamId": workstream_id,
            "assignedAgentRole": assigned_agent_role,
            "phases": phases,
            "tasks": tasks,
            "fileOwnership": file_ownership,
        }

        envelope = {
            "schemaVersion": "1.0.0",
            "contractId": f"plan-{workstream_id.lower()}",
            "contractType": "implementation",
            "title": title,
            "status": "DRAFT",
            "lifecycleGate": "G4",
            "createdAt": now_iso,
            "updatedAt": now_iso,
            "author": {
                "role": assigned_agent_role,
                "identifier": "mcp-planning-agent",
            },
            "data": contract_payload,
        }

        # Validate contract
        is_valid, env_errs, pay_errs, warns = ContractValidator.validate_contract(envelope)
        if not is_valid:
            return {
                "success": False,
                "dryRun": dry_run,
                "error": "Work plan failed schema validation",
                "envelopeErrors": env_errs,
                "payloadErrors": pay_errs,
                "warnings": warns,
            }

        target_file = self.workspace_root / "contracts" / "implementation" / "contract.json"
        persisted_path = None

        if not dry_run:
            self.fs_adapter.atomic_write_json(target_file, envelope)
            persisted_path = str(target_file.relative_to(self.workspace_root))

        return {
            "success": True,
            "dryRun": dry_run,
            "contractId": envelope["contractId"],
            "status": envelope["status"],
            "targetPath": persisted_path or f"(dry run) would write to contracts/implementation/contract.json",
            "tasksCount": len(tasks),
            "phasesCount": len(phases),
            "contractEnvelope": envelope,
            "warnings": warns,
        }

    # ========================================================================
    # 8. PROPOSED-ACTION TOOL: advance_lifecycle_gate
    # ========================================================================
    def advance_lifecycle_gate(
        self,
        target_gate: str,
        condition: str,
        approved_by: Optional[str] = None,
        is_exempt: bool = False,
        exemption_justification: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Request a transition through the existing lifecycle engine.
        Enforce prerequisites, valid transitions, required approvals, and contract validation.
        Do not provide a bypass for mandatory gates.
        """
        state_file = self.workspace_root / "memory" / "execution-state.json"
        state_data, _, load_err = self.reconciler_mod.load_execution_state(state_file)
        if load_err:
            return {"success": False, "error": f"Failed to load execution state: {load_err}"}

        current_gate = state_data.get("currentGate", "G0")

        # Verify contract for current gate is approved
        current_gate_spec = self.lifecycle_engine.get_gate(current_gate)
        req_contract_type = current_gate_spec.get("requiredContractType", "project")
        contract_file = self.workspace_root / "contracts" / req_contract_type / "contract.json"

        # Check required contract approval unless G2 exemption
        if not (current_gate == "G1" and target_gate == "G3" and is_exempt):
            if not contract_file.exists():
                return {
                    "success": False,
                    "error": f"Mandatory gate prerequisite missing: contracts/{req_contract_type}/contract.json does not exist.",
                }
            with open(contract_file, "r", encoding="utf-8") as f:
                c_data = json.load(f)
            if c_data.get("status") != "APPROVED":
                return {
                    "success": False,
                    "error": (
                        f"Mandatory gate prerequisite failed: contract '{req_contract_type}' "
                        f"status is '{c_data.get('status')}', but must be 'APPROVED' before advancing."
                    ),
                }

        # Check transition legality via core LifecycleEngine
        is_allowed, reason = self.lifecycle_engine.can_transition(
            current_gate=current_gate,
            target_gate=target_gate,
            condition=condition,
            is_exempt=is_exempt,
            exemption_justification=exemption_justification,
        )

        if not is_allowed:
            return {
                "success": False,
                "currentGate": current_gate,
                "targetGate": target_gate,
                "error": f"Lifecycle transition blocked: {reason}",
            }

        # Check required human approval
        matching_trans = [
            t for t in self.lifecycle_engine.transitions
            if t["fromGate"] == current_gate and t["toGate"] == target_gate
        ]
        requires_approval = any(t.get("requiresHumanApproval", False) for t in matching_trans)

        if requires_approval and (not approved_by or len(approved_by.strip()) < 3):
            return {
                "success": False,
                "currentGate": current_gate,
                "targetGate": target_gate,
                "requiresHumanApproval": True,
                "error": "Transition requires explicit human approval ('approved_by' parameter missing or empty).",
            }

        # If not dry run, persist update atomically
        if not dry_run:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            state_data["currentGate"] = target_gate
            if target_gate.startswith("G") and target_gate[1:].isdigit():
                state_data["activePhase"] = int(target_gate[1:])
            state_data["lastReconciledAt"] = now_iso
            self.fs_adapter.atomic_write_json(state_file, state_data)

        return {
            "success": True,
            "dryRun": dry_run,
            "previousGate": current_gate,
            "currentGate": target_gate if not dry_run else current_gate,
            "proposedGate": target_gate,
            "condition": condition,
            "reason": reason,
            "approvedBy": approved_by,
            "persisted": not dry_run,
        }

    # ========================================================================
    # 9. PROPOSED-ACTION TOOL: reconcile_project_memory
    # ========================================================================
    def reconcile_project_memory(
        self,
        update_mode: bool = False,
        repair_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Use the existing reconciler. Support a preview or dry-run mode before
        changes are persisted. Preserve uncommitted user work and never store secrets in memory.
        """
        state_file = self.workspace_root / "memory" / "execution-state.json"
        template_file = self.workspace_root / "memory" / "templates" / "execution-state.template.json"

        reconciler = self.reconciler_mod.StateReconciler(
            repo_root=self.workspace_root,
            state_file=state_file,
            template_file=template_file,
        )

        report = reconciler.reconcile(
            update_mode=update_mode,
            repair_mode=repair_mode,
        )

        report_dict = report.to_dict()

        # Scrub report output for any detected secret patterns
        scrubbed_json = SecretScrubber.redact_secrets(json.dumps(report_dict, ensure_ascii=False))
        return json.loads(scrubbed_json)

    # ========================================================================
    # 10. PROPOSED-ACTION TOOL: run_project_checks
    # ========================================================================
    def run_project_checks(
        self,
        check_type: str = "all_tests",
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """
        Allow only approved, project-configured commands.
        Use an allowlist, bounded output, timeouts, and safe working-directory rules.
        Do not accept arbitrary shell commands from the model.
        """
        result = self.subprocess_runner.run_check(
            check_name=check_type,
            timeout_seconds=timeout_seconds,
        )
        return result.to_dict()
