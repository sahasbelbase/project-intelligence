"""
Project Intelligence - Handoff Claim Checker
Checks what an agent tells the next agent against evidence it could actually have seen.
Deterministic only: no model is called. A claim is "supported" when its evidence is in the
run's record, and "unsupported" when it is not. Unsupported is not proof of a lie, only that
nothing in the trace backs it, so the report says "unsupported" and never "hallucinated".

Claims are found two ways:
- explicit: the step lists {"text", "evidence": [quotes]}; every quote must appear in the evidence.
- extracted: file paths, `backticked` identifiers, and counts with a unit ("12 passed", "3 files")
  found in the handoff payload text.
Evidence for a handoff from step N is the task, every earlier step's output, and every tool
output up to and including step N. The sender's own output is not evidence for itself.
Zero external dependencies (Python standard library only).
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:py|js|ts|tsx|jsx|json|md|yml|yaml|toml|sh|html|css|java|go|rs|c|cpp|h|rb|sql|txt))\b")
_TICKED = re.compile(r"`([^`\n]{2,80})`")
_COUNT = re.compile(r"\b(\d+(?:\.\d+)?)\s*(%|ms|s|seconds|tests?|files?|lines?|errors?|failures?|passed|failed|warnings?|requests?|tokens?)(?![\w])", re.I)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _payload_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False) if payload is not None else ""


def evidence_for(trace: Dict[str, Any], step_index: int) -> str:
    """All text the sender at step_index could have legitimately seen."""
    parts: List[str] = [str(trace.get("task", ""))]
    for i, step in enumerate(trace["steps"][: step_index + 1]):
        if i < step_index:
            parts.append(step.get("output", ""))
        parts.extend(t.get("output", "") for t in step.get("toolOutputs") or [])
    return _norm("\n".join(parts))


def extract_claims(text: str) -> List[Dict[str, str]]:
    claims: List[Dict[str, str]] = []
    seen = set()
    for kind, pattern in (("file", _FILE), ("identifier", _TICKED)):
        for m in pattern.finditer(text):
            value = m.group(1)
            if kind == "identifier" and _FILE.fullmatch(value):
                continue  # already a file claim
            if (kind, value) not in seen:
                seen.add((kind, value))
                claims.append({"kind": kind, "value": value, "text": value})
    for m in _COUNT.finditer(text):
        value = f"{m.group(1)} {m.group(2)}"
        if ("count", value) not in seen:
            seen.add(("count", value))
            claims.append({"kind": "count", "value": value, "text": m.group(0)})
    return claims


def _supported(claim: Dict[str, str], evidence: str, workspace: Optional[Path]) -> bool:
    value = _norm(claim["value"])
    if claim["kind"] == "file":
        if workspace is not None:
            try:
                if (workspace / claim["value"]).resolve().is_relative_to(workspace.resolve()) and (workspace / claim["value"]).exists():
                    return True
            except OSError:
                pass
        return value in evidence
    if claim["kind"] == "count":
        number, unit = value.split(" ", 1)
        return re.search(rf"\b{re.escape(number)}\s*{re.escape(unit)}", evidence) is not None
    return value in evidence


def check_handoffs(trace: Dict[str, Any], workspace: Optional[Path] = None) -> List[Dict[str, Any]]:
    """One result per handoff: claims checked, which are unsupported, and field fidelity."""
    results: List[Dict[str, Any]] = []
    for index, step in enumerate(trace["steps"]):
        handoff = step.get("handoff")
        explicit = step.get("claims") or []
        if not handoff and not explicit:
            continue
        evidence = evidence_for(trace, index)
        checked: List[Dict[str, Any]] = []
        for claim in explicit:
            quotes = claim.get("evidence") or []
            ok = bool(quotes) and all(_norm(q) in evidence for q in quotes)
            checked.append({"kind": "explicit", "text": claim["text"], "supported": ok})
        payload = (handoff or {}).get("payload")
        for claim in extract_claims(_payload_text(payload)):
            checked.append({"kind": claim["kind"], "text": claim["text"], "supported": _supported(claim, evidence, workspace)})
        required = (handoff or {}).get("requiredFields") or []
        present = [f for f in required if isinstance(payload, dict) and payload.get(f) not in (None, "", [], {})]
        results.append({
            "from": step["stepId"],
            "to": (handoff or {}).get("to"),
            "claims": len(checked),
            "unsupported": [c for c in checked if not c["supported"]],
            "requiredFields": len(required),
            "missingFields": [f for f in required if f not in present],
        })
    return results
