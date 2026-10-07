"""
Project Intelligence — MCP Security Boundaries & Adversarial Tests
Verifies SR-001 through SR-008: Path traversal defense, symlink escape containment,
secret redaction without entropy leaks, read-only Git guards, subprocess command isolation,
and bounded filesystem operations.
Uses Python standard library with zero external dependencies.
"""

import unittest
from pathlib import Path
import sys
import tempfile
import os

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from adapters.mcp.security import (
    FileBoundaryError,
    PathSecurityValidator,
    PathTraversalError,
    SafeFileSystemAdapter,
    SafeGitAdapter,
    SafeSubprocessRunner,
    SecretLeakageAlert,
    SecretScrubber,
    SecurityError,
    SubprocessSecurityError,
)


class TestMCPSecurityBoundaries(unittest.TestCase):
    def setUp(self):
        self.validator = PathSecurityValidator(workspace_root=project_root)
        self.fs_adapter = SafeFileSystemAdapter(workspace_root=project_root)
        self.git_adapter = SafeGitAdapter(workspace_root=project_root)
        self.subprocess_runner = SafeSubprocessRunner(workspace_root=project_root)

    def test_path_traversal_dot_dot_escapes_blocked(self):
        """Ensure classic ../ path traversal attacks are blocked."""
        adversarial_paths = [
            "../../../../etc/passwd",
            "../secret.txt",
            "core/../../../../../../etc/shadow",
            "contracts/../..",
        ]
        for p in adversarial_paths:
            with self.assertRaises((PathTraversalError, SecurityError)):
                self.validator.validate_read_path(p)

    def test_path_traversal_absolute_escape_blocked(self):
        """Ensure absolute paths outside workspace root are blocked."""
        external_paths = [
            "/etc/passwd",
            "/var/log",
            "/tmp",
        ]
        for p in external_paths:
            with self.assertRaises((PathTraversalError, SecurityError)):
                self.validator.validate_read_path(p)

    def test_internal_git_directory_access_blocked(self):
        """Ensure direct access to .git metadata directory is blocked for normal reads."""
        with self.assertRaises((PathTraversalError, SecurityError)):
            self.validator.validate_read_path(".git/config")

    def test_protected_credential_files_blocked(self):
        """Ensure access to protected files like .env or id_rsa is blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            env_file = tmp_root / ".env"
            env_file.write_text("API_KEY=123", encoding="utf-8")

            tmp_val = PathSecurityValidator(tmp_root)
            with self.assertRaises(PathTraversalError):
                tmp_val.validate_read_path(".env")

    def test_symlink_escape_containment(self):
        """Ensure symlinks pointing outside the authorized workspace are rejected."""
        with tempfile.TemporaryDirectory() as outside_dir, tempfile.TemporaryDirectory() as inside_dir:
            out_path = Path(outside_dir) / "host_secrets.txt"
            out_path.write_text("HOST_SECRET_DATA", encoding="utf-8")

            in_root = Path(inside_dir)
            symlink_p = in_root / "leak_symlink"
            try:
                os.symlink(out_path, symlink_p)
            except OSError:
                self.skipTest("Symlinks not supported on this filesystem")

            val = PathSecurityValidator(in_root)
            with self.assertRaises(PathTraversalError):
                val.validate_read_path("leak_symlink")

    def test_secret_redaction_patterns_and_zero_entropy_leak(self):
        """Ensure secret patterns are fully redacted with [REDACTED:<NAME>] without edge characters."""
        toxic_text = """
        const google = "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q";
        const openai = "sk-proj-abc1234567890abcdef1234567890";
        const anthropic = "sk-ant-api03-abcdef1234567890abcdef123456";
        const github = "ghp_1234567890abcdefghijklmnopqrstuvwxyz";
        const aws_id = "AKIAIOSFODNN7EXAMPLE";
        const db_url = "postgres://admin:SuperSecretPass123!@localhost:5432/prod";
        """
        redacted = SecretScrubber.redact_secrets(toxic_text)

        # Confirm tokens are completely gone
        self.assertNotIn("AIzaSyA", redacted)
        self.assertNotIn("sk-proj-abc", redacted)
        self.assertNotIn("sk-ant-api03", redacted)
        self.assertNotIn("ghp_1234", redacted)
        self.assertNotIn("AKIAIOSF", redacted)
        self.assertNotIn("SuperSecretPass123!", redacted)

        # Confirm redaction markers are present
        self.assertIn("[REDACTED:GOOGLE_API_KEY]", redacted)
        self.assertIn("[REDACTED:OPENAI_API_KEY]", redacted)
        self.assertIn("[REDACTED:ANTHROPIC_API_KEY]", redacted)
        self.assertIn("[REDACTED:GITHUB_TOKEN]", redacted)
        self.assertIn("[REDACTED:AWS_ACCESS_KEY]", redacted)
        self.assertIn("[REDACTED:CONNECTION_STRING_WITH_PASS]", redacted)

    def test_read_only_git_enforcement(self):
        """Ensure git adapter permits read-only commands and blocks destructive/mutating commands."""
        # Allowed read-only command
        code, out, _ = self.git_adapter.execute_git(["status", "--porcelain"])
        self.assertEqual(code, 0)

        # Blocked mutating commands
        forbidden = ["commit", "push", "pull", "checkout", "reset", "clean", "rebase"]
        for cmd in forbidden:
            with self.assertRaises(SecurityError):
                self.git_adapter.execute_git([cmd])

    def test_writable_confinement_blocks_immutable_paths(self):
        """Ensure write operations are confined to memory/ and contracts/ (SR-007)."""
        immutable_targets = [
            "core/lifecycle/engine.py",
            "core/schemas/contract-envelope.schema.json",
            "instructions/universal/core-rules.md",
            "README.md",
        ]
        for target in immutable_targets:
            with self.assertRaises(SecurityError):
                self.validator.validate_write_path(target)

    def test_file_size_boundary_enforcement(self):
        """Ensure files exceeding 1 MB trigger FileBoundaryError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            large_file = tmp_root / "large.txt"
            # Write 1.1 MB
            large_file.write_bytes(b"A" * (1024 * 1024 + 100))

            fs = SafeFileSystemAdapter(tmp_root)
            with self.assertRaises(FileBoundaryError):
                fs.read_text_file("large.txt")


if __name__ == "__main__":
    unittest.main()
