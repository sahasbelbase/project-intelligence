"""
Project Intelligence — Council Referee
The referee runs the council *process*; the model running each persona supplies the
*reasoning*. The referee:

- routes a task to a tier (0 answer, 1 specialist, 2 council, 3 cross-council),
- convenes a small, relevant set of personas (chair + critic + specialists),
- builds each persona's prompt from its registry definition,
- validates every round (blinding, challenge budget, responses to challenges),
- assembles a schema-valid decision brief with dissent preserved, and
- writes the session record to memory/council-briefs/ for the web app to display.

It never invents persona opinions. core/council/engine.py remains available as an
offline simulator for tests and demos; its output is labelled mode="simulated".
Zero external dependencies (Python standard library only).
"""

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.council.schema_lite import validate as validate_schema  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

RECOMMENDATIONS = ["Build", "Test further", "Pilot", "Pivot", "Defer", "Stop"]
CHALLENGE_TYPES = ["BLIND_SPOT", "OVERLOOKED_RISK", "COMPETING_PRIORITY", "UNEXAMINED_ASSUMPTION", "SCOPE_CREEP"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RESPONSES = ["ACCEPTED", "PARTIALLY_ACCEPTED", "REJECTED"]
BLINDING = ["separate-agents", "single-agent"]

_QUESTION = re.compile(r"^\s*(what|how|why|where|when|which|who|does|do|is|are|can|explain|describe|define|tell me|list)\b", re.I)
_ACTION = re.compile(r"\b(add|build|create|design|redesign|implement|change|fix|improve|refactor|migrate|launch|ship|replace|remove|overhaul|decide|plan|write|set up|make|choose|pick|check|estimate|compare|map|rotate|rewrite|convene|profile|version)\b", re.I)
# Signals that a change is broad enough for a council rather than one specialist.
_BROAD = re.compile(r"\b(redesign|overhaul|rethink|architecture|architect|strategy|council|trade-?off|decide|decision|whole|entire|migrate|irreversible|breaking change|rewrite|should we)\b", re.I)
# Signals that a request spans product, design and engineering (tier 3), together with
# strong matches in at least two councils.
_SCOPE = re.compile(r"\b(new feature|from scratch|end-to-end|launch (a|an|the) [\w\s-]*?(product|platform|service|app|portal)|new (product|module|platform)|\w+ module)\b", re.I)
_COUNCIL_NAMES = {
    "design": re.compile(r"\bdesign council\b", re.I),
    "development": re.compile(r"\b(development|dev|engineering) council\b", re.I),
    "product": re.compile(r"\bproduct council\b", re.I),
}
STRONG = 0.5  # minimum council score that counts as a real signal

_COUNCIL_HINTS = {
    "design": ["ui", "ux", "page", "screen", "layout", "visual", "design", "interface", "redesign", "look"],
    "development": ["code", "backend", "service", "server", "engine", "module", "implementation", "system"],
    "product": ["feature", "users", "customer", "should we", "value", "prioritize", "roadmap", "scope"],
}


class RefereeError(Exception):
    """Raised for invalid registry state or unusable session input."""


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s[:limit].rstrip("-")) or "decision"


def _contains(text: str, keyword: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?:s|es)?(?![a-z0-9])", text) is not None


class Referee:
    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root) if root else ROOT
        self.config = json.loads((self.root / "core" / "council" / "councils.json").read_text(encoding="utf-8"))
        self.limits = self.config["limits"]
        self.persona_schema = json.loads((self.root / "core" / "schemas" / "persona-definition.schema.json").read_text(encoding="utf-8"))
        self.brief_schema = json.loads((self.root / "core" / "schemas" / "council-brief.schema.json").read_text(encoding="utf-8"))
        self.personas: Dict[str, Dict[str, Any]] = {}
        self.persona_paths: Dict[str, Path] = {}
        self._load_personas()

    # ------------------------------------------------------------------ registry
    def _load_personas(self) -> None:
        for path in sorted((self.root / "core" / "council" / "personas").rglob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.personas[data["personaId"]] = data
            self.persona_paths[data["personaId"]] = path
        for path in sorted((self.root / "agents").rglob("agent.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            pid = data.get("personaId")
            if pid and pid not in self.personas:
                self.personas[pid] = data
                self.persona_paths[pid] = path

    def persona(self, persona_id: str) -> Dict[str, Any]:
        if persona_id not in self.personas:
            raise RefereeError(f"Unknown persona '{persona_id}'")
        return self.personas[persona_id]

    def council(self, council_id: str) -> Dict[str, Any]:
        councils = self.config["councils"]
        if council_id not in councils:
            raise RefereeError(f"Unknown council '{council_id}'. Known: {', '.join(councils)}")
        return councils[council_id]

    def validate_registry(self) -> List[str]:
        """Check every rostered persona exists, conforms to the schema, and has routing data."""
        errors: List[str] = []
        known_skills = {p.name for p in (self.root / "skills").iterdir() if p.is_dir()}
        vendor_dir = self.root / "vendor" / "skills"
        vendored = {p.name for p in vendor_dir.iterdir() if p.is_dir()} if vendor_dir.exists() else set()
        registry_path = vendor_dir / "registry.json"
        referenced = set()
        if registry_path.exists():
            referenced = {r["id"] for r in json.loads(registry_path.read_text(encoding="utf-8")).get("referenced", [])}

        for cid, council in self.config["councils"].items():
            roster = council["roster"]
            for role in ("chair", "critic"):
                if council[role] not in roster:
                    errors.append(f"{cid}: {role} '{council[role]}' is not on the roster")
            for pid in roster:
                if pid not in self.personas:
                    errors.append(f"{cid}: persona '{pid}' has no definition")
                    continue
                for err in validate_schema(self.personas[pid], self.persona_schema):
                    errors.append(f"{cid}/{pid}: {err}")
                for skill in council.get("skills", {}).get(pid, []):
                    if skill.startswith("vendor:") and skill[7:] not in vendored:
                        errors.append(f"{cid}/{pid}: vendored skill '{skill[7:]}' not found")
                    elif skill.startswith("ext:") and skill[4:] not in referenced:
                        errors.append(f"{cid}/{pid}: referenced skill '{skill[4:]}' not in registry")
                    elif ":" not in skill and skill not in known_skills:
                        errors.append(f"{cid}/{pid}: skill '{skill}' not found in skills/")
            for pid in council.get("routingKeywords", {}):
                if pid not in roster:
                    errors.append(f"{cid}: routing keywords for '{pid}', who is not on the roster")
        return errors

    # ------------------------------------------------------------------ routing
    def _keyword_owners(self) -> Dict[str, int]:
        """How many personas list each keyword; shared words carry less weight."""
        if not hasattr(self, "_owners"):
            owners: Dict[str, int] = {}
            for c in self.config["councils"].values():
                for words in c.get("routingKeywords", {}).values():
                    for w in set(words):
                        owners[w] = owners.get(w, 0) + 1
            self._owners = owners
        return self._owners

    def _weight(self, keyword: str) -> float:
        # Rare keywords and multi-word phrases are stronger evidence than common words.
        return (1.0 / self._keyword_owners().get(keyword, 1)) * (1.5 if " " in keyword else 1.0)

    def _keyword_hits(self, council_id: str, text: str) -> Dict[str, List[str]]:
        hits: Dict[str, List[str]] = {}
        for pid, words in self.council(council_id).get("routingKeywords", {}).items():
            matched = [w for w in words if _contains(text, w)]
            if matched:
                hits[pid] = matched
        return hits

    def persona_scores(self, task: str) -> List[Dict[str, Any]]:
        """Every persona with at least one keyword match, strongest first."""
        text = (task or "").lower()
        scored = []
        for cid in self.config["councils"]:
            for pid, matched in self._keyword_hits(cid, text).items():
                scored.append({"personaId": pid, "councilId": cid, "keywords": matched,
                               "score": round(sum(self._weight(w) for w in matched), 3)})
        roster_pos = {pid: i for c in self.config["councils"].values() for i, pid in enumerate(c["roster"])}
        return sorted(scored, key=lambda x: (-x["score"], -len(x["keywords"]), roster_pos.get(x["personaId"], 99)))

    def council_scores(self, task: str) -> Dict[str, float]:
        text = (task or "").lower()
        scores: Dict[str, float] = {}
        for item in self.persona_scores(task):
            scores[item["councilId"]] = scores.get(item["councilId"], 0.0) + item["score"]
        for cid, words in _COUNCIL_HINTS.items():
            hint = sum(0.3 for w in words if _contains(text, w))
            if hint:
                scores[cid] = scores.get(cid, 0.0) + hint
        return {k: round(v, 3) for k, v in scores.items()}

    def evidence(self, task: str, overridden: bool = False) -> Dict[str, Any]:
        """Why the router chose what it chose, and how sure it is.

        Confidence is low when nothing matched, when the top match rests on a single
        keyword (one word is weak evidence), or when the runner-up is close. The agent
        should then confirm the choice or override it with an explicit council or persona."""
        people = self.persona_scores(task)
        top = people[:3]
        if overridden:
            confidence = "high"
        elif not people:
            confidence = "low"
        else:
            margin = people[0]["score"] - (people[1]["score"] if len(people) > 1 else 0.0)
            enough = len(people[0]["keywords"]) >= 2 or people[0]["score"] >= 1.5
            confidence = "high" if enough and margin >= 0.3 else "low"
        return {"confidence": confidence,
                "evidence": [{"personaId": p["personaId"], "keywords": p["keywords"], "score": p["score"]} for p in top]}

    def classify(self, task: str, council: Optional[str] = None) -> Dict[str, Any]:
        """Decide how much process a task needs. Deterministic and explainable."""
        text = (task or "").lower()
        if council:
            self.council(council)
            return {"tier": 2, "councils": [council], "reason": f"The {council} council was requested."}
        named = [cid for cid, rx in _COUNCIL_NAMES.items() if rx.search(text)]
        if named:
            return {"tier": 2, "councils": [named[0]], "reason": f"The {named[0]} council was named in the request."}

        scores = self.council_scores(task)
        order = self.config["pipeline"]
        strong = sorted([c for c, v in scores.items() if v >= STRONG], key=lambda c: (-scores[c], order.index(c)))
        ranked = sorted(scores, key=lambda c: (-scores[c], order.index(c)))

        stripped = (task or "").strip()
        asks_for_work = re.search(r"\b(can|could|would) you\b|\bshould we\b|\bplease\b", text)
        is_question = _QUESTION.search(stripped) and (stripped.endswith("?") or not _ACTION.search(stripped))
        if is_question and not asks_for_work:
            return {"tier": 0, "councils": [], "reason": "A question that can be answered directly."}
        if _SCOPE.search(text) and len(strong) >= 2:
            return {"tier": 3, "councils": [c for c in order if c in self.config["councils"]],
                    "reason": "A new capability that spans product, design and engineering."}
        if _BROAD.search(text):
            if re.search(r"\bshould we\b", text) and "product" in self.config["councils"]:
                return {"tier": 2, "councils": ["product"], "reason": "A product decision between options."}
            if ranked:
                return {"tier": 2, "councils": [ranked[0]], "reason": f"Broad change within the {ranked[0]} council's area."}
        people = self.persona_scores(task)
        if people:
            return {"tier": 1, "councils": [people[0]["councilId"]], "reason": "A focused task one specialist can handle."}
        if ranked:
            return {"tier": 1, "councils": [ranked[0]], "reason": "A focused task; no specialist matched, so the council chair takes it."}
        return {"tier": 1, "councils": [], "reason": "No council matched; route to the most relevant single agent."}

    # ------------------------------------------------------------------ sessions
    def convene(self, council_id: str, task: str, size: Optional[int] = None,
                include: Optional[List[str]] = None, full_roster: bool = False) -> Dict[str, Any]:
        council = self.council(council_id)
        text = (task or "").lower()
        if full_roster:
            chosen = list(council["roster"])
        else:
            size = size or self.limits["defaultConveneSize"]
            if size > self.limits["maxConveneSize"]:
                raise RefereeError(f"Convene size {size} exceeds the limit of {self.limits['maxConveneSize']}; pass full_roster=True to opt in.")
            size = max(size, 2)
            chosen = [council["chair"], council["critic"]]
            for pid in include or []:
                if pid not in council["roster"]:
                    raise RefereeError(f"'{pid}' is not on the {council_id} roster")
                if pid not in chosen:
                    chosen.append(pid)
            hits = self._keyword_hits(council_id, text)
            ranked = sorted(hits, key=lambda p: (-len(hits[p]), council["roster"].index(p)))
            for pid in ranked:
                if len(chosen) >= size:
                    break
                if pid not in chosen:
                    chosen.append(pid)

        hits = self._keyword_hits(council_id, text)
        members = []
        for pid in chosen:
            p = self.persona(pid)
            role = "chair" if pid == council["chair"] else "critic" if pid == council["critic"] else "specialist"
            members.append({
                "personaId": pid,
                "title": p["title"],
                "role": role,
                "skills": council.get("skills", {}).get(pid, []),
                "matchedKeywords": hits.get(pid, []),
            })
        return {
            "sessionId": f"{council_id}-{_slug(task, 32)}",
            "councilId": council_id,
            "councilTitle": council["title"],
            "task": task,
            "createdAt": _now(),
            "workOrder": council.get("workOrder", []),
            "limits": {
                "maxChallengesPerPersona": self.limits["maxChallengesPerPersona"],
                "criticMinChallenges": self.limits["criticMinChallenges"],
            },
            "convened": members,
        }

    def session_for(self, council_id: str, task: str, persona_ids: List[str]) -> Dict[str, Any]:
        """Rebuild a session from the personas that actually took part (used by `record`)."""
        council = self.council(council_id)
        for role in ("chair", "critic"):
            if council[role] not in persona_ids:
                raise RefereeError(f"The {role} '{council[role]}' must take part in every {council_id} council session")
        extra = [p for p in persona_ids if p not in (council["chair"], council["critic"])]
        full = len(persona_ids) > self.limits["maxConveneSize"]
        session = self.convene(council_id, task, include=None if full else extra, size=None if full else max(len(persona_ids), 2), full_roster=full)
        session["convened"] = [m for m in session["convened"] if m["personaId"] in persona_ids]
        missing = set(persona_ids) - {m["personaId"] for m in session["convened"]}
        if missing:
            raise RefereeError(f"Not on the {council_id} roster: {', '.join(sorted(missing))}")
        return session

    def record(self, data: Dict[str, Any]) -> Path:
        """Validate a finished session described as JSON and save it. See `record` in the CLI help."""
        for key in ("councilId", "task", "convened", "round1", "challenges", "revisions", "synthesis"):
            if key not in data:
                raise RefereeError(f"Session file is missing '{key}'")
        session = self.session_for(data["councilId"], data["task"], list(data["convened"]))
        blinding = data.get("blinding", "single-agent")
        if blinding not in BLINDING:
            raise RefereeError(f"blinding must be one of {BLINDING}")
        rec = self.assemble(session, data["round1"], data["challenges"], data["revisions"], data["synthesis"],
                            mode=data.get("mode", "deliberated"), blinding=blinding, context=data.get("context"))
        return self.save(rec)

    def plan(self, task: str, full_roster: bool = False, council: Optional[str] = None,
             persona: Optional[str] = None, include: Optional[List[str]] = None) -> Dict[str, Any]:
        """Route a task. `council` or `persona` override the automatic choice (the agent states why);
        `include` adds named personas to the first council convened."""
        if persona and not council:
            owner = next((cid for cid, c in self.config["councils"].items() if persona in c["roster"]), None)
            if owner is None:
                raise RefereeError(f"Unknown persona '{persona}'")
            p = self.persona(persona)
            return {"task": task, "tier": 1, "councils": [owner], "reason": f"{p['title']} was requested.", "sessions": [],
                    "confidence": "high", "evidence": [],
                    "specialist": {"personaId": persona, "title": p["title"],
                                   "skills": self.council(owner).get("skills", {}).get(persona, [])}}
        route = self.classify(task, council=council)
        plan: Dict[str, Any] = {"task": task, **route, "sessions": [], **self.evidence(task, overridden=bool(council))}
        if route["tier"] >= 2:
            include = ([persona] if persona else []) + list(include or []) or None
            plan["sessions"] = [self.convene(c, task, include=include if c == route["councils"][0] else None, full_roster=full_roster)
                                for c in route["councils"]]
            if route["tier"] == 3:
                plan["qualityReview"] = self.config["quality"]["personas"]
        elif route["tier"] == 1 and route["councils"]:
            people = self.persona_scores(task)
            best = people[0]["personaId"] if people else self.council(route["councils"][0])["chair"]
            owner = people[0]["councilId"] if people else route["councils"][0]
            plan["specialist"] = {"personaId": best, "title": self.persona(best)["title"],
                                  "skills": self.council(owner).get("skills", {}).get(best, [])}
        return plan

    # ------------------------------------------------------------------ prompts
    def persona_prompt(self, session: Dict[str, Any], persona_id: str, round_number: int,
                       context: Optional[str] = None) -> str:
        """Build the instruction a model follows when speaking as one persona in one round.

        `context` is background every persona may see (facts about the project, or the
        previous council's hand-off in a tier 3 pipeline). It never contains other
        personas' Round 1 answers."""
        p = self.persona(persona_id)
        member = next((m for m in session["convened"] if m["personaId"] == persona_id), None)
        if member is None:
            raise RefereeError(f"'{persona_id}' is not convened in session {session['sessionId']}")
        boundaries = p.get("boundaries", {})
        prohibitions = boundaries.get("prohibitions", boundaries if isinstance(boundaries, list) else [])
        lines = [
            f"You are the {p['title']} on the {session['councilTitle']}.",
            f"Mission: {p['mission']}",
            f"Role in this session: {member['role']}.",
            "Expertise: " + "; ".join(p.get("expertise", [])),
            "Questions you characteristically ask: " + " | ".join(p.get("typicalQuestions", [])[:3]),
            "You must not: " + "; ".join(prohibitions),
            "Known failure modes to avoid in yourself: " + "; ".join(p.get("failureModes", [])),
        ]
        if member["skills"]:
            lines.append("Skills to apply: " + ", ".join(member["skills"]))
        lines.append(f"Task: {session['task']}")
        if context:
            lines.append("Background shared with every persona:\n" + context.strip())
        lines.append("Label every statement as VERIFIED_FACT (with source), ASSUMPTION, ESTIMATE or UNKNOWN. Never invent sources, quotes or statistics.")
        if round_number == 1:
            lines.append("Round 1 (blinded): give your own assessment without referring to other personas. Return JSON with personaId, recommendation (one of "
                         + ", ".join(RECOMMENDATIONS) + "), stance, keyArguments[], risks[], assumptions[], evidence[].")
        elif round_number == 2:
            lines.append(f"Round 2: read the Round 1 submissions and raise at most {session['limits']['maxChallengesPerPersona']} challenges, aimed at the claims you most disagree with. "
                         "Return JSON list of {challengerId, targetId, challengeType (" + ", ".join(CHALLENGE_TYPES) + "), severity, critique, counterProposal}.")
            if member["role"] == "critic":
                lines.append(f"As critic you must raise at least {session['limits']['criticMinChallenges']} challenge, and include the case for the simplest option.")
        elif round_number == 3:
            lines.append("Round 3: respond to every challenge aimed at you (ACCEPTED, PARTIALLY_ACCEPTED or REJECTED, with reason), then give revisedRecommendation, whatChanged[], whatRemainedUnchanged[].")
        elif round_number == 4:
            if member["role"] != "chair":
                raise RefereeError("Only the chair writes the Round 4 synthesis")
            lines.append("Round 4 (chair): synthesize a decision brief matching core/schemas/council-brief.schema.json. Keep disagreements that were not resolved in 'dissent'. Do not force consensus.")
        else:
            raise RefereeError("round_number must be 1, 2, 3 or 4")
        return "\n".join(lines)

    # ------------------------------------------------------------------ validation
    def _ids(self, session: Dict[str, Any]) -> List[str]:
        return [m["personaId"] for m in session["convened"]]

    def validate_round1(self, session: Dict[str, Any], submissions: List[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        ids = self._ids(session)
        seen = {s.get("personaId") for s in submissions}
        for pid in ids:
            if pid not in seen:
                errors.append(f"round1: no submission from '{pid}'")
        for s in submissions:
            pid = s.get("personaId")
            if pid not in ids:
                errors.append(f"round1: '{pid}' is not convened")
                continue
            if s.get("recommendation") not in RECOMMENDATIONS:
                errors.append(f"round1/{pid}: recommendation must be one of {RECOMMENDATIONS}")
            for field in ("keyArguments", "risks", "assumptions"):
                if not isinstance(s.get(field), list) or not s[field]:
                    errors.append(f"round1/{pid}: '{field}' must be a non-empty list")
            body = json.dumps({k: s.get(k) for k in ("stance", "keyArguments", "risks", "assumptions")}).lower()
            for other in ids:
                if other != pid and (other in body or self.persona(other)["title"].lower() in body):
                    errors.append(f"round1/{pid}: refers to '{other}'; Round 1 must be blinded")
        return errors

    def validate_challenges(self, session: Dict[str, Any], challenges: List[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        ids = self._ids(session)
        counts: Dict[str, int] = {}
        for i, c in enumerate(challenges):
            who, target = c.get("challengerId"), c.get("targetId")
            if who not in ids:
                errors.append(f"round2[{i}]: challenger '{who}' is not convened")
                continue
            if target not in ids:
                errors.append(f"round2[{i}]: target '{target}' is not convened")
            if who == target:
                errors.append(f"round2[{i}]: '{who}' cannot challenge itself in a multi-persona session")
            if c.get("challengeType") not in CHALLENGE_TYPES:
                errors.append(f"round2[{i}]: challengeType must be one of {CHALLENGE_TYPES}")
            if c.get("severity") not in SEVERITIES:
                errors.append(f"round2[{i}]: severity must be one of {SEVERITIES}")
            if not c.get("critique") or not c.get("counterProposal"):
                errors.append(f"round2[{i}]: critique and counterProposal are required")
            counts[who] = counts.get(who, 0) + 1
        cap = session["limits"]["maxChallengesPerPersona"]
        for who, n in counts.items():
            if n > cap:
                errors.append(f"round2: '{who}' raised {n} challenges; the budget is {cap}")
        critic = next(m["personaId"] for m in session["convened"] if m["role"] == "critic")
        if counts.get(critic, 0) < session["limits"]["criticMinChallenges"]:
            errors.append(f"round2: critic '{critic}' must raise at least {session['limits']['criticMinChallenges']} challenge")
        return errors

    def validate_revisions(self, session: Dict[str, Any], challenges: List[Dict[str, Any]],
                           revisions: List[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        by_persona = {r.get("personaId"): r for r in revisions}
        for pid in self._ids(session):
            r = by_persona.get(pid)
            if r is None:
                errors.append(f"round3: no revision from '{pid}'")
                continue
            if r.get("revisedRecommendation") not in RECOMMENDATIONS:
                errors.append(f"round3/{pid}: revisedRecommendation must be one of {RECOMMENDATIONS}")
            answered = {(a.get("challengerId"), a.get("response")) for a in r.get("responses", [])}
            for a in r.get("responses", []):
                if a.get("response") not in RESPONSES:
                    errors.append(f"round3/{pid}: response must be one of {RESPONSES}")
                if not a.get("reason"):
                    errors.append(f"round3/{pid}: every response needs a reason")
            received = [c for c in challenges if c.get("targetId") == pid]
            answered_by = {a for a, _ in answered}
            for c in received:
                if c.get("challengerId") not in answered_by:
                    errors.append(f"round3/{pid}: did not respond to the challenge from '{c.get('challengerId')}'")
        return errors

    def validate_brief(self, brief: Dict[str, Any]) -> List[str]:
        return validate_schema(brief, self.brief_schema)

    # ------------------------------------------------------------------ records
    def assemble(self, session: Dict[str, Any], round1: List[Dict[str, Any]], challenges: List[Dict[str, Any]],
                 revisions: List[Dict[str, Any]], synthesis: Dict[str, Any], mode: str = "deliberated",
                 blinding: str = "single-agent", context: Optional[str] = None) -> Dict[str, Any]:
        """Validate all rounds, add any unrecorded dissent, and return a session record."""
        errors = (self.validate_round1(session, round1) + self.validate_challenges(session, challenges)
                  + self.validate_revisions(session, challenges, revisions))
        brief = dict(synthesis)
        brief.setdefault("decisionId", f"dec-{_slug(session['task'])}")
        brief.setdefault("topic", session["task"])
        brief["participatingPersonas"] = self._ids(session)
        dissent = list(brief.get("dissent", []))
        recorded = {d.get("personaId") for d in dissent if isinstance(d, dict)}
        for r in revisions:
            pid = r.get("personaId")
            if r.get("revisedRecommendation") != brief.get("recommendation") and pid not in recorded:
                dissent.append({
                    "personaId": pid,
                    "objection": f"Recommends '{r.get('revisedRecommendation')}' instead of '{brief.get('recommendation')}'.",
                    "rationale": "; ".join(r.get("whatRemainedUnchanged", [])) or "Position held after the challenge round.",
                })
        brief["dissent"] = dissent
        errors += self.validate_brief(brief)
        if errors:
            raise RefereeError("Session record is invalid:\n- " + "\n- ".join(errors))
        return {
            "record": "council-session",
            "schemaVersion": "1.1.0",
            "mode": mode,
            # separate-agents: each persona ran as its own agent and Round 1 was truly blind.
            # single-agent: one agent wrote every persona, so blinding was not enforced.
            "blinding": blinding,
            "sessionId": session["sessionId"],
            "councilId": session["councilId"],
            "councilTitle": session["councilTitle"],
            "task": session["task"],
            "createdAt": session.get("createdAt") or _now(),
            "convened": session["convened"],
            **({"context": context.strip()} if context else {}),
            "rounds": {"independent": round1, "challenges": challenges, "revisions": revisions},
            "brief": brief,
        }

    def save(self, record: Dict[str, Any], directory: Optional[Path] = None) -> Path:
        # Records belong to the project being worked on (the current folder), not to the
        # framework's own install location, which a plugin update replaces.
        directory = Path(directory) if directory else Path.cwd() / "memory" / "council-briefs"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{record['brief']['decisionId']}.json"
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def validate_record(self, record: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for key in ("record", "mode", "sessionId", "councilId", "task", "convened", "rounds", "brief"):
            if key not in record:
                errors.append(f"record: missing '{key}'")
        if errors:
            return errors
        if record["mode"] not in ("deliberated", "simulated"):
            errors.append("record: mode must be 'deliberated' or 'simulated'")
        if record.get("blinding", "single-agent") not in BLINDING:
            errors.append(f"record: blinding must be one of {BLINDING}")
        session = {"sessionId": record["sessionId"], "convened": record["convened"],
                   "limits": {"maxChallengesPerPersona": self.limits["maxChallengesPerPersona"],
                              "criticMinChallenges": self.limits["criticMinChallenges"]}}
        rounds = record["rounds"]
        errors += self.validate_round1(session, rounds.get("independent", []))
        errors += self.validate_challenges(session, rounds.get("challenges", []))
        errors += self.validate_revisions(session, rounds.get("challenges", []), rounds.get("revisions", []))
        errors += self.validate_brief(record["brief"])
        return errors

    def sheet(self, council_id: str, task: str, include: Optional[List[str]] = None,
              context: Optional[str] = None, full_roster: bool = False) -> Dict[str, Any]:
        """Everything an orchestrator needs to start Round 1: the convened personas and
        each one's own prompt, to hand to separate agents at the same time."""
        session = self.convene(council_id, task, include=include, full_roster=full_roster)
        return {
            "councilId": council_id,
            "task": task,
            "convened": [m["personaId"] for m in session["convened"]],
            "chair": next(m["personaId"] for m in session["convened"] if m["role"] == "chair"),
            "critic": next(m["personaId"] for m in session["convened"] if m["role"] == "critic"),
            "round1": [{"personaId": m["personaId"], "title": m["title"], "role": m["role"],
                        "prompt": self.persona_prompt(session, m["personaId"], 1, context)} for m in session["convened"]],
        }

    def find_record(self, decision_id: str) -> Dict[str, Any]:
        path = Path.cwd() / "memory" / "council-briefs" / f"{decision_id}.json"
        if not path.exists():
            raise RefereeError(f"No saved decision '{decision_id}' in {path.parent}")
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def handoff_text(record: Dict[str, Any]) -> str:
        """Hand-off as plain text, ready to pass as --context to the next council."""
        h = Referee.handoff(record)
        def items(xs):
            return "; ".join(x if isinstance(x, str) else (x.get("description") or x.get("objection") or json.dumps(x)) for x in xs) or "none"
        return (f"The {h['fromCouncil']} council decided '{h['recommendation']}' ({h['decisionId']}). "
                f"In scope: {items(h['mvpScope'])}. Out of scope: {items(h['excludedScope'])}. "
                f"Assumptions: {items(h['assumptions'])}. Risks: {items(h['risks'])}. Open dissent: {items(h['openDissent'])}.")

    @staticmethod
    def handoff(record: Dict[str, Any]) -> Dict[str, Any]:
        """Compact summary passed to the next council in a tier 3 pipeline."""
        b = record["brief"]
        return {
            "fromCouncil": record["councilId"],
            "decisionId": b["decisionId"],
            "recommendation": b["recommendation"],
            "mvpScope": b["mvpScope"],
            "excludedScope": b["excludedScope"],
            "assumptions": b["assumptions"],
            "risks": b["risks"],
            "openDissent": b["dissent"],
        }


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m core.council.referee", description="Plan and validate council sessions.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_plan = sub.add_parser("plan", help="Route a task and convene councils")
    p_plan.add_argument("task")
    p_plan.add_argument("--full-roster", action="store_true")
    p_prompt = sub.add_parser("prompt", help="Print a persona prompt for a planned session")
    p_prompt.add_argument("council")
    p_prompt.add_argument("persona")
    p_prompt.add_argument("round", type=int)
    p_prompt.add_argument("task")
    p_prompt.add_argument("--context", help="File with background every persona may see (for example a hand-off)")
    p_sheet = sub.add_parser("sheet", help="Print every convened persona's Round 1 prompt as JSON, for separate agents")
    p_sheet.add_argument("council")
    p_sheet.add_argument("task")
    p_sheet.add_argument("--include", action="append", default=[], help="Persona id to convene (repeatable)")
    p_sheet.add_argument("--context", help="File with background every persona may see")
    p_sheet.add_argument("--full-roster", action="store_true")
    p_handoff = sub.add_parser("handoff", help="Print a saved decision as context for the next council")
    p_handoff.add_argument("decision_id")
    p_record = sub.add_parser("record", help="Validate a finished session JSON file and save it to memory/council-briefs/")
    p_record.add_argument("file", help="JSON with councilId, task, convened (persona ids), round1, challenges, revisions, synthesis")
    sub.add_parser("check", help="Validate the persona registry and every saved record")
    sub.add_parser("list", help="List councils and their rosters")
    args = parser.parse_args(argv)

    ref = Referee()
    if args.cmd == "plan":
        print(json.dumps(ref.plan(args.task, full_roster=args.full_roster), indent=2))
    elif args.cmd == "prompt":
        session = ref.convene(args.council, args.task, include=[args.persona])
        context = Path(args.context).read_text(encoding="utf-8") if args.context else None
        print(ref.persona_prompt(session, args.persona, args.round, context))
    elif args.cmd == "sheet":
        context = Path(args.context).read_text(encoding="utf-8") if args.context else None
        print(json.dumps(ref.sheet(args.council, args.task, include=args.include, context=context,
                                   full_roster=args.full_roster), indent=2))
    elif args.cmd == "handoff":
        try:
            print(ref.handoff_text(ref.find_record(args.decision_id)))
        except RefereeError as err:
            print(str(err), file=sys.stderr)
            return 1
    elif args.cmd == "record":
        try:
            path = ref.record(json.loads(Path(args.file).read_text(encoding="utf-8")))
        except (RefereeError, json.JSONDecodeError, OSError) as err:
            print(f"Not saved: {err}", file=sys.stderr)
            return 1
        print(f"Saved {path}")
    elif args.cmd == "list":
        for cid, c in ref.config["councils"].items():
            print(f"{c['title']} ({len(c['roster'])}): chair {c['chair']}, critic {c['critic']}")
            for pid in c["roster"]:
                print(f"  - {pid}: {ref.persona(pid)['title']}")
    elif args.cmd == "check":
        errors = ref.validate_registry()
        briefs = Path.cwd() / "memory" / "council-briefs"
        for path in sorted(briefs.glob("*.json")) if briefs.exists() else []:
            errors += [f"{path.name}: {e}" for e in ref.validate_record(json.loads(path.read_text(encoding="utf-8")))]
        if errors:
            print("\n".join(errors))
            return 1
        print(f"OK: {len(ref.personas)} personas, {len(ref.config['councils'])} councils, records valid.")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
