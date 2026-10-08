"""
Project Intelligence — Shared Evidence Classifier & Honesty Validator
Provides epistemic categorization, empirical evidence validation, and fact-vs-assumption separation.
Zero external dependencies (Python standard library only).
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import re


class EvidenceCategory(str, Enum):
    """Canonical epistemic categories for claims, arguments, and deliverables."""
    VERIFIED_FACT = "VERIFIED_FACT"
    ASSUMPTION = "ASSUMPTION"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"
    RECOMMENDATION = "RECOMMENDATION"
    RISK = "RISK"


@dataclass
class EvidenceItem:
    """Structured representation of an epistemic item with supporting basis."""
    category: EvidenceCategory
    statement: str
    source: str = ""
    confidence: float = 1.0
    basis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for JSON serialization."""
        return {
            "category": self.category.value if isinstance(self.category, EvidenceCategory) else str(self.category),
            "statement": self.statement,
            "source": self.source,
            "confidence": float(self.confidence),
            "basis": self.basis
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceItem":
        """Instantiate EvidenceItem from dictionary representation."""
        cat_raw = data.get("category", "UNKNOWN")
        if isinstance(cat_raw, EvidenceCategory):
            category = cat_raw
        else:
            try:
                category = EvidenceCategory(str(cat_raw).strip().upper())
            except (ValueError, KeyError):
                category = EvidenceCategory.UNKNOWN
        return cls(
            category=category,
            statement=str(data.get("statement", "")),
            source=str(data.get("source", "")),
            confidence=float(data.get("confidence", 1.0)),
            basis=str(data.get("basis", ""))
        )

    def is_verified(self) -> bool:
        """Determines if the item satisfies rigorous verification criteria."""
        return (
            self.category == EvidenceCategory.VERIFIED_FACT
            and bool(self.source and self.source.strip())
            and self.confidence >= 0.8
        )


def classify_statement(
    statement: str,
    source: str = "",
    basis: str = "",
    context: Optional[Dict[str, Any]] = None
) -> EvidenceItem:
    """
    Classifies a statement into its canonical EvidenceCategory based on
    explicit tags, linguistic markers, and supporting proof.
    """
    clean = statement.strip()
    upper = clean.upper()

    # 1. Check explicit bracket or prefix tags
    tag_match = re.match(r"^\[([A-Z_]+)\]\s*(.*)$", clean)
    if tag_match:
        tag, rest = tag_match.group(1), tag_match.group(2)
        try:
            category = EvidenceCategory(tag)
            confidence = 1.0 if category == EvidenceCategory.VERIFIED_FACT else (0.1 if category == EvidenceCategory.UNKNOWN else 0.7)
            return EvidenceItem(
                category=category,
                statement=rest,
                source=source,
                confidence=confidence,
                basis=basis or f"Explicit tag [{tag}]"
            )
        except ValueError:
            pass

    # Alternate shorthand tags
    if upper.startswith("[FACT]") or upper.startswith("FACT:"):
        stmt = re.sub(r"^(\[FACT\]|FACT:)\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement=stmt,
            source=source,
            confidence=0.95 if source else 0.7,
            basis=basis or "Marked as fact"
        )
    if upper.startswith("[ASSUMPTION]") or upper.startswith("ASSUMPTION:"):
        stmt = re.sub(r"^(\[ASSUMPTION\]|ASSUMPTION:)\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.ASSUMPTION,
            statement=stmt,
            source=source,
            confidence=0.6,
            basis=basis or "Marked as assumption"
        )
    if upper.startswith("[ESTIMATE]") or upper.startswith("ESTIMATE:"):
        stmt = re.sub(r"^(\[ESTIMATE\]|ESTIMATE:)\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.ESTIMATE,
            statement=stmt,
            source=source,
            confidence=0.7,
            basis=basis or "Marked as estimate"
        )
    if upper.startswith("[UNKNOWN]") or upper.startswith("UNKNOWN:") or upper.startswith("[TBD]"):
        stmt = re.sub(r"^(\[UNKNOWN\]|UNKNOWN:|\[TBD\])\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.UNKNOWN,
            statement=stmt,
            source=source,
            confidence=0.1,
            basis=basis or "Marked as unknown"
        )
    if upper.startswith("[RECOMMENDATION]") or upper.startswith("RECOMMENDATION:"):
        stmt = re.sub(r"^(\[RECOMMENDATION\]|RECOMMENDATION:)\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.RECOMMENDATION,
            statement=stmt,
            source=source,
            confidence=0.85,
            basis=basis or "Marked as recommendation"
        )
    if upper.startswith("[RISK]") or upper.startswith("RISK:"):
        stmt = re.sub(r"^(\[RISK\]|RISK:)\s*", "", clean, flags=re.IGNORECASE)
        return EvidenceItem(
            category=EvidenceCategory.RISK,
            statement=stmt,
            source=source,
            confidence=0.8,
            basis=basis or "Marked as risk"
        )

    # 2. Semantic and pattern-based classification

    # Unknown patterns
    if re.search(r"\b(unknown|uncertain|unclear|to be determined|tbd|cannot determine|lacking data|unverified|needs investigation|not yet determined)\b", clean, re.IGNORECASE):
        return EvidenceItem(
            category=EvidenceCategory.UNKNOWN,
            statement=clean,
            source=source,
            confidence=0.15,
            basis=basis or "Linguistic unknown indicators"
        )

    # Risk patterns
    if re.search(r"\b(risk of|vulnerability|hazard|threat|single point of failure|bottleneck|failure mode|pitfall|data loss|catastrophic|security defect)\b", clean, re.IGNORECASE):
        return EvidenceItem(
            category=EvidenceCategory.RISK,
            statement=clean,
            source=source,
            confidence=0.8,
            basis=basis or "Linguistic risk indicators"
        )

    # Recommendation patterns
    if re.search(r"\b(recommend|we should|must be|ought to|propose that|advise to|suggest using|action item:|next step:)\b", clean, re.IGNORECASE):
        return EvidenceItem(
            category=EvidenceCategory.RECOMMENDATION,
            statement=clean,
            source=source,
            confidence=0.85,
            basis=basis or "Linguistic recommendation indicators"
        )

    # Estimate patterns (quantitative approximations)
    if re.search(r"\b(approximately|approx\.?|roughly|about \d+|around \d+|~\s*\d+|\d+\s*[-–]\s*\d+\s*(hours|days|weeks|ms|seconds|users|%)|estimated (at|to be)|projected to)\b", clean, re.IGNORECASE):
        return EvidenceItem(
            category=EvidenceCategory.ESTIMATE,
            statement=clean,
            source=source,
            confidence=0.7,
            basis=basis or "Quantitative estimation markers"
        )

    # Assumption patterns
    if re.search(r"\b(assume|assuming|assumed|assumption|presume|presuming|suppose|likely|probably|hypothesize|hypothesis|believe|believes|we think|expected to be)\b", clean, re.IGNORECASE):
        return EvidenceItem(
            category=EvidenceCategory.ASSUMPTION,
            statement=clean,
            source=source,
            confidence=0.5,
            basis=basis or "Speculative linguistic markers"
        )

    # Verified Fact patterns (empirical references, exit codes, hashes, citations)
    has_empirical_proof = (
        bool(source and source.strip())
        or bool(re.search(r"\b(exit code 0|commit [0-9a-f]{6,}|git rev-parse|test passed|tests? passing|checksum|sha[0-9]+|measured at|measured in|file exists at|according to [a-zA-Z0-9_\-\.]+)\b", clean, re.IGNORECASE))
    )
    if has_empirical_proof:
        return EvidenceItem(
            category=EvidenceCategory.VERIFIED_FACT,
            statement=clean,
            source=source or "empirical execution",
            confidence=1.0 if source else 0.9,
            basis=basis or "Empirical proof reference"
        )

    # Default fallback: If factual statement without empirical proof or speculative marker
    # Treat as ASSUMPTION unless proven
    return EvidenceItem(
        category=EvidenceCategory.ASSUMPTION,
        statement=clean,
        source=source,
        confidence=0.5,
        basis=basis or "Unverified assertion defaults to assumption"
    )


def validate_evidence_honesty(
    items: Union[List[EvidenceItem], List[Dict[str, Any]], str]
) -> Tuple[bool, List[str]]:
    """
    Validates adherence to BL-006 (Strict Verification Honesty) and epistemic standards:
    - VERIFIED_FACT items must have a concrete, non-empty source or empirical proof.
    - Speculative assertions must not masquerade as VERIFIED_FACT.
    - UNKNOWN items must not claim high confidence.
    - ASSUMPTION items must not claim 100% certainty.
    Returns (is_honest, violations).
    """
    violations: List[str] = []

    # If input is a raw string, tokenize into lines
    item_objs: List[EvidenceItem] = []
    if isinstance(items, str):
        lines = [line.strip() for line in items.splitlines() if line.strip() and not line.strip().startswith("#")]
        for l in lines:
            item_objs.append(classify_statement(l))
    elif isinstance(items, list):
        for it in items:
            if isinstance(it, EvidenceItem):
                item_objs.append(it)
            elif isinstance(it, dict):
                item_objs.append(EvidenceItem.from_dict(it))
            elif isinstance(it, str):
                item_objs.append(classify_statement(it))

    speculative_pattern = re.compile(
        r"\b(probably|likely|we assume|assume|assuming|hypothetically|presumably|might be|could be|supposedly)\b",
        re.IGNORECASE
    )

    for idx, item in enumerate(item_objs, start=1):
        # 1. Fact without verifiable source
        if item.category == EvidenceCategory.VERIFIED_FACT:
            if not item.source or not item.source.strip() or item.source.strip().lower() in {"none", "n/a", "unknown", "trust me"}:
                violations.append(
                    f"Item {idx}: Claimed VERIFIED_FACT lacks reproducible source or empirical reference: '{item.statement}'"
                )
            # 2. Speculation masquerading as fact
            if speculative_pattern.search(item.statement):
                violations.append(
                    f"Item {idx}: Speculative language masquerading as VERIFIED_FACT: '{item.statement}'"
                )

        # 3. Epistemic overconfidence on unknowns
        if item.category == EvidenceCategory.UNKNOWN:
            if item.confidence > 0.5:
                violations.append(
                    f"Item {idx}: Epistemic dishonesty — UNKNOWN item claims excessive confidence {item.confidence:.2f}: '{item.statement}'"
                )

        # 4. Epistemic dishonesty on assumptions
        if item.category == EvidenceCategory.ASSUMPTION:
            if item.confidence >= 1.0:
                violations.append(
                    f"Item {idx}: Epistemic dishonesty — ASSUMPTION item claims 100% confidence without empirical proof: '{item.statement}'"
                )

    return (len(violations) == 0, violations)


def separate_facts_and_assumptions(
    items: List[Union[EvidenceItem, Dict[str, Any], str]]
) -> Dict[str, List[EvidenceItem]]:
    """
    Separates a mixed collection of evidence items into distinct epistemic buckets:
    facts, assumptions, estimates, unknowns, risks, and recommendations.
    """
    buckets: Dict[str, List[EvidenceItem]] = {
        "facts": [],
        "assumptions": [],
        "estimates": [],
        "unknowns": [],
        "risks": [],
        "recommendations": []
    }

    for it in items:
        if isinstance(it, EvidenceItem):
            item = it
        elif isinstance(it, dict):
            item = EvidenceItem.from_dict(it)
        else:
            item = classify_statement(str(it))

        if item.category == EvidenceCategory.VERIFIED_FACT:
            buckets["facts"].append(item)
        elif item.category == EvidenceCategory.ASSUMPTION:
            buckets["assumptions"].append(item)
        elif item.category == EvidenceCategory.ESTIMATE:
            buckets["estimates"].append(item)
        elif item.category == EvidenceCategory.UNKNOWN:
            buckets["unknowns"].append(item)
        elif item.category == EvidenceCategory.RISK:
            buckets["risks"].append(item)
        elif item.category == EvidenceCategory.RECOMMENDATION:
            buckets["recommendations"].append(item)

    return buckets


def format_evidence_report(
    items: List[Union[EvidenceItem, Dict[str, Any], str]],
    title: str = "Evidence & Assumptions Report"
) -> str:
    """
    Formats an evidence collection into a structured Markdown document with
    clear epistemic boundaries, satisfying BL-001 (Zero decorative emojis).
    """
    buckets = separate_facts_and_assumptions(items)

    lines = [
        f"# {title}",
        "",
        "## 1. Verified Facts (Empirical Evidence)",
    ]
    if buckets["facts"]:
        for f in buckets["facts"]:
            src_str = f" [Source: {f.source}]" if f.source else ""
            lines.append(f"- {f.statement}{src_str}")
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## 2. Documented Assumptions",
    ])
    if buckets["assumptions"]:
        for a in buckets["assumptions"]:
            lines.append(f"- {a.statement} (Confidence: {a.confidence:.2f})")
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## 3. Quantitative Estimates",
    ])
    if buckets["estimates"]:
        for e in buckets["estimates"]:
            lines.append(f"- {e.statement} (Basis: {e.basis or 'estimated'})")
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## 4. Known Unknowns & Data Gaps",
    ])
    if buckets["unknowns"]:
        for u in buckets["unknowns"]:
            lines.append(f"- {u.statement}")
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## 5. Identified Risks",
    ])
    if buckets["risks"]:
        for r in buckets["risks"]:
            lines.append(f"- {r.statement}")
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## 6. Recommendations",
    ])
    if buckets["recommendations"]:
        for rec in buckets["recommendations"]:
            lines.append(f"- {rec.statement}")
    else:
        lines.append("- None recorded.")

    lines.append("")
    return "\n".join(lines)


def check_deliverable_evidence_separation(
    content: Union[str, List[EvidenceItem]]
) -> Dict[str, Any]:
    """
    Audits a deliverable document or item list to confirm that verified facts
    and assumptions are cleanly separated into distinct sections without blurring.
    """
    violations: List[str] = []

    if isinstance(content, list):
        buckets = separate_facts_and_assumptions(content)
        fact_count = len(buckets["facts"])
        assumption_count = len(buckets["assumptions"])
        unknown_count = len(buckets["unknowns"])
        risk_count = len(buckets["risks"])
        is_honest, honesty_violations = validate_evidence_honesty(content)
        violations.extend(honesty_violations)
        return {
            "is_compliant": len(violations) == 0,
            "fact_count": fact_count,
            "assumption_count": assumption_count,
            "unknown_count": unknown_count,
            "risk_count": risk_count,
            "has_separated_sections": True,
            "violations": violations
        }

    # If markdown text
    text = str(content)
    has_facts_section = bool(re.search(r"^#+\s*.*(fact|verified).*$", text, re.IGNORECASE | re.MULTILINE))
    has_assumptions_section = bool(re.search(r"^#+\s*.*(assumption|hypothesis).*$", text, re.IGNORECASE | re.MULTILINE))

    if not has_facts_section and not has_assumptions_section:
        violations.append("Deliverable lacks explicit dedicated sections for Facts and Assumptions.")

    # Check whether assumptions are embedded inside facts section
    sections = re.split(r"^#+\s+", text, flags=re.MULTILINE)
    facts_text = ""
    for s in sections:
        header_line = s.split("\n", 1)[0].lower() if s else ""
        if "fact" in header_line or "verified" in header_line:
            facts_text += s

    if facts_text:
        speculative_words = ["probably", "likely", "we assume", "assuming", "hypothetically", "believe"]
        for sw in speculative_words:
            if re.search(rf"\b{sw}\b", facts_text, re.IGNORECASE):
                violations.append(f"Speculative term '{sw}' found in Facts section without boundary demarcation.")

    # Count items in text
    fact_matches = len(re.findall(r"(\[FACT\]|VERIFIED_FACT|exit code 0)", text, re.IGNORECASE))
    assumption_matches = len(re.findall(r"(\[ASSUMPTION\]|assume|assuming)", text, re.IGNORECASE))
    unknown_matches = len(re.findall(r"(\[UNKNOWN\]|unknown|tbd)", text, re.IGNORECASE))
    risk_matches = len(re.findall(r"(\[RISK\]|risk of|vulnerability)", text, re.IGNORECASE))

    return {
        "is_compliant": len(violations) == 0,
        "fact_count": fact_matches,
        "assumption_count": assumption_matches,
        "unknown_count": unknown_matches,
        "risk_count": risk_matches,
        "has_separated_sections": has_facts_section and has_assumptions_section,
        "violations": violations
    }
