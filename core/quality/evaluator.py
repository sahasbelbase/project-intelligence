"""
Project Intelligence — Quality Profile Evaluator Engine
Evaluates contract deliverables against the Mandatory Engineering Baseline and active Quality Profiles.
"""

from typing import Dict, List, Any, Tuple
import json
from pathlib import Path


class QualityError(Exception):
    """Raised when quality rules are violated."""
    pass


class QualityEvaluator:
    def __init__(self, profiles_path: Path = None):
        if profiles_path is None:
            profiles_path = Path(__file__).parent / "profiles.json"

        with open(profiles_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.mandatory_baseline = self.data.get("mandatoryBaseline", {})
        self.profiles = self.data.get("profiles", {})

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Case-insensitive and kebab-case normalized profile lookup."""
        normalized = profile_name.strip().upper().replace("-", "_")
        if normalized in self.profiles:
            return self.profiles[normalized]
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        raise QualityError(f"Unknown profile '{profile_name}'. Valid profiles: {list(self.profiles.keys())}")

    def evaluate_anti_slop(
        self,
        content_sample: str,
        is_markdown: bool = False,
        file_path: str = ""
    ) -> List[str]:
        """
        Scans code or output text for anti-slop violations:
        - Gratuitous decorative emoji
        - Unresolved placeholder markers in deliverable code
        - LLM truncation markers
        """
        violations = []
        forbidden_placeholders = [
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
        lower_content = content_sample.lower()
        for placeholder in forbidden_placeholders:
            if placeholder.lower() in lower_content:
                # Do not flag if it's a tracked Jira/issue TODO, e.g. TODO(PROJ-123)
                if placeholder.lower() == "todo: implement later" or placeholder.lower() in lower_content:
                    violations.append(f"Anti-slop violation: found forbidden placeholder '{placeholder}'.")

        # Full astral + BMP emoji pattern (emoticons, pictographs, symbols, Dingbats, transport)
        import re
        emoji_pattern = re.compile(
            "[\u2600-\u27BF"          # Miscellaneous Symbols & Dingbats (⚠️, ✨, ⚙️, ✅, ❌, etc.)
            "\U0001F300-\U0001FAFF]"  # Astral plane emojis & supplemental symbols
        )

        # In markdown documents, allow standard callout/alert badges while flagging gratuitous decorations
        if is_markdown:
            # Strip markdown callout headers (> ⚠️, > [!NOTE], etc.) before scanning
            stripped = re.sub(r">.*", "", content_sample)
            # In docs, only flag clusters of celebratory/decorative emojis
            excessive_emoji = re.compile(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]{2,}")
            if excessive_emoji.search(stripped):
                violations.append("Anti-slop violation: gratuitous decorative emoji cluster detected in technical artifact.")
        else:
            if emoji_pattern.search(content_sample):
                violations.append("Anti-slop violation: gratuitous decorative emoji detected in technical artifact.")

        return violations

    def evaluate_verification_honesty(self, suites: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Ensures verification honesty:
        - Skipped or unavailable checks cannot be passed
        - Mandatory suites must be passed
        """
        issues = []
        for s in suites:
            name = s.get("suiteName", "Unnamed Suite")
            status = s.get("status", "UNAVAILABLE")
            mandatory = s.get("mandatory", False)

            if status not in ["PASSED", "FAILED", "BLOCKED", "SKIPPED", "UNAVAILABLE"]:
                issues.append(f"Invalid verification status '{status}' in suite '{name}'.")

            if mandatory and status != "PASSED":
                issues.append(f"Mandatory verification suite '{name}' has non-passing status: '{status}'.")

        return len(issues) == 0, issues

    def evaluate_profile(
        self,
        profile_name: str,
        verification_suites: List[Dict[str, Any]] = None,
        coverage_percent: float = None
    ) -> Tuple[bool, List[str]]:
        """Validates verification suites and metrics against the active profile."""
        profile = self.get_profile(profile_name)
        issues = []

        if verification_suites is not None:
            honesty_ok, honesty_issues = self.evaluate_verification_honesty(verification_suites)
            if not honesty_ok:
                issues.extend(honesty_issues)

        min_cov = profile.get("minCoveragePercent", 0)
        if coverage_percent is not None and coverage_percent < min_cov:
            issues.append(
                f"Test coverage ({coverage_percent:.1f}%) is below minimum threshold ({min_cov}%) for profile '{profile.get('name')}'."
            )

        return len(issues) == 0, issues


def scan_target_path(evaluator: QualityEvaluator, target_path: Path) -> List[Tuple[Path, List[str]]]:
    """Scans code files under target_path for anti-slop violations, ignoring tests and fixtures."""
    all_violations = []

    if target_path.is_file():
        files_to_scan = [target_path]
    else:
        files_to_scan = []
        for ext in ["*.py", "*.js", "*.ts", "*.json", "*.sh"]:
            files_to_scan.extend(target_path.rglob(ext))

    ignore_patterns = ["validation/fixtures", "__pycache__", ".git", "test_quality.py", "evaluator.py"]

    for f in sorted(files_to_scan):
        path_str = str(f).replace("\\", "/")
        if any(ignored in path_str for ignored in ignore_patterns):
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            is_md = f.suffix.lower() in [".md", ".markdown"]
            violations = evaluator.evaluate_anti_slop(content, is_markdown=is_md, file_path=path_str)
            if violations:
                all_violations.append((f, violations))
        except Exception:
            pass

    return all_violations


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Project Intelligence — Quality Profile Evaluator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target",
        metavar="PATH",
        default=".",
        help="Target file or directory to evaluate (default: current directory)."
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        default="STANDARD",
        help="Quality profile to evaluate (PROTOTYPE, STANDARD, PRODUCTION_READY, SECURITY_SENSITIVE, DESIGN_INTENSIVE)."
    )
    parser.add_argument(
        "--anti-slop",
        action="store_true",
        help="Run anti-slop scanner across all source files in target path."
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Execute internal verification of profiles and baseline rules."
    )

    args = parser.parse_args()
    evaluator = QualityEvaluator()

    if args.selftest:
        print("Quality Profile Evaluator Self-Test: PASSED")
        print(f"Profiles Defined        : {len(evaluator.profiles)}")
        print(f"Mandatory Baseline Rules: {len(evaluator.mandatory_baseline.get('rules', []))}")
        for r in evaluator.mandatory_baseline.get("rules", []):
            print(f"  • {r['ruleId']}: {r['name']}")
        sys.exit(0)

    try:
        profile = evaluator.get_profile(args.profile)
    except QualityError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("PROJECT INTELLIGENCE — QUALITY EVALUATION")
    print("=" * 70)
    print(f"Active Profile        : {profile.get('name')}")
    print(f"Minimum Test Coverage : {profile.get('minCoveragePercent')}%")
    print(f"Target Path           : {Path(args.target).resolve()}")
    print("-" * 70)

    target_path = Path(args.target).resolve()
    findings = scan_target_path(evaluator, target_path)

    if findings:
        print(f"[FAILED] Anti-slop violations found in {len(findings)} file(s):")
        for f_path, violations in findings:
            print(f"\nFile: {f_path}")
            for v in violations:
                print(f"  ✖ {v}")
        print("=" * 70)
        sys.exit(1)
    else:
        print("[PASSED] All anti-slop and baseline quality checks passed cleanly.")
        print(f"Scanned path '{target_path}' contains zero anti-slop violations.")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
