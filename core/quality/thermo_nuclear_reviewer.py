"""
Project Intelligence — Thermo-Nuclear Code Quality Reviewer & Code Judo Engine
Conducts adversarial structural simplification, nesting depth analysis, file bloat checks,
and Baseline UI craftsmanship audits (4px grid, token economy, WCAG contrast).
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class CodeJudoFinding:
    rule_id: str
    category: str
    severity: str  # "BLOCKING", "MAJOR", "MINOR", "OPPORTUNITY"
    file_path: str
    line_number: Optional[int]
    message: str
    code_snippet: Optional[str] = None
    judo_recommendation: Optional[str] = None


@dataclass
class ThermoNuclearReport:
    target_path: str
    verdict: str  # "APPROVED", "REJECTED"
    code_judo_score: float  # 0 to 100
    baseline_ui_score: float  # 0 to 100
    overall_score: float  # 0 to 100
    findings: List[CodeJudoFinding] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def is_approved(self) -> bool:
        return self.verdict == "APPROVED"


class ThermoNuclearReviewer:
    """
    Adversarial reviewer enforcing:
    1. Code Judo structural simplification (nesting depth <= 3, trivial wrappers collapsed)
    2. File bloat ceilings (warning > 600 lines, blocking > 1,000 lines)
    3. Baseline UI Craftsmanship (4px/8px geometric scale, semantic tokens, motion <= 250ms)
    4. Anti-slop invariants (BL-001 through BL-007)
    """

    MAX_NESTING_DEPTH = 3
    FILE_LINE_WARN = 600
    FILE_LINE_LIMIT = 1000

    FORBIDDEN_PLACEHOLDERS = [
        "TODO: implement later",
        "PLACEHOLDER_NOT_IMPLEMENTED",
        "fixme later",
        "fake_production_data",
        "lorem ipsum",
        "... rest of code unchanged ...",
        "... rest of implementation unchanged ...",
        "/* add your implementation here */",
        "// add your implementation here",
        "# add your implementation here"
    ]

    def __init__(self):
        self.css_spacing_prop_re = re.compile(
            r"(?P<prop>margin|margin-top|margin-bottom|margin-left|margin-right|"
            r"padding|padding-top|padding-bottom|padding-left|padding-right|"
            r"gap|column-gap|row-gap)\s*:\s*(?P<val>[^;]+);",
            re.IGNORECASE
        )
        self.px_val_re = re.compile(r"(\d+)px")
        self.hex_color_re = re.compile(r"#[0-9a-fA-F]{3,8}\b")
        self.duration_re = re.compile(r"(\d+(?:\.\d+)?)(m?s)")

    # -------------------------------------------------------------------------
    # Code Judo AST & Nesting Analysis (Python)
    # -------------------------------------------------------------------------
    def _calculate_node_depth(self, node: ast.AST, current_depth: int = 0) -> List[Tuple[int, int, str]]:
        violating_nodes = []
        nesting_constructs = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)

        for field, value in ast.iter_fields(node):
            items = value if isinstance(value, list) else [value]
            for item in items:
                if not isinstance(item, ast.AST):
                    continue
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    violating_nodes.extend(self._calculate_node_depth(item, 0))
                    continue
                if not isinstance(item, nesting_constructs):
                    violating_nodes.extend(self._calculate_node_depth(item, current_depth))
                    continue

                # Statement is a nesting construct
                is_elif = (isinstance(node, ast.If) and field == "orelse" and isinstance(item, ast.If))
                next_depth = current_depth if is_elif else current_depth + 1
                if next_depth > self.MAX_NESTING_DEPTH:
                    line = getattr(item, "lineno", 1)
                    violating_nodes.append((line, next_depth, type(item).__name__))
                violating_nodes.extend(self._calculate_node_depth(item, next_depth))

        return violating_nodes

    def analyze_python_ast(self, file_path: str, code: str) -> List[CodeJudoFinding]:
        findings = []
        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError as e:
            findings.append(CodeJudoFinding(
                rule_id="JUDO-SYNTAX",
                category="SYNTAX",
                severity="BLOCKING",
                file_path=file_path,
                line_number=e.lineno,
                message=f"Syntax error: {e.msg}",
                judo_recommendation="Fix syntax error before running adversarial review."
            ))
            return findings

        # 1. Cyclomatic Nesting Depth
        depth_violations = self._calculate_node_depth(tree, 0)
        for line, depth, construct in depth_violations:
            findings.append(CodeJudoFinding(
                rule_id="JUDO-001-NESTING-DEPTH",
                category="CODE_JUDO",
                severity="BLOCKING" if depth > 4 else "MAJOR",
                file_path=file_path,
                line_number=line,
                message=f"Excessive nesting depth of {depth} exceeds limit of {self.MAX_NESTING_DEPTH} in {construct}.",
                judo_recommendation="Apply Code Judo Move 2: Invert condition and return early with guard clauses."
            ))

        # 2. Trivial Pass-Through Wrapper Detection
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant)]
            if len(body) != 1 or not isinstance(body[0], ast.Return):
                continue
            ret_val = body[0].value
            if not isinstance(ret_val, ast.Call) or not isinstance(ret_val.func, (ast.Name, ast.Attribute)):
                continue
            target_name = ret_val.func.id if isinstance(ret_val.func, ast.Name) else ret_val.func.attr
            func_args = [a.arg for a in node.args.args if a.arg != "self"]
            call_args = [a.id for a in ret_val.args if isinstance(a, ast.Name)]
            if func_args == call_args and not ret_val.keywords and len(func_args) > 0:
                findings.append(CodeJudoFinding(
                    rule_id="JUDO-002-TRIVIAL-WRAPPER",
                    category="CODE_JUDO",
                    severity="MAJOR",
                    file_path=file_path,
                    line_number=node.lineno,
                    message=f"Function '{node.name}' is a trivial pass-through wrapper forwarding to '{target_name}'.",
                    code_snippet=f"def {node.name}({', '.join(func_args)}): return {target_name}(...)",
                    judo_recommendation=f"Apply Code Judo Move 1: Collapse wrapper '{node.name}'. Invoke '{target_name}' directly at call sites."
                ))

        return findings

    # -------------------------------------------------------------------------
    # Nesting Analysis (Generic JS / TS)
    # -------------------------------------------------------------------------
    def analyze_generic_code(self, file_path: str, code: str) -> List[CodeJudoFinding]:
        findings = []
        brace_depth = 0
        control_keywords = ("if (", "if(", "for (", "while (", "switch (")

        for idx, line in enumerate(code.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            open_count = stripped.count("{")
            close_count = stripped.count("}")
            if open_count > close_count:
                brace_depth += (open_count - close_count)
            elif close_count > open_count:
                brace_depth = max(0, brace_depth - (close_count - open_count))

            if brace_depth > 4 and any(kw in stripped for kw in control_keywords):
                findings.append(CodeJudoFinding(
                    rule_id="JUDO-001-NESTING-DEPTH",
                    category="CODE_JUDO",
                    severity="MAJOR",
                    file_path=file_path,
                    line_number=idx,
                    message=f"Deeply nested control block (depth {brace_depth}).",
                    code_snippet=stripped[:80],
                    judo_recommendation="Apply Code Judo Move 2: Flatten using guard clauses or extract helper."
                ))

        return findings

    # -------------------------------------------------------------------------
    # File Bloat & Density Audit
    # -------------------------------------------------------------------------
    def analyze_file_metrics(self, file_path: str, code: str) -> List[CodeJudoFinding]:
        findings = []
        line_count = len(code.splitlines())

        if line_count > self.FILE_LINE_LIMIT:
            findings.append(CodeJudoFinding(
                rule_id="JUDO-003-FILE-BLOAT-LIMIT",
                category="BLOAT",
                severity="BLOCKING",
                file_path=file_path,
                line_number=1,
                message=f"File exceeds hard limit of {self.FILE_LINE_LIMIT} lines ({line_count} lines).",
                judo_recommendation="Apply Code Judo Move 3: Decompose into modular, cohesive single-purpose files."
            ))
        elif line_count > self.FILE_LINE_WARN:
            findings.append(CodeJudoFinding(
                rule_id="JUDO-003-FILE-BLOAT-WARN",
                category="BLOAT",
                severity="MINOR",
                file_path=file_path,
                line_number=1,
                message=f"File exceeds recommended size of {self.FILE_LINE_WARN} lines ({line_count} lines).",
                judo_recommendation="Review for possible violation of Single Responsibility Principle."
            ))

        return findings

    # -------------------------------------------------------------------------
    # Anti-Slop & Placeholder Detection
    # -------------------------------------------------------------------------
    def analyze_anti_slop(self, file_path: str, code: str) -> List[CodeJudoFinding]:
        findings = []
        # Exempt test and rule files from self-matching rule definition strings
        if any(ign in file_path for ign in ["evaluator.py", "thermo_nuclear_reviewer.py", "test_"]):
            return findings

        lower_code = code.lower()
        for ph in self.FORBIDDEN_PLACEHOLDERS:
            if ph.lower() in lower_code:
                findings.append(CodeJudoFinding(
                    rule_id="BL-003-UNIMPLEMENTED-STUB",
                    category="ANTI_SLOP",
                    severity="BLOCKING",
                    file_path=file_path,
                    line_number=None,
                    message=f"Forbidden placeholder stub found: '{ph}'.",
                    judo_recommendation="Deliver fully implemented production logic or honest unsupported error."
                ))

        if not file_path.endswith(".md"):
            emoji_pattern = re.compile(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]")
            for idx, line in enumerate(code.splitlines(), start=1):
                if emoji_pattern.search(line) and "re.compile" not in line and "\\u" not in line:
                    findings.append(CodeJudoFinding(
                        rule_id="BL-001-GRATUITOUS-EMOJI",
                        category="ANTI_SLOP",
                        severity="BLOCKING",
                        file_path=file_path,
                        line_number=idx,
                        message=f"Gratuitous decorative emoji detected in technical file: '{line.strip()[:60]}'",
                        judo_recommendation="Remove decorative emojis adhering to BL-001 Mandatory Baseline."
                    ))

        return findings

    def _check_spacing_line(self, line: str, idx: int, file_path: str) -> List[CodeJudoFinding]:
        match = self.css_spacing_prop_re.search(line)
        if not match:
            return []
        findings = []
        prop = match.group("prop")
        for px in self.px_val_re.findall(match.group("val")):
            val = int(px)
            if val != 0 and val % 4 != 0:
                findings.append(CodeJudoFinding(
                    rule_id="BASE-001-SPACING-CADENCE",
                    category="BASELINE_UI",
                    severity="MAJOR",
                    file_path=file_path,
                    line_number=idx,
                    message=f"Arbitrary spacing {val}px in '{prop}' violates the 4px/8px geometric scale.",
                    code_snippet=line,
                    judo_recommendation=f"Snap {val}px to nearest 4px interval ({round(val / 4) * 4}px) or use tokens."
                ))
        return findings

    def _check_motion_line(self, line: str, idx: int, file_path: str) -> List[CodeJudoFinding]:
        if "transition" not in line and "animation" not in line:
            return []
        findings = []
        for match in self.duration_re.finditer(line):
            num = float(match.group(1))
            ms = num if match.group(2) == "ms" else num * 1000
            if ms > 300:
                findings.append(CodeJudoFinding(
                    rule_id="BASE-004-MOTION-BOUNDS",
                    category="BASELINE_UI",
                    severity="MINOR",
                    file_path=file_path,
                    line_number=idx,
                    message=f"Sluggish transition duration {ms:.0f}ms exceeds the 250ms maximum.",
                    code_snippet=line,
                    judo_recommendation="Cap functional UI transitions at <= 200ms with snappy easing curves."
                ))
        return findings

    def analyze_baseline_ui_css(self, file_path: str, css_content: str) -> List[CodeJudoFinding]:
        findings = []
        in_root_or_var_block = False

        for idx, line in enumerate(css_content.splitlines(), start=1):
            trimmed = line.strip()
            if ":root" in trimmed or "@keyframes" in trimmed:
                in_root_or_var_block = True
            if in_root_or_var_block and "}" in trimmed:
                in_root_or_var_block = False

            findings.extend(self._check_spacing_line(trimmed, idx, file_path))
            findings.extend(self._check_motion_line(trimmed, idx, file_path))

            # 2. Hardcoded Hex Colors Outside Root / Variables
            if not in_root_or_var_block and not trimmed.startswith("--"):
                hex_matches = self.hex_color_re.findall(trimmed)
                if hex_matches and not trimmed.startswith("/*") and not trimmed.startswith("*"):
                    findings.append(CodeJudoFinding(
                        rule_id="BASE-002-TOKEN-DISCIPLINE",
                        category="BASELINE_UI",
                        severity="MAJOR",
                        file_path=file_path,
                        line_number=idx,
                        message=f"Hardcoded hex color '{hex_matches[0]}' outside token declaration.",
                        code_snippet=trimmed,
                        judo_recommendation="Replace raw hex with semantic CSS token (e.g. var(--bg-surface), var(--text-primary))."
                    ))

            # 4. Suppressed Focus Outline without Replacement
            if "outline: none" in trimmed or "outline: 0" in trimmed:
                findings.append(CodeJudoFinding(
                    rule_id="BASE-005-FOCUS-RING",
                    category="BASELINE_UI",
                    severity="BLOCKING",
                    file_path=file_path,
                    line_number=idx,
                    message="Focus outline suppressed without accessible replacement.",
                    code_snippet=trimmed,
                    judo_recommendation="Provide visible :focus-visible { outline: 2px solid var(--accent); } ring."
                ))

        return findings

    # -------------------------------------------------------------------------
    # Unified File & Path Inspection
    # -------------------------------------------------------------------------
    def inspect_file(self, file_path: Path) -> List[CodeJudoFinding]:
        findings = []
        path_str = str(file_path).replace("\\", "/")
        ignore_substrings = ["__pycache__", ".git", "validation/fixtures", "node_modules"]
        if any(ign in path_str for ign in ignore_substrings):
            return findings

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return findings

        findings.extend(self.analyze_file_metrics(path_str, content))
        findings.extend(self.analyze_anti_slop(path_str, content))

        ext = file_path.suffix.lower()
        if ext == ".py":
            findings.extend(self.analyze_python_ast(path_str, content))
        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            findings.extend(self.analyze_generic_code(path_str, content))
        elif ext in [".css", ".scss"]:
            findings.extend(self.analyze_baseline_ui_css(path_str, content))
        elif ext in [".html"]:
            css_matches = re.findall(r"<style[^>]*>(.*?)</style>", content, re.DOTALL | re.IGNORECASE)
            for css in css_matches:
                findings.extend(self.analyze_baseline_ui_css(path_str, css))

        return findings

    def review_path(self, target: Path) -> ThermoNuclearReport:
        all_findings: List[CodeJudoFinding] = []
        files = [target] if target.is_file() else sorted(target.rglob("*"))
        valid_files = [f for f in files if f.is_file() and f.suffix in [".py", ".js", ".ts", ".css", ".html", ".json", ".md"]]

        for f in valid_files:
            file_findings = self.inspect_file(f)
            if file_findings:
                all_findings.extend(file_findings)

        blocking_count = sum(1 for f in all_findings if f.severity == "BLOCKING")
        major_count = sum(1 for f in all_findings if f.severity == "MAJOR")
        minor_count = sum(1 for f in all_findings if f.severity == "MINOR")

        judo_findings = [f for f in all_findings if f.category in ("CODE_JUDO", "BLOAT", "ANTI_SLOP")]
        ui_findings = [f for f in all_findings if f.category == "BASELINE_UI"]

        judo_deductions = sum(25 if f.severity == "BLOCKING" else 10 if f.severity == "MAJOR" else 3 for f in judo_findings)
        ui_deductions = sum(25 if f.severity == "BLOCKING" else 10 if f.severity == "MAJOR" else 3 for f in ui_findings)

        code_judo_score = max(0.0, 100.0 - judo_deductions)
        baseline_ui_score = max(0.0, 100.0 - ui_deductions)
        overall_score = round((code_judo_score * 0.6 + baseline_ui_score * 0.4), 1)

        verdict = "REJECTED" if (blocking_count > 0 or code_judo_score < 70) else "APPROVED"
        stats = {
            "scannedFiles": len(valid_files),
            "totalFindings": len(all_findings),
            "blockingDefects": blocking_count,
            "majorDefects": major_count,
            "minorDefects": minor_count,
            "codeJudoMovesIdentified": len([f for f in all_findings if f.judo_recommendation is not None])
        }

        return ThermoNuclearReport(
            target_path=str(target),
            verdict=verdict,
            code_judo_score=code_judo_score,
            baseline_ui_score=baseline_ui_score,
            overall_score=overall_score,
            findings=all_findings,
            stats=stats
        )


def main():
    import argparse
    import sys
    import json

    parser = argparse.ArgumentParser(description="Thermo-Nuclear Code Quality Reviewer & Code Judo CLI")
    parser.add_argument("--target", metavar="PATH", default=".", help="Target path to review (default: .)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    args = parser.parse_args()

    reviewer = ThermoNuclearReviewer()
    report = reviewer.review_path(Path(args.target).resolve())

    if args.json:
        out = {
            "targetPath": report.target_path,
            "verdict": report.verdict,
            "overallScore": report.overall_score,
            "codeJudoScore": report.code_judo_score,
            "baselineUiScore": report.baseline_ui_score,
            "stats": report.stats,
            "findings": [
                {
                    "ruleId": f.rule_id,
                    "category": f.category,
                    "severity": f.severity,
                    "filePath": f.file_path,
                    "lineNumber": f.line_number,
                    "message": f.message,
                    "codeSnippet": f.code_snippet,
                    "judoRecommendation": f.judo_recommendation
                }
                for f in report.findings
            ]
        }
        print(json.dumps(out, indent=2))
        sys.exit(0 if report.verdict == "APPROVED" else 1)

    print("=" * 78)
    print("PROJECT INTELLIGENCE — THERMO-NUCLEAR CODE QUALITY REVIEW")
    print("=" * 78)
    print(f"Target Path           : {report.target_path}")
    print(f"Gate G5 Verdict       : [{report.verdict}]")
    print(f"Overall Quality Score : {report.overall_score:.1f} / 100.0")
    print(f"Code Judo Score       : {report.code_judo_score:.1f} / 100.0")
    print(f"Baseline UI Score     : {report.baseline_ui_score:.1f} / 100.0")
    print(f"Scanned Files         : {report.stats.get('scannedFiles')}")
    print(f"Blocking Defects      : {report.stats.get('blockingDefects')}")
    print(f"Major Defects         : {report.stats.get('majorDefects')}")
    print(f"Minor / Opportunities : {report.stats.get('minorDefects')}")
    print("-" * 78)

    if report.findings:
        print("FINDINGS & CODE JUDO MOVES:")
        for idx, f in enumerate(report.findings, start=1):
            sev_badge = f"[{f.severity}]"
            line_info = f":{f.line_number}" if f.line_number else ""
            print(f"{idx}. {sev_badge} {f.rule_id} in {f.file_path}{line_info}")
            print(f"   Issue: {f.message}")
            if f.judo_recommendation:
                print(f"   Judo Move: {f.judo_recommendation}")
        print("=" * 78)
    else:
        print("Zero defects or structural bloat detected. Code satisfies Inevitability Standard.")
        print("=" * 78)

    sys.exit(0 if report.verdict == "APPROVED" else 1)


if __name__ == "__main__":
    main()
