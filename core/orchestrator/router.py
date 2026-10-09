"""
Project Intelligence — Universal Intent Parser & Task Router
Implements intent categorization, domain classification, and execution planning matching Sections 3, 14, & 15.
Enforces the core architectural principle: "Minimum necessary complexity, maximum useful expertise".
Zero external dependencies (Python standard library only).
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import re


class IntentCategory(str, Enum):
    """Canonical categories of user intents and task archetypes."""
    SINGLE_PERSONA = "SINGLE_PERSONA"
    SEQUENTIAL_WORKFLOW = "SEQUENTIAL_WORKFLOW"
    COUNCIL = "COUNCIL"
    VERIFICATION = "VERIFICATION"
    REVIEW = "REVIEW"


class TaskRouter:
    """
    Parses user requests and constructs deterministic execution plans,
    selecting optimal personas and skills while strictly avoiding over-engineering.
    """

    # Available framework personas with capability profiles
    PERSONA_CATALOG: Dict[str, Dict[str, Any]] = {
        "orchestrator": {
            "title": "Lead Coordinator & Gatekeeper",
            "group": "governance",
            "skills": ["phase-planning", "failure-recovery-and-improvement"]
        },
        "discovery": {
            "title": "Requirements & Discovery Specialist",
            "group": "discovery",
            "skills": ["project-discovery", "existing-project-analysis"]
        },
        "architecture": {
            "title": "Systems Architecture Specialist",
            "group": "architecture",
            "skills": ["architecture-and-contracts", "existing-project-analysis"]
        },
        "design": {
            "title": "Design System & UI/UX Specialist",
            "group": "design",
            "skills": ["design-discovery", "design-system-engineering"]
        },
        "planning": {
            "title": "Phase & Task Planning Engineer",
            "group": "planning",
            "skills": ["phase-planning"]
        },
        "implementation": {
            "title": "Controlled Implementation Engineer",
            "group": "engineering",
            "skills": ["controlled-implementation", "cross-platform-adaptation"]
        },
        "verification": {
            "title": "Testing & Verification Engineer",
            "group": "quality",
            "skills": ["testing-and-verification"]
        },
        "independent-review": {
            "title": "Adversarial Quality & Review Auditor",
            "group": "quality",
            "skills": ["independent-review"]
        },
        "documentation-and-memory": {
            "title": "Handoff & Memory Reconciliation Specialist",
            "group": "documentation",
            "skills": ["documentation-and-handoff"]
        },
        "legacy-analysis": {
            "title": "Legacy Code & Knowledge Base Specialist",
            "group": "analysis",
            "skills": ["legacy-codebase-knowledge-base", "existing-project-analysis"]
        },
        "modernization-architect": {
            "title": "Systems Modernization & Refactoring Specialist",
            "group": "analysis",
            "skills": ["safe-refactoring-and-migration", "controlled-implementation"]
        },
        "security-auditor": {
            "title": "Application Security & Hardening Specialist",
            "group": "security",
            "skills": ["security-audit-and-hardening", "independent-review"]
        },
        "database-migration-specialist": {
            "title": "Database Migration & Schema Evolution Specialist",
            "group": "engineering",
            "skills": ["database-migration-and-schema-evolution", "architecture-and-contracts"]
        },
        "api-contract-engineer": {
            "title": "API Protocols & Contract Specialist",
            "group": "architecture",
            "skills": ["api-contract-and-openapi-spec", "architecture-and-contracts"]
        },
        "devops-automation-engineer": {
            "title": "CI/CD & DevOps Automation Engineer",
            "group": "operations",
            "skills": ["ci-cd-pipeline-engineering", "testing-and-verification"]
        },
        "performance-engineer": {
            "title": "Runtime Performance & Scalability Specialist",
            "group": "quality",
            "skills": ["runtime-performance-profiling", "testing-and-verification"]
        },
        "web-scraping-researcher": {
            "title": "Web Scraping & Online Intelligence Specialist",
            "group": "research",
            "skills": ["web-scraping-and-research", "project-discovery"]
        },
        "open-design-architect": {
            "title": "Open Design & Rapid Prototyping Architect",
            "group": "design",
            "skills": ["open-design-system-and-prototyping", "design-system-engineering"]
        }
    }

    # Available skills
    ALL_SKILLS: List[str] = [
        "project-discovery",
        "existing-project-analysis",
        "legacy-codebase-knowledge-base",
        "safe-refactoring-and-migration",
        "security-audit-and-hardening",
        "database-migration-and-schema-evolution",
        "api-contract-and-openapi-spec",
        "ci-cd-pipeline-engineering",
        "runtime-performance-profiling",
        "web-scraping-and-research",
        "open-design-system-and-prototyping",
        "design-discovery",
        "design-system-engineering",
        "architecture-and-contracts",
        "phase-planning",
        "controlled-implementation",
        "testing-and-verification",
        "independent-review",
        "documentation-and-handoff",
        "cross-platform-adaptation",
        "failure-recovery-and-improvement"
    ]

    def parse_user_intent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parses user intent from query text, identifying domain, complexity score,
        risk level, target personas, required skills, and the primary IntentCategory.
        """
        clean = (query or "").strip()
        lower = clean.lower()

        # 1. Detect Domain
        domains: List[str] = []
        if re.search(r"\b(security|vulnerability|auth|jwt|credential|permission|threat)\b", lower):
            domains.append("security")
        if re.search(r"\b(arch|architecture|adr|system design|schema|interface|modular|coupling)\b", lower):
            domains.append("architecture")
        if re.search(r"\b(ui|ux|css|visual|layout|design system|responsive|breakpoint)\b", lower):
            domains.append("design")
        if re.search(r"\b(test|testing|assert|unittest|pytest|verify|verification|exit code|pass rate)\b", lower):
            domains.append("testing")
        if re.search(r"\b(review|audit|adversarial|inspect|pr review|code review|anti-slop)\b", lower):
            domains.append("review")
        if re.search(r"\b(plan|schedule|phases|milestone|breakdown|roadmap|backlog)\b", lower):
            domains.append("planning")
        if re.search(r"\b(requirements|scope|discovery|spec|problem statement|use case)\b", lower):
            domains.append("discovery")
        if re.search(r"\b(knowledge base|knowledgebase|legacy code|old code|code archaeology|reverse engineer|codebase scan)\b", lower):
            domains.append("legacy-analysis")
        if re.search(r"\b(moderniz(e|ation)|strangler[- ]fig|safe refactor|codemod)\b", lower):
            domains.append("modernization")
        if re.search(r"\b(database migration|schema evolution|reversible migration|rollback script)\b", lower):
            domains.append("database")
        if re.search(r"\b(openapi|api contract|swagger|breaking api change)\b", lower):
            domains.append("api-contract")
        if re.search(r"\b(ci/cd|github actions|gitlab ci|container build)\b", lower):
            domains.append("devops")
        if re.search(r"\b(runtime profile|flamegraph|latency budget|n\+1 query|memory leak profiling)\b", lower):
            domains.append("performance")
        if re.search(r"\b(scrap(e|ing)|crawl(er|ing)?|web extract|online docs|fetch documentation|package registry|online intelligence)\b", lower):
            domains.append("research")
        if re.search(r"\b(open[- ]design|design\.md|interactive prototype|live dashboard|brand refresh|ui prototype)\b", lower):
            domains.append("open-design")
        if re.search(r"\b(doc|documentation|memory|reconcile|git|changelog|readme|handoff)\b", lower):
            domains.append("documentation")
        if re.search(r"\b(code|implement|function|class|method|refactor|fix|bug|endpoint|algorithm)\b", lower):
            domains.append("engineering")

        primary_domain = domains[0] if domains else "engineering"

        # 2. Compute Complexity Score (1 to 10)
        complexity = 3  # baseline

        # Boost complexity for cross-discipline or high-stakes topics
        if len(domains) >= 3:
            complexity += 3
        elif len(domains) == 2:
            complexity += 1

        if re.search(r"\b(migrate|rewrite|database engine|breaking change|irreversible|security model|production-wide)\b", lower):
            complexity += 4
        if re.search(r"\b(trade-off|tradeoff|versus|vs|council|debate|decision|pivot|build or buy)\b", lower):
            complexity += 3
        if re.search(r"\b(end-to-end|full feature|lifecycle|all phases|from scratch)\b", lower):
            complexity += 3

        # Reduce complexity for targeted, self-contained operations
        if re.search(r"\b(typo|rename|lookup|explain|format|lint|simple|quick|comment|docstring)\b", lower):
            complexity = max(1, complexity - 4)
        if len(clean.split()) < 8 and not re.search(r"\b(council|decision|migrate|rewrite)\b", lower):
            complexity = max(1, complexity - 2)

        complexity = max(1, min(10, complexity))

        # 3. Assess Risk Level
        if complexity >= 8 or "security" in domains or "irreversible" in lower:
            risk_level = "HIGH" if complexity < 9 else "CRITICAL"
        elif complexity >= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # 4. Determine IntentCategory
        # Priority 1: Multi-Persona Council
        is_explicit_council = bool(re.search(r"\b(council|deliberat(e|ion)|debate|trade-off|tradeoff|pivot or build|build or buy|type 1 decision)\b", lower))
        is_strategic_cross_discipline = (complexity >= 8 and len(domains) >= 2 and any(d in domains for d in ["architecture", "security"]))

        if is_explicit_council or is_strategic_cross_discipline:
            category = IntentCategory.COUNCIL
            complexity = max(complexity, 8)
            risk_level = "HIGH" if complexity < 9 else "CRITICAL"
            target_personas = ["architecture", "implementation", "verification"]
            if "security" in domains:
                target_personas.append("independent-review")
            if "design" in domains:
                target_personas.append("design")
            required_skills = ["architecture-and-contracts", "controlled-implementation", "testing-and-verification"]
            workflow = "council_deliberation"
            rationale = "High-stakes strategic or cross-discipline architectural decision requires multi-persona council."

        # Priority 2: Verification
        elif (
            primary_domain == "testing"
            or re.search(r"\b(run|execute|check|verify|assert|validate)\b.*?\b(tests?|test suite|assertions?|exit code|evidence)\b", lower)
            or re.search(r"\b(run (the )?tests?|verify tests?|run test suite|assert exit code|check assertions|validate evidence|execute unit test)\b", lower)
        ) and "review" not in domains:
            category = IntentCategory.VERIFICATION
            target_personas = ["verification"]
            required_skills = ["testing-and-verification"]
            workflow = "verification_run"
            rationale = "Direct automated testing and evidence verification request."

        # Priority 3: Adversarial Review / Quality Audit
        elif re.search(r"\b(audit|code review|adversarial review|pr review|inspect quality|anti-slop audit)\b", lower):
            category = IntentCategory.REVIEW
            target_personas = ["independent-review"]
            required_skills = ["independent-review"]
            workflow = "adversarial_review"
            rationale = "Read-only quality audit and compliance review request."

        # Priority 4: Sequential Multi-Stage Workflow
        elif complexity >= 6 or re.search(r"\b(end-to-end|lifecycle|implement (a |new )?feature|from scratch|multi-stage)\b", lower):
            category = IntentCategory.SEQUENTIAL_WORKFLOW
            target_personas = ["discovery", "architecture", "implementation", "verification"]
            if "design" in domains:
                target_personas.insert(2, "design")
            required_skills = ["project-discovery", "architecture-and-contracts", "controlled-implementation", "testing-and-verification"]
            workflow = "sequential_pipeline"
            rationale = "Multi-phase implementation spanning multiple lifecycle gates requires sequential workflow pipeline."

        # Priority 5: Single Persona (Direct, minimal overhead)
        else:
            category = IntentCategory.SINGLE_PERSONA
            workflow = "direct_execution"
            if primary_domain == "testing":
                target_personas = ["verification"]
                required_skills = ["testing-and-verification"]
            elif primary_domain == "review":
                target_personas = ["independent-review"]
                required_skills = ["independent-review"]
            elif primary_domain == "architecture":
                target_personas = ["architecture"]
                required_skills = ["architecture-and-contracts"]
            elif primary_domain == "design":
                target_personas = ["design"]
                required_skills = ["design-system-engineering"]
            elif primary_domain == "planning":
                target_personas = ["planning"]
                required_skills = ["phase-planning"]
            elif primary_domain == "discovery":
                target_personas = ["discovery"]
                required_skills = ["project-discovery"]
            elif primary_domain == "documentation":
                target_personas = ["documentation-and-memory"]
                required_skills = ["documentation-and-handoff"]
            elif primary_domain == "legacy-analysis":
                target_personas = ["legacy-analysis"]
                required_skills = ["legacy-codebase-knowledge-base"]
            elif primary_domain == "modernization":
                target_personas = ["modernization-architect"]
                required_skills = ["safe-refactoring-and-migration"]
            elif primary_domain == "security":
                target_personas = ["security-auditor"]
                required_skills = ["security-audit-and-hardening"]
            elif primary_domain == "database":
                target_personas = ["database-migration-specialist"]
                required_skills = ["database-migration-and-schema-evolution"]
            elif primary_domain == "api-contract":
                target_personas = ["api-contract-engineer"]
                required_skills = ["api-contract-and-openapi-spec"]
            elif primary_domain == "devops":
                target_personas = ["devops-automation-engineer"]
                required_skills = ["ci-cd-pipeline-engineering"]
            elif primary_domain == "performance":
                target_personas = ["performance-engineer"]
                required_skills = ["runtime-performance-profiling"]
            elif primary_domain == "research":
                target_personas = ["web-scraping-researcher"]
                required_skills = ["web-scraping-and-research"]
            elif primary_domain == "open-design":
                target_personas = ["open-design-architect"]
                required_skills = ["open-design-system-and-prototyping"]
            else:
                target_personas = ["implementation"]
                required_skills = ["controlled-implementation"]

            rationale = f"Focused, bounded single-domain request assigned to {target_personas[0]} to minimize overhead."

        return {
            "query": clean,
            "intentCategory": category,
            "domain": primary_domain,
            "allDomains": domains,
            "complexityScore": complexity,
            "riskLevel": risk_level,
            "targetPersonas": target_personas,
            "requiredSkills": required_skills,
            "workflow": workflow,
            "rationale": rationale
        }

    def route_request(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Produces an actionable execution plan adhering strictly to
        'minimum necessary complexity, maximum useful expertise'.
        Returns routeType, selectedPersonas, selectedSkills, executionPlan, and explanation.
        """
        intent = self.parse_user_intent(query, context)
        category = intent["intentCategory"]
        target_personas = intent["targetPersonas"]
        required_skills = intent["requiredSkills"]
        complexity = intent["complexityScore"]
        risk_level = intent["riskLevel"]

        # Execution plan steps construction
        steps: List[Dict[str, Any]] = []

        if category == IntentCategory.COUNCIL:
            route_type = "council"
            governance = "COUNCIL_GATE"
            steps = [
                {"step": 1, "round": "Round 1", "description": "Independent analysis across participating personas"},
                {"step": 2, "round": "Round 2", "description": "Cross-examination and challenge generation"},
                {"step": 3, "round": "Round 3", "description": "Revision and defense addressing critiques"},
                {"step": 4, "round": "Round 4", "description": "Synthesis of Council Decision Brief with preserved dissent"}
            ]
            explanation = (
                f"Selected multi-persona council with {len(target_personas)} personas "
                f"({', '.join(target_personas)}) due to high complexity (score: {complexity}) "
                f"and strategic trade-offs. Preserves diverse perspectives and dissent."
            )

        elif category == IntentCategory.SEQUENTIAL_WORKFLOW:
            route_type = "workflow"
            governance = "STANDARD_LIFECYCLE"
            for idx, p in enumerate(target_personas, start=1):
                role_skills = self.PERSONA_CATALOG.get(p, {}).get("skills", ["controlled-implementation"])
                steps.append({
                    "step": idx,
                    "persona": p,
                    "skill": role_skills[0] if role_skills else "controlled-implementation",
                    "description": f"Execute {p} phase within lifecycle pipeline"
                })
            explanation = (
                f"Selected sequential workflow across {len(target_personas)} phases "
                f"to maintain structured lifecycle discipline without council overhead."
            )

        elif category == IntentCategory.VERIFICATION:
            route_type = "verification"
            governance = "EVIDENCE_GATE"
            steps = [{
                "step": 1,
                "persona": "verification",
                "skill": "testing-and-verification",
                "description": "Execute automated test suites and collect empirical verification evidence"
            }]
            explanation = (
                "Directly routed to Verification Engineer to capture empirical evidence "
                "with zero intermediate overhead."
            )

        elif category == IntentCategory.REVIEW:
            route_type = "review"
            governance = "INDEPENDENT_AUDIT"
            steps = [{
                "step": 1,
                "persona": "independent-review",
                "skill": "independent-review",
                "description": "Conduct read-only adversarial review for quality, security, and anti-slop compliance"
            }]
            explanation = (
                "Directly routed to Independent Reviewer for read-only adversarial evaluation."
            )

        else:  # SINGLE_PERSONA
            route_type = "direct"
            governance = "LIGHTWEIGHT"
            assigned = target_personas[0]
            assigned_skill = required_skills[0]
            steps = [{
                "step": 1,
                "persona": assigned,
                "skill": assigned_skill,
                "description": f"Directly execute task within {assigned} domain"
            }]
            explanation = (
                f"Assigned directly to single persona '{assigned}' with skill '{assigned_skill}' "
                f"(complexity score: {complexity}). Bypasses multi-persona overhead per "
                f"'minimum necessary complexity, maximum useful expertise'."
            )

        return {
            "routeType": route_type,
            "intentCategory": category,
            "selectedPersonas": target_personas,
            "selectedSkills": required_skills,
            "complexityScore": complexity,
            "riskLevel": risk_level,
            "governanceLevel": governance,
            "executionPlan": steps,
            "explanation": explanation
        }


# Module-level convenience functions
_router_instance = TaskRouter()


def parse_user_intent(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience functional wrapper for intent parsing."""
    return _router_instance.parse_user_intent(query, context)


def route_request(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience functional wrapper for request routing."""
    return _router_instance.route_request(query, context)
