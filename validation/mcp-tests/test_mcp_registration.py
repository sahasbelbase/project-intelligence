"""
Project Intelligence — MCP Tools Registration & Schema Tests
Verifies that all 10 canonical tools are registered with valid Draft-07 schemas,
accurate parameter definitions, descriptions, and read-only/mutation classifications.
Uses Python standard library with zero external dependencies.
"""

import unittest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from adapters.mcp.server import MCPServer


class TestMCPRegistration(unittest.TestCase):
    def setUp(self):
        self.server = MCPServer(workspace_root=project_root)

    def test_all_ten_tools_registered(self):
        """Ensure exactly 10 canonical tools are registered."""
        expected_tools = [
            "project_status",
            "inspect_project",
            "get_next_action",
            "validate_contract",
            "evaluate_quality",
            "get_project_memory",
            "create_work_plan",
            "advance_lifecycle_gate",
            "reconcile_project_memory",
            "run_project_checks",
        ]
        registered = list(self.server.tools_registry.keys())
        self.assertEqual(len(registered), 10, f"Expected 10 tools, got: {registered}")
        for t in expected_tools:
            self.assertIn(t, self.server.tools_registry, f"Missing tool: '{t}'")

    def test_tool_descriptions_and_input_schemas(self):
        """Verify each tool has a meaningful description and valid JSON Schema."""
        for name, info in self.server.tools_registry.items():
            self.assertTrue(len(info["description"].strip()) > 10, f"Tool '{name}' description too short")
            schema = info["inputSchema"]
            self.assertEqual(schema.get("type"), "object", f"Tool '{name}' schema type must be 'object'")
            self.assertIn("properties", schema, f"Tool '{name}' schema missing 'properties'")
            self.assertFalse(schema.get("additionalProperties", True), f"Tool '{name}' must reject additionalProperties")

    def test_read_only_versus_mutation_classification(self):
        """Verify exact classification of read-only vs proposed-action tools."""
        expected_readonly = {
            "project_status": True,
            "inspect_project": True,
            "get_next_action": True,
            "validate_contract": True,
            "evaluate_quality": True,
            "get_project_memory": True,
            "create_work_plan": False,
            "advance_lifecycle_gate": False,
            "reconcile_project_memory": False,
            "run_project_checks": False,
        }
        for name, is_ro in expected_readonly.items():
            self.assertEqual(
                self.server.tools_registry[name]["isReadOnly"],
                is_ro,
                f"Tool '{name}' isReadOnly mismatch",
            )

    def test_required_fields_enforcement(self):
        """Verify required fields in tool schemas."""
        work_plan_schema = self.server.tools_registry["create_work_plan"]["inputSchema"]
        for req in ["workstream_id", "title", "assigned_agent_role", "phases", "tasks", "file_ownership"]:
            self.assertIn(req, work_plan_schema.get("required", []))

        advance_gate_schema = self.server.tools_registry["advance_lifecycle_gate"]["inputSchema"]
        for req in ["target_gate", "condition"]:
            self.assertIn(req, advance_gate_schema.get("required", []))


if __name__ == "__main__":
    unittest.main()
