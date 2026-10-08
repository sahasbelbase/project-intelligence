#!/usr/bin/env python3
"""
reconciler.py — Git-Aware Memory & State Reconciliation Engine

Workstream: WS-07 (Project Intelligence)
Conformance: core/schemas/memory.schema.json, ADR-0001, ADR-0002, ADR-0003

This script inspects repository git status/log, detects memory drift, identifies
uncommitted developer edits, scans for secret exposures, and safely reconciles
`memory/execution-state.json` without destroying human developer edits.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# Constants & Regular Expressions
# ============================================================================

ZERO_COMMIT_SHA = "0000000000000000000000000000000000000000"

SECRET_PATTERNS: Dict[str, Tuple[re.Pattern, str]] = {
    "google_api_key": (
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
        "Google API / Gemini Key"
    ),
    "openai_api_key": (
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        "OpenAI Secret Key"
    ),
    "anthropic_api_key": (
        re.compile(r"sk-ant-[A-Za-z0-9-_]{32,}"),
        "Anthropic API Key"
    ),
    "github_token": (
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
        "GitHub Access Token"
    ),
    "aws_access_key": (
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "AWS Access Key ID"
    ),
    "private_key_header": (
        re.compile(r"-----BEGIN (?:[A-Z ]+)PRIVATE KEY-----"),
        "Cryptographic Private Key"
    ),
    "generic_secret_assignment": (
        re.compile(
            r"""(?i)(?:password|api[_-]?key|secret[_-]?token|auth[_-]?token)\s*[:=]\s*['"][a-zA-Z0-9_\-.~!@#$%^&*+=]{12,}['"]"""
        ),
        "Generic Password/Secret Assignment"
    ),
    "connection_string_with_pass": (
        re.compile(
            r"""(?i)(?:mongodb|postgres(?:ql)?|mysql|redis):\/\/[^:\s]+:[^@\s]+@[a-zA-Z0-9.-]+"""
        ),
        "Database Connection String with Credentials"
    ),
}


class ReconciliationStatus(str, Enum):
    CLEAN = "CLEAN"
    COMMIT_DRIFT = "COMMIT_DRIFT"
    BRANCH_SWITCH = "BRANCH_SWITCH"
    HISTORY_REWRITE = "HISTORY_REWRITE"
    UNCOMMITTED_CHANGES = "UNCOMMITTED_CHANGES"
    SECRET_ALERT = "SECRET_ALERT"
    UNINITIALIZED = "UNINITIALIZED"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    ERROR = "ERROR"


@dataclass
class SecretFinding:
    rule_name: str
    description: str
    source: str
    line_number: Optional[int]
    masked_sample: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UncommittedChange:
    file_path: str
    status_code: str
    is_staged: bool
    is_memory_file: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReconciliationReport:
    timestamp: str
    repo_root: str
    is_git_repo: bool
    current_branch: str
    current_head: str
    last_reconciled_commit: str
    last_reconciled_at: Optional[str]
    commits_ahead: int
    is_ancestor: bool
    has_uncommitted_changes: bool
    uncommitted_files: List[UncommittedChange] = field(default_factory=list)
    secret_findings: List[SecretFinding] = field(default_factory=list)
    drift_detected: bool = False
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.CLEAN
    status_message: str = ""
    reconciliation_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["reconciliation_status"] = self.reconciliation_status.value
        return data


# ============================================================================
# Git Utility Functions
# ============================================================================

def run_git(args: List[str], cwd: pathlib.Path) -> Tuple[int, str, str]:
    """Execute a git command safely and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return proc.returncode, proc.stdout.rstrip("\r\n"), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", "git executable not found in PATH"
    except subprocess.TimeoutExpired:
        return 124, "", "git command timed out after 30 seconds"
    except Exception as exc:
        return 1, "", str(exc)


def mask_secret(value: str) -> str:
    """Mask a secret value, revealing only brief edge characters."""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{'*' * (len(value) - 8)}...{value[-2:]}"


def scan_text_for_secrets(text: str, source_name: str) -> List[SecretFinding]:
    """Scan text line-by-line for potential secrets."""
    findings: List[SecretFinding] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Skip comment headers or obvious placeholder strings
        if "REDACTED" in line or "EXAMPLE" in line.upper() or "TEMPLATE" in line.upper():
            continue
        for rule_name, (pattern, desc) in SECRET_PATTERNS.items():
            matches = pattern.finditer(line)
            for match in matches:
                matched_str = match.group(0)
                # Filter false positives: zero hashes or schema URLs
                if matched_str.startswith("0000000000000000") or "schema.json" in line:
                    continue
                findings.append(
                    SecretFinding(
                        rule_name=rule_name,
                        description=desc,
                        source=source_name,
                        line_number=idx,
                        masked_sample=mask_secret(matched_str),
                    )
                )
    return findings


# ============================================================================
# Git Environment Inspector
# ============================================================================

def inspect_git_repository(repo_root: pathlib.Path) -> Dict[str, Any]:
    """Examine git status, commit history, branch, and uncommitted modifications."""
    result: Dict[str, Any] = {
        "is_git_repo": False,
        "has_commits": False,
        "current_branch": "unknown",
        "current_head": ZERO_COMMIT_SHA,
        "commit_date": None,
        "uncommitted_files": [],
        "diff_text": "",
    }

    # Verify repo
    code, out, _ = run_git(["rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    if code != 0 or out.lower() != "true":
        return result
    result["is_git_repo"] = True

    # Branch name
    code, out, _ = run_git(["symbolic-ref", "--short", "HEAD"], cwd=repo_root)
    if code == 0 and out:
        result["current_branch"] = out
    else:
        # Fallback for detached HEAD or initial repo
        code, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
        if code == 0 and out and out != "HEAD":
            result["current_branch"] = out
        else:
            code, out, _ = run_git(["rev-parse", "--short", "HEAD"], cwd=repo_root)
            result["current_branch"] = f"DETACHED_HEAD:{out}" if code == 0 else "master"

    # Check if any commits exist
    code, head_sha, _ = run_git(["rev-parse", "HEAD"], cwd=repo_root)
    if code == 0 and head_sha:
        result["has_commits"] = True
        result["current_head"] = head_sha
        code_date, commit_date, _ = run_git(["log", "-1", "--format=%cI"], cwd=repo_root)
        if code_date == 0:
            result["commit_date"] = commit_date
    else:
        result["has_commits"] = False
        result["current_head"] = ZERO_COMMIT_SHA

    # Status porcelain
    code, status_out, _ = run_git(["status", "--porcelain=v1"], cwd=repo_root)
    uncommitted_files: List[UncommittedChange] = []
    if code == 0 and status_out:
        for line in status_out.splitlines():
            if len(line) < 4:
                continue
            status_code = line[:2]
            file_path = line[3:].strip()
            # Handle renamed files
            if " -> " in file_path:
                file_path = file_path.split(" -> ")[-1].strip()
            # Handle quoted paths
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            is_staged = status_code[0] not in (" ", "?")
            is_mem = file_path == "memory" or file_path == "memory/" or file_path.startswith("memory/")
            uncommitted_files.append(
                UncommittedChange(
                    file_path=file_path,
                    status_code=status_code,
                    is_staged=is_staged,
                    is_memory_file=is_mem,
                )
            )
    result["uncommitted_files"] = uncommitted_files

    # Diff text for secret scanning (staged + unstaged modifications)
    _, diff_unstaged, _ = run_git(["diff"], cwd=repo_root)
    _, diff_staged, _ = run_git(["diff", "--cached"], cwd=repo_root)
    diff_parts = [diff_unstaged, diff_staged]

    # Also scan untracked text files (e.g. newly created .env or credentials)
    for u in uncommitted_files:
        if u.status_code.strip() == "??" and not u.is_memory_file:
            target_p = repo_root / u.file_path
            if target_p.is_file() and target_p.stat().st_size <= 256 * 1024:
                try:
                    text_content = target_p.read_text(encoding="utf-8", errors="replace")
                    diff_parts.append(f"\n--- untracked: {u.file_path} ---\n{text_content}")
                except Exception:
                    pass

    result["diff_text"] = "\n".join(p for p in diff_parts if p)

    return result


# ============================================================================
# State File Management & Schema Validation
# ============================================================================

def load_execution_state(
    state_file: pathlib.Path, template_file: Optional[pathlib.Path] = None
) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    """
    Load execution-state.json. If missing, attempts to initialize from template.
    Returns (state_data, initialized_from_template, error_message).
    """
    if not state_file.exists():
        if template_file and template_file.exists():
            try:
                with open(template_file, "r", encoding="utf-8") as tf:
                    data = json.load(tf)
                return data, True, None
            except Exception as err:
                return {}, False, f"Failed to read template {template_file}: {err}"
        return {}, False, f"State file {state_file} does not exist and no template provided"

    try:
        with open(state_file, "r", encoding="utf-8") as sf:
            data = json.load(sf)
        return data, False, None
    except Exception as err:
        return {}, False, f"Failed to parse state file {state_file}: {err}"


def validate_execution_state_dict(data: Dict[str, Any]) -> List[str]:
    """Validate core required keys and gate values."""
    errors: List[str] = []
    if not isinstance(data, dict):
        return ["Execution state must be a JSON object"]

    # Schema version
    if "schemaVersion" not in data:
        errors.append("Missing required field 'schemaVersion'")
    elif not isinstance(data["schemaVersion"], str):
        errors.append("'schemaVersion' must be a string")

    # Check for flat or wrapped executionState
    exec_dict = data.get("executionState", data)

    required_keys = ["currentGate", "activePhase", "activeTasks", "completedTasks", "blockedTasks"]
    for rk in required_keys:
        if rk not in exec_dict:
            errors.append(f"Missing required execution state field '{rk}'")

    if "currentGate" in exec_dict:
        valid_gates = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
        if exec_dict["currentGate"] not in valid_gates:
            errors.append(f"Invalid currentGate '{exec_dict['currentGate']}'. Must be one of {valid_gates}")

    if "activePhase" in exec_dict and not isinstance(exec_dict["activePhase"], int):
        errors.append("'activePhase' must be an integer")

    for arr_field in ["activeTasks", "completedTasks"]:
        if arr_field in exec_dict and not isinstance(exec_dict[arr_field], list):
            errors.append(f"'{arr_field}' must be an array")

    return errors


def atomic_write_json(file_path: pathlib.Path, data: Dict[str, Any]) -> None:
    """Safely write JSON data using an atomic rename operation."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    dir_path = file_path.parent
    temp_fd, temp_path = tempfile.mkstemp(dir=str(dir_path), prefix="reconcile_", suffix=".tmp")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # Replace atomically
        os.replace(temp_path, str(file_path))
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


# ============================================================================
# Core Reconciliation Engine
# ============================================================================

class StateReconciler:
    def __init__(
        self,
        repo_root: pathlib.Path,
        state_file: pathlib.Path,
        template_file: Optional[pathlib.Path] = None,
    ):
        self.repo_root = repo_root.resolve()
        self.state_file = state_file.resolve()
        self.template_file = template_file.resolve() if template_file else None

    def reconcile(
        self, update_mode: bool = False, repair_mode: bool = False
    ) -> ReconciliationReport:
        """
        Main reconciliation execution method.
        Inspects git, validates memory state, scans secrets, determines drift,
        and optionally updates execution-state.json preserving human changes.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        git_info = inspect_git_repository(self.repo_root)

        report = ReconciliationReport(
            timestamp=now_iso,
            repo_root=str(self.repo_root),
            is_git_repo=git_info["is_git_repo"],
            current_branch=git_info["current_branch"],
            current_head=git_info["current_head"],
            last_reconciled_commit=ZERO_COMMIT_SHA,
            last_reconciled_at=None,
            commits_ahead=0,
            is_ancestor=True,
            has_uncommitted_changes=bool(git_info["uncommitted_files"]),
            uncommitted_files=git_info["uncommitted_files"],
            secret_findings=[],
            drift_detected=False,
            reconciliation_status=ReconciliationStatus.CLEAN,
            status_message="",
            reconciliation_actions=[],
        )

        if not git_info["is_git_repo"]:
            report.reconciliation_status = ReconciliationStatus.ERROR
            report.status_message = "Target directory is not a valid git repository"
            return report

        # Secret scanning in git diff
        diff_secrets = scan_text_for_secrets(git_info["diff_text"], "git-diff")
        report.secret_findings.extend(diff_secrets)

        # Load state file
        state_data, initialized_from_template, load_err = load_execution_state(
            self.state_file, self.template_file if repair_mode or not self.state_file.exists() else None
        )

        if load_err and not repair_mode:
            report.reconciliation_status = ReconciliationStatus.ERROR
            report.status_message = f"Failed to load execution state: {load_err}"
            return report

        if initialized_from_template:
            report.reconciliation_actions.append(
                f"Initialized execution state from template: {self.template_file}"
            )

        # Validate schema of loaded state
        validation_errors = validate_execution_state_dict(state_data)
        if validation_errors:
            report.reconciliation_status = ReconciliationStatus.ERROR
            report.status_message = f"Execution state schema errors: {'; '.join(validation_errors)}"
            return report

        # Secret scanning in state file content
        state_text = json.dumps(state_data)
        state_secrets = scan_text_for_secrets(state_text, str(self.state_file))
        report.secret_findings.extend(state_secrets)

        if report.secret_findings:
            report.reconciliation_status = ReconciliationStatus.SECRET_ALERT
            report.status_message = (
                f"CRITICAL: {len(report.secret_findings)} secret pattern(s) detected. "
                "Persisting memory is blocked until credentials are scrubbed."
            )
            return report

        # Read state anchor
        last_commit = state_data.get("lastReconciledCommit", ZERO_COMMIT_SHA)
        report.last_reconciled_commit = last_commit
        report.last_reconciled_at = state_data.get("lastReconciledAt")
        recorded_branch = state_data.get("currentBranch", git_info["current_branch"])

        # Determine drift conditions
        drift_reasons: List[str] = []

        # 1. Branch mismatch
        if recorded_branch != git_info["current_branch"] and recorded_branch != "master" and git_info["current_branch"] != "master":
            drift_reasons.append(
                f"Active branch '{git_info['current_branch']}' differs from recorded branch '{recorded_branch}'"
            )
            report.reconciliation_status = ReconciliationStatus.BRANCH_SWITCH

        # 2. Commit differences
        if git_info["has_commits"]:
            if last_commit != git_info["current_head"]:
                if last_commit == ZERO_COMMIT_SHA:
                    drift_reasons.append("State not yet reconciled with initial commit")
                    report.reconciliation_status = ReconciliationStatus.UNINITIALIZED
                else:
                    # Check ancestry
                    code, _, _ = run_git(
                        ["merge-base", "--is-ancestor", last_commit, git_info["current_head"]],
                        cwd=self.repo_root,
                    )
                    if code == 0:
                        report.is_ancestor = True
                        code_ahead, ahead_str, _ = run_git(
                            ["rev-list", "--count", f"{last_commit}..{git_info['current_head']}"],
                            cwd=self.repo_root,
                        )
                        if code_ahead == 0 and ahead_str.isdigit():
                            report.commits_ahead = int(ahead_str)
                            drift_reasons.append(
                                f"Repository is {report.commits_ahead} commit(s) ahead of execution state"
                            )
                        report.reconciliation_status = ReconciliationStatus.COMMIT_DRIFT
                    else:
                        report.is_ancestor = False
                        drift_reasons.append(
                            f"Recorded commit {last_commit[:8]} is not an ancestor of HEAD (rebase or branch divergence)"
                        )
                        report.reconciliation_status = ReconciliationStatus.HISTORY_REWRITE
        else:
            # Unborn branch / repo with no commits yet
            if last_commit != ZERO_COMMIT_SHA:
                drift_reasons.append("Repository has no commits yet, but state recorded a commit hash")
            report.reconciliation_status = ReconciliationStatus.UNINITIALIZED

        # 3. Uncommitted modifications
        if report.has_uncommitted_changes:
            human_changes = [f for f in report.uncommitted_files if not f.is_memory_file]
            if human_changes:
                drift_reasons.append(
                    f"Working tree has {len(human_changes)} uncommitted human developer file(s)"
                )
                if report.reconciliation_status == ReconciliationStatus.CLEAN:
                    report.reconciliation_status = ReconciliationStatus.UNCOMMITTED_CHANGES

        report.drift_detected = bool(drift_reasons)
        if drift_reasons:
            report.status_message = " | ".join(drift_reasons)
        else:
            if not git_info["has_commits"]:
                report.reconciliation_status = ReconciliationStatus.UNINITIALIZED
                report.status_message = "Repository has no commits yet (unborn branch initialized)."
            else:
                report.reconciliation_status = ReconciliationStatus.CLEAN
                report.status_message = "Execution state is clean and fully synchronized with git"

        # Safe non-destructive update if requested
        if update_mode or (repair_mode and initialized_from_template):
            self._apply_reconciliation_update(state_data, git_info, report, now_iso)

        return report

    def _apply_reconciliation_update(
        self,
        state_data: Dict[str, Any],
        git_info: Dict[str, Any],
        report: ReconciliationReport,
        timestamp_iso: str,
    ) -> None:
        """
        Safely update execution-state.json telemetry without modifying
        human-entered fields (currentGate, activePhase, tasks, blockedTasks).
        """
        # Ensure schemaVersion exists
        if "schemaVersion" not in state_data:
            state_data["schemaVersion"] = "1.0.0"

        # Update telemetry
        state_data["lastReconciledCommit"] = git_info["current_head"]
        state_data["lastReconciledAt"] = timestamp_iso
        state_data["currentBranch"] = git_info["current_branch"]
        state_data["driftDetected"] = False
        state_data["reconciliationStatus"] = (
            ReconciliationStatus.CLEAN.value if git_info["has_commits"] else ReconciliationStatus.UNINITIALIZED.value
        )

        # Summarize uncommitted changes safely
        state_data["uncommittedChanges"] = [
            {
                "file": u.file_path,
                "statusCode": u.status_code,
                "isStaged": u.is_staged,
                "isMemoryFile": u.is_memory_file,
            }
            for u in git_info["uncommitted_files"]
        ]

        # Write atomically to execution-state.json
        atomic_write_json(self.state_file, state_data)

        # Mirror to state.json for backward compatibility with existing hooks and skills
        if self.state_file.name == "execution-state.json":
            try:
                mirror_path = self.state_file.parent / "state.json"
                atomic_write_json(mirror_path, state_data)
            except Exception:
                pass

        report.reconciliation_actions.append(
            f"Updated {self.state_file} with commit {git_info['current_head'][:8]} and branch {git_info['current_branch']}"
        )
        report.status_message = f"Reconciled successfully. Anchor: {git_info['current_head'][:8]} on {git_info['current_branch']}."
        report.drift_detected = False
        report.reconciliation_status = (
            ReconciliationStatus.CLEAN if git_info["has_commits"] else ReconciliationStatus.UNINITIALIZED
        )


# ============================================================================
# Self Test Suite
# ============================================================================

def run_self_tests() -> int:
    """Execute integrated unit and behavioral verification checks."""
    print("======================================================================")
    print("RUNNING RECONCILER ENGINE SELF-TEST SUITE")
    print("======================================================================")
    failures = 0

    def assert_true(cond: bool, msg: str) -> None:
        nonlocal failures
        if cond:
            print(f"  [PASS] {msg}")
        else:
            print(f"  [FAIL] {msg}")
            failures += 1

    # Test 1: Secret detection regex
    print("\n--- Test 1: Secret Scanning Patterns ---")
    findings = scan_text_for_secrets(
        "const key = 'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q';",
        "test-buffer"
    )
    assert_true(len(findings) == 1, "Detects Google API Key pattern")
    assert_true("..." in findings[0].masked_sample, "Secret sample is masked")

    oa_findings = scan_text_for_secrets("export OPENAI_KEY=sk-abcdef1234567890abcdef123456", "test-buffer")
    assert_true(len(oa_findings) == 1, "Detects OpenAI secret key pattern")

    clean_findings = scan_text_for_secrets("const config = { host: 'localhost', port: 8080 };", "test-buffer")
    assert_true(len(clean_findings) == 0, "No false positives on standard clean config")

    # Test 2: Schema validation logic
    print("\n--- Test 2: Execution State Schema Validation ---")
    valid_data = {
        "schemaVersion": "1.0.0",
        "lastReconciledCommit": ZERO_COMMIT_SHA,
        "currentGate": "G0",
        "activePhase": 0,
        "activeTasks": ["TASK-001"],
        "completedTasks": [],
        "blockedTasks": [],
    }
    errors = validate_execution_state_dict(valid_data)
    assert_true(len(errors) == 0, "Valid execution state dict produces 0 errors")

    invalid_data = {
        "schemaVersion": "1.0.0",
        "currentGate": "G99",  # Invalid gate
        "activePhase": "not-an-int",
    }
    errors_inv = validate_execution_state_dict(invalid_data)
    assert_true(len(errors_inv) >= 2, f"Invalid execution state caught {len(errors_inv)} schema errors")

    # Test 3: Non-destructive field merge & Atomic write
    print("\n--- Test 3: Non-Destructive Update & Atomic Persistence ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        state_file = tmp_path / "execution-state.json"
        initial_state = {
            "schemaVersion": "1.0.0",
            "lastReconciledCommit": "1111111111111111111111111111111111111111",
            "currentGate": "G2",
            "activePhase": 2,
            "activeTasks": ["HUMAN-TASK-ALPHA"],
            "completedTasks": ["HUMAN-DONE-1"],
            "blockedTasks": [{"taskId": "HUMAN-BLOCK", "reason": "Awaiting external spec"}],
        }
        with open(state_file, "w", encoding="utf-8") as sf:
            json.dump(initial_state, sf)

        reconciler = StateReconciler(repo_root=tmp_path, state_file=state_file)
        # Mock git info
        git_info = {
            "is_git_repo": True,
            "has_commits": True,
            "current_branch": "feature/reconciliation",
            "current_head": "2222222222222222222222222222222222222222",
            "uncommitted_files": [
                UncommittedChange(file_path="src/index.ts", status_code=" M", is_staged=False, is_memory_file=False)
            ],
        }
        rep = ReconciliationReport(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            repo_root=str(tmp_path),
            is_git_repo=True,
            current_branch="feature/reconciliation",
            current_head="2222222222222222222222222222222222222222",
            last_reconciled_commit="1111111111111111111111111111111111111111",
            last_reconciled_at=None,
            commits_ahead=1,
            is_ancestor=True,
            has_uncommitted_changes=True,
        )

        reconciler._apply_reconciliation_update(
            initial_state, git_info, rep, datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

        # Reload and verify human fields preserved
        with open(state_file, "r", encoding="utf-8") as rf:
            reloaded = json.load(rf)

        assert_true(reloaded["currentGate"] == "G2", "Preserves human currentGate")
        assert_true(reloaded["activeTasks"] == ["HUMAN-TASK-ALPHA"], "Preserves human activeTasks")
        assert_true(reloaded["completedTasks"] == ["HUMAN-DONE-1"], "Preserves human completedTasks")
        assert_true(reloaded["blockedTasks"][0]["taskId"] == "HUMAN-BLOCK", "Preserves human blockedTasks")
        assert_true(
            reloaded["lastReconciledCommit"] == "2222222222222222222222222222222222222222",
            "Updates lastReconciledCommit telemetry",
        )
        assert_true(reloaded["currentBranch"] == "feature/reconciliation", "Updates currentBranch telemetry")
        assert_true(len(reloaded["uncommittedChanges"]) == 1, "Persists uncommitted file summary")

    print("\n----------------------------------------------------------------------")
    if failures == 0:
        print("SELF-TEST SUMMARY: ALL CHECKS PASSED (0 failures)")
        return 0
    else:
        print(f"SELF-TEST SUMMARY: {failures} CHECK(S) FAILED")
        return 1


# ============================================================================
# Main Entry Point & CLI
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Git-Aware Memory & State Reconciliation Engine (Project Intelligence)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Autodetect defaults based on script directory
    script_dir = pathlib.Path(__file__).resolve().parent
    default_memory_dir = script_dir.parent
    default_repo_root = default_memory_dir.parent
    default_state_file = default_memory_dir / "execution-state.json"
    default_template_file = default_memory_dir / "templates" / "execution-state.template.json"

    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=default_repo_root,
        help="Path to repository root",
    )
    parser.add_argument(
        "--state-file",
        type=pathlib.Path,
        default=default_state_file,
        help="Path to memory/execution-state.json",
    )
    parser.add_argument(
        "--template-file",
        type=pathlib.Path,
        default=default_template_file,
        help="Path to execution-state.template.json",
    )
    parser.add_argument(
        "--reconcile",
        "--update",
        dest="update",
        action="store_true",
        help="Update execution-state.json with current git commit and state",
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair or initialize missing/damaged execution-state.json from template",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output structured JSON report to stdout",
    )
    parser.add_argument(
        "--scan-secrets",
        action="store_true",
        help="Run explicit secret scanner on working tree diff and state files",
    )
    parser.add_argument(
        "--test",
        "--selftest",
        dest="selftest",
        action="store_true",
        help="Execute internal self-test suite and exit",
    )

    args = parser.parse_args()

    if args.selftest:
        return run_self_tests()

    reconciler = StateReconciler(
        repo_root=args.repo_root,
        state_file=args.state_file,
        template_file=args.template_file,
    )

    report = reconciler.reconcile(
        update_mode=args.update,
        repair_mode=args.repair,
    )

    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        # Human-readable output
        print("======================================================================")
        print("PROJECT INTELLIGENCE --- MEMORY & STATE RECONCILIATION REPORT")
        print("======================================================================")
        print(f"Timestamp:              {report.timestamp}")
        print(f"Repository Root:        {report.repo_root}")
        print(f"Active Branch:          {report.current_branch}")
        print(f"Git HEAD SHA:           {report.current_head[:8]}")
        print(f"Last Reconciled Commit: {report.last_reconciled_commit[:8]}")
        print(f"Last Reconciled At:     {report.last_reconciled_at or 'Never'}")
        print(f"Commits Ahead:          {report.commits_ahead}")
        print(f"Is Ancestor:            {report.is_ancestor}")
        print(f"Uncommitted Changes:    {report.has_uncommitted_changes} ({len(report.uncommitted_files)} files)")
        print(f"Drift Detected:         {report.drift_detected}")
        print(f"Reconciliation Status:  {report.reconciliation_status.value}")
        print(f"Status Detail:          {report.status_message}")

        if report.secret_findings:
            print("\n[!] CRITICAL SECRET FINDINGS:")
            for sf in report.secret_findings:
                print(f"    - {sf.rule_name} ({sf.description}) in {sf.source}:{sf.line_number or '?'} -> {sf.masked_sample}")

        if report.uncommitted_files:
            print("\n[*] Uncommitted Files in Working Tree:")
            for uf in report.uncommitted_files:
                tag = "[MEMORY]" if uf.is_memory_file else "[HUMAN] "
                staged = "STAGED  " if uf.is_staged else "UNSTAGED"
                print(f"    {tag} [{staged}] ({uf.status_code}) {uf.file_path}")

        if report.reconciliation_actions:
            print("\n[+] Actions Taken:")
            for act in report.reconciliation_actions:
                print(f"    - {act}")
        print("======================================================================")

    # Determine exit code
    if report.reconciliation_status == ReconciliationStatus.SECRET_ALERT:
        return 2
    elif report.reconciliation_status in (ReconciliationStatus.ERROR,):
        return 3
    elif report.reconciliation_status in (
        ReconciliationStatus.COMMIT_DRIFT,
        ReconciliationStatus.BRANCH_SWITCH,
        ReconciliationStatus.HISTORY_REWRITE,
        ReconciliationStatus.UNCOMMITTED_CHANGES,
        ReconciliationStatus.DRIFT_DETECTED,
        ReconciliationStatus.UNINITIALIZED,
    ) and not args.update:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
