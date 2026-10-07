"""
Project Intelligence — Schema Validation Tests
Validates all canonical JSON schemas in core/schemas/ and verifies all contract instances in contracts/.
Uses Python standard library with zero external dependencies.
"""

import unittest
import json
from pathlib import Path


class TestCoreSchemas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.schemas_dir = cls.project_root / "core" / "schemas"
        cls.contracts_dir = cls.project_root / "contracts"

    def test_all_schemas_exist_and_are_valid_json(self):
        """Ensure all required core schemas exist and parse as valid JSON."""
        expected_schemas = [
          "contract-envelope.schema.json",
          "project-contract.schema.json",
          "requirements-contract.schema.json",
          "design-contract.schema.json",
          "architecture-contract.schema.json",
          "implementation-contract.schema.json",
          "quality-contract.schema.json",
          "release-contract.schema.json",
          "memory.schema.json",
          "lifecycle.schema.json",
          "agent-definition.schema.json",
          "skill-definition.schema.json"
        ]
        for schema_name in expected_schemas:
            schema_path = self.schemas_dir / schema_name
            self.assertTrue(schema_path.exists(), f"Missing schema file: {schema_name}")
            with open(schema_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("type"), "object", f"Schema {schema_name} root type must be 'object'")
            self.assertIn("title", data, f"Schema {schema_name} must declare a 'title'")
            self.assertIn("properties", data, f"Schema {schema_name} must declare 'properties'")
            self.assertIn("required", data, f"Schema {schema_name} must declare 'required'")

    def test_contract_envelope_structure(self):
        """Validate envelope fields on all concrete contract files."""
        contract_files = list(self.contracts_dir.glob("**/contract.json"))
        self.assertGreaterEqual(len(contract_files), 7, "Must have at least 7 canonical contracts")

        with open(self.schemas_dir / "contract-envelope.schema.json", "r", encoding="utf-8") as f:
            envelope_schema = json.load(f)
        required_fields = envelope_schema["required"]

        for c_file in contract_files:
            with open(c_file, "r", encoding="utf-8") as f:
                contract = json.load(f)

            # Check required envelope fields
            for rf in required_fields:
                self.assertIn(rf, contract, f"Contract {c_file.name} in {c_file.parent.name} missing '{rf}'")

            # Check valid status
            self.assertIn(contract["status"], ["DRAFT", "UNDER_REVIEW", "APPROVED", "REJECTED", "SUPERSEDED", "DEPRECATED"])

            # Check valid gate
            self.assertIn(contract["lifecycleGate"], ["G0", "G1", "G2", "G3", "G4", "G5", "G6"])

            # Check author object
            self.assertIn("role", contract["author"])
            self.assertIn("identifier", contract["author"])

    def test_specific_contract_payloads(self):
        """Verify contract data payload fields match expected contract type."""
        type_to_required = {
            "project": ["projectName", "projectSlug", "missionStatement", "inScope", "outOfScope"],
            "requirements": ["functionalRequirements", "nonFunctionalRequirements", "acceptanceCriteria", "edgeCases"],
            "design": ["isApplicable", "designSystem", "responsiveBreakpoints", "componentStates"],
            "architecture": ["systemOverview", "components", "technologyStack", "interfaceContracts"],
            "implementation": ["workstreamId", "assignedAgentRole", "phases", "tasks", "fileOwnership"],
            "quality": ["activeProfile", "baselineRulesEnforced", "verificationSuites", "antiSlopPolicy"],
            "release": ["releaseVersion", "acceptanceStatus", "verifiedDeliverables", "knownLimitations"]
        }

        contract_files = list(self.contracts_dir.glob("**/contract.json"))
        for c_file in contract_files:
            with open(c_file, "r", encoding="utf-8") as f:
                contract = json.load(f)

            c_type = contract["contractType"]
            self.assertIn(c_type, type_to_required, f"Unknown contract type {c_type}")

            data = contract["data"]
            for expected_field in type_to_required[c_type]:
                self.assertIn(expected_field, data, f"Contract {c_type} missing payload field '{expected_field}'")


if __name__ == "__main__":
    unittest.main()
