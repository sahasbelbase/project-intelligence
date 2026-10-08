"""
Project Intelligence — Routing accuracy.
cases.json is the tuning set; holdout.json was written after tuning and is never
tuned against. The thresholds guard against regressions, and the calibration test
checks that wrong specialist picks on unseen requests are flagged as low confidence,
which tells the agent to confirm or override.
Zero external dependencies (Python standard library only).
"""

import json
import unittest
from pathlib import Path

from core.council.referee import Referee

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "validation" / "fixtures" / "routing"


def _describe(case, plan):
    got = plan.get("specialist", {}).get("personaId") or ",".join(plan.get("councils", []))
    want = case.get("specialist") or case.get("council") or "-"
    fired = "; ".join(f"{e['personaId']}: {'/'.join(e['keywords'])}" for e in plan.get("evidence", [])) or "no keywords matched"
    return (f"'{case['task']}': expected tier {case['tier']} ({want}), got tier {plan['tier']} ({got}), "
            f"confidence {plan.get('confidence')}; keywords fired: {fired}")


def _check(ref, case):
    plan = ref.plan(case["task"])
    if plan["tier"] != case["tier"]:
        return False, plan
    if case["tier"] == 1 and "specialist" in case:
        return plan.get("specialist", {}).get("personaId") == case["specialist"], plan
    if case["tier"] == 2:
        session = plan["sessions"][0]
        ids = [m["personaId"] for m in session["convened"]]
        return session["councilId"] == case["council"] and all(i in ids for i in case.get("include", [])), plan
    return True, plan


class TestRoutingAccuracy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referee(ROOT)

    def _score(self, name):
        cases = [c for c in json.loads((FIXTURES / name).read_text())["cases"] if not c.get("knownMiss")]
        results = [(c, *_check(self.ref, c)) for c in cases]
        correct = sum(1 for _, ok, _ in results if ok)
        print(f"\n  routing {name}: {correct}/{len(cases)} correct", end="")
        return correct / len(cases), results

    def test_tuning_set(self):
        accuracy, results = self._score("cases.json")
        misses = "\n  ".join(_describe(c, p) for c, ok, p in results if not ok)
        self.assertGreaterEqual(accuracy, 0.95, f"misrouted:\n  {misses}")

    def test_holdout_set(self):
        accuracy, _ = self._score("holdout.json")
        self.assertGreaterEqual(accuracy, 0.75)

    def test_every_wrong_route_is_flagged_low(self):
        """Council decision dec-routing-keywords-vs-model: a wrong tier or a wrong specialist,
        on either set, must carry confidence=low so the agent is told to check it."""
        for name in ("cases.json", "holdout.json"):
            for case in json.loads((FIXTURES / name).read_text())["cases"]:
                ok, plan = _check(self.ref, case)
                if not ok and plan["tier"] > 0:
                    with self.subTest(fixture=name, task=case["task"]):
                        self.assertEqual(plan["confidence"], "low", _describe(case, plan))

    def test_known_misses_are_recorded(self):
        known = [c for c in json.loads((FIXTURES / "cases.json").read_text())["cases"] if c.get("knownMiss")]
        holdout = {c["task"] for c in json.loads((FIXTURES / "holdout.json").read_text())["cases"]}
        self.assertEqual(len(known), 4)
        self.assertTrue(all(c["task"] in holdout for c in known), "known misses come from the held-out set")

    def test_overrides_win(self):
        plan = self.ref.plan("Store the session token in a cookie", persona="security-engineer")
        self.assertEqual(plan["specialist"]["personaId"], "security-engineer")
        plan = self.ref.plan("Decide whether to move from SQLite to Postgres", council="development")
        self.assertEqual(plan["tier"], 2)
        self.assertEqual(plan["sessions"][0]["councilId"], "development")


if __name__ == "__main__":
    unittest.main()
