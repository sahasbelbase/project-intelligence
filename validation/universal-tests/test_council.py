"""
Project Intelligence — Multi-Persona Council Engine Automated Tests
Tests the 4-Round Council Protocol, decision synthesis, schema conformance, and dissent preservation.
Zero external dependencies (Python standard library only).
"""

import unittest
from pathlib import Path
import json

from core.council.engine import CouncilEngine, CouncilError


class TestCouncilEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[2]
        cls.brief_schema_path = cls.project_root / "core" / "schemas" / "council-brief.schema.json"
        cls.persona_schema_path = cls.project_root / "core" / "schemas" / "persona-definition.schema.json"

        # Load schemas for validation
        with open(cls.brief_schema_path, "r", encoding="utf-8") as f:
            cls.brief_schema = json.load(f)
        with open(cls.persona_schema_path, "r", encoding="utf-8") as f:
            cls.persona_schema = json.load(f)

        # Canonical test personas conforming to Section 4
        cls.test_personas = [
            {
                "personaId": "systems-architect",
                "title": "Systems Architecture Specialist",
                "group": "architecture",
                "mission": "Design robust, modular system architectures, define component boundaries and interface contracts.",
                "expertise": ["distributed systems", "data modeling", "contract architecture"],
                "responsibilities": ["author ADRs", "define interface contracts", "evaluate trade-offs"],
                "typicalQuestions": [
                    "What are the modular component boundaries?",
                    "How are state transitions made deterministic?",
                    "What is the long-term maintainability impact?"
                ],
                "inputs": ["requirements contract", "design contract"],
                "outputs": ["architecture contract", "ADR records"],
                "boundaries": {
                    "prohibitions": ["no direct application code writing in production"],
                    "delegations": ["implementation to Implementation Engineer"],
                    "scopeLimits": ["system-level component topologies"]
                },
                "evidenceRequirements": {
                    "mandatoryEvidence": ["interface specifications", "schema validation"],
                    "acceptableSources": ["architecture-contract.schema.json"],
                    "minimumConfidence": 0.8
                },
                "failureModes": ["premature generalization", "architectural over-engineering"],
                "collaborationResponsibilities": {
                    "primaryPartners": ["implementation", "independent-review"],
                    "challengeFocus": "feasibility and modular boundaries",
                    "handoffProtocols": ["deliver signed G3 architecture contract"]
                },
                "whenToInvoke": ["architectural decisions", "contract design", "ADR authoring"],
                "whenNotToInvoke": ["trivial bug fixes", "copywriting"]
            },
            {
                "personaId": "security-engineer",
                "title": "Security & Quality Specialist",
                "group": "security",
                "mission": "Enforce strict security boundaries, least privilege, zero credential leakage, and test verification.",
                "expertise": ["threat modeling", "authentication", "credential hygiene", "fuzz testing"],
                "responsibilities": ["audit attack surfaces", "enforce anti-slop rules", "validate evidence honesty"],
                "typicalQuestions": [
                    "Where do credentials live?",
                    "What are the trust boundaries?",
                    "How is input sanitized?"
                ],
                "inputs": ["architecture contract", "code diffs"],
                "outputs": ["security review", "threat model", "verification audit"],
                "boundaries": {
                    "prohibitions": ["cannot approve unverified or skipped checks"],
                    "delegations": ["code remediation to implementation"],
                    "scopeLimits": ["security posture and verification"]
                },
                "evidenceRequirements": {
                    "mandatoryEvidence": ["test execution logs with exit code 0"],
                    "acceptableSources": ["process execution telemetry"],
                    "minimumConfidence": 0.95
                },
                "failureModes": ["security paranoia paralysis", "blocking without actionable mitigation"],
                "collaborationResponsibilities": {
                    "primaryPartners": ["architecture", "verification"],
                    "challengeFocus": "threat exposure and verification honesty",
                    "handoffProtocols": ["sign security review audit"]
                },
                "whenToInvoke": ["authentication changes", "permission modifications", "destructive tool usage"],
                "whenNotToInvoke": ["pure cosmetic layout fixes"]
            },
            {
                "personaId": "product-strategist",
                "title": "Product Strategy & Value Specialist",
                "group": "product",
                "mission": "Maximize user value delivery, eliminate bloat, and ensure roadmap alignment.",
                "expertise": ["product roadmap", "user journeys", "MVP scoping"],
                "responsibilities": ["define MVP scope", "prevent gold-plating", "measure success metrics"],
                "typicalQuestions": [
                    "Does this solve the immediate user problem?",
                    "What is the cost of delaying release?",
                    "Can we ship an MVP sooner?"
                ],
                "inputs": ["project charter", "user feedback"],
                "outputs": ["requirements contract", "MVP boundary"],
                "boundaries": {
                    "prohibitions": ["cannot compromise security or anti-slop baselines"],
                    "delegations": ["technical design to architecture"],
                    "scopeLimits": ["functional scope and milestone scheduling"]
                },
                "evidenceRequirements": {
                    "mandatoryEvidence": ["user requirements and acceptance criteria"],
                    "acceptableSources": ["requirements contract"],
                    "minimumConfidence": 0.7
                },
                "failureModes": ["rushing without testing", "ignoring architectural debt"],
                "collaborationResponsibilities": {
                    "primaryPartners": ["orchestrator", "discovery"],
                    "challengeFocus": "scope creep and over-engineering",
                    "handoffProtocols": ["deliver signed G1 requirements contract"]
                },
                "whenToInvoke": ["scope definition", "feature prioritization", "MVP trade-offs"],
                "whenNotToInvoke": ["internal code refactoring"]
            }
        ]

    def setUp(self):
        self.engine = CouncilEngine(brief_schema_path=self.brief_schema_path)
        self.sample_brief = {
            "decisionId": "dec-sqlite-vs-postgres",
            "topic": "Local Storage Engine: SQLite vs Embedded PostgreSQL",
            "context": "Selecting the durable local database storage engine for Project Intelligence.",
            "constraints": ["Local-first execution", "Zero external background daemon required"],
            "goals": ["Deterministic state persistence", "Atomic transactions", "Sub-10ms query latency"],
            "risk_profile": "HIGH"
        }

    def test_persona_schema_validation(self):
        """Verify that canonical persona definitions strictly validate against persona-definition.schema.json."""
        required_fields = self.persona_schema["required"]
        self.assertEqual(len(required_fields), 15)

        for p in self.test_personas:
            for field in required_fields:
                self.assertIn(field, p, f"Persona {p['personaId']} missing required field '{field}'")
            self.assertRegex(p["personaId"], "^[a-z0-9-]+$")
            self.assertGreaterEqual(len(p["expertise"]), 1)
            self.assertGreaterEqual(len(p["responsibilities"]), 1)
            self.assertGreaterEqual(len(p["typicalQuestions"]), 1)

    def test_round1_independent_analysis(self):
        """Test Round 1 blinded independent evaluation across personas."""
        r1 = self.engine.run_independent_analysis(self.test_personas, self.sample_brief)

        self.assertEqual(len(r1), 3)
        for pid in ["systems-architect", "security-engineer", "product-strategist"]:
            self.assertIn(pid, r1)
            analysis = r1[pid]
            self.assertIn(analysis["initialRecommendation"], self.engine.VALID_RECOMMENDATIONS)
            self.assertIn("stance", analysis)
            self.assertGreaterEqual(len(analysis["keyArguments"]), 1)
            self.assertGreaterEqual(len(analysis["identifiedRisks"]), 1)
            self.assertGreaterEqual(len(analysis["assumptions"]), 1)

        # Check distinct disciplinary perspectives
        # Security engineer should have conservative stance given HIGH risk profile
        sec = r1["security-engineer"]
        self.assertEqual(sec["stance"], "CONCERNED")
        self.assertEqual(sec["initialRecommendation"], "Test further")

        # Product strategist should favor progress
        prod = r1["product-strategist"]
        self.assertEqual(prod["stance"], "FAVORABLE")
        self.assertEqual(prod["initialRecommendation"], "Build")

    def test_round2_challenge_round(self):
        """Test Round 2 adversarial cross-examination and challenge generation."""
        r1 = self.engine.run_independent_analysis(self.test_personas, self.sample_brief)
        r2 = self.engine.run_challenge_round(r1, self.sample_brief)

        self.assertEqual(len(r2), 3)
        # Each challenger challenges every peer (2 peers each = 2 challenges)
        for challenger_id, challenges in r2.items():
            self.assertEqual(len(challenges), 2)
            for ch in challenges:
                self.assertIn("targetPersonaId", ch)
                self.assertIn("challengeType", ch)
                self.assertIn("critique", ch)
                self.assertIn(ch["severity"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                self.assertIn("counterProposal", ch)
                self.assertNotEqual(ch["targetPersonaId"], challenger_id)

    def test_round3_revision_round(self):
        """Test Round 3 revision, concessions, and preserved non-negotiable invariants."""
        r1 = self.engine.run_independent_analysis(self.test_personas, self.sample_brief)
        r2 = self.engine.run_challenge_round(r1, self.sample_brief)
        r3 = self.engine.run_revision_round(r1, r2)

        self.assertEqual(len(r3), 3)
        for pid, revision in r3.items():
            self.assertIn("whatChanged", revision)
            self.assertIn("whyChanged", revision)
            self.assertIn("whatRemainedUnchanged", revision)
            self.assertIn("revisedRecommendation", revision)
            self.assertIn(revision["revisedRecommendation"], self.engine.VALID_RECOMMENDATIONS)
            self.assertGreaterEqual(len(revision["whatChanged"]), 1)
            self.assertGreaterEqual(len(revision["whatRemainedUnchanged"]), 1)

        # Product strategist initially wanted 'Build', but faced high severity security challenge
        # Product strategist should concede to 'Pilot'
        prod_rev = r3["product-strategist"]
        self.assertEqual(prod_rev["initialRecommendation"], "Build")
        self.assertEqual(prod_rev["revisedRecommendation"], "Pilot")
        self.assertTrue(any("Pilot" in c for c in prod_rev["whatChanged"]))

    def test_round4_synthesize_decision_brief_schema_conformance(self):
        """Verify that Round 4 produces a brief adhering strictly to council-brief.schema.json."""
        r1 = self.engine.run_independent_analysis(self.test_personas, self.sample_brief)
        r2 = self.engine.run_challenge_round(r1, self.sample_brief)
        r3 = self.engine.run_revision_round(r1, r2)
        brief = self.engine.synthesize_decision_brief(self.sample_brief, r1, r2, r3)

        # Validate all 21 required fields from the schema
        required_fields = self.brief_schema["required"]
        self.assertEqual(len(required_fields), 21)

        for rf in required_fields:
            self.assertIn(rf, brief, f"Synthesized brief missing required field '{rf}'")

        # Check types and enums
        self.assertEqual(brief["decisionId"], "dec-sqlite-vs-postgres")
        self.assertIn(brief["recommendation"], ["Build", "Test further", "Pilot", "Pivot", "Defer", "Stop"])
        self.assertIn(brief["confidenceLevel"], ["HIGH", "MEDIUM", "LOW"])
        self.assertEqual(len(brief["participatingPersonas"]), 3)
        self.assertIsInstance(brief["evidence"], list)
        self.assertIsInstance(brief["assumptions"], list)
        self.assertIsInstance(brief["tradeOffs"], list)
        self.assertIsInstance(brief["risks"], list)
        self.assertIsInstance(brief["mitigations"], list)
        self.assertIsInstance(brief["mvpScope"], list)
        self.assertIsInstance(brief["excludedScope"], list)
        self.assertIsInstance(brief["validationExperiments"], list)
        self.assertIsInstance(brief["owners"], list)
        self.assertIsInstance(brief["successMetrics"], list)
        self.assertIsInstance(brief["dependencies"], list)
        self.assertIsInstance(brief["conditionsToChange"], list)
        self.assertIsInstance(brief["dissent"], list)

    def test_dissent_preservation(self):
        """Verify that dissenting viewpoints and persisting objections are explicitly preserved in the brief."""
        # Create a scenario where one persona strongly dissents
        r1 = self.engine.run_independent_analysis(self.test_personas, self.sample_brief)
        r2 = self.engine.run_challenge_round(r1, self.sample_brief)
        r3 = self.engine.run_revision_round(r1, r2)

        # Explicitly simulate a dissenting revised vote
        r3["security-engineer"]["revisedRecommendation"] = "Stop"
        r3["security-engineer"]["persistingObjections"] = [
            "Local storage engines without hardware encryption pose unacceptable exfiltration risk."
        ]

        brief = self.engine.synthesize_decision_brief(self.sample_brief, r1, r2, r3)

        # Dissent list must not be empty
        self.assertGreater(len(brief["dissent"]), 0)

        # Security engineer's objection must be recorded
        dissenting_ids = [
            d["personaId"] if isinstance(d, dict) else str(d)
            for d in brief["dissent"]
        ]
        self.assertIn("security-engineer", dissenting_ids)

        sec_dissent = [d for d in brief["dissent"] if isinstance(d, dict) and d.get("personaId") == "security-engineer"][0]
        self.assertIn("Stop", sec_dissent["objection"])
        self.assertIn("rationale", sec_dissent)
        self.assertIn("suggestedAlternative", sec_dissent)

    def test_execute_council_end_to_end(self):
        """Test full council workflow execution end-to-end."""
        res = self.engine.execute_council(self.sample_brief, self.test_personas)

        self.assertIn("decisionBrief", res)
        self.assertIn("telemetry", res)
        self.assertIn("rounds", res)

        telemetry = res["telemetry"]
        self.assertEqual(telemetry["participatingCount"], 3)
        self.assertEqual(telemetry["roundsExecuted"], 4)
        self.assertIn(telemetry["recommendation"], self.engine.VALID_RECOMMENDATIONS)

        rounds = res["rounds"]
        self.assertIn("round1IndependentAnalysis", rounds)
        self.assertIn("round2ChallengeRound", rounds)
        self.assertIn("round3RevisionRound", rounds)

    def test_empty_personas_raises_error(self):
        """Council requires at least one persona; empty list raises CouncilError."""
        with self.assertRaises(CouncilError):
            self.engine.run_independent_analysis([], self.sample_brief)


if __name__ == "__main__":
    unittest.main()
