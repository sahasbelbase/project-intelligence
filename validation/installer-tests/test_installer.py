"""
Project Intelligence — Portable Installer & Platform Adapter Tests
Tests the zero-dependency portable installer across clean installations,
preexisting user configuration preservation, doctor diagnostics, idempotency,
and clean uninstallation.
Conformance: Python standard library unittest only.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestPortableInstaller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.bin_cli = cls.project_root / "bin" / "cli.js"
        cls.node_bin = "node"

        # Verify node is available
        res = subprocess.run([cls.node_bin, "--version"], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Node.js runtime not found or returned error: {res.stderr}")

    def _run_cli(self, args, cwd=None):
        cmd = [self.node_bin, str(self.bin_cli)] + args
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else str(self.project_root),
            capture_output=True,
            text=True,
        )

    def test_init_clean_temp_antigravity(self):
        """Verify init on a clean temp directory with --client antigravity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "antigravity", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}\n{res.stdout}")

            # Antigravity artifacts
            gemini_md = tmp_path / "GEMINI.md"
            self.assertTrue(gemini_md.exists(), "GEMINI.md was not created")
            gemini_content = gemini_md.read_text(encoding="utf-8")
            self.assertIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", gemini_content)
            self.assertIn("<!-- END PROJECT-INTELLIGENCE -->", gemini_content)
            self.assertIn("Non-Negotiable Operational Rules", gemini_content)

            agents_rules = tmp_path / ".agents" / "rules" / "AGENTS.md"
            self.assertTrue(agents_rules.exists(), ".agents/rules/AGENTS.md was not created")

            orchestrator_skill = tmp_path / ".agents" / "skills" / "orchestrator" / "SKILL.md"
            self.assertTrue(orchestrator_skill.exists(), "Antigravity orchestrator skill was not created")
            self.assertIn("name: orchestrator", orchestrator_skill.read_text(encoding="utf-8"))

            mcp_config = tmp_path / ".agents" / "mcp_config.json"
            self.assertTrue(mcp_config.exists(), ".agents/mcp_config.json was not created")
            mcp_data = json.loads(mcp_config.read_text(encoding="utf-8"))
            self.assertIn("project-intelligence", mcp_data.get("mcpServers", {}))

            # Claude artifacts must NOT exist
            claude_md = tmp_path / "CLAUDE.md"
            self.assertFalse(claude_md.exists(), "CLAUDE.md should not exist for antigravity-only install")

            manifest = tmp_path / ".project-intelligence" / "install-manifest.json"
            self.assertTrue(manifest.exists(), "install-manifest.json was not created")

    def test_init_installs_vendored_skills_with_licenses(self):
        """Vendored third-party skills are installed with every file, including LICENSE, and removed on uninstall."""
        registry = json.loads((self.bin_cli.parents[1] / "vendor" / "skills" / "registry.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}\n{res.stdout}")
            for entry in registry["vendored"]:
                for base in (".claude/skills", ".agents/skills"):
                    for f in entry["files"]:
                        self.assertTrue((tmp_path / base / entry["id"] / f).exists(), f"{base}/{entry['id']}/{f} missing")
            un_res = self._run_cli(["uninstall", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(un_res.returncode, 0, f"Uninstall failed: {un_res.stderr}")
            for entry in registry["vendored"]:
                self.assertFalse((tmp_path / ".claude" / "skills" / entry["id"] / "LICENSE").exists())

    def test_installed_orchestrator_calls_the_dispatcher(self):
        """The installed /orchestrator command and skill point at this package's CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}")
            cli = json.dumps(str(self.bin_cli))
            command = (tmp_path / ".claude" / "commands" / "orchestrator.md").read_text(encoding="utf-8")
            self.assertIn("$ARGUMENTS", command)
            self.assertIn("council sheet", command)
            self.assertTrue((tmp_path / ".claude" / "agents" / "council-member.md").exists())
            self.assertIn(f"node {cli} ask", command)
            for skill in (tmp_path / ".claude" / "skills" / "orchestrator" / "SKILL.md", tmp_path / ".agents" / "skills" / "orchestrator" / "SKILL.md"):
                text = skill.read_text(encoding="utf-8")
                self.assertIn(f"node {cli} council prompt", text)
                self.assertIn("plan_task", text)

    def test_init_clean_temp_claude(self):
        """Verify init on a clean temp directory with --client claude."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "claude", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}\n{res.stdout}")

            # Claude Code artifacts
            claude_md = tmp_path / "CLAUDE.md"
            self.assertTrue(claude_md.exists(), "CLAUDE.md was not created")
            claude_content = claude_md.read_text(encoding="utf-8")
            self.assertIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", claude_content)
            self.assertIn("<!-- END PROJECT-INTELLIGENCE -->", claude_content)

            command_file = tmp_path / ".claude" / "commands" / "orchestrator.md"
            self.assertTrue(command_file.exists(), ".claude/commands/orchestrator.md was not created")

            skill_file = tmp_path / ".claude" / "skills" / "orchestrator" / "SKILL.md"
            self.assertTrue(skill_file.exists(), ".claude/skills/orchestrator/SKILL.md was not created")

            settings_file = tmp_path / ".claude" / "settings.json"
            self.assertTrue(settings_file.exists(), ".claude/settings.json was not created")
            settings = json.loads(settings_file.read_text(encoding="utf-8"))
            self.assertIn("hooks", settings)
            self.assertIn("SessionStart", settings["hooks"])
            self.assertIn("PreToolUse", settings["hooks"])
            self.assertIn("Stop", settings["hooks"])

            session_hook = tmp_path / ".claude" / "hooks" / "session-start.sh"
            self.assertTrue(session_hook.exists(), "session-start.sh hook was not created")
            self.assertTrue(os.access(session_hook, os.X_OK), "session-start.sh is not executable")

            mcp_file = tmp_path / ".claude" / "mcp.json"
            self.assertTrue(mcp_file.exists(), ".claude/mcp.json was not created")
            mcp_data = json.loads(mcp_file.read_text(encoding="utf-8"))
            self.assertIn("project-intelligence", mcp_data.get("mcpServers", {}))

            # Antigravity artifacts must NOT exist
            gemini_md = tmp_path / "GEMINI.md"
            self.assertFalse(gemini_md.exists(), "GEMINI.md should not exist for claude-only install")

    def test_init_clean_temp_all(self):
        """Verify init on a clean temp directory with --client all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}\n{res.stdout}")

            self.assertTrue((tmp_path / "GEMINI.md").exists())
            self.assertTrue((tmp_path / "CLAUDE.md").exists())
            self.assertTrue((tmp_path / ".claude" / "commands" / "orchestrator.md").exists())
            self.assertTrue((tmp_path / ".agents" / "skills" / "orchestrator" / "SKILL.md").exists())
            self.assertTrue((tmp_path / ".claude" / "mcp.json").exists())
            self.assertTrue((tmp_path / ".agents" / "mcp_config.json").exists())

    def test_init_preserves_preexisting_files(self):
        """Verify init on project with preexisting CLAUDE.md and GEMINI.md non-destructively preserves user content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            user_claude_original = "# User Original Claude Instructions\n\nAlways use TypeScript strict mode.\nDo not edit this block.\n"
            user_gemini_original = "# User Original Gemini Directives\n\nFollow hexagonal architecture principles.\n"

            (tmp_path / "CLAUDE.md").write_text(user_claude_original, encoding="utf-8")
            (tmp_path / "GEMINI.md").write_text(user_gemini_original, encoding="utf-8")

            res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0, f"Init failed: {res.stderr}\n{res.stdout}")

            claude_content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertTrue(
                claude_content.startswith("# User Original Claude Instructions"),
                "User original header in CLAUDE.md was overwritten",
            )
            self.assertIn("Always use TypeScript strict mode.", claude_content)
            self.assertIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", claude_content)
            self.assertIn("<!-- END PROJECT-INTELLIGENCE -->", claude_content)

            gemini_content = (tmp_path / "GEMINI.md").read_text(encoding="utf-8")
            self.assertTrue(
                gemini_content.startswith("# User Original Gemini Directives"),
                "User original header in GEMINI.md was overwritten",
            )
            self.assertIn("Follow hexagonal architecture principles.", gemini_content)
            self.assertIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", gemini_content)
            self.assertIn("<!-- END PROJECT-INTELLIGENCE -->", gemini_content)

    def test_doctor_diagnostic_reporting(self):
        """Verify doctor subcommand inspects environment and reports health status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Run doctor on uninitialized directory
            res = self._run_cli(["doctor", "--dir", str(tmp_path)])
            self.assertEqual(res.returncode, 0, f"Doctor failed: {res.stderr}\n{res.stdout}")
            self.assertIn("Node.js Runtime", res.stdout)
            self.assertIn("Python Runtime", res.stdout)
            self.assertIn("Git Repository", res.stdout)
            self.assertIn("Client Configuration Status", res.stdout)

            # Initialize directory and run doctor again
            self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            res_after = self._run_cli(["doctor", "--dir", str(tmp_path)])
            self.assertEqual(res_after.returncode, 0)
            self.assertIn("Install manifest valid", res_after.stdout)
            self.assertIn("DOCTOR STATUS: HEALTHY / PASS", res_after.stdout)

    def test_uninstall_cleanly_removes_files_and_reverts_blocks(self):
        """Verify uninstall cleanly removes created files and reverts injected blocks to original content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            user_claude = "# Custom Claude Config\nUse 2-space indentation.\n"
            user_gemini = "# Custom Gemini Config\nKeep methods short.\n"
            (tmp_path / "CLAUDE.md").write_text(user_claude, encoding="utf-8")
            (tmp_path / "GEMINI.md").write_text(user_gemini, encoding="utf-8")

            # Also create preexisting settings.json
            claude_dir = tmp_path / ".claude"
            claude_dir.mkdir(parents=True, exist_ok=True)
            preexisting_settings = {"userPreference": "dark_mode"}
            (claude_dir / "settings.json").write_text(json.dumps(preexisting_settings), encoding="utf-8")

            # Install
            init_res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(init_res.returncode, 0)

            # Uninstall
            un_res = self._run_cli(["uninstall", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(un_res.returncode, 0, f"Uninstall failed: {un_res.stderr}\n{un_res.stdout}")

            # Verify created files deleted
            self.assertFalse((tmp_path / ".claude" / "commands" / "orchestrator.md").exists())
            self.assertFalse((tmp_path / ".claude" / "skills").exists())
            self.assertFalse((tmp_path / ".agents" / "skills").exists())
            self.assertFalse((tmp_path / ".project-intelligence").exists())

            # Verify preexisting files reverted to EXACT original content
            reverted_claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertEqual(reverted_claude, user_claude)
            self.assertNotIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", reverted_claude)

            reverted_gemini = (tmp_path / "GEMINI.md").read_text(encoding="utf-8")
            self.assertEqual(reverted_gemini, user_gemini)
            self.assertNotIn("<!-- BEGIN PROJECT-INTELLIGENCE -->", reverted_gemini)

            # Verify settings preserved user keys and dropped project-intelligence hooks
            reverted_settings = json.loads((tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(reverted_settings.get("userPreference"), "dark_mode")
            self.assertNotIn("hooks", reverted_settings)

    def test_repeated_init_idempotency(self):
        """Verify repeated init does not duplicate blocks or corrupt configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            user_claude = "# Base Claude\n"
            (tmp_path / "CLAUDE.md").write_text(user_claude, encoding="utf-8")

            # Run init twice
            res1 = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res1.returncode, 0)
            res2 = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res2.returncode, 0)

            content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
            # Must contain exactly ONE begin marker
            self.assertEqual(
                content.count("<!-- BEGIN PROJECT-INTELLIGENCE -->"),
                1,
                "Marker block was duplicated across repeated init calls",
            )
            self.assertEqual(
                content.count("<!-- END PROJECT-INTELLIGENCE -->"),
                1,
                "End marker was duplicated across repeated init calls",
            )

    def test_init_dry_run_leaves_filesystem_untouched(self):
        """Verify --dry-run produces preview logs without writing any files to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "all", "--dir", str(tmp_path), "--dry-run"])
            self.assertEqual(res.returncode, 0)
            self.assertIn("DRY RUN", res.stdout)
            # The directory should remain completely empty
            self.assertEqual(len(os.listdir(tmpdir)), 0, "Dry run created files on disk")

    def test_init_mcp_disabled(self):
        """Verify --mcp false does not create mcp configuration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            res = self._run_cli(["init", "--client", "all", "--mcp", "false", "--dir", str(tmp_path), "--yes"])
            self.assertEqual(res.returncode, 0)
            self.assertFalse((tmp_path / ".claude" / "mcp.json").exists())
            self.assertFalse((tmp_path / ".agents" / "mcp_config.json").exists())


if __name__ == "__main__":
    unittest.main()
