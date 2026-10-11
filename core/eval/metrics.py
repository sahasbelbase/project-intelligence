"""
Project Intelligence - Eval Metrics
Turns a trace into numbers: tokens, time, handoff unsupported-claim rate, handoff fidelity, task success.
Token counts are the provider's when the trace has them; otherwise they are estimated at about four
characters per token and flagged "estimated" so nobody mistakes them for billing data.
Zero external dependencies (Python standard library only).
"""

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.eval.claims import check_handoffs

CHARS_PER_TOKEN = 4


def _estimate(text: str) -> int:
    return max(1, round(len(text) / CHARS_PER_TOKEN)) if text else 0


def _iso(value: Optional[str]) -> Optional[datetime.datetime]:
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None
    except (ValueError, AttributeError):
        return None


def _step_duration_ms(step: Dict[str, Any]) -> Optional[float]:
    if step.get("durationMs") is not None:
        return float(step["durationMs"])
    start, end = _iso(step.get("startedAt")), _iso(step.get("endedAt"))
    return (end - start).total_seconds() * 1000 if start and end else None


def evaluate_trace(trace: Dict[str, Any], workspace: Optional[Path] = None,
                   price_in: Optional[float] = None, price_out: Optional[float] = None) -> Dict[str, Any]:
    """Score one run. price_in and price_out are dollars per million tokens."""
    steps_out: List[Dict[str, Any]] = []
    estimated = False
    for step in trace["steps"]:
        tin, tout = step.get("tokensIn"), step.get("tokensOut")
        source = "reported"
        if tin is None or tout is None:
            source = "estimated"
            estimated = True
            tin = tin if tin is not None else _estimate(trace.get("task", "") if not steps_out else steps_out[-1]["outputText"])
            tout = tout if tout is not None else _estimate(step.get("output", ""))
        steps_out.append({
            "stepId": step["stepId"], "agent": step["agent"], "model": step.get("model") or trace.get("model"),
            "tokensIn": tin, "tokensOut": tout, "tokenSource": source,
            "durationMs": _step_duration_ms(step), "outputText": step.get("output", ""),
        })
    for s in steps_out:
        del s["outputText"]

    handoffs = check_handoffs(trace, workspace)
    claims = sum(h["claims"] for h in handoffs)
    unsupported = sum(len(h["unsupported"]) for h in handoffs)
    fields = sum(h["requiredFields"] for h in handoffs)
    missing = sum(len(h["missingFields"]) for h in handoffs)

    durations = [s["durationMs"] for s in steps_out if s["durationMs"] is not None]
    starts = [_iso(s.get("startedAt")) for s in trace["steps"]]
    ends = [_iso(s.get("endedAt")) for s in trace["steps"]]
    if all(starts) and all(ends):
        wall_ms: Optional[float] = (max(ends) - min(starts)).total_seconds() * 1000
    else:
        wall_ms = None

    tokens_in = sum(s["tokensIn"] for s in steps_out)
    tokens_out = sum(s["tokensOut"] for s in steps_out)
    cost = None
    if price_in is not None and price_out is not None:
        cost = round(tokens_in * price_in / 1e6 + tokens_out * price_out / 1e6, 6)

    expected = (trace.get("expected") or {}).get("finalContains")
    final = (trace["steps"][-1].get("output") or "").lower()
    success = None if not expected else all(str(e).lower() in final for e in expected)

    return {
        "runId": trace.get("runId"),
        "model": trace.get("model") or next((s["model"] for s in steps_out if s["model"]), None),
        "steps": steps_out,
        "tokensIn": tokens_in, "tokensOut": tokens_out, "tokensTotal": tokens_in + tokens_out,
        "tokensEstimated": estimated, "costUsd": cost,
        "stepTimeMs": round(sum(durations), 1) if durations else None,
        "wallClockMs": round(wall_ms, 1) if wall_ms is not None else None,
        "handoffs": handoffs,
        "handoffClaims": claims, "unsupportedClaims": unsupported,
        "unsupportedClaimRate": round(unsupported / claims, 4) if claims else None,
        "handoffFieldsRequired": fields, "handoffFieldsMissing": missing,
        "handoffFidelity": round(1 - missing / fields, 4) if fields else None,
        "taskSuccess": success,
    }


def _mean(values: List[Optional[float]]) -> Optional[float]:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 4) if values else None


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Group runs by model and average the metrics."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        groups.setdefault(r["model"] or "unknown", []).append(r)
    out: Dict[str, Dict[str, Any]] = {}
    for model, runs in groups.items():
        successes = [r["taskSuccess"] for r in runs if r["taskSuccess"] is not None]
        claims = sum(r["handoffClaims"] for r in runs)
        out[model] = {
            "runs": len(runs),
            "meanTokensTotal": _mean([r["tokensTotal"] for r in runs]),
            "meanCostUsd": _mean([r["costUsd"] for r in runs]),
            "meanWallClockMs": _mean([r["wallClockMs"] if r["wallClockMs"] is not None else r["stepTimeMs"] for r in runs]),
            "unsupportedClaimRate": round(sum(r["unsupportedClaims"] for r in runs) / claims, 4) if claims else None,
            "meanHandoffFidelity": _mean([r["handoffFidelity"] for r in runs]),
            "taskSuccessRate": round(sum(successes) / len(successes), 4) if successes else None,
            "anyTokensEstimated": any(r["tokensEstimated"] for r in runs),
        }
    return out
