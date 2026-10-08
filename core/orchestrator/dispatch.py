"""
Project Intelligence — Orchestrator Dispatch
The single entry point every client uses to decide what happens with a request:

- Claude Code:     /orchestrator <task>        (installed slash command)
- Copilot CLI and other MCP clients:  the `plan_task` MCP tool
- Any terminal:    node bin/cli.js ask "<task>"   or   python3 -m core.orchestrator.dispatch "<task>"

It combines the council referee (tier, councils, convened personas) with the
lifecycle state (current gate) and the task router (fallback persona and skill),
and returns one plan plus the next commands to run. It plans; it never invents
persona opinions. Council rounds are carried out by the model following the
prompts the referee builds, then validated and saved by the referee.
Zero external dependencies (Python standard library only).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.council.referee import Referee  # noqa: E402
from core.orchestrator.router import route_request  # noqa: E402

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]


def _current_gate(workspace: Path) -> Optional[str]:
    for rel in ("memory/execution-state.json", "memory/state.json"):
        path = workspace / rel
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8")).get("currentGate")
            except (OSError, json.JSONDecodeError):
                return None
    return None


def skill_label(skill: str) -> str:
    """Human label for a council skill reference (vendor:/ext: prefixes from councils.json)."""
    if skill.startswith("vendor:"):
        return skill[7:]
    if skill.startswith("ext:"):
        return f"{skill[4:]} (install separately)"
    return skill


def _quote(task: str) -> str:
    return '"' + task.replace('"', '\\"') + '"'


def dispatch(task: str, workspace: Optional[Path] = None, full_roster: bool = False) -> Dict[str, Any]:
    """Plan a request. Returns a JSON-serializable dict."""
    task = (task or "").strip()
    if not task:
        raise ValueError("Describe the task, for example: Redesign the settings page")
    ref = Referee(FRAMEWORK_ROOT)
    plan = ref.plan(task, full_roster=full_roster)
    workspace = Path(workspace) if workspace else FRAMEWORK_ROOT
    tier = plan["tier"]

    result: Dict[str, Any] = {
        "task": task,
        "tier": tier,
        "tierName": ref.config["tiers"][str(tier)]["name"],
        "reason": plan["reason"],
        "currentGate": _current_gate(workspace),
        "councils": plan["councils"],
        "steps": [],
        "next": [],
    }

    if tier == 0:
        result["steps"].append({"kind": "answer", "text": "Answer directly from the framework's files. No skills or councils needed."})
        return result

    if tier == 1:
        spec = plan.get("specialist")
        if spec:
            result["specialist"] = spec
            result["steps"].append({"kind": "specialist", "personaId": spec["personaId"], "title": spec["title"], "skills": spec["skills"],
                                    "text": f"{spec['title']} handles this with {', '.join(map(skill_label, spec['skills'])) or 'its own checklist'}."})
        else:
            route = route_request(task)
            persona = route["selectedPersonas"][0]
            skills = route["selectedSkills"]
            result["specialist"] = {"personaId": persona, "title": persona, "skills": skills}
            result["steps"].append({"kind": "specialist", "personaId": persona, "title": persona, "skills": skills,
                                    "text": f"The {persona} agent handles this with {', '.join(skills)}."})
        result["steps"].append({"kind": "gate", "text": "Changes go through the current gate's checks before they count as done."})
        return result

    sessions = plan["sessions"]
    result["sessions"] = [{
        "councilId": s["councilId"],
        "councilTitle": s["councilTitle"],
        "workOrder": s["workOrder"],
        "convened": s["convened"],
    } for s in sessions]
    for i, s in enumerate(sessions):
        members = ", ".join(f"{m['title']} ({m['role']})" if m["role"] != "specialist" else m["title"] for m in s["convened"])
        result["steps"].append({"kind": "council", "councilId": s["councilId"], "text": f"{s['councilTitle']} convenes: {members}."})
        if i < len(sessions) - 1:
            result["steps"].append({"kind": "handoff", "text": f"Hands its decision brief to the {sessions[i + 1]['councilTitle'].lower()}."})
    if plan.get("qualityReview"):
        result["qualityReview"] = plan["qualityReview"]
        result["steps"].append({"kind": "quality", "text": "Quality review adds test scenarios and acceptance criteria before the final synthesis."})
    result["steps"].append({"kind": "rounds", "text": "Each council runs four rounds: independent views, up to two challenges each, revisions, then the chair's decision with dissent kept."})
    result["steps"].append({"kind": "record", "text": "The referee validates the session and saves it to memory/council-briefs/ for review and the website."})

    first = sessions[0]
    chair = next(m["personaId"] for m in first["convened"] if m["role"] == "chair")
    result["next"] = [
        f"python3 -m core.council.referee prompt {first['councilId']} {chair} 1 {_quote(task)}",
        "python3 -m core.council.referee check",
    ]
    return result


def render_text(result: Dict[str, Any]) -> str:
    """Plain-text rendering for terminals and chat clients."""
    lines: List[str] = [
        f"Task:  {result['task']}",
        f"Route: tier {result['tier']} ({result['tierName']}) - {result['reason']}",
    ]
    if result.get("currentGate"):
        lines.append(f"Gate:  {result['currentGate']}")
    lines.append("")
    for n, step in enumerate(result["steps"], 1):
        lines.append(f"{n}. {step['text']}")
    for s in result.get("sessions", []):
        lines.append("")
        lines.append(f"{s['councilTitle']} ({' -> '.join(s['workOrder'])})")
        for m in s["convened"]:
            role = f" [{m['role']}]" if m["role"] != "specialist" else ""
            skills = f"  skills: {', '.join(map(skill_label, m['skills']))}" if m["skills"] else ""
            lines.append(f"  - {m['title']}{role}{skills}")
    if result.get("next"):
        lines.append("")
        lines.append("Next:")
        lines.extend(f"  {c}" for c in result["next"])
    return "\n".join(lines)


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m core.orchestrator.dispatch", description="Plan how Project Intelligence handles a request.")
    parser.add_argument("task", nargs="+", help="What you want done, in plain words")
    parser.add_argument("--json", action="store_true", help="Print the plan as JSON")
    parser.add_argument("--workspace", help="Project folder whose lifecycle state to read (default: the framework folder)")
    parser.add_argument("--full-roster", action="store_true", help="Convene every persona on the council (major redesigns only)")
    args = parser.parse_args(argv)
    try:
        result = dispatch(" ".join(args.task), Path(args.workspace) if args.workspace else None, args.full_roster)
    except ValueError as err:
        print(str(err), file=sys.stderr)
        return 2
    if args.json:
        result["summary"] = render_text(result)
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
