"""
Project Intelligence — MCP Security & Boundaries Enforcement Module
Implements SR-001 through SR-008: Zero-trust reference monitor for MCP adapter.
Conformance: Python 3.10+ standard library only.
"""

from __future__ import annotations

import enum
import json
import os
import pathlib
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ============================================================================
# Security Exceptions
# ============================================================================

class SecurityError(Exception):
    """Base exception for all MCP security violations."""
    pass


class PathTraversalError(SecurityError):
    """Raised when a path escapes the authorized project root or targets a prohibited location."""
    pass


class SubprocessSecurityError(SecurityError):
    """Raised when an unauthorized command or unsafe subprocess execution is attempted."""
    pass


class FileBoundaryError(SecurityError):
    """Raised when file size, directory entry count, or file type bounds are violated."""
    pass


class SecretLeakageAlert(SecurityError):
    """Raised when an unredacted secret is detected in a write payload or memory state."""
    pass


# ============================================================================
# Enhanced Secret Redaction Pipeline (SR-003)
# ============================================================================

SECRET_PATTERNS: Dict[str, Tuple[re.Pattern, str]] = {
    "google_api_key": (
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
        "Google API / Gemini Key"
    ),
    "anthropic_api_key": (
        re.compile(r"sk-ant-[A-Za-z0-9-_]{32,}"),
        "Anthropic API Key"
    ),
    "openai_api_key": (
        re.compile(r"sk-(?!ant-)(?:proj-)?[A-Za-z0-9-_]{20,}"),
        "OpenAI Secret Key"
    ),
    "github_token": (
        re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{82})"),
        "GitHub Access Token"
    ),
    "aws_access_key": (
        re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
        "AWS Access Key ID"
    ),
    "aws_secret_key": (
        re.compile(r"""(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['"]?[A-Za-z0-9/+=]{40}['"]?"""),
        "AWS Secret Access Key"
    ),
    "slack_token": (
        re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"),
        "Slack Token"
    ),
    "huggingface_token": (
        re.compile(r"hf_[A-Za-z0-9]{34,}"),
        "Hugging Face User Access Token"
    ),
    "jwt_bearer_token": (
        re.compile(r"Bearer\s+eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
        "Bearer JWT Token"
    ),
    "private_key_header": (
        re.compile(r"-----BEGIN (?:[A-Z0-9 ]+)PRIVATE KEY(?: BLOCK)?-----"),
        "Cryptographic Private Key Header"
    ),
    "generic_secret_assignment": (
        re.compile(
            r"""(?i)(?:password|passwd|api[_-]?key|secret[_-]?token|auth[_-]?token|client[_-]?secret)\s*[:=]\s*['"][a-zA-Z0-9_\-.~!@#$%^&*+=]{10,}['"]"""
        ),
        "Generic Password/Secret Assignment"
    ),
    "connection_string_with_pass": (
        re.compile(
            r"""(?i)(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|mssql):\/\/[^:\s]+:[^@\s]+@[a-zA-Z0-9.-]+(?::[0-9]+)?(?:\/[^\s"']*)?"""
        ),
        "Database Connection String with Password"
    ),
}


class SecretScrubber:
    """Provides high-performance text sanitization and secret masking."""

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """
        Replaces all detected secret patterns in text with [REDACTED:<RULE_NAME>].
        Does not reveal edge characters or entropy.
        """
        if not text:
            return ""

        scrubbed = text
        for rule_name, (pattern, _) in SECRET_PATTERNS.items():
            scrubbed = pattern.sub(f"[REDACTED:{rule_name.upper()}]", scrubbed)
        return scrubbed

    @classmethod
    def scan_for_secrets(cls, text: str) -> List[Tuple[str, str]]:
        """
        Scans text for secrets and returns a list of (rule_name, description).
        Returns empty list if clean.
        """
        findings = []
        for rule_name, (pattern, desc) in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append((rule_name, desc))
        return findings

    @classmethod
    def sanitize_error(cls, exc: Exception) -> str:
        """Sanitizes an exception message, redacting any embedded paths or keys."""
        err_msg = str(exc)
        return cls.redact_secrets(err_msg)


# ============================================================================
# Path Traversal & Workspace Boundary Enforcement (SR-001, SR-002)
# ============================================================================

class PathSecurityValidator:
    """Validates paths against authorized workspace root, symlinks, and forbidden paths."""

    FORBIDDEN_INTERNAL_DIRS: Set[str] = {
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
    }

    FORBIDDEN_FILE_PATTERNS: List[re.Pattern] = [
        re.compile(r"^\.env(?:\..*)?$", re.IGNORECASE),
        re.compile(r".*\.(?:pem|key|pkcs12|pfx|p12)$", re.IGNORECASE),
        re.compile(r"^id_(?:rsa|dsa|ecdsa|ed25519)$", re.IGNORECASE),
        re.compile(r"^(?:credentials|service[_-]account.*)\.json$", re.IGNORECASE),
    ]

    MUTABLE_SUBDIRECTORIES: Set[str] = {
        "memory",
        "contracts",
        "validation/reports",
    }

    def __init__(self, workspace_root: pathlib.Path):
        self.workspace_root = workspace_root.resolve(strict=True)

    def validate_read_path(
        self,
        target_path: Union[str, pathlib.Path],
        allow_internal_git: bool = False,
    ) -> pathlib.Path:
        """
        Validates that a path requested for reading is strictly within the workspace,
        resolves symlinks safely, and is not a protected sensitive credential file.
        """
        return self._resolve_and_verify(
            target_path=target_path,
            must_exist=True,
            for_write=False,
            allow_internal_git=allow_internal_git,
        )

    def validate_write_path(
        self,
        target_path: Union[str, pathlib.Path],
    ) -> pathlib.Path:
        """
        Validates that a path requested for writing is within the workspace root,
        belongs to an explicitly mutable subdirectory (SR-007), and does not overwrite
        immutable framework schemas or instructions.
        """
        resolved = self._resolve_and_verify(
            target_path=target_path,
            must_exist=False,
            for_write=True,
            allow_internal_git=False,
        )

        # Check against allowed mutable directories
        relative = resolved.relative_to(self.workspace_root)
        rel_str = str(relative).replace("\\", "/")

        is_allowed_mutable = any(
            rel_str == mutable_dir or rel_str.startswith(f"{mutable_dir}/")
            for mutable_dir in self.MUTABLE_SUBDIRECTORIES
        )

        if not is_allowed_mutable:
            raise SecurityError(
                f"Write operation denied by SR-007: '{rel_str}' is outside authorized mutable boundaries {sorted(list(self.MUTABLE_SUBDIRECTORIES))}"
            )

        return resolved

    def _resolve_and_verify(
        self,
        target_path: Union[str, pathlib.Path],
        must_exist: bool,
        for_write: bool,
        allow_internal_git: bool,
    ) -> pathlib.Path:
        raw_path = pathlib.Path(target_path)

        # Guard against pathlib '/' leading-slash escape bug:
        # If target_path is absolute, ensure it starts with workspace_root
        if raw_path.is_absolute():
            candidate = raw_path
        else:
            candidate = self.workspace_root / raw_path

        # Resolve symlinks and parent hops
        try:
            if must_exist:
                resolved = candidate.resolve(strict=True)
            else:
                # If target does not exist yet (for write), resolve existing parent
                parent_resolved = candidate.parent.resolve(strict=True)
                resolved = parent_resolved / candidate.name
        except FileNotFoundError as err:
            raise PathTraversalError(f"File or directory not found: {candidate}") from err
        except (PermissionError, RuntimeError) as err:
            raise PathTraversalError(f"Path resolution failed for '{target_path}': {err}") from err

        # Verify confinement within workspace root
        if not resolved.is_relative_to(self.workspace_root):
            raise PathTraversalError(
                f"Security Violation (SR-001): Path '{target_path}' resolves to '{resolved}', which escapes authorized workspace '{self.workspace_root}'"
            )

        # Verify symlink target does not point outside workspace
        if candidate.is_symlink():
            try:
                symlink_target = candidate.readlink()
                if symlink_target.is_absolute():
                    target_resolved = symlink_target.resolve()
                else:
                    target_resolved = (candidate.parent / symlink_target).resolve()

                if not target_resolved.is_relative_to(self.workspace_root):
                    raise PathTraversalError(
                        f"Security Violation (SR-002): Symlink '{candidate}' points to external destination '{target_resolved}'"
                    )
            except OSError as err:
                raise PathTraversalError(f"Error inspecting symlink '{candidate}': {err}") from err

        # Inspect internal directory restrictions
        rel_parts = resolved.relative_to(self.workspace_root).parts
        if not allow_internal_git:
            for part in rel_parts:
                if part in self.FORBIDDEN_INTERNAL_DIRS:
                    raise PathTraversalError(
                        f"Access denied to internal metadata directory: '{part}'"
                    )

        # Inspect sensitive credential file patterns
        file_name = resolved.name
        for pattern in self.FORBIDDEN_FILE_PATTERNS:
            if pattern.match(file_name):
                raise PathTraversalError(
                    f"Access denied to protected credential file: '{file_name}'"
                )

        return resolved


# ============================================================================
# Git Safety Guard (SR-004)
# ============================================================================

class SafeGitAdapter:
    """Executes strictly read-only Git queries with timeout and injection defenses."""

    ALLOWED_READONLY_COMMANDS: Set[str] = {
        "status",
        "diff",
        "log",
        "rev-parse",
        "show",
        "merge-base",
        "branch",
        "rev-list",
        "symbolic-ref",
        "describe",
    }

    FORBIDDEN_GIT_COMMANDS: Set[str] = {
        "commit",
        "push",
        "pull",
        "checkout",
        "restore",
        "reset",
        "clean",
        "rebase",
        "merge",
        "cherry-pick",
        "stash",
        "tag",
        "config",
        "remote",
        "clone",
        "init",
    }

    def __init__(self, workspace_root: pathlib.Path):
        self.workspace_root = workspace_root.resolve(strict=True)

    def execute_git(
        self,
        args: List[str],
        timeout_seconds: int = 15,
        max_output_chars: int = 50_000,
    ) -> Tuple[int, str, str]:
        """
        Executes a Git sub-command strictly verifying that it is on the read-only allowlist.
        Returns (exit_code, scrubbed_stdout, scrubbed_stderr).
        """
        if not args:
            raise SecurityError("Git command argument list cannot be empty")

        subcommand = args[0].strip()

        if subcommand in self.FORBIDDEN_GIT_COMMANDS:
            raise SecurityError(
                f"Security Violation (SR-004): Git mutation command '{subcommand}' is strictly forbidden in MCP server."
            )

        if subcommand not in self.ALLOWED_READONLY_COMMANDS:
            raise SecurityError(
                f"Security Violation (SR-004): Git subcommand '{subcommand}' is not on authorized read-only allowlist."
            )

        # Additional flag sanitation: prevent subshell execution or config flags
        for arg in args[1:]:
            if arg.startswith("--exec-path") or arg.startswith("--upload-pack"):
                raise SecurityError(f"Forbidden Git parameter: '{arg}'")

        try:
            proc = subprocess.run(
                ["git"] + args,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                shell=False,
            )
            stdout = proc.stdout[:max_output_chars]
            stderr = proc.stderr[:max_output_chars]

            clean_stdout = SecretScrubber.redact_secrets(stdout)
            clean_stderr = SecretScrubber.redact_secrets(stderr)

            return proc.returncode, clean_stdout, clean_stderr

        except subprocess.TimeoutExpired:
            return 124, "", f"Git command timed out after {timeout_seconds}s"
        except Exception as exc:
            return 1, "", SecretScrubber.sanitize_error(exc)


# ============================================================================
# Subprocess Safety & Check Execution (SR-005, SR-006)
# ============================================================================

class ProjectCheckType(str, enum.Enum):
    ALL_TESTS = "all_tests"
    SCHEMA_VERIFICATION = "schemas"
    LIFECYCLE_VERIFICATION = "lifecycle"
    QUALITY_EVALUATION = "quality"
    MEMORY_VERIFICATION = "memory"
    ADAPTER_CONFORMANCE = "adapters"
    RECONCILER_STATUS = "reconciler"


@dataclass
class CheckExecutionResult:
    check_id: str
    command_executed: List[str]
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    status: str  # PASSED, FAILED, TIMEOUT, BLOCKED
    truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkId": self.check_id,
            "command": " ".join(self.command_executed),
            "exitCode": self.exit_code,
            "durationSeconds": self.duration_seconds,
            "status": self.status,
            "truncated": self.truncated,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class SafeSubprocessRunner:
    """Manages secure execution of predefined verification checks."""

    MAX_OUTPUT_CHARS = 50_000
    DEFAULT_TIMEOUT_SECONDS = 30
    MAX_TIMEOUT_SECONDS = 60

    CHECK_REGISTRY: Dict[ProjectCheckType, Tuple[str, ...]] = {
        ProjectCheckType.ALL_TESTS: (
            "python3",
            "validation/test_runner.py",
        ),
        ProjectCheckType.SCHEMA_VERIFICATION: (
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "validation/schema-tests",
            "-p",
            "test_*.py",
        ),
        ProjectCheckType.LIFECYCLE_VERIFICATION: (
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "validation/lifecycle-tests",
            "-p",
            "test_*.py",
        ),
        ProjectCheckType.QUALITY_EVALUATION: (
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "validation/quality-tests",
            "-p",
            "test_*.py",
        ),
        ProjectCheckType.MEMORY_VERIFICATION: (
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "validation/memory-tests",
            "-p",
            "test_*.py",
        ),
        ProjectCheckType.ADAPTER_CONFORMANCE: (
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "validation/adapter-conformance",
            "-p",
            "test_*.py",
        ),
        ProjectCheckType.RECONCILER_STATUS: (
            "python3",
            "memory/reconciliation-rules/reconciler.py",
            "--json",
        ),
    }

    def __init__(self, workspace_root: pathlib.Path):
        self.workspace_root = workspace_root.resolve(strict=True)

    def _get_clean_environment(self) -> Dict[str, str]:
        """Creates an environment copy with sensitive API keys removed."""
        env = os.environ.copy()
        sensitive_env_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "GEMINI_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "SLACK_BOT_TOKEN",
            "DATABASE_URL",
        ]
        for key in sensitive_env_keys:
            env.pop(key, None)
        return env

    def run_check(
        self,
        check_name: str,
        timeout_seconds: Optional[int] = None,
    ) -> CheckExecutionResult:
        """
        Executes a project check by verified enum identifier.
        Enforces shell=False, timeout, safe cwd, output truncation, and secret scrubbing.
        """
        try:
            check_enum = ProjectCheckType(check_name)
        except ValueError:
            valid_keys = [e.value for e in ProjectCheckType]
            raise SubprocessSecurityError(
                f"Unauthorized check identifier '{check_name}'. Valid checks: {valid_keys}"
            )

        cmd_args = list(self.CHECK_REGISTRY[check_enum])
        timeout = min(
            timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS,
            self.MAX_TIMEOUT_SECONDS,
        )

        start_time = time.time()
        truncated = False

        try:
            proc = subprocess.run(
                cmd_args,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=False,  # MANDATORY: Prevent shell injection
                env=self._get_clean_environment(),
            )
            duration = round(time.time() - start_time, 3)

            raw_stdout = proc.stdout
            raw_stderr = proc.stderr

            if len(raw_stdout) > self.MAX_OUTPUT_CHARS:
                raw_stdout = raw_stdout[: self.MAX_OUTPUT_CHARS] + "\n... [OUTPUT TRUNCATED BY BUFFER LIMIT]"
                truncated = True

            if len(raw_stderr) > self.MAX_OUTPUT_CHARS:
                raw_stderr = raw_stderr[: self.MAX_OUTPUT_CHARS] + "\n... [STDERR TRUNCATED BY BUFFER LIMIT]"
                truncated = True

            clean_stdout = SecretScrubber.redact_secrets(raw_stdout)
            clean_stderr = SecretScrubber.redact_secrets(raw_stderr)
            status = "PASSED" if proc.returncode == 0 else "FAILED"

            return CheckExecutionResult(
                check_id=check_enum.value,
                command_executed=cmd_args,
                exit_code=proc.returncode,
                duration_seconds=duration,
                stdout=clean_stdout,
                stderr=clean_stderr,
                status=status,
                truncated=truncated,
            )

        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 3)
            return CheckExecutionResult(
                check_id=check_enum.value,
                command_executed=cmd_args,
                exit_code=124,
                duration_seconds=duration,
                stdout="",
                stderr=f"Check timed out after {timeout} seconds",
                status="TIMEOUT",
                truncated=False,
            )
        except Exception as exc:
            duration = round(time.time() - start_time, 3)
            return CheckExecutionResult(
                check_id=check_enum.value,
                command_executed=cmd_args,
                exit_code=1,
                duration_seconds=duration,
                stdout="",
                stderr=SecretScrubber.sanitize_error(exc),
                status="FAILED",
                truncated=False,
            )


# ============================================================================
# Bounded Filesystem Adapter (SR-006, SR-007)
# ============================================================================

class SafeFileSystemAdapter:
    """Provides bounded file read, directory listing, and atomic write operations."""

    MAX_FILE_READ_BYTES = 1_048_576  # 1 MB
    MAX_DIR_ENTRIES = 500
    MAX_RECURSION_DEPTH = 5

    def __init__(self, workspace_root: pathlib.Path):
        self.workspace_root = workspace_root.resolve(strict=True)
        self.validator = PathSecurityValidator(self.workspace_root)

    def read_text_file(
        self,
        file_path: Union[str, pathlib.Path],
        offset_chars: int = 0,
        limit_chars: int = 50_000,
    ) -> Dict[str, Any]:
        """
        Safely reads a text file within size bounds, checks for binary content,
        and redacts any detected secrets.
        """
        resolved = self.validator.validate_read_path(file_path)

        file_size = resolved.stat().st_size
        if file_size > self.MAX_FILE_READ_BYTES:
            raise FileBoundaryError(
                f"File '{resolved.name}' size ({file_size} bytes) exceeds maximum limit of {self.MAX_FILE_READ_BYTES} bytes. Use bounded range reads."
            )

        with open(resolved, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                raise FileBoundaryError(f"Cannot read binary file '{resolved.name}' as text.")

        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        total_length = len(content)
        slice_content = content[offset_chars : offset_chars + limit_chars]
        is_truncated = (offset_chars + limit_chars) < total_length

        clean_text = SecretScrubber.redact_secrets(slice_content)

        return {
            "path": str(resolved.relative_to(self.workspace_root)),
            "sizeBytes": file_size,
            "totalCharacters": total_length,
            "offset": offset_chars,
            "returnedCharacters": len(clean_text),
            "isTruncated": is_truncated,
            "content": clean_text,
        }

    def list_directory(
        self,
        dir_path: Union[str, pathlib.Path] = ".",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Lists directory contents safely, bounded by MAX_DIR_ENTRIES and MAX_RECURSION_DEPTH.
        """
        resolved = self.validator.validate_read_path(dir_path)

        if not resolved.is_dir():
            raise FileBoundaryError(f"Path '{dir_path}' is not a directory")

        entries: List[Dict[str, Any]] = []

        if not recursive:
            for item in sorted(resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
                if len(entries) >= self.MAX_DIR_ENTRIES:
                    break
                if item.name in self.validator.FORBIDDEN_INTERNAL_DIRS:
                    continue
                entries.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.workspace_root)),
                    "isDirectory": item.is_dir(),
                    "sizeBytes": item.stat().st_size if item.is_file() else None,
                })
        else:
            depth_base = len(resolved.parts)
            for root, dirs, files in os.walk(resolved):
                root_path = pathlib.Path(root)
                current_depth = len(root_path.parts) - depth_base

                if current_depth > self.MAX_RECURSION_DEPTH:
                    dirs.clear()
                    continue

                dirs[:] = [d for d in dirs if d not in self.validator.FORBIDDEN_INTERNAL_DIRS]

                for f in sorted(files):
                    if len(entries) >= self.MAX_DIR_ENTRIES:
                        return entries
                    file_p = root_path / f
                    entries.append({
                        "name": f,
                        "path": str(file_p.relative_to(self.workspace_root)),
                        "isDirectory": False,
                        "sizeBytes": file_p.stat().st_size,
                    })

        return entries

    def atomic_write_json(
        self,
        file_path: Union[str, pathlib.Path],
        data: Dict[str, Any],
        schema_validator_func: Optional[Any] = None,
    ) -> pathlib.Path:
        """
        Safely writes JSON data using atomic replacement (tempfile + os.replace).
        Scans content for secret leakage before persistence (SR-003, SR-007).
        """
        resolved = self.validator.validate_write_path(file_path)

        if schema_validator_func:
            schema_validator_func(data)

        serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

        leaks = SecretScrubber.scan_for_secrets(serialized)
        if leaks:
            rule_names = [leak[0] for leak in leaks]
            raise SecretLeakageAlert(
                f"Persistence blocked by SR-003: payload contains potential secret patterns: {rule_names}"
            )

        resolved.parent.mkdir(parents=True, exist_ok=True)
        dir_path = resolved.parent

        temp_fd, temp_path = tempfile.mkstemp(
            dir=str(dir_path), prefix=".mcp_atomic_", suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(serialized)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, str(resolved))
            return resolved
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
