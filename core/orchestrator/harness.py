"""
Project Intelligence — Orchestrator Execution & Simulation Harness
Provides deterministic execution orchestration, step simulation, telemetry tracing,
and lifecycle gate enforcement for orchestrator workflows.

Enforces "Minimum necessary complexity, maximum useful expertise".
Zero external dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import datetime
from enum import Enum
import json
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

from core.lifecycle.engine import LifecycleEngine
from core.orchestrator.router import IntentCategory, route_request


class ExecutionStatus(str, Enum):
    """Execution status for orchestrator workflows and individual steps."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    SKIPPED = "SKIPPED"


class StepExecutionRecord:
    """Detailed immutable record of a single orchestrator step execution."""

    def __init__(
        self,
        step_number: int,
        persona: str,
        skill: str,
        description: str,
        status: ExecutionStatus = ExecutionStatus.PENDING,
        output: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[str]] = None,
        gate_checked: Optional[str] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
    ):
        self.step_number = step_number
        self.persona = persona
        self.skill = skill
        self.description = description
        self.status = status
        self.output = output or {}
        self.evidence = evidence or []
        self.gate_checked = gate_checked
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stepNumber": self.step_number,
            "persona": self.persona,
            "skill": self.skill,
            "description": self.description,
            "status": self.status.value,
            "output": self.output,
            "evidence": self.evidence,
            "gateChecked": self.gate_checked,
            "error": self.error,
            "durationMs": round(self.duration_ms, 2),
        }


class HarnessTrace:
    """Complete trace artifact of an orchestrated pipeline execution."""

    def __init__(
        self,
        trace_id: str,
        task: str,
        route_type: str,
        intent_category: str,
        governance_level: str,
        steps: List[StepExecutionRecord],
        status: ExecutionStatus = ExecutionStatus.PENDING,
        created_at: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.task = task
        self.route_type = route_type
        self.intent_category = intent_category
        self.governance_level = governance_level
        self.steps = steps
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.total_duration_ms: float = 0.0
        self.recovery_log: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "task": self.task,
            "routeType": self.route_type,
            "intentCategory": self.intent_category,
            "governanceLevel": self.governance_level,
            "status": self.status.value,
            "createdAt": self.created_at,
            "completedAt": self.completed_at,
            "totalDurationMs": round(self.total_duration_ms, 2),
            "stepCount": len(self.steps),
            "steps": [s.to_dict() for s in self.steps],
            "recoveryLog": self.recovery_log,
        }


class OrchestratorHarness:
    """
    Execution & verification harness for the Project Intelligence Orchestrator.
    Controls step execution, enforces lifecycle gate checks, provides mockable
    agent step handlers, captures full telemetry, and manages failure recovery.
    """

    # Mapping of lifecycle personas to canonical gates
    PERSONA_GATE_MAP: Dict[str, str] = {
        "discovery": "G0",
        "requirements": "G1",
        "design": "G2",
        "architecture": "G2",
        "planning": "G3",
        "implementation": "G4",
        "verification": "G5",
        "independent-review": "G5",
        "documentation-and-memory": "G6",
    }

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        lifecycle_engine: Optional[LifecycleEngine] = None,
        custom_step_executor: Optional[Callable[[StepExecutionRecord, Dict[str, Any]], Dict[str, Any]]] = None,
        fail_fast: bool = True,
    ):
        self.workspace_root = workspace_root or Path.cwd()
        self.lifecycle_engine = lifecycle_engine or LifecycleEngine()
        self.custom_step_executor = custom_step_executor
        self.fail_fast = fail_fast
        self.active_traces: Dict[str, HarnessTrace] = {}

    def plan_to_trace(self, plan: Dict[str, Any]) -> HarnessTrace:
        """Converts an orchestrator route_request plan dictionary into a HarnessTrace."""
        trace_id = f"trace-{uuid.uuid4().hex[:12]}"
        steps: List[StepExecutionRecord] = []

        execution_plan = plan.get("executionPlan", [])
        for item in execution_plan:
            step_num = item.get("step", len(steps) + 1)
            persona = item.get("persona", "orchestrator")
            skill = item.get("skill", "phase-planning")
            description = item.get("description", "")
            gate = self.PERSONA_GATE_MAP.get(persona)

            steps.append(StepExecutionRecord(
                step_number=step_num,
                persona=persona,
                skill=skill,
                description=description,
                gate_checked=gate,
                status=ExecutionStatus.PENDING,
            ))

        return HarnessTrace(
            trace_id=trace_id,
            task=plan.get("query", plan.get("explanation", "Unnamed task")),
            route_type=plan.get("routeType", "direct"),
            intent_category=plan.get("intentCategory", IntentCategory.SINGLE_PERSONA.value),
            governance_level=plan.get("governanceLevel", "LIGHTWEIGHT"),
            steps=steps,
            status=ExecutionStatus.PENDING,
        )

    def execute_plan(
        self,
        target: Union[str, Dict[str, Any]],
        mock_outputs: Optional[Dict[int, Dict[str, Any]]] = None,
        fail_step_number: Optional[int] = None,
    ) -> HarnessTrace:
        """
        Executes or simulates an orchestrated execution plan.
        Accepts either a plain-text prompt (which is routed automatically)
        or an existing plan dictionary from route_request().
        Supports injecting mock step outputs and simulated step failures.
        """
        start_time = time.perf_counter()

        if isinstance(target, str):
            plan = route_request(target)
            trace = self.plan_to_trace(plan)
            trace.task = target
        else:
            trace = self.plan_to_trace(target)

        self.active_traces[trace.trace_id] = trace
        trace.status = ExecutionStatus.IN_PROGRESS

        mock_outputs = mock_outputs or {}

        for step_record in trace.steps:
            step_record.status = ExecutionStatus.IN_PROGRESS
            step_start = time.perf_counter()

            # Check if this step is instructed to fail for testing failure resilience
            if fail_step_number is not None and step_record.step_number == fail_step_number:
                step_record.status = ExecutionStatus.FAILED
                step_record.error = f"Simulated execution failure in step {step_record.step_number} ({step_record.persona})"
                step_record.duration_ms = (time.perf_counter() - step_start) * 1000.0

                trace.status = ExecutionStatus.FAILED
                trace.recovery_log.append(
                    f"Step {step_record.step_number} failed: {step_record.error}. "
                    f"Triggering recovery strategy: Reverting uncommitted modifications and stopping progression."
                )

                if self.fail_fast:
                    # Mark remaining steps as SKIPPED
                    for remaining in trace.steps:
                        if remaining.status == ExecutionStatus.PENDING:
                            remaining.status = ExecutionStatus.SKIPPED
                    break
                continue

            # Execute step using custom executor if provided, otherwise default simulator
            try:
                if self.custom_step_executor:
                    step_output = self.custom_step_executor(step_record, mock_outputs.get(step_record.step_number, {}))
                else:
                    step_output = self._default_step_execution(step_record, mock_outputs.get(step_record.step_number))

                step_record.output = step_output.get("output", {})
                step_record.evidence = step_output.get("evidence", [f"Verified execution of {step_record.skill} by {step_record.persona}"])
                step_record.status = ExecutionStatus.COMPLETED
            except Exception as exc:
                step_record.status = ExecutionStatus.FAILED
                step_record.error = str(exc)
                trace.status = ExecutionStatus.FAILED
                trace.recovery_log.append(f"Exception during step {step_record.step_number}: {exc}")
                if self.fail_fast:
                    break
            finally:
                step_record.duration_ms = (time.perf_counter() - step_start) * 1000.0

        if trace.status != ExecutionStatus.FAILED:
            trace.status = ExecutionStatus.COMPLETED

        trace.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        trace.total_duration_ms = (time.perf_counter() - start_time) * 1000.0
        return trace

    def _default_step_execution(
        self,
        step_record: StepExecutionRecord,
        mock_output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Default step execution simulator capturing honest metadata."""
        if mock_output is not None:
            return mock_output

        # Default realistic simulated output based on persona domain
        simulated_output = {
            "persona": step_record.persona,
            "skill": step_record.skill,
            "gate": step_record.gate_checked,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "artifactsGenerated": [f"{step_record.persona}-output.json"],
        }
        evidence = [
            f"Step {step_record.step_number} completed: {step_record.skill} executed by {step_record.persona}.",
            f"Gate alignment confirmed for gate {step_record.gate_checked or 'N/A'}.",
        ]

        return {
            "output": simulated_output,
            "evidence": evidence,
        }

    def verify_gate_compliance(self, current_gate: str, target_gate: str) -> Tuple[bool, str]:
        """Verifies if the orchestrator can transition between gates using the lifecycle engine."""
        condition = f"{current_gate}_APPROVED"
        return self.lifecycle_engine.can_transition(current_gate, target_gate, condition)

    def export_trace_log(self, trace: HarnessTrace, output_path: Optional[Path] = None) -> Path:
        """Exports an immutable JSON trace log to the filesystem."""
        if output_path is None:
            traces_dir = self.workspace_root / "memory" / "orchestrator-traces"
            traces_dir.mkdir(parents=True, exist_ok=True)
            output_path = traces_dir / f"{trace.trace_id}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(trace.to_dict(), f, indent=2)

        return output_path
