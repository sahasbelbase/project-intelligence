"""
Project Intelligence — Universal Personas and Skills Catalog Test Suite
Validates universal persona definitions, skill definitions, and persona deliverable structures.
Zero external dependencies (Python standard library only).
"""

import json
from pathlib import Path
import re
import unittest


class TestUniversalPersonasAndSkills(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.schemas_dir = cls.project_root / "core" / "schemas"
        cls.agents_dir = cls.project_root / "agents"
        cls.skills_dir = cls.project_root / "skills"
        cls.contracts_dir = cls.project_root / "contracts"

        # Load schemas
        persona_schema_path = cls.schemas_dir / "persona-definition.schema.json"
        if not persona_schema_path.exists():
            persona_schema_path = cls.schemas_dir / "agent-definition.schema.json"
        with open(persona_schema_path, "r", encoding="utf-8") as f:
            cls.persona_schema = json.load(f)

        skill_schema_path = cls.schemas_dir / "skill-definition.schema.json"
        with open(skill_schema_path, "r", encoding="utf-8") as f:
            cls.skill_schema = json.load(f)

        council_brief_schema_path = cls.schemas_dir / "council-brief.schema.json"
        if council_brief_schema_path.exists():
            with open(council_brief_schema_path, "r", encoding="utf-8") as f:
                cls.council_brief_schema = json.load(f)
        else:
            cls.council_brief_schema = None

    # -------------------------------------------------------------------------
    # Helper Validation Methods (JSON Schema Draft-07 subset, stdlib only)
    # -------------------------------------------------------------------------
    def _validate_persona(self, persona_data: dict, file_label: str):
        """Validate persona dictionary against persona-definition schema."""
        required = self.persona_schema.get("required", [])
        for req_field in required:
            self.assertIn(req_field, persona_data, f"{file_label} missing required field '{req_field}'")

        # Validate allowed properties (additionalProperties: false)
        allowed = set(self.persona_schema.get("properties", {}).keys())
        for key in persona_data.keys():
            self.assertIn(key, allowed, f"{file_label} contains unauthorized property '{key}'")

        # Specific field checks
        self.assertTrue(
            re.match(r"^[a-z0-9-]+$", persona_data["personaId"]),
            f"{file_label} personaId '{persona_data['personaId']}' must be kebab-case"
        )
        self.assertGreaterEqual(len(persona_data["title"]), 3, f"{file_label} title must be >= 3 chars")
        self.assertGreaterEqual(len(persona_data["group"]), 2, f"{file_label} group must be >= 2 chars")
        self.assertGreaterEqual(len(persona_data["mission"]), 10, f"{file_label} mission must be >= 10 chars")

        array_fields = [
            "expertise", "responsibilities", "typicalQuestions",
            "inputs", "outputs", "failureModes", "whenToInvoke", "whenNotToInvoke"
        ]
        for field in array_fields:
            val = persona_data[field]
            self.assertIsInstance(val, list, f"{file_label} '{field}' must be a list")
            self.assertGreater(len(val), 0, f"{file_label} '{field}' must not be empty")
            for item in val:
                self.assertIsInstance(item, str, f"{file_label} items in '{field}' must be strings")

        # boundaries check (oneOf: list of strings OR object with prohibitions, delegations, scopeLimits)
        boundaries = persona_data["boundaries"]
        if isinstance(boundaries, list):
            self.assertGreater(len(boundaries), 0)
            self.assertTrue(all(isinstance(x, str) for x in boundaries))
        elif isinstance(boundaries, dict):
            for k in ["prohibitions", "delegations", "scopeLimits"]:
                if k in boundaries:
                    self.assertIsInstance(boundaries[k], list)
                    self.assertTrue(all(isinstance(x, str) for x in boundaries[k]))
        else:
            self.fail(f"{file_label} boundaries must be a list or object")

        # evidenceRequirements check
        evidence = persona_data["evidenceRequirements"]
        if isinstance(evidence, list):
            self.assertGreater(len(evidence), 0)
            self.assertTrue(all(isinstance(x, str) for x in evidence))
        elif isinstance(evidence, dict):
            if "mandatoryEvidence" in evidence:
                self.assertIsInstance(evidence["mandatoryEvidence"], list)
            if "acceptableSources" in evidence:
                self.assertIsInstance(evidence["acceptableSources"], list)
            if "minimumConfidence" in evidence:
                self.assertIsInstance(evidence["minimumConfidence"], (int, float))
                self.assertGreaterEqual(evidence["minimumConfidence"], 0.0)
                self.assertLessEqual(evidence["minimumConfidence"], 1.0)
        else:
            self.fail(f"{file_label} evidenceRequirements must be a list or object")

        # collaborationResponsibilities check
        collab = persona_data["collaborationResponsibilities"]
        if isinstance(collab, list):
            self.assertGreater(len(collab), 0)
            self.assertTrue(all(isinstance(x, str) for x in collab))
        elif isinstance(collab, dict):
            if "primaryPartners" in collab:
                self.assertIsInstance(collab["primaryPartners"], list)
            if "challengeFocus" in collab:
                self.assertIsInstance(collab["challengeFocus"], str)
            if "handoffProtocols" in collab:
                self.assertIsInstance(collab["handoffProtocols"], list)
        else:
            self.fail(f"{file_label} collaborationResponsibilities must be a list or object")

    def _validate_skill(self, skill_data: dict, file_label: str):
        """Validate skill dictionary against skill-definition schema."""
        required = self.skill_schema.get("required", [])
        for req_field in required:
            self.assertIn(req_field, skill_data, f"{file_label} missing required field '{req_field}'")

        # Validate allowed properties (additionalProperties: false)
        allowed = set(self.skill_schema.get("properties", {}).keys())
        for key in skill_data.keys():
            self.assertIn(key, allowed, f"{file_label} contains unauthorized property '{key}'")

        # Specific field checks
        self.assertTrue(
            re.match(r"^[a-z0-9-]+$", skill_data["skillId"]),
            f"{file_label} skillId '{skill_data['skillId']}' must be kebab-case"
        )
        self.assertIsInstance(skill_data["name"], str)
        self.assertIsInstance(skill_data["purpose"], str)

        self.assertIsInstance(skill_data["whenToUse"], list)
        self.assertGreater(len(skill_data["whenToUse"]), 0)
        self.assertIsInstance(skill_data["prerequisites"], list)

        # inputs check
        self.assertIsInstance(skill_data["inputs"], list)
        for inp in skill_data["inputs"]:
            self.assertIsInstance(inp, dict)
            self.assertIn("name", inp)
            self.assertIn("type", inp)
            self.assertIn("description", inp)

        # procedure check
        self.assertIsInstance(skill_data["procedure"], list)
        self.assertGreater(len(skill_data["procedure"]), 0)
        for proc in skill_data["procedure"]:
            self.assertIsInstance(proc, dict)
            self.assertIn("stepNumber", proc)
            self.assertIn("title", proc)
            self.assertIn("action", proc)
            self.assertIsInstance(proc["stepNumber"], int)

        # expectedOutputs
        self.assertIsInstance(skill_data["expectedOutputs"], list)
        self.assertGreater(len(skill_data["expectedOutputs"]), 0)

        # applicableApprovalGates
        valid_gates = {"G0", "G1", "G2", "G3", "G4", "G5", "G6"}
        self.assertIsInstance(skill_data["applicableApprovalGates"], list)
        for gate in skill_data["applicableApprovalGates"]:
            self.assertIn(gate, valid_gates, f"{file_label} invalid gate '{gate}'")

        # failureAndRecovery
        fnr = skill_data["failureAndRecovery"]
        self.assertIsInstance(fnr, dict)
        self.assertIn("potentialFailures", fnr)
        self.assertIn("recoveryStrategy", fnr)
        self.assertIsInstance(fnr["potentialFailures"], list)
        self.assertIsInstance(fnr["recoveryStrategy"], str)

        # verificationCriteria
        self.assertIsInstance(skill_data["verificationCriteria"], list)
        self.assertGreater(len(skill_data["verificationCriteria"]), 0)

        # relevantContractsAndMemory
        rcm = skill_data["relevantContractsAndMemory"]
        self.assertIsInstance(rcm, dict)
        self.assertIn("contracts", rcm)
        self.assertIn("memoryRecords", rcm)
        self.assertIsInstance(rcm["contracts"], list)
        self.assertIsInstance(rcm["memoryRecords"], list)

    # -------------------------------------------------------------------------
    # Test 1: Persona Definitions Conformance
    # -------------------------------------------------------------------------
    def test_universal_personas_exist_and_conform_to_schema(self):
        """Validate all 8 universal personas exist with agent.json and agent.md conforming to schema."""
        expected_personas = [
            ("strategy/strategy-analyst", "strategy-analyst", "strategy"),
            ("business/business-analyst", "business-analyst", "business"),
            ("business/product-manager", "product-manager", "business"),
            ("business/project-manager", "project-manager", "business"),
            ("business/project-coordinator", "project-coordinator", "business"),
            ("quality/qa-analyst", "qa-analyst", "quality"),
            ("commercial/sales-strategist", "sales-strategist", "commercial"),
            ("commercial/customer-advocate", "customer-advocate", "commercial"),
        ]

        for subpath, expected_id, expected_group in expected_personas:
            p_dir = self.agents_dir / subpath
            self.assertTrue(p_dir.exists(), f"Persona directory does not exist: {p_dir}")

            json_file = p_dir / "agent.json"
            self.assertTrue(json_file.exists(), f"Persona agent.json missing: {json_file}")

            md_file = p_dir / "agent.md"
            self.assertTrue(md_file.exists(), f"Persona agent.md missing: {md_file}")

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data.get("personaId"), expected_id, f"personaId mismatch in {json_file}")
            self.assertEqual(data.get("group"), expected_group, f"group mismatch in {json_file}")

            # Schema validation
            self._validate_persona(data, f"{subpath}/agent.json")

            # Markdown validation
            md_content = md_file.read_text(encoding="utf-8")
            self.assertIn(f"# {data['title']}", md_content, f"{md_file} missing title heading")
            self.assertIn("Operational Mandate", md_content, f"{md_file} missing Operational Mandate section")
            self.assertIn("Canonical System Prompt Template", md_content, f"{md_file} missing Prompt Template section")

    # -------------------------------------------------------------------------
    # Test 2: Skill Definitions Conformance
    # -------------------------------------------------------------------------
    def test_universal_skills_exist_and_conform_to_schema(self):
        """Validate all 7 universal skills exist with skill.json and SKILL.md conforming to schema."""
        expected_skills = [
            ("orchestrator", "orchestrator"),
            ("requirements-analysis", "requirements-analysis"),
            ("test-case-generation", "test-case-generation"),
            ("project-planning", "project-planning"),
            ("business-case", "business-case"),
            ("feature-prioritization", "feature-prioritization"),
            ("council-review", "council-review"),
        ]

        for folder_name, expected_skill_id in expected_skills:
            s_dir = self.skills_dir / folder_name
            self.assertTrue(s_dir.exists(), f"Skill directory does not exist: {s_dir}")

            json_file = s_dir / "skill.json"
            self.assertTrue(json_file.exists(), f"skill.json missing in {s_dir}")

            md_file = s_dir / "SKILL.md"
            self.assertTrue(md_file.exists(), f"SKILL.md missing in {s_dir}")

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data.get("skillId"), expected_skill_id, f"skillId mismatch in {json_file}")

            # Schema validation
            self._validate_skill(data, f"skills/{folder_name}/skill.json")

            # Markdown frontmatter check
            md_content = md_file.read_text(encoding="utf-8")
            self.assertTrue(md_content.startswith("---"), f"{md_file} must begin with YAML frontmatter delimiter '---'")
            self.assertIn(f"skillId: {expected_skill_id}", md_content, f"{md_file} frontmatter missing skillId")
            self.assertIn("## 1. Purpose", md_content, f"{md_file} missing '## 1. Purpose' section")
            self.assertIn("## 5. Procedure", md_content, f"{md_file} missing '## 5. Procedure' section")
            self.assertIn("## 9. Verification Criteria", md_content, f"{md_file} missing '## 9. Verification Criteria'")

    # -------------------------------------------------------------------------
    # Test 3: Core Personas Produce Expected Deliverable Structures
    # -------------------------------------------------------------------------
    def test_core_personas_deliverable_structures(self):
        """Verify that core personas produce expected deliverable structures matching domain requirements."""

        # 1. Business Analyst Deliverable: Requirements Specification & Contract structure
        ba_deliverable = {
            "functionalRequirements": [
                {
                    "reqId": "REQ-001",
                    "title": "User Workspace Export",
                    "description": "System shall allow authenticated users to export all project artifacts in encrypted zip format.",
                    "priority": "HIGH"
                }
            ],
            "nonFunctionalRequirements": [
                {
                    "nfrId": "NFR-001",
                    "category": "PERFORMANCE",
                    "metric": "p95 export generation time",
                    "targetThreshold": "< 2000ms"
                }
            ],
            "acceptanceCriteria": [
                {
                    "criterionId": "AC-001",
                    "reqRef": "REQ-001",
                    "given": "An authenticated administrator on workspace settings",
                    "when": "The user clicks 'Download Encrypted Export'",
                    "then": "An AES-256 encrypted zip archive is streamed and an audit event is logged"
                }
            ],
            "edgeCases": [
                {
                    "caseId": "EC-001",
                    "description": "Network disruption occurs during a multi-gigabyte export stream",
                    "expectedBehavior": "Stream terminates cleanly and partial temporary files are deleted immediately"
                }
            ],
            "businessRules": [
                {
                    "ruleId": "BR-001",
                    "statement": "Users with role READ_ONLY cannot initiate workspace exports"
                }
            ]
        }
        self.assertIn("functionalRequirements", ba_deliverable)
        self.assertIn("acceptanceCriteria", ba_deliverable)
        self.assertIn("businessRules", ba_deliverable)
        self.assertIn("edgeCases", ba_deliverable)
        self.assertEqual(ba_deliverable["acceptanceCriteria"][0]["reqRef"], ba_deliverable["functionalRequirements"][0]["reqId"])

        # 2. QA Analyst Deliverable: Comprehensive Test Suite & RTM Traceability
        qa_deliverable = {
            "testSuites": [
                {
                    "suiteId": "TS-EXPORT",
                    "name": "Workspace Export Verification Suite",
                    "testCases": [
                        {
                            "testId": "TC-001",
                            "reqRef": "REQ-001",
                            "type": "POSITIVE",
                            "title": "Successful export with valid credentials",
                            "assertions": ["HTTP 200 OK", "Content-Type application/zip", "Audit log created"]
                        },
                        {
                            "testId": "TC-002",
                            "reqRef": "REQ-001",
                            "type": "NEGATIVE",
                            "title": "Export rejected for read-only user",
                            "assertions": ["HTTP 403 Forbidden", "Zero bytes transferred"]
                        },
                        {
                            "testId": "TC-003",
                            "reqRef": "REQ-001",
                            "type": "SECURITY",
                            "title": "Export prevents cross-tenant path traversal",
                            "assertions": ["Path traversal characters sanitized", "No foreign tenant files leaked"]
                        }
                    ]
                }
            ],
            "traceabilityMatrix": [
                {"reqId": "REQ-001", "testIds": ["TC-001", "TC-002", "TC-003"], "coverageStatus": "FULL"}
            ]
        }
        self.assertIn("testSuites", qa_deliverable)
        self.assertIn("traceabilityMatrix", qa_deliverable)
        test_types = {tc["type"] for tc in qa_deliverable["testSuites"][0]["testCases"]}
        self.assertTrue({"POSITIVE", "NEGATIVE", "SECURITY"}.issubset(test_types))
        self.assertEqual(qa_deliverable["traceabilityMatrix"][0]["coverageStatus"], "FULL")

        # 3. Product Manager Deliverable: Value vs Risk vs Complexity Prioritization & MVP Scope
        pm_deliverable = {
            "prioritizationMatrix": [
                {
                    "featureId": "FEAT-001",
                    "title": "Encrypted Export",
                    "userValue": 5,
                    "businessValue": 4,
                    "technicalComplexity": 2,
                    "executionRisk": 2,
                    "priorityScore": 4.5,
                    "classification": "QUICK_WIN"
                },
                {
                    "featureId": "FEAT-002",
                    "title": "Custom Blockchain Audit Trail",
                    "userValue": 2,
                    "businessValue": 2,
                    "technicalComplexity": 5,
                    "executionRisk": 5,
                    "priorityScore": 0.8,
                    "classification": "TIME_SINK"
                }
            ],
            "mvpScope": [
                "FEAT-001"
            ],
            "explicitExclusions": [
                {
                    "featureId": "FEAT-002",
                    "exclusionRationale": "High technical complexity and execution risk with negligible verified customer demand.",
                    "deferredToPhase": "Phase 3 or Post-Evaluation"
                }
            ]
        }
        self.assertIn("prioritizationMatrix", pm_deliverable)
        self.assertIn("mvpScope", pm_deliverable)
        self.assertIn("explicitExclusions", pm_deliverable)
        self.assertIn("FEAT-001", pm_deliverable["mvpScope"])
        self.assertEqual(pm_deliverable["explicitExclusions"][0]["featureId"], "FEAT-002")

        # 4. Project Manager & Coordinator Deliverable: WBS, Critical Path, and Disjoint Ownership
        pm_plan_deliverable = {
            "milestone": "M1-Foundations",
            "criticalPath": ["TASK-001", "TASK-002", "TASK-004"],
            "tasks": [
                {
                    "taskId": "TASK-001",
                    "title": "Export Schema Specification",
                    "assignedRole": "business-analyst",
                    "fileOwnership": ["core/schemas/export.schema.json"],
                    "prerequisites": [],
                    "verificationCriteria": ["python3 -m unittest validation/schema-tests/test_schemas.py"]
                },
                {
                    "taskId": "TASK-002",
                    "title": "Export Service Core Engine",
                    "assignedRole": "implementation",
                    "fileOwnership": ["core/export/engine.py"],
                    "prerequisites": ["TASK-001"],
                    "verificationCriteria": ["python3 -m unittest tests/test_export.py"]
                },
                {
                    "taskId": "TASK-003",
                    "title": "Export UI Button",
                    "assignedRole": "design",
                    "fileOwnership": ["ui/components/ExportButton.tsx"],
                    "prerequisites": ["TASK-001"],
                    "verificationCriteria": ["npm test ui/components/ExportButton.test.tsx"]
                },
                {
                    "taskId": "TASK-004",
                    "title": "Export Integration Verification",
                    "assignedRole": "qa-analyst",
                    "fileOwnership": ["validation/export-tests/test_export_e2e.py"],
                    "prerequisites": ["TASK-002", "TASK-003"],
                    "verificationCriteria": ["python3 -m unittest validation/export-tests/test_export_e2e.py"]
                }
            ]
        }
        self.assertIn("criticalPath", pm_plan_deliverable)
        self.assertIn("tasks", pm_plan_deliverable)
        # Verify disjoint file boundaries between concurrent tasks (TASK-002 and TASK-003)
        files_t2 = set(pm_plan_deliverable["tasks"][1]["fileOwnership"])
        files_t3 = set(pm_plan_deliverable["tasks"][2]["fileOwnership"])
        self.assertEqual(len(files_t2.intersection(files_t3)), 0, "Concurrent tasks must have disjoint file boundaries")

        # 5. Sales Strategist & Commercial Deliverable: Commercial Business Case & Objections
        sales_deliverable = {
            "valueProposition": {
                "headline": "Zero-Loss Data Portability for Enterprise Compliance",
                "painReliever": "Eliminates 40 hours of manual audit preparation per quarter",
                "gainCreator": "Guarantees SOC2 and GDPR compliance readiness out of the box"
            },
            "roiModel": {
                "annualCostWithoutSolution": 65000.0,
                "annualCostWithSolution": 15000.0,
                "netAnnualSavings": 50000.0,
                "paybackPeriodMonths": 3.6,
                "threeYearRoiMultiplier": 3.33
            },
            "objectionHandling": [
                {
                    "objection": "Will exporting large archives degrade production database performance?",
                    "buyerConcern": "System latency and downtime risk",
                    "rebuttalStrategy": "Exports execute asynchronously against read-replicas with capped background I/O priority."
                }
            ],
            "commercialRisks": [
                {
                    "riskId": "CRISK-001",
                    "description": "Extended enterprise procurement security audit cycles",
                    "mitigation": "Provide pre-packaged SOC2 Type II compliance pack and DPA template."
                }
            ]
        }
        self.assertIn("valueProposition", sales_deliverable)
        self.assertIn("roiModel", sales_deliverable)
        self.assertIn("objectionHandling", sales_deliverable)
        self.assertGreater(sales_deliverable["roiModel"]["netAnnualSavings"], 0)

        # 6. Customer Advocate Deliverable: Customer Journey Map & Friction Analysis
        cust_deliverable = {
            "customerJourney": [
                {
                    "stage": "Discovery",
                    "userAction": "Browsing export settings",
                    "emotionalState": "Curious",
                    "frictionLevel": "LOW"
                },
                {
                    "stage": "Initiation",
                    "userAction": "Clicking download without configuring GPG key",
                    "emotionalState": "Confused",
                    "frictionLevel": "HIGH",
                    "frictionRootCause": "Cryptic error message 'Missing key ID 0x0'",
                    "recommendedRemedy": "Inline wizard guiding user to create or upload GPG key in 1 click"
                }
            ],
            "timeToValueMetrics": {
                "targetTimeToFirstExportSeconds": 60,
                "baselineTimeToFirstExportSeconds": 480
            }
        }
        self.assertIn("customerJourney", cust_deliverable)
        self.assertIn("timeToValueMetrics", cust_deliverable)
        self.assertEqual(cust_deliverable["customerJourney"][1]["frictionLevel"], "HIGH")

        # 7. Council Review Deliverable: Council Decision Brief conforming to council-brief.schema.json
        council_brief_deliverable = {
            "decisionId": "DEC-2026-10-001",
            "topic": "Adopt Asynchronous Background Workers for Project Exports",
            "participatingPersonas": [
                "business-analyst",
                "qa-analyst",
                "product-manager",
                "sales-strategist"
            ],
            "recommendation": "Build",
            "strongestArgumentsFor": [
                "Prevents HTTP request timeouts for multi-gigabyte workspace exports",
                "Decouples long-running CPU workloads from synchronous API servers"
            ],
            "strongestArgumentsAgainst": [
                "Introduces Redis/worker queue operational dependency and infrastructure cost"
            ],
            "evidence": [
                "Benchmark logs show 99% of exports >50MB timeout when handled synchronously"
            ],
            "assumptions": [
                "Managed queue service latency remains under 50ms"
            ],
            "unknowns": [
                "Peak concurrent export volume during quarter-end reporting periods"
            ],
            "tradeOffs": [
                {
                    "aspect": "Architecture Complexity vs System Reliability",
                    "chosen": "Asynchronous background queue architecture",
                    "sacrificed": "Simple monolithic synchronous endpoint",
                    "rationale": "Reliability and zero-downtime during large exports outweigh simplicity"
                }
            ],
            "risks": [
                {
                    "riskId": "RISK-001",
                    "description": "Worker queue process crash during active export",
                    "severity": "HIGH",
                    "probability": "LOW"
                }
            ],
            "mitigations": [
                {
                    "riskRef": "RISK-001",
                    "strategy": "Implement transactional task acknowledgement with dead-letter queue retry",
                    "owner": "implementation"
                }
            ],
            "mvpScope": [
                "Background worker with Redis queue and S3 artifact streaming"
            ],
            "excludedScope": [
                "Multi-region geo-distributed worker clusters"
            ],
            "validationExperiments": [
                {
                    "hypothesis": "Background workers reduce sync API p99 latency by 85%",
                    "experiment": "Load test 50 concurrent exports on staging",
                    "passMetric": "API p99 latency < 250ms with zero timeout errors"
                }
            ],
            "owners": [
                "implementation",
                "qa-analyst"
            ],
            "successMetrics": [
                {
                    "metric": "Export success rate",
                    "target": "99.95%",
                    "timeframe": "30 days post-launch"
                }
            ],
            "dependencies": [
                "Managed Redis queue instance configured on staging"
            ],
            "conditionsToChange": [
                "If monthly queue infrastructure cost exceeds $500 with <100 exports per month"
            ],
            "dissent": [
                {
                    "personaId": "sales-strategist",
                    "objection": "Customer setup becomes more complicated if on-premises customers must deploy Redis",
                    "rationale": "Small on-premise customers prefer single-binary deployments without external services",
                    "suggestedAlternative": "Offer an embedded SQLite-based worker fallback mode for single-node deployments"
                }
            ],
            "confidenceLevel": "HIGH"
        }

        # Validate against council-brief schema if present
        if self.council_brief_schema:
            req_brief_fields = self.council_brief_schema.get("required", [])
            for field in req_brief_fields:
                self.assertIn(field, council_brief_deliverable, f"Council Decision Brief missing required field '{field}'")
            self.assertEqual(council_brief_deliverable["recommendation"], "Build")
            self.assertEqual(council_brief_deliverable["confidenceLevel"], "HIGH")
            self.assertEqual(len(council_brief_deliverable["dissent"]), 1)


if __name__ == "__main__":
    unittest.main()
