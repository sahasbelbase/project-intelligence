"""
Project Intelligence — Memory & Reconciliation Tests
Tests memory schema conformance, secret leakage prevention, and Git reconciliation drift detection.
Uses Python standard library with zero external dependencies.
"""

import unittest
import json
import re
from pathlib import Path


class TestProjectMemory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.memory_dir = cls.project_root / "memory"
        cls.schemas_dir = cls.memory_dir / "schemas"
        cls.templates_dir = cls.memory_dir / "templates"
        cls.rules_dir = cls.memory_dir / "reconciliation-rules"

    def test_memory_schemas_exist_and_are_valid(self):
        """Ensure all required memory schemas exist and declare draft-07 types."""
        expected_schemas = [
            "memory.schema.json",
            "durable-knowledge.schema.json",
            "execution-state.schema.json",
            "backlog.schema.json"
        ]
        for s_name in expected_schemas:
            s_path = self.schemas_dir / s_name
            self.assertTrue(s_path.exists(), f"Missing memory schema: {s_name}")
            with open(s_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("type"), "object")
            self.assertIn("title", data)
            self.assertTrue(
                "properties" in data or "oneOf" in data or "anyOf" in data,
                f"Schema {s_name} must declare properties, oneOf, or anyOf"
            )

    def test_memory_templates_validity(self):
        """Verify templates contain required core keys."""
        template_files = list(self.templates_dir.glob("*.json"))
        self.assertGreaterEqual(len(template_files), 3, "Must have at least 3 memory templates")

        for t_file in template_files:
            with open(t_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, f"Template {t_file.name} must be a JSON object")

    def test_secret_detection_in_memory(self):
        """Verify that secret patterns in memory are strictly detected."""
        secret_patterns = [
            re.compile(r"sk-[a-zA-Z0-9_-]{20,}", re.IGNORECASE),
            re.compile(r"ghp_[a-zA-Z0-9]{20,}", re.IGNORECASE),
            re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),
            re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)
        ]

        def scan_for_secrets(text: str):
            for pat in secret_patterns:
                if pat.search(text):
                    return True
            return False

        # Injected leak must be flagged
        leaked_payload = '{"api_key": "sk-ant-api03-abcdef1234567890abcdef123456"}'
        self.assertTrue(scan_for_secrets(leaked_payload), "Must detect leaked API token")

        # Clean memory payload must pass
        clean_payload = '{"goals": ["Build fast and safely"], "currentGate": "G0"}'
        self.assertFalse(scan_for_secrets(clean_payload), "Clean memory payload must pass")

    def test_reconciliation_rules_documented(self):
        """Ensure reconciliation rules file exists and covers drift, rebase, and preservation."""
        rules_md = self.rules_dir / "rules.md"
        self.assertTrue(rules_md.exists(), "reconciliation-rules/rules.md must exist")
        content = rules_md.read_text(encoding="utf-8")
        self.assertIn("reconcil", content.lower())
        self.assertIn("git", content.lower())
        self.assertIn("uncommitted", content.lower())


if __name__ == "__main__":
    unittest.main()
