"""
Project Intelligence — Regression Tests: Quality Evaluator & Memory Reconciler
Tests expanded emoji coverage, LLM truncation slop detection,
markdown callout handling, and git reconciler engine behavior.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.quality.evaluator import QualityEvaluator
import importlib.util

reconciler_path = PROJECT_ROOT / "memory" / "reconciliation-rules" / "reconciler.py"
spec = importlib.util.spec_from_file_location("reconciler", reconciler_path)
reconciler_mod = importlib.util.module_from_spec(spec)
sys.modules["reconciler"] = reconciler_mod
spec.loader.exec_module(reconciler_mod)

ZERO_COMMIT_SHA = reconciler_mod.ZERO_COMMIT_SHA
ReconciliationStatus = reconciler_mod.ReconciliationStatus
StateReconciler = reconciler_mod.StateReconciler
inspect_git_repository = reconciler_mod.inspect_git_repository
scan_text_for_secrets = reconciler_mod.scan_text_for_secrets


class TestQualityPrecisionRegressions(unittest.TestCase):
    def setUp(self):
        self.evaluator = QualityEvaluator()

    def test_bmp_emojis_detected_in_code(self):
        """Ensure BMP emojis (Dingbats, Miscellaneous Symbols) are caught in code files."""
        samples = [
            'status = "Task completed! ✅"',
            'log.warning("⚠️ High latency detected")',
            'print("✨ Magical completion ✨")',
            'status_marker = "❌ Failed step"'
        ]
        for s in samples:
            violations = self.evaluator.evaluate_anti_slop(s, is_markdown=False)
            self.assertGreater(
                len(violations), 0,
                f"Must detect BMP emoji in technical code: {s}"
            )

    def test_llm_truncation_slop_detected(self):
        """Ensure LLM code truncation placeholders are caught."""
        truncation_samples = [
            "def calculate(x):\n    # ... rest of code unchanged ...\n    return x * 2",
            "class Engine:\n    /* add your implementation here */\n    pass",
            "function process() {\n    // add your implementation here\n}"
        ]
        for s in truncation_samples:
            violations = self.evaluator.evaluate_anti_slop(s, is_markdown=False)
            self.assertGreater(
                len(violations), 0,
                f"Must flag LLM truncation slop in: {s}"
            )

    def test_markdown_informational_callouts_not_flagged(self):
        """Ensure standard markdown documentation callouts do not trigger false positive violations."""
        markdown_sample = """# Usage Guide

> ⚠️ Ensure environment variables are loaded before execution.
> [!NOTE] This framework requires Python 3.10 or higher.
"""
        violations = self.evaluator.evaluate_anti_slop(markdown_sample, is_markdown=True)
        self.assertEqual(len(violations), 0, f"Markdown callouts should not trigger violations: {violations}")

    def test_corrupted_memory_fixture_detects_anti_slop(self):
        """Ensure defects injected in corrupted-memory fixture are recognized."""
        fixture_path = PROJECT_ROOT / "validation" / "fixtures" / "corrupted-memory" / "fixture.json"
        self.assertTrue(fixture_path.exists())
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for defect in data.get("injectedDefects", []):
            if defect.get("type") == "ANTI_SLOP_VIOLATION":
                violations = self.evaluator.evaluate_anti_slop(defect.get("sample", ""))
                self.assertGreater(len(violations), 0)


class TestReconcilerGitRegressions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        # Initialize an isolated temporary git repo
        subprocess.run(["git", "init"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "test@project-intelligence.dev"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=self.repo, check=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_unborn_branch_status(self):
        """Ensure unborn git branch with 0 commits returns UNINITIALIZED and ZERO_COMMIT_SHA."""
        git_info = inspect_git_repository(self.repo)
        self.assertTrue(git_info["is_git_repo"])
        self.assertFalse(git_info["has_commits"])
        self.assertEqual(git_info["current_head"], ZERO_COMMIT_SHA)

    def test_reconciler_initializes_cleanly_on_unborn_branch(self):
        """Ensure reconciler can initialize state from template on unborn branch without crashing."""
        state_file = self.repo / "memory" / "execution-state.json"
        template_file = PROJECT_ROOT / "memory" / "templates" / "execution-state.template.json"

        reconciler = StateReconciler(
            repo_root=self.repo,
            state_file=state_file,
            template_file=template_file
        )
        report = reconciler.reconcile(update_mode=True, repair_mode=True)
        self.assertTrue(state_file.exists())
        self.assertEqual(report.reconciliation_status, ReconciliationStatus.UNINITIALIZED)

        # Ensure state.json mirror was also created
        mirror_file = self.repo / "memory" / "state.json"
        self.assertTrue(mirror_file.exists())

    def test_secret_scanner_detects_untracked_files(self):
        """Ensure untracked files containing secrets are detected."""
        secret_file = self.repo / ".env"
        secret_file.write_text("AIzaSyB_1234567890abcdef1234567890abcdef")

        git_info = inspect_git_repository(self.repo)
        findings = scan_text_for_secrets(git_info["diff_text"], source_name="working_tree_diff")
        self.assertGreater(len(findings), 0, "Untracked .env file with Google API key must be detected")


if __name__ == "__main__":
    unittest.main()
