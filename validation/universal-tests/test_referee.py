"""
Project Intelligence — Council Referee Tests
Covers the persona registry, tier routing, convening limits, round validation,
dissent preservation, record round-trips and the vendored skills registry.
Zero external dependencies (Python standard library only).
"""

import json
import tempfile
import unittest
from pathlib import Path

from core.council.referee import Referee, RefereeError
from core.council.schema_lite import validate


ROOT = Path(__file__).resolve().parents[2]


def _session_inputs(session):
    ids = [m["personaId"] for m in session["convened"]]
    critic = next(m["personaId"] for m in session["convened"] if m["role"] == "critic")
    chair = next(m["personaId"] for m in session["convened"] if m["role"] == "chair")
    round1 = [{
        "personaId": pid,
        "recommendation": "Build",
        "stance": "Supports a narrow first release.",
        "keyArguments": ["Solves the stated problem with existing components."],
        "risks": ["Scope may grow during implementation."],
        "assumptions": ["Current users want this (ASSUMPTION)."],
        "evidence": [],
    } for pid in ids]
    challenges = [{
        "challengerId": critic, "targetId": chair, "challengeType": "SCOPE_CREEP", "severity": "MEDIUM",
        "critique": "The proposal includes two optional surfaces.", "counterProposal": "Ship one surface first.",
    }]
    revisions = [{
        "personaId": pid,
        "revisedRecommendation": "Pilot" if pid == critic else "Build",
        "whatChanged": ["Scope reduced to one surface."] if pid == chair else [],
        "whatRemainedUnchanged": ["Wants evidence of use before expanding."] if pid == critic else ["Core approach."],
        "responses": ([{"challengerId": critic, "response": "ACCEPTED", "reason": "One surface is enough to learn."}]
                      if pid == chair else []),
    } for pid in ids]
    synthesis = {
        "recommendation": "Build",
        "strongestArgumentsFor": ["Uses existing components."],
        "strongestArgumentsAgainst": ["Unproven demand."],
        "evidence": [{"category": "ASSUMPTION", "statement": "Users want this."}],
        "assumptions": ["Users want this."],
        "unknowns": ["Adoption rate."],
        "tradeOffs": [{"aspect": "Scope", "chosen": "One surface", "sacrificed": "Second surface"}],
        "risks": [{"riskId": "R1", "description": "Scope growth", "severity": "MEDIUM"}],
        "mitigations": ["Fixed scope list."],
        "mvpScope": ["One surface."],
        "excludedScope": ["Second surface."],
        "validationExperiments": [],
        "owners": [chair],
        "successMetrics": [{"metric": "Weekly use", "target": "Measured after two weeks"}],
        "dependencies": [],
        "conditionsToChange": ["Low use after two weeks."],
        "dissent": [],
        "confidenceLevel": "MEDIUM",
    }
    return round1, challenges, revisions, synthesis


class TestPersonaRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def test_registry_is_valid(self):
        self.assertEqual(self.ref.validate_registry(), [])

    def test_roster_sizes(self):
        sizes = {cid: len(c["roster"]) for cid, c in self.ref.config["councils"].items()}
        self.assertEqual(sizes, {"design": 13, "development": 13, "product": 12})

    def test_product_council_reuses_existing_agents(self):
        for pid in self.ref.config["councils"]["product"]["agentPersonas"]:
            self.assertIn("agents", str(self.ref.persona_paths[pid]))

    def test_persona_ids_are_unique_across_registry_files(self):
        ids = [json.loads(p.read_text())["personaId"] for p in (ROOT / "core/council/personas").rglob("*.json")]
        self.assertEqual(len(ids), len(set(ids)))

    def test_schema_lite_rejects_unknown_fields(self):
        persona = dict(self.ref.persona("restraint-specialist"))
        persona["madeUpField"] = True
        self.assertTrue(any("madeUpField" in e for e in validate(persona, self.ref.persona_schema)))


class TestRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def test_question_is_tier_zero(self):
        self.assertEqual(self.ref.classify("What does gate G3 check?")["tier"], 0)

    def test_focused_fix_is_tier_one(self):
        plan = self.ref.plan("Fix the contrast on this button")
        self.assertEqual(plan["tier"], 1)
        self.assertIn(plan["specialist"]["personaId"], {"accessibility-specialist", "color-harmony-specialist"})

    def test_redesign_is_tier_two_design(self):
        plan = self.ref.plan("Redesign the agents page navigation and colors")
        self.assertEqual(plan["tier"], 2)
        ids = [m["personaId"] for m in plan["sessions"][0]["convened"]]
        self.assertIn("color-harmony-specialist", ids)
        self.assertIn("information-architect", ids)

    def test_new_feature_is_tier_three_in_pipeline_order(self):
        plan = self.ref.plan("Add a new feature: team workspaces with permissions, pricing and a new dashboard")
        self.assertEqual(plan["tier"], 3)
        self.assertEqual([s["councilId"] for s in plan["sessions"]], ["product", "design", "development"])
        self.assertIn("qa-analyst", plan["qualityReview"])


class TestConvening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def test_chair_and_critic_always_attend(self):
        s = self.ref.convene("design", "tidy the footer")
        roles = {m["role"] for m in s["convened"]}
        self.assertTrue({"chair", "critic"} <= roles)

    def test_size_limit_enforced(self):
        with self.assertRaises(RefereeError):
            self.ref.convene("design", "anything", size=9)

    def test_full_roster_is_opt_in(self):
        s = self.ref.convene("design", "complete redesign", full_roster=True)
        self.assertEqual(len(s["convened"]), 13)

    def test_prompt_contains_mission_and_round_rules(self):
        s = self.ref.convene("design", "palette for dark mode")
        prompt = self.ref.persona_prompt(s, "critical-design-reviewer", 2)
        self.assertIn(self.ref.persona("critical-design-reviewer")["mission"], prompt)
        self.assertIn("at least 1 challenge", prompt)
        with self.assertRaises(RefereeError):
            self.ref.persona_prompt(s, "critical-design-reviewer", 4)


class TestRoundValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def setUp(self):
        self.session = self.ref.convene("design", "Redesign the navigation and colors")
        self.round1, self.challenges, self.revisions, self.synthesis = _session_inputs(self.session)

    def test_valid_session_assembles(self):
        record = self.ref.assemble(self.session, self.round1, self.challenges, self.revisions, self.synthesis)
        self.assertEqual(record["mode"], "deliberated")
        self.assertEqual(self.ref.validate_record(record), [])

    def test_unrecorded_dissent_is_added(self):
        record = self.ref.assemble(self.session, self.round1, self.challenges, self.revisions, self.synthesis)
        critic = next(m["personaId"] for m in self.session["convened"] if m["role"] == "critic")
        self.assertIn(critic, [d["personaId"] for d in record["brief"]["dissent"]])

    def test_blinding_violation_detected(self):
        other = self.session["convened"][1]["personaId"]
        self.round1[0]["keyArguments"] = [f"I agree with {other}."]
        self.assertTrue(any("blinded" in e for e in self.ref.validate_round1(self.session, self.round1)))

    def test_challenge_budget_enforced(self):
        extra = dict(self.challenges[0])
        too_many = [extra, dict(extra), dict(extra)]
        errors = self.ref.validate_challenges(self.session, too_many)
        self.assertTrue(any("budget" in e for e in errors))

    def test_critic_must_challenge(self):
        errors = self.ref.validate_challenges(self.session, [])
        self.assertTrue(any("critic" in e for e in errors))

    def test_unanswered_challenge_detected(self):
        for r in self.revisions:
            r["responses"] = []
        errors = self.ref.validate_revisions(self.session, self.challenges, self.revisions)
        self.assertTrue(any("did not respond" in e for e in errors))

    def test_invalid_brief_rejected(self):
        self.synthesis["recommendation"] = "Ship it"
        with self.assertRaises(RefereeError):
            self.ref.assemble(self.session, self.round1, self.challenges, self.revisions, self.synthesis)

    def test_save_and_handoff(self):
        record = self.ref.assemble(self.session, self.round1, self.challenges, self.revisions, self.synthesis)
        with tempfile.TemporaryDirectory() as tmp:
            path = self.ref.save(record, Path(tmp))
            loaded = json.loads(path.read_text())
            self.assertEqual(self.ref.validate_record(loaded), [])
        handoff = Referee.handoff(record)
        self.assertEqual(handoff["fromCouncil"], "design")
        self.assertEqual(handoff["mvpScope"], ["One surface."])


class TestSavedRecords(unittest.TestCase):
    def test_every_saved_record_is_valid(self):
        ref = Referee(ROOT)
        for path in sorted((ROOT / "memory" / "council-briefs").glob("*.json")):
            with self.subTest(record=path.name):
                self.assertEqual(ref.validate_record(json.loads(path.read_text())), [])


class TestVendoredSkills(unittest.TestCase):
    def test_vendored_skills_have_license_and_registry_entry(self):
        vendor = ROOT / "vendor" / "skills"
        registry = json.loads((vendor / "registry.json").read_text())
        entries = {e["id"]: e for e in registry["vendored"]}
        dirs = sorted(p.name for p in vendor.iterdir() if p.is_dir())
        self.assertEqual(dirs, sorted(entries))
        for sid, entry in entries.items():
            with self.subTest(skill=sid):
                self.assertIn(entry["license"], {"MIT", "Apache-2.0"})
                self.assertRegex(entry["commit"], r"^[0-9a-f]{40}$")
                for f in entry["files"]:
                    self.assertTrue((vendor / sid / f).exists(), f"{sid}/{f} missing")
                self.assertTrue((vendor / sid / "SKILL.md").read_text().startswith("---"))

    def test_referenced_skills_are_not_redistributed(self):
        vendor = ROOT / "vendor" / "skills"
        registry = json.loads((vendor / "registry.json").read_text())
        for entry in registry["referenced"]:
            self.assertFalse((vendor / entry["id"]).exists())
            self.assertTrue(entry["install"])


if __name__ == "__main__":
    unittest.main()


class TestOrchestratorDispatch(unittest.TestCase):
    """The orchestrator's single entry point, as used by the CLI, MCP and the website."""

    def test_tiers_and_text(self):
        from core.orchestrator.dispatch import dispatch, render_text
        cases = {
            "What does gate G3 check?": 0,
            "Fix the contrast on the primary button": 1,
            "Redesign the agents page navigation and colors": 2,
            "Add a new feature: team workspaces with permissions, pricing and a new dashboard": 3,
        }
        for task, tier in cases.items():
            with self.subTest(task=task):
                plan = dispatch(task)
                self.assertEqual(plan["tier"], tier)
                text = render_text(plan)
                self.assertIn(f"tier {tier}", text)
        council = dispatch("Redesign the agents page navigation and colors")
        self.assertIn("council prompt design visual-design-director 1", council["next"][0])

    def test_empty_task_rejected(self):
        from core.orchestrator.dispatch import dispatch
        with self.assertRaises(ValueError):
            dispatch("   ")

    def test_cli_ask_and_council_commands(self):
        import shutil
        import subprocess
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        res = subprocess.run(["node", str(ROOT / "bin" / "cli.js"), "ask", "--json", "Fix the contrast on the primary button"],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["specialist"]["personaId"], "accessibility-specialist")
        res = subprocess.run(["node", str(ROOT / "bin" / "cli.js"), "council", "check"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        res = subprocess.run(["node", str(ROOT / "bin" / "cli.js"), "ask"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 2)

    def test_record_rejects_session_without_critic(self):
        ref = Referee(ROOT)
        with self.assertRaises(RefereeError):
            ref.record({"councilId": "design", "task": "x", "convened": ["visual-design-director"],
                        "round1": [], "challenges": [], "revisions": [], "synthesis": {}})

    def test_website_plan_endpoint(self):
        import shutil
        import subprocess
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        script = """
const {server} = require('./web/server.js');
server.listen(0, '127.0.0.1', async () => {
  const base = 'http://127.0.0.1:' + server.address().port + '/api/plan';
  const ok = await fetch(base, {method: 'POST', body: JSON.stringify({task: 'Redesign the settings page layout'})});
  const bad = await fetch(base, {method: 'POST', body: JSON.stringify({task: 'x'.repeat(2001)})});
  console.log(JSON.stringify({ok: ok.status, tier: (await ok.json()).tier, bad: bad.status}));
  server.close();
});"""
        res = subprocess.run(["node", "-e", script], capture_output=True, text=True, cwd=ROOT, timeout=60)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout.strip().splitlines()[-1]), {"ok": 200, "tier": 2, "bad": 400})


class TestSeparateAgentSessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def test_sheet_gives_each_persona_only_its_own_prompt(self):
        sheet = self.ref.sheet("design", "Redesign the settings page", include=["accessibility-specialist"],
                               context="The app has 40k monthly users.")
        self.assertIn("accessibility-specialist", sheet["convened"])
        for item in sheet["round1"]:
            with self.subTest(persona=item["personaId"]):
                self.assertIn(self.ref.persona(item["personaId"])["mission"], item["prompt"])
                self.assertIn("40k monthly users", item["prompt"])
                others = [p for p in sheet["convened"] if p != item["personaId"]]
                self.assertFalse(any(self.ref.persona(o)["mission"] in item["prompt"] for o in others))

    def test_blinding_recorded_and_validated(self):
        session = self.ref.convene("design", "Redesign the navigation and colors")
        r1, ch, rv, syn = _session_inputs(session)
        rec = self.ref.assemble(session, r1, ch, rv, syn, blinding="separate-agents", context="Background.")
        self.assertEqual(rec["blinding"], "separate-agents")
        self.assertEqual(rec["context"], "Background.")
        self.assertEqual(self.ref.validate_record(rec), [])
        rec["blinding"] = "telepathy"
        self.assertTrue(any("blinding" in e for e in self.ref.validate_record(rec)))

    def test_handoff_text_names_scope_and_dissent(self):
        record = json.loads((ROOT / "memory" / "council-briefs" / "dec-website-revamp-slate.json").read_text())
        text = Referee.handoff_text(record)
        self.assertIn("design council decided 'Build'", text)
        self.assertIn("Open dissent", text)
