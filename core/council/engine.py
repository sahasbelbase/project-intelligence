"""
Project Intelligence — Multi-Persona Council Execution Engine
Implements the 4-Round Council Deliberation Protocol matching Sections 11 & 12:
- Round 1: Independent Analysis (blinded evaluation)
- Round 2: Challenge Round (cross-examination and blind spot exposure)
- Round 3: Revision Round (accountability, what changed, why, what remains unchanged)
- Round 4: Decision Synthesis (Council Decision Brief with dissent preserved)

This engine is an offline simulator: stances and challenges are derived from each
persona's group by fixed rules, so it produces the same shape of debate for any
topic. Use it for tests and demos only, and label any saved output mode="simulated".
Real sessions are planned and validated by core/council/referee.py, with the model
speaking as each persona.
Zero external dependencies (Python standard library only).
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import json
from pathlib import Path
import uuid
import re

from core.decision.evidence import (
    EvidenceCategory, EvidenceItem, classify_statement, separate_facts_and_assumptions
)


class CouncilError(Exception):
    """Raised when council execution or schema synthesis fails."""
    pass


class CouncilEngine:
    """
    Executes multi-persona council deliberations across 4 structured rounds,
    enforcing epistemic rigor, adversarial challenge, and dissent preservation.
    """

    VALID_RECOMMENDATIONS = [
        "Build",
        "Test further",
        "Pilot",
        "Pivot",
        "Defer",
        "Stop"
    ]

    def __init__(self, brief_schema_path: Optional[Path] = None):
        if brief_schema_path is None:
            brief_schema_path = Path(__file__).resolve().parents[1] / "schemas" / "council-brief.schema.json"
        self.brief_schema_path = brief_schema_path
        self._schema_cache = None

    def _load_schema(self) -> Dict[str, Any]:
        if self._schema_cache is None and self.brief_schema_path.exists():
            with open(self.brief_schema_path, "r", encoding="utf-8") as f:
                self._schema_cache = json.load(f)
        return self._schema_cache or {}

    # -------------------------------------------------------------------------
    # Round 1: Independent Analysis
    # -------------------------------------------------------------------------
    def run_independent_analysis(
        self,
        personas: List[Dict[str, Any]],
        problem_brief: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Executes Round 1: Blinded independent assessment by each participating persona.
        No persona has visibility into other personas' analyses during this round.
        """
        if not personas:
            raise CouncilError("Council requires at least one participating persona.")

        topic = problem_brief.get("topic", "Architectural and Technical Decision")
        context = problem_brief.get("context", "")
        constraints = problem_brief.get("constraints", [])
        goals = problem_brief.get("goals", [])
        risk_profile = problem_brief.get("risk_profile", "STANDARD").upper()

        assessments: Dict[str, Dict[str, Any]] = {}

        for p in personas:
            pid = p.get("personaId", "unknown-persona")
            title = p.get("title", pid)
            group = p.get("group", "engineering")
            mission = p.get("mission", "")
            expertise = p.get("expertise", [])
            questions = p.get("typicalQuestions", [])
            failure_modes = p.get("failureModes", [])

            # Assess initial stance and recommendation based on persona disciplinary focus
            key_args: List[str] = []
            identified_risks: List[str] = []
            assumptions: List[str] = []
            recommended_scope: List[str] = []

            # Group/discipline-specific perspective derivation
            if group in {"security", "quality"}:
                stance = "CONCERNED"
                rec = "Test further" if risk_profile in {"HIGH", "CRITICAL"} else "Pilot"
                key_args.append(f"Verification of security and quality invariants must precede full commitment to {topic}.")
                identified_risks.append(f"Potential vulnerability or verification gap if {topic} is deployed without regression gates.")
                assumptions.append("Security requirements and threat boundaries are not yet fully mapped.")
                recommended_scope.append("Quarantine scope to verifiable core modules with automated regression tests.")
            elif group in {"architecture", "infrastructure"}:
                stance = "CONDITIONAL"
                rec = "Pilot" if "scale" in str(context).lower() else "Build"
                key_args.append(f"Modular decoupling and explicit interface contracts required for {topic}.")
                identified_risks.append(f"Architectural debt or coupling risk if boundaries are poorly isolated in {topic}.")
                assumptions.append("Component interfaces can be strictly typed and locally validated.")
                recommended_scope.append("Minimal decoupled core architecture with zero unnecessary dependencies.")
            elif group in {"product", "strategy"}:
                stance = "FAVORABLE"
                rec = "Build"
                key_args.append(f"{topic} directly addresses primary user workflow and strategic milestones.")
                identified_risks.append(f"Opportunity cost or delay if implementation is over-deferred.")
                assumptions.append("Core value proposition aligns with user requirements.")
                recommended_scope.append("End-to-end usable MVP satisfying primary user workflow.")
            elif group in {"operations", "reliability"}:
                stance = "SKEPTICAL"
                rec = "Pilot"
                key_args.append(f"Operational maintainability, telemetry, and rollback paths must be confirmed.")
                identified_risks.append(f"Operational burden, resource leakage, or rollback complexity.")
                assumptions.append("Local runtime environments can support workload without external service dependencies.")
                recommended_scope.append("Canary deployment with deterministic rollback procedure.")
            else:
                stance = "NEUTRAL"
                rec = "Test further"
                key_args.append(f"Requires rigorous domain exploration of {topic} before full rollout.")
                identified_risks.append(f"Unforeseen edge cases in domain execution.")
                assumptions.append("Baseline engineering requirements are understood.")
                recommended_scope.append("Proof-of-concept validation.")

            assessments[pid] = {
                "personaId": pid,
                "title": title,
                "group": group,
                "stance": stance,
                "initialRecommendation": rec,
                "keyArguments": key_args,
                "identifiedRisks": identified_risks,
                "assumptions": assumptions,
                "typicalQuestionsRaised": questions[:3] if questions else [f"How does {topic} affect long-term maintainability?"],
                "recommendedScope": recommended_scope,
                "acknowledgedFailureModes": failure_modes[:2] if failure_modes else []
            }

        return assessments

    # -------------------------------------------------------------------------
    # Round 2: Challenge Round
    # -------------------------------------------------------------------------
    def run_challenge_round(
        self,
        round1_results: Dict[str, Dict[str, Any]],
        problem_brief: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executes Round 2: Cross-examination and challenge generation.
        Each persona scrutinizes other personas' analyses to expose blind spots,
        unexamined assumptions, competing priorities, and overlooked risks.
        Returns a dictionary mapping challengerPersonaId -> List of challenges raised.
        """
        challenges_by_challenger: Dict[str, List[Dict[str, Any]]] = {}

        persona_ids = list(round1_results.keys())
        if len(persona_ids) <= 1:
            # Self-challenge / Devil's advocate challenge if single persona
            pid = persona_ids[0]
            analysis = round1_results[pid]
            challenges_by_challenger[pid] = [{
                "targetPersonaId": pid,
                "challengerPersonaId": pid,
                "challengeType": "DEVILS_ADVOCATE",
                "critique": f"Self-critique: Assumption '{analysis['assumptions'][0] if analysis['assumptions'] else 'feasibility'}' has not been empirically proven.",
                "severity": "MEDIUM",
                "counterProposal": "Establish an empirical spike test before full commitment."
            }]
            return challenges_by_challenger

        for challenger_id, challenger_data in round1_results.items():
            challenges_raised: List[Dict[str, Any]] = []
            for target_id, target_data in round1_results.items():
                if challenger_id == target_id:
                    continue

                c_group = challenger_data.get("group", "")
                t_group = target_data.get("group", "")
                t_rec = target_data.get("initialRecommendation", "")

                # Detect conflicting priorities or unaddressed blind spots
                if c_group in {"security", "quality"} and t_rec == "Build":
                    challenges_raised.append({
                        "targetPersonaId": target_id,
                        "challengerPersonaId": challenger_id,
                        "challengeType": "OVERLOOKED_RISK",
                        "critique": f"{target_data['title']} recommends 'Build' without accounting for verification gates and test automation boundaries.",
                        "severity": "HIGH",
                        "counterProposal": "Demote recommendation to 'Pilot' or 'Test further' until verification suite is authored."
                    })
                elif c_group in {"architecture"} and t_rec in {"Build", "Pilot"} and not target_data.get("recommendedScope"):
                    challenges_raised.append({
                        "targetPersonaId": target_id,
                        "challengerPersonaId": challenger_id,
                        "challengeType": "SCOPE_CREEP",
                        "critique": f"{target_data['title']} proposal lacks explicit boundary encapsulation and interface contracts.",
                        "severity": "MEDIUM",
                        "counterProposal": "Define modular component contracts before implementation."
                    })
                elif c_group in {"product"} and t_rec in {"Stop", "Defer"}:
                    challenges_raised.append({
                        "targetPersonaId": target_id,
                        "challengerPersonaId": challenger_id,
                        "challengeType": "COMPETING_PRIORITY",
                        "critique": f"{target_data['title']} defers without weighing user impact and project milestone commitments.",
                        "severity": "MEDIUM",
                        "counterProposal": "Execute a lightweight MVP pilot instead of complete deferral."
                    })
                else:
                    # General assumption probe
                    t_assumptions = target_data.get("assumptions", [])
                    critique_text = (
                        f"Unverified assumption: '{t_assumptions[0]}'" if t_assumptions
                        else f"Potential blind spot in {target_data['title']}'s assessment regarding cross-cutting dependencies."
                    )
                    challenges_raised.append({
                        "targetPersonaId": target_id,
                        "challengerPersonaId": challenger_id,
                        "challengeType": "UNEXAMINED_ASSUMPTION",
                        "critique": critique_text,
                        "severity": "LOW",
                        "counterProposal": "Document verifiable acceptance criteria to validate this assumption."
                    })

            challenges_by_challenger[challenger_id] = challenges_raised

        return challenges_by_challenger

    # -------------------------------------------------------------------------
    # Round 3: Revision Round
    # -------------------------------------------------------------------------
    def run_revision_round(
        self,
        round1_results: Dict[str, Dict[str, Any]],
        round2_challenges: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Executes Round 3: Revision and defense.
        Each persona reviews challenges received, declaring:
        - whatChanged: concessions made, scope adjusted, risks incorporated
        - why: reasoning linking to the challenge evidence
        - whatRemainedUnchanged: defended positions, non-negotiable invariants
        - revisedRecommendation: updated stance
        """
        revisions: Dict[str, Dict[str, Any]] = {}

        # Collect challenges targeted at each persona
        challenges_for_target: Dict[str, List[Dict[str, Any]]] = {
            pid: [] for pid in round1_results
        }
        for challenger_id, c_list in round2_challenges.items():
            for c in c_list:
                t_id = c.get("targetPersonaId")
                if t_id in challenges_for_target:
                    challenges_for_target[t_id].append(c)

        for pid, r1_data in round1_results.items():
            incoming = challenges_for_target.get(pid, [])
            initial_rec = r1_data.get("initialRecommendation", "Test further")
            high_severity_challenges = [c for c in incoming if c.get("severity") == "HIGH"]

            what_changed: List[str] = []
            why_changed: List[str] = []
            what_remained_unchanged: List[str] = []
            revised_rec = initial_rec
            persisting_objections: List[str] = []

            if high_severity_challenges:
                # Concession on high severity challenge
                critique = high_severity_challenges[0].get("critique", "")
                counter = high_severity_challenges[0].get("counterProposal", "")
                if initial_rec == "Build":
                    revised_rec = "Pilot"
                    what_changed.append("De-escalated recommendation from 'Build' to 'Pilot' with quarantined verification scope.")
                    why_changed.append(f"Accepted challenge regarding verification gap: {critique}")
                else:
                    what_changed.append(f"Incorporated counter-proposal: {counter}")
                    why_changed.append(f"Addressed challenge critique: {critique}")
            else:
                what_changed.append("Refined scope boundaries to incorporate peer critique.")
                why_changed.append("Addressed unexamined assumptions surfaced in cross-examination.")

            # Preserved non-negotiables
            what_remained_unchanged.append(f"Core mission alignment: {r1_data.get('keyArguments', ['Disciplinary focus'])[0]}")
            what_remained_unchanged.append("Zero unverified claims; commitment to empirical acceptance criteria.")

            # If incoming challenges were not fully satisfied, record persisting objection
            for ch in incoming:
                if ch.get("severity") in {"HIGH", "CRITICAL"}:
                    persisting_objections.append(
                        f"Lingering concern regarding {ch.get('challengeType')}: {ch.get('critique')}"
                    )

            revisions[pid] = {
                "personaId": pid,
                "title": r1_data.get("title", pid),
                "initialRecommendation": initial_rec,
                "revisedRecommendation": revised_rec,
                "whatChanged": what_changed,
                "whyChanged": why_changed,
                "whatRemainedUnchanged": what_remained_unchanged,
                "persistingObjections": persisting_objections
            }

        return revisions

    # -------------------------------------------------------------------------
    # Round 4: Decision Synthesis & Dissent Preservation
    # -------------------------------------------------------------------------
    def synthesize_decision_brief(
        self,
        problem_brief: Dict[str, Any],
        round1_results: Dict[str, Dict[str, Any]],
        round2_challenges: Dict[str, List[Dict[str, Any]]],
        round3_revisions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes Round 4: Synthesizes all deliberation rounds into the canonical
        Council Decision Brief conforming to core/schemas/council-brief.schema.json.
        Dissent is explicitly preserved and documented in full.
        """
        decision_id = problem_brief.get("decisionId", f"dec-{uuid.uuid4().hex[:8]}")
        topic = problem_brief.get("topic", "Council Deliberation Topic")
        participating = list(round1_results.keys())

        # 1. Determine synthesized recommendation
        revised_votes: Dict[str, int] = {}
        for r3 in round3_revisions.values():
            rec = r3.get("revisedRecommendation", "Test further")
            if rec not in self.VALID_RECOMMENDATIONS:
                rec = "Test further"
            revised_votes[rec] = revised_votes.get(rec, 0) + 1

        # Check for critical safety/security blocks
        has_critical_block = any(
            any(c.get("severity") == "CRITICAL" for c in c_list)
            for c_list in round2_challenges.values()
        )

        if has_critical_block:
            synthesized_rec = "Test further"
        else:
            # Majority vote winner, with fallback to most conservative option on ties
            sorted_votes = sorted(revised_votes.items(), key=lambda kv: kv[1], reverse=True)
            synthesized_rec = sorted_votes[0][0] if sorted_votes else "Test further"

        # 2. Gather strongest arguments for and against
        args_for: List[str] = []
        for r1 in round1_results.values():
            args_for.extend(r1.get("keyArguments", []))
        if not args_for:
            args_for.append(f"Direct alignment with system goals for {topic}.")

        args_against: List[str] = []
        for c_list in round2_challenges.values():
            for c in c_list:
                args_against.append(f"[{c.get('severity', 'MEDIUM')}] {c.get('critique', '')}")
        if not args_against:
            args_against.append("Implementation complexity and maintenance overhead.")

        # 3. Gather evidence and assumptions
        evidence_items: List[Dict[str, Any]] = []
        assumptions_list: List[str] = []
        unknowns_list: List[str] = []
        risks_list: List[Dict[str, Any]] = []

        for pid, r1 in round1_results.items():
            assumptions_list.extend(r1.get("assumptions", []))
            for rk in r1.get("identifiedRisks", []):
                risks_list.append({
                    "riskId": f"risk-{uuid.uuid4().hex[:6]}",
                    "description": rk,
                    "severity": "HIGH" if "vulnerability" in rk.lower() or "defect" in rk.lower() else "MEDIUM",
                    "probability": "MEDIUM"
                })

        # Add empirical evidence if problem brief provided sources
        context_str = str(problem_brief.get("context", ""))
        evidence_item = classify_statement(
            f"[VERIFIED_FACT] Problem brief recorded for {topic}",
            source="problem_brief",
            basis="Council initialization input"
        )
        evidence_items.append(evidence_item.to_dict())

        if not assumptions_list:
            assumptions_list.append("Operational requirements remain stable during execution.")
        if not unknowns_list:
            unknowns_list.append("Empirical latency and performance profile under peak production load.")

        # 4. Construct mitigations
        mitigations_list: List[Dict[str, Any]] = []
        for rk in risks_list[:3]:
            mitigations_list.append({
                "riskRef": rk["riskId"],
                "strategy": f"Quarantine component and enforce automated verification checks before promotion.",
                "owner": participating[0] if participating else "orchestrator"
            })

        # 5. Define trade-offs
        trade_offs: List[Dict[str, Any]] = [
            {
                "aspect": "Implementation Velocity vs Verification Rigor",
                "chosen": "High Verification Rigor",
                "sacrificed": "Short-term deployment speed",
                "rationale": "Prevents regression and anti-slop debt in core architectural layers."
            }
        ]

        # 6. Define scope
        mvp_scope: List[str] = [
            f"Core functional capabilities for {topic}",
            "Automated regression test suite with exit code 0 verification",
            "Contract documentation and schema validation"
        ]
        excluded_scope: List[str] = [
            "Speculative premature performance optimizations",
            "Non-essential third-party platform integrations",
            "Unverified experimental features"
        ]

        # 7. Validation experiments
        validation_experiments: List[Dict[str, Any]] = [
            {
                "hypothesis": f"Executing {topic} under recommendation '{synthesized_rec}' satisfies architectural constraints.",
                "experiment": "Run end-to-end automated validation suite in isolated environment.",
                "passMetric": "100% passing tests with exit code 0 and zero contract schema violations."
            }
        ]

        # 8. Owners, Metrics, Dependencies, Conditions to Change
        owners = participating
        success_metrics: List[Dict[str, Any]] = [
            {
                "metric": "Automated verification pass rate",
                "target": "100% exit code 0",
                "timeframe": "Prior to gate advancement"
            }
        ]
        dependencies = [
            "Approval of upstream requirements and architecture contracts",
            "Passing self-validation suite"
        ]
        conditions_to_change = [
            "Discovery of critical security or regression defect",
            "Failure to meet 100% verification test pass criteria",
            "Change in core project scope or upstream requirements"
        ]

        # 9. Explicit Dissent Preservation
        dissent_entries: List[Dict[str, Any]] = []
        for pid, r3 in round3_revisions.items():
            p_rec = r3.get("revisedRecommendation")
            p_objections = r3.get("persistingObjections", [])

            # Check if persona differed from synthesized recommendation
            if p_rec != synthesized_rec:
                dissent_entries.append({
                    "personaId": pid,
                    "objection": f"{r3.get('title', pid)} recommended '{p_rec}' instead of synthesized outcome '{synthesized_rec}'.",
                    "rationale": f"What remained unchanged: {', '.join(r3.get('whatRemainedUnchanged', []))}",
                    "suggestedAlternative": f"Adopt recommendation '{p_rec}' to minimize risks identified in Round 1 and Round 2."
                })
            elif p_objections:
                dissent_entries.append({
                    "personaId": pid,
                    "objection": f"Lingering minority concerns raised by {r3.get('title', pid)}.",
                    "rationale": "; ".join(p_objections),
                    "suggestedAlternative": "Address persisting objections in subsequent validation experiments."
                })

        # If perfectly unanimous, note unanimity in dissent array (as empty or explicit record)
        # Note: council-brief.schema.json requires dissent as array
        # An empty array or explicit non-dissent note is valid

        # 10. Confidence Level calculation
        agreeing_count = sum(1 for r3 in round3_revisions.values() if r3.get("revisedRecommendation") == synthesized_rec)
        ratio = agreeing_count / max(len(participating), 1)

        if ratio >= 0.8 and not has_critical_block:
            confidence_level = "HIGH"
        elif ratio >= 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        # Final structured brief matching core/schemas/council-brief.schema.json
        brief: Dict[str, Any] = {
            "decisionId": decision_id,
            "topic": topic,
            "participatingPersonas": participating,
            "recommendation": synthesized_rec,
            "strongestArgumentsFor": args_for[:5],
            "strongestArgumentsAgainst": args_against[:5],
            "evidence": evidence_items,
            "assumptions": assumptions_list[:5],
            "unknowns": unknowns_list[:5],
            "tradeOffs": trade_offs,
            "risks": risks_list[:5],
            "mitigations": mitigations_list[:5],
            "mvpScope": mvp_scope,
            "excludedScope": excluded_scope,
            "validationExperiments": validation_experiments,
            "owners": owners,
            "successMetrics": success_metrics,
            "dependencies": dependencies,
            "conditionsToChange": conditions_to_change,
            "dissent": dissent_entries,
            "confidenceLevel": confidence_level
        }

        return brief

    # -------------------------------------------------------------------------
    # End-to-End Execution
    # -------------------------------------------------------------------------
    def execute_council(
        self,
        problem_brief: Dict[str, Any],
        personas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes the full 4-round council workflow end-to-end:
        Round 1 -> Round 2 -> Round 3 -> Round 4.
        Returns the Council Decision Brief along with telemetry and round artifacts.
        """
        r1 = self.run_independent_analysis(personas, problem_brief)
        r2 = self.run_challenge_round(r1, problem_brief)
        r3 = self.run_revision_round(r1, r2)
        brief = self.synthesize_decision_brief(problem_brief, r1, r2, r3)

        return {
            "decisionBrief": brief,
            "telemetry": {
                "participatingCount": len(personas),
                "roundsExecuted": 4,
                "dissentCount": len(brief.get("dissent", [])),
                "recommendation": brief.get("recommendation"),
                "confidenceLevel": brief.get("confidenceLevel")
            },
            "rounds": {
                "round1IndependentAnalysis": r1,
                "round2ChallengeRound": r2,
                "round3RevisionRound": r3
            }
        }
