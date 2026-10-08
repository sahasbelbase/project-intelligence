"""
Project Intelligence — Task Routing & Intent Parsing Automated Tests
Tests intent categorization, domain classification, execution planning,
and enforcement of 'minimum necessary complexity, maximum useful expertise'.
Zero external dependencies (Python standard library only).
"""

import unittest

from core.orchestrator.router import (
    IntentCategory,
    TaskRouter,
    parse_user_intent,
    route_request
)


class TestTaskRouting(unittest.TestCase):

    def setUp(self):
        self.router = TaskRouter()

    def test_intent_category_enum(self):
        """Verify all 5 canonical intent categories exist and have valid string representations."""
        expected = {
            "SINGLE_PERSONA",
            "SEQUENTIAL_WORKFLOW",
            "COUNCIL",
            "VERIFICATION",
            "REVIEW"
        }
        actual = {c.value for c in IntentCategory}
        self.assertEqual(expected, actual)

    def test_parse_single_persona_intent(self):
        """Focused, bounded single-domain queries route to SINGLE_PERSONA."""
        # 1. Implementation typo fix
        res_impl = parse_user_intent("Fix typo in calculate_tax function docstring")
        self.assertEqual(res_impl["intentCategory"], IntentCategory.SINGLE_PERSONA)
        self.assertIn("implementation", res_impl["targetPersonas"])
        self.assertLessEqual(res_impl["complexityScore"], 4)

        # 2. Design layout request
        res_design = parse_user_intent("Update button hover CSS styling and responsive breakpoint")
        self.assertEqual(res_design["intentCategory"], IntentCategory.SINGLE_PERSONA)
        self.assertIn("design", res_design["targetPersonas"])
        self.assertEqual(res_design["domain"], "design")

        # 3. Architecture ADR drafting
        res_arch = parse_user_intent("Author an ADR documenting modular decoupling of the event bus")
        self.assertEqual(res_arch["intentCategory"], IntentCategory.SINGLE_PERSONA)
        self.assertIn("architecture", res_arch["targetPersonas"])
        self.assertEqual(res_arch["domain"], "architecture")

    def test_parse_verification_intent(self):
        """Automated test execution requests route to VERIFICATION."""
        res = parse_user_intent("Run the test suite and verify all exit codes are 0")
        self.assertEqual(res["intentCategory"], IntentCategory.VERIFICATION)
        self.assertIn("verification", res["targetPersonas"])
        self.assertIn("testing-and-verification", res["requiredSkills"])
        self.assertEqual(res["workflow"], "verification_run")

    def test_parse_review_intent(self):
        """Adversarial quality and anti-slop audits route to REVIEW."""
        res = parse_user_intent("Perform an adversarial code review and quality audit for PR #104")
        self.assertEqual(res["intentCategory"], IntentCategory.REVIEW)
        self.assertIn("independent-review", res["targetPersonas"])
        self.assertIn("independent-review", res["requiredSkills"])
        self.assertEqual(res["workflow"], "adversarial_review")

    def test_parse_council_intent(self):
        """High-stakes decisions, debates, and explicit council requests route to COUNCIL."""
        # Explicit council keyword
        res1 = parse_user_intent("Convene a multi-persona council to debate local SQLite vs embedded PostgreSQL")
        self.assertEqual(res1["intentCategory"], IntentCategory.COUNCIL)
        self.assertGreaterEqual(len(res1["targetPersonas"]), 3)
        self.assertEqual(res1["workflow"], "council_deliberation")
        self.assertGreaterEqual(res1["complexityScore"], 8)

        # High-stakes architectural trade-off
        res2 = parse_user_intent("Evaluate architectural trade-off between microservices versus monolithic local-first architecture")
        self.assertEqual(res2["intentCategory"], IntentCategory.COUNCIL)
        self.assertGreaterEqual(len(res2["targetPersonas"]), 3)

    def test_parse_sequential_workflow_intent(self):
        """Multi-stage feature implementations route to SEQUENTIAL_WORKFLOW."""
        res = parse_user_intent("Implement a new user notification feature from scratch through all lifecycle gates")
        self.assertEqual(res["intentCategory"], IntentCategory.SEQUENTIAL_WORKFLOW)
        self.assertGreaterEqual(len(res["targetPersonas"]), 3)
        self.assertIn("discovery", res["targetPersonas"])
        self.assertIn("implementation", res["targetPersonas"])
        self.assertIn("verification", res["targetPersonas"])
        self.assertEqual(res["workflow"], "sequential_pipeline")

    def test_route_request_minimum_necessary_complexity_enforcement(self):
        """Verify routing output enforces minimum necessary complexity and maximum useful expertise."""
        # Simple task -> Direct route, no council
        plan_simple = route_request("Fix indentation in config.py")
        self.assertEqual(plan_simple["routeType"], "direct")
        self.assertEqual(plan_simple["intentCategory"], IntentCategory.SINGLE_PERSONA)
        self.assertEqual(len(plan_simple["selectedPersonas"]), 1)
        self.assertEqual(plan_simple["governanceLevel"], "LIGHTWEIGHT")
        self.assertIn("minimum necessary complexity", plan_simple["explanation"].lower())

        # Testing task -> Direct verification route
        plan_verify = route_request("Execute unit test assertions")
        self.assertEqual(plan_verify["routeType"], "verification")
        self.assertEqual(plan_verify["governanceLevel"], "EVIDENCE_GATE")

        # Review task -> Direct review route
        plan_review = route_request("Adversarial code review for PR 55")
        self.assertEqual(plan_review["routeType"], "review")
        self.assertEqual(plan_review["governanceLevel"], "INDEPENDENT_AUDIT")

        # Council task -> 4-round council execution plan
        plan_council = route_request("Council debate on irreversible database migration vs backward compatibility")
        self.assertEqual(plan_council["routeType"], "council")
        self.assertEqual(plan_council["governanceLevel"], "COUNCIL_GATE")
        self.assertEqual(len(plan_council["executionPlan"]), 4)
        self.assertEqual(plan_council["executionPlan"][0]["round"], "Round 1")
        self.assertEqual(plan_council["executionPlan"][1]["round"], "Round 2")
        self.assertEqual(plan_council["executionPlan"][2]["round"], "Round 3")
        self.assertEqual(plan_council["executionPlan"][3]["round"], "Round 4")

    def test_edge_cases_and_resilience(self):
        """Verify router handles empty, short, or ambiguous queries gracefully without crashing."""
        # Empty string
        res_empty = route_request("")
        self.assertIn("routeType", res_empty)
        self.assertIn("intentCategory", res_empty)

        # Whitespace
        res_ws = route_request("   \n\t  ")
        self.assertIn("routeType", res_ws)

        # Ambiguous single word
        res_single = route_request("Architecture")
        self.assertEqual(res_single["intentCategory"], IntentCategory.SINGLE_PERSONA)
        self.assertIn("architecture", res_single["selectedPersonas"])

        # Security high-risk detection
        res_sec = route_request("Examine JWT secret token exfiltration vulnerability")
        self.assertIn(res_sec["riskLevel"], ["HIGH", "CRITICAL"])


if __name__ == "__main__":
    unittest.main()
