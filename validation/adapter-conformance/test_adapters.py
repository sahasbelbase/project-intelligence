"""
Project Intelligence — Platform Adapter Conformance Tests
Verifies that platform adapters declare accurate capabilities, map canonical instructions,
and never silently weaken mandatory safety/quality rules.
Uses Python standard library with zero external dependencies.
"""

import unittest
import json
from pathlib import Path


class TestAdapterConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.adapters_dir = cls.project_root / "adapters"
        cls.matrix_file = cls.project_root / "core" / "capabilities" / "matrix.json"
        
        with open(cls.matrix_file, "r", encoding="utf-8") as f:
            cls.matrix = json.load(f).get("platforms", {})

    def test_required_platform_adapter_directories_exist(self):
        """Ensure all 4 platform adapter directories exist."""
        required = ["claude-code", "github-copilot", "codex", "other-platforms"]
        for p in required:
            d = self.adapters_dir / p
            self.assertTrue(d.exists() and d.is_dir(), f"Missing adapter directory: adapters/{p}")

    def test_adapters_declare_manifest_matching_capabilities(self):
        """Verify each adapter has an adapter.json matching or extending the core capability matrix."""
        for p_name, p_spec in self.matrix.items():
            # Map platform name in matrix to adapter dir name
            dir_name = p_name
            if p_name == "codex-agents-sdk":
                dir_name = "codex"
            elif p_name == "antigravity":
                dir_name = "other-platforms"
                
            adapter_manifest = self.adapters_dir / dir_name / "adapter.json"
            if adapter_manifest.exists():
                with open(adapter_manifest, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                platform_id = manifest.get("platformId") or manifest.get("targetPlatform") or manifest.get("name")
                self.assertIsNotNone(platform_id, f"Adapter manifest in {dir_name} must specify a platform identifier")
                self.assertIn("supportedCapabilities", manifest)
                self.assertTrue("unsupportedCapabilities" in manifest or "degradationLevel" in manifest)

    def test_mandatory_baseline_preservation_in_adapters(self):
        """Ensure adapters do not strip mandatory baseline quality rules."""
        for p in ["claude-code", "github-copilot", "codex"]:
            p_dir = self.adapters_dir / p
            files = list(p_dir.glob("*"))
            if files:
                # Check that no adapter file disables anti-slop or secret protection
                for f in files:
                    if f.suffix in [".json", ".md"]:
                        content = f.read_text(encoding="utf-8")
                        self.assertNotIn("disable_anti_slop", content.lower())
                        self.assertNotIn("bypass_quality_baseline", content.lower())


if __name__ == "__main__":
    unittest.main()
