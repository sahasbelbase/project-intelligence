"""
Project Intelligence — Standard Library Contract & Schema Validator
Zero-dependency JSON Schema validator for contract envelopes and payload data.
Conformance: Python 3.10+ standard library only.
"""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class ContractValidationError(Exception):
    """Raised when a contract structure or payload is invalid."""
    pass


class ContractValidator:
    """Validates contract envelopes and payload data using Python standard library."""

    VALID_GATES: Set[str] = {"G0", "G1", "G2", "G3", "G4", "G5", "G6"}
    VALID_STATUSES: Set[str] = {
        "DRAFT",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        "SUPERSEDED",
        "DEPRECATED",
    }
    VALID_CONTRACT_TYPES: Set[str] = {
        "project",
        "requirements",
        "design",
        "architecture",
        "implementation",
        "quality",
        "release",
    }

    REQUIRED_PAYLOAD_FIELDS: Dict[str, List[str]] = {
        "project": ["projectName", "projectSlug", "missionStatement", "inScope", "outOfScope"],
        "requirements": ["functionalRequirements", "nonFunctionalRequirements", "acceptanceCriteria", "edgeCases"],
        "design": ["isApplicable", "designSystem", "responsiveBreakpoints", "componentStates"],
        "architecture": ["systemOverview", "components", "technologyStack", "interfaceContracts"],
        "implementation": ["workstreamId", "assignedAgentRole", "phases", "tasks", "fileOwnership"],
        "quality": ["activeProfile", "baselineRulesEnforced", "verificationSuites", "antiSlopPolicy"],
        "release": ["releaseVersion", "acceptanceStatus", "verifiedDeliverables", "knownLimitations"],
    }

    CONTRACT_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
    SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    TASK_ID_PATTERN = re.compile(r"^TASK-[0-9]{3,}$")

    @classmethod
    def validate_envelope(cls, contract: Dict[str, Any]) -> List[str]:
        """Validates envelope fields required by contract-envelope.schema.json."""
        errors: List[str] = []
        if not isinstance(contract, dict):
            return ["Contract root must be a JSON object"]

        required_envelope = [
            "schemaVersion",
            "contractId",
            "contractType",
            "title",
            "status",
            "lifecycleGate",
            "createdAt",
            "updatedAt",
            "author",
            "data",
        ]

        for rf in required_envelope:
            if rf not in contract:
                errors.append(f"Missing required envelope field: '{rf}'")

        if "schemaVersion" in contract:
            if not isinstance(contract["schemaVersion"], str) or not cls.SEMVER_PATTERN.match(contract["schemaVersion"]):
                errors.append(f"Invalid schemaVersion '{contract.get('schemaVersion')}': must match SemVer (e.g. 1.0.0)")

        if "contractId" in contract:
            if not isinstance(contract["contractId"], str) or not cls.CONTRACT_ID_PATTERN.match(contract["contractId"]):
                errors.append(f"Invalid contractId '{contract.get('contractId')}': must match ^[a-z0-9-]+$")

        if "contractType" in contract:
            c_type = contract["contractType"]
            if c_type not in cls.VALID_CONTRACT_TYPES:
                errors.append(f"Invalid contractType '{c_type}'. Must be one of {sorted(list(cls.VALID_CONTRACT_TYPES))}")

        if "status" in contract:
            c_status = contract["status"]
            if c_status not in cls.VALID_STATUSES:
                errors.append(f"Invalid status '{c_status}'. Must be one of {sorted(list(cls.VALID_STATUSES))}")

        if "lifecycleGate" in contract:
            c_gate = contract["lifecycleGate"]
            if c_gate not in cls.VALID_GATES:
                errors.append(f"Invalid lifecycleGate '{c_gate}'. Must be one of {sorted(list(cls.VALID_GATES))}")

        if "title" in contract:
            if not isinstance(contract["title"], str) or len(contract["title"].strip()) < 3:
                errors.append("Field 'title' must be a string with minimum 3 characters")

        if "author" in contract:
            author = contract["author"]
            if not isinstance(author, dict):
                errors.append("'author' must be a JSON object")
            else:
                if "role" not in author or not str(author["role"]).strip():
                    errors.append("Author missing required field 'role'")
                if "identifier" not in author or not str(author["identifier"]).strip():
                    errors.append("Author missing required field 'identifier'")

        if "data" in contract and not isinstance(contract["data"], dict):
            errors.append("Field 'data' must be a JSON object")

        return errors

    @classmethod
    def validate_payload(cls, contract_type: str, data: Dict[str, Any]) -> List[str]:
        """Validates specific data payload against contract type requirements."""
        errors: List[str] = []
        if not isinstance(data, dict):
            return ["Payload data must be a JSON object"]

        expected_fields = cls.REQUIRED_PAYLOAD_FIELDS.get(contract_type)
        if not expected_fields:
            errors.append(f"Unknown contract type '{contract_type}' for payload validation")
            return errors

        for ef in expected_fields:
            if ef not in data:
                errors.append(f"Contract payload missing required field '{ef}' for type '{contract_type}'")

        # Specific type validations
        if contract_type == "implementation":
            if "phases" in data and isinstance(data["phases"], list):
                if len(data["phases"]) == 0:
                    errors.append("Implementation contract must define at least 1 phase")
                for idx, ph in enumerate(data["phases"]):
                    if not isinstance(ph, dict) or "phaseNumber" not in ph or "name" not in ph:
                        errors.append(f"Phase at index {idx} missing required fields (phaseNumber, name)")
            elif "phases" in data:
                errors.append("'phases' must be an array")

            if "tasks" in data and isinstance(data["tasks"], list):
                if len(data["tasks"]) == 0:
                    errors.append("Implementation contract must define at least 1 task")
                for idx, t in enumerate(data["tasks"]):
                    if not isinstance(t, dict):
                        errors.append(f"Task at index {idx} must be a JSON object")
                        continue
                    task_id = t.get("taskId")
                    if not task_id or not cls.TASK_ID_PATTERN.match(str(task_id)):
                        errors.append(f"Task at index {idx} invalid taskId '{task_id}': must match ^TASK-[0-9]{{3,}}$")
                    for required_task_field in ["phaseNumber", "title", "assignedAgent", "dependencies", "allowedFiles", "forbiddenFiles", "status"]:
                        if required_task_field not in t:
                            errors.append(f"Task '{task_id or idx}' missing required field '{required_task_field}'")
            elif "tasks" in data:
                errors.append("'tasks' must be an array")

        return errors

    @classmethod
    def check_dag_acyclicity(cls, tasks: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Verifies task dependencies DAG has no cycles and references existing tasks."""
        errors: List[str] = []
        task_ids = {t["taskId"] for t in tasks if isinstance(t, dict) and "taskId" in t}
        adj: Dict[str, List[str]] = {t_id: [] for t_id in task_ids}

        for t in tasks:
            if not isinstance(t, dict) or "taskId" not in t:
                continue
            t_id = t["taskId"]
            deps = t.get("dependencies", [])
            if not isinstance(deps, list):
                errors.append(f"Task '{t_id}' dependencies must be an array")
                continue
            for dep in deps:
                if dep not in task_ids:
                    errors.append(f"Task '{t_id}' depends on non-existent task '{dep}'")
                else:
                    adj[t_id].append(dep)

        if errors:
            return False, errors

        # Cycle detection via DFS
        visited: Dict[str, int] = {t_id: 0 for t_id in task_ids}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(node: str, path: List[str]) -> bool:
            visited[node] = 1
            for nxt in adj.get(node, []):
                if visited[nxt] == 1:
                    errors.append(f"Circular dependency detected: {' -> '.join(path + [nxt])}")
                    return True
                elif visited[nxt] == 0:
                    if dfs(nxt, path + [nxt]):
                        return True
            visited[node] = 2
            return False

        for node in task_ids:
            if visited[node] == 0:
                dfs(node, [node])

        return len(errors) == 0, errors

    @classmethod
    def validate_contract(cls, contract: Dict[str, Any]) -> Tuple[bool, List[str], List[str], List[str]]:
        """
        Validates full contract dict.
        Returns (is_valid, envelope_errors, payload_errors, warnings).
        """
        envelope_errors = cls.validate_envelope(contract)
        payload_errors: List[str] = []
        warnings: List[str] = []

        if "contractType" in contract and "data" in contract:
            payload_errors = cls.validate_payload(contract["contractType"], contract["data"])

        # Warnings check
        if contract.get("status") == "APPROVED" and "approval" not in contract:
            warnings.append("Contract is marked APPROVED but lacks an 'approval' record")

        if contract.get("contractType") == "implementation" and "data" in contract:
            tasks = contract["data"].get("tasks", [])
            if isinstance(tasks, list) and tasks:
                dag_ok, dag_errors = cls.check_dag_acyclicity(tasks)
                if not dag_ok:
                    payload_errors.extend(dag_errors)

        is_valid = len(envelope_errors) == 0 and len(payload_errors) == 0
        return is_valid, envelope_errors, payload_errors, warnings

    @classmethod
    def validate_file(cls, file_path: pathlib.Path) -> Tuple[bool, Dict[str, Any], List[str], List[str], List[str]]:
        """
        Loads and validates a contract file from disk.
        Returns (is_valid, contract_data, envelope_errors, payload_errors, warnings).
        """
        if not file_path.exists():
            return False, {}, [f"Contract file does not exist: {file_path}"], [], []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as err:
            return False, {}, [f"Malformed JSON in contract file: {err}"], [], []
        except Exception as err:
            return False, {}, [f"Failed to read contract file: {err}"], [], []

        is_valid, env_errs, pay_errs, warns = cls.validate_contract(data)
        return is_valid, data, env_errs, pay_errs, warns
