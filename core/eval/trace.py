"""
Project Intelligence - Eval Trace
Loads and validates a multi-agent run trace. A trace is plain JSON, so a lab can export it from any
framework (LangGraph, AutoGen, CrewAI, a hand-written loop) without installing this one.

Trace shape (all fields optional unless marked required):
{
  "runId": "run-1", "task": "what the user asked", "model": "model name for comparisons",
  "workspace": "folder the agents worked in (lets the checker confirm cited files exist)",
  "expected": {"finalContains": ["text the final answer must contain"]},
  "steps": [                                   # required, in execution order
    {"stepId": "s1", "agent": "planner",       # stepId and agent required
     "model": "...", "durationMs": 1200, "startedAt": "ISO", "endedAt": "ISO",
     "tokensIn": 900, "tokensOut": 200,        # provider-reported; estimated from text if absent
     "output": "text the agent produced",
     "toolOutputs": [{"tool": "pytest", "output": "12 passed"}],
     "handoff": {"to": "s2", "requiredFields": ["files"], "payload": {"files": "..."}},
     "claims": [{"text": "tests pass", "evidence": ["12 passed"]}]}
  ]
}
Zero external dependencies (Python standard library only).
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class TraceError(Exception):
    """The trace file is not usable. The message says what to fix."""


def _check_step(step: Any, index: int) -> List[str]:
    where = f"steps[{index}]"
    if not isinstance(step, dict):
        return [f"{where} must be an object"]
    errors = [f"{where} needs a non-empty '{key}'" for key in ("stepId", "agent") if not step.get(key)]
    for key in ("tokensIn", "tokensOut", "durationMs"):
        value = step.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
            errors.append(f"{where}.{key} must be a non-negative number")
    for key in ("output",):
        if key in step and not isinstance(step[key], str):
            errors.append(f"{where}.{key} must be text")
    for j, tool in enumerate(step.get("toolOutputs") or []):
        if not isinstance(tool, dict) or not isinstance(tool.get("output", ""), str):
            errors.append(f"{where}.toolOutputs[{j}] must be an object with text 'output'")
    handoff = step.get("handoff")
    if handoff is not None and (not isinstance(handoff, dict) or not handoff.get("to")):
        errors.append(f"{where}.handoff needs a 'to' step id")
    for j, claim in enumerate(step.get("claims") or []):
        if not isinstance(claim, dict) or not claim.get("text"):
            errors.append(f"{where}.claims[{j}] needs 'text'")
    return errors


def validate_trace(trace: Any) -> List[str]:
    """Return a list of problems; empty means the trace is usable."""
    if not isinstance(trace, dict):
        return ["trace must be a JSON object"]
    steps = trace.get("steps")
    if not isinstance(steps, list) or not steps:
        return ["trace needs a non-empty 'steps' list"]
    errors: List[str] = []
    ids = [s.get("stepId") for s in steps if isinstance(s, dict)]
    for i, step in enumerate(steps):
        errors.extend(_check_step(step, i))
    if len(set(ids)) != len(ids):
        errors.append("stepId values must be unique")
    for i, step in enumerate(steps):
        target = (step.get("handoff") or {}).get("to") if isinstance(step, dict) else None
        if target and target not in ids:
            errors.append(f"steps[{i}].handoff.to '{target}' is not a stepId in this trace")
    return errors


def load_trace(path: Path) -> Dict[str, Any]:
    """Read one trace from a .json file, or the first line-delimited run from .jsonl."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        raise TraceError(f"Cannot read {path}: {err}") from err
    try:
        if path.suffix == ".jsonl":
            lines = [line for line in text.splitlines() if line.strip()]
            trace = json.loads(lines[0]) if lines else None
        else:
            trace = json.loads(text)
    except json.JSONDecodeError as err:
        raise TraceError(f"{path} is not valid JSON: {err}") from err
    errors = validate_trace(trace)
    if errors:
        raise TraceError(f"{path} is not a usable trace:\n  - " + "\n  - ".join(errors))
    trace.setdefault("runId", path.stem)
    return trace


def load_traces(path: Path) -> List[Dict[str, Any]]:
    """Load a file, or every .json/.jsonl file in a folder. A .jsonl file may hold many runs."""
    path = Path(path)
    files = sorted(p for p in path.iterdir() if p.suffix in (".json", ".jsonl")) if path.is_dir() else [path]
    if not files:
        raise TraceError(f"No .json or .jsonl traces found in {path}")
    traces: List[Dict[str, Any]] = []
    for f in files:
        if f.suffix == ".jsonl":
            for n, line in enumerate((l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()), 1):
                try:
                    trace = json.loads(line)
                except json.JSONDecodeError as err:
                    raise TraceError(f"{f} line {n} is not valid JSON: {err}") from err
                errors = validate_trace(trace)
                if errors:
                    raise TraceError(f"{f} line {n} is not a usable trace:\n  - " + "\n  - ".join(errors))
                trace.setdefault("runId", f"{f.stem}-{n}")
                traces.append(trace)
        else:
            traces.append(load_trace(f))
    return traces
