"""
Project Intelligence - Multi-agent Evaluation Tests
Planted problems must be flagged and clean runs must score clean, so the checker is measured,
not assumed. Zero external dependencies (Python standard library only).
"""

import json
import tempfile
import unittest
from pathlib import Path

from core.eval.claims import check_handoffs, extract_claims
from core.eval.metrics import evaluate_trace, summarize
from core.eval.report import render_markdown, run, _main
from core.eval.trace import TraceError, load_traces, validate_trace

EXAMPLES = Path(__file__).resolve().parents[2] / "core" / "eval" / "examples"


def _trace(**over):
    base = {
        "runId": "t", "task": "do the thing in a.py",
        "steps": [
            {"stepId": "s1", "agent": "a", "tokensIn": 10, "tokensOut": 5, "durationMs": 100,
             "toolOutputs": [{"tool": "pytest", "output": "7 passed"}], "output": "ok",
             "handoff": {"to": "s2", "requiredFields": ["f"], "payload": {"f": "a.py, 7 passed"}}},
            {"stepId": "s2", "agent": "b", "tokensIn": 10, "tokensOut": 5, "durationMs": 50, "output": "done"},
        ],
    }
    base.update(over)
    return base


class TestTraceValidation(unittest.TestCase):
    def test_valid_trace(self):
        self.assertEqual(validate_trace(_trace()), [])

    def test_problems_are_named(self):
        self.assertTrue(validate_trace({"steps": []}))
        bad = _trace()
        bad["steps"][0]["tokensIn"] = -1
        bad["steps"][0]["handoff"]["to"] = "missing"
        errors = " ".join(validate_trace(bad))
        self.assertIn("tokensIn", errors)
        self.assertIn("not a stepId", errors)

    def test_duplicate_step_ids_rejected(self):
        bad = _trace()
        bad["steps"][1]["stepId"] = "s1"
        self.assertTrue(any("unique" in e for e in validate_trace(bad)))

    def test_load_rejects_bad_json_and_jsonl_runs(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "x.json").write_text("{nope", encoding="utf-8")
            with self.assertRaises(TraceError):
                load_traces(Path(d) / "x.json")
            many = Path(d) / "many.jsonl"
            many.write_text(json.dumps(_trace()) + "\n" + json.dumps(_trace(runId="u")) + "\n", encoding="utf-8")
            self.assertEqual([t["runId"] for t in load_traces(many)], ["t", "u"])


class TestClaimChecker(unittest.TestCase):
    def test_extraction(self):
        kinds = {(c["kind"], c["value"]) for c in extract_claims("Edited src/a.py, call `run_it`, 12 passed and 3 files.")}
        self.assertIn(("file", "src/a.py"), kinds)
        self.assertIn(("identifier", "run_it"), kinds)
        self.assertIn(("count", "12 passed"), kinds)
        self.assertIn(("count", "3 files"), kinds)

    def test_supported_claims_score_zero(self):
        (h,) = check_handoffs(_trace())
        self.assertEqual(h["unsupported"], [])
        self.assertEqual(h["missingFields"], [])

    def test_planted_unsupported_claims_are_flagged(self):
        t = _trace()
        t["steps"][0]["handoff"]["payload"] = {"f": "a.py and ghost.py, 99 passed, `made_up`"}
        (h,) = check_handoffs(t)
        flagged = {c["text"] for c in h["unsupported"]}
        self.assertEqual(flagged, {"ghost.py", "99 passed", "made_up"})

    def test_sender_output_is_not_evidence_for_itself(self):
        t = _trace()
        t["steps"][0]["output"] = "ghost.py exists"
        t["steps"][0]["handoff"]["payload"] = {"f": "ghost.py"}
        (h,) = check_handoffs(t)
        self.assertEqual([c["text"] for c in h["unsupported"]], ["ghost.py"])

    def test_earlier_step_output_is_evidence(self):
        t = _trace()
        t["steps"].insert(0, {"stepId": "s0", "agent": "z", "output": "found ghost.py", "durationMs": 1})
        t["steps"][1]["handoff"]["payload"] = {"f": "ghost.py"}
        (h,) = check_handoffs(t)
        self.assertEqual(h["unsupported"], [])

    def test_file_confirmed_by_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "real.py").write_text("x", encoding="utf-8")
            t = _trace()
            t["steps"][0]["handoff"]["payload"] = {"f": "real.py and ../real.py"}
            (h,) = check_handoffs(t, Path(d))
            # real.py exists in the workspace; a ../ path escapes it and is not confirmed
            self.assertEqual([c["text"] for c in h["unsupported"]], ["../real.py"])

    def test_explicit_claims_need_quoted_evidence(self):
        t = _trace()
        t["steps"][0]["claims"] = [{"text": "tests pass", "evidence": ["7 passed"]}, {"text": "lint clean", "evidence": ["0 errors"]}, {"text": "bare"}]
        (h,) = check_handoffs(t)
        self.assertEqual({c["text"] for c in h["unsupported"]}, {"lint clean", "bare"})

    def test_missing_required_fields(self):
        t = _trace()
        t["steps"][0]["handoff"]["requiredFields"] = ["f", "g"]
        (h,) = check_handoffs(t)
        self.assertEqual(h["missingFields"], ["g"])


class TestMetrics(unittest.TestCase):
    def test_tokens_time_and_cost(self):
        r = evaluate_trace(_trace(), price_in=2.0, price_out=10.0)
        self.assertEqual((r["tokensIn"], r["tokensOut"], r["tokensTotal"]), (20, 10, 30))
        self.assertFalse(r["tokensEstimated"])
        self.assertEqual(r["stepTimeMs"], 150.0)
        self.assertAlmostEqual(r["costUsd"], 20 * 2 / 1e6 + 10 * 10 / 1e6)

    def test_missing_tokens_are_estimated_and_flagged(self):
        t = _trace()
        del t["steps"][1]["tokensIn"]
        r = evaluate_trace(t)
        self.assertTrue(r["tokensEstimated"])
        self.assertEqual(r["steps"][1]["tokenSource"], "estimated")

    def test_wall_clock_from_timestamps(self):
        t = _trace()
        t["steps"][0].update(startedAt="2026-01-01T00:00:00Z", endedAt="2026-01-01T00:00:02Z")
        t["steps"][1].update(startedAt="2026-01-01T00:00:03Z", endedAt="2026-01-01T00:00:05Z")
        for s in t["steps"]:
            s.pop("durationMs")
        self.assertEqual(evaluate_trace(t)["wallClockMs"], 5000.0)

    def test_no_claims_means_no_rate_not_zero(self):
        t = _trace()
        t["steps"][0].pop("handoff")
        self.assertIsNone(evaluate_trace(t)["unsupportedClaimRate"])

    def test_task_success(self):
        t = _trace(expected={"finalContains": ["done"]})
        self.assertTrue(evaluate_trace(t)["taskSuccess"])
        t["expected"] = {"finalContains": ["nope"]}
        self.assertFalse(evaluate_trace(t)["taskSuccess"])


class TestShippedExamples(unittest.TestCase):
    """The examples users run first must behave exactly as documented."""

    def test_clean_vs_planted(self):
        report = run([EXAMPLES], None, None, None)
        by_id = {r["runId"]: r for r in report["results"]}
        clean, bad = by_id["clean-run"], by_id["planted-problems"]
        self.assertEqual(clean["unsupportedClaims"], 0)
        self.assertEqual(clean["handoffFidelity"], 1.0)
        self.assertTrue(clean["taskSuccess"])
        flagged = {c["text"] for h in bad["handoffs"] for c in h["unsupported"]}
        self.assertEqual(flagged, {"src/validators.py", "sanitize_input", "40 tests", "3 files"})
        self.assertEqual(sorted(f for h in bad["handoffs"] for f in h["missingFields"]), ["line", "owner"])
        self.assertFalse(bad["taskSuccess"])
        self.assertEqual(set(report["summary"]), {"model-a", "model-b"})

    def test_markdown_and_gate_exit_code(self):
        report = run([EXAMPLES], None, None, None)
        md = render_markdown(report["results"], report["summary"])
        self.assertIn("not proof of fabrication", md)
        self.assertEqual(_main([str(EXAMPLES / "clean-run.json"), "--max-unsupported", "0"]), 0)
        self.assertEqual(_main([str(EXAMPLES / "planted-problems.json"), "--max-unsupported", "0.1"]), 1)
        self.assertEqual(_main(["/nonexistent/trace.json"]), 2)


if __name__ == "__main__":
    unittest.main()
