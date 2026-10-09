"""
Project Intelligence — Website Tests
Checks text contrast for the site's color tokens, that the generated data matches
the repository, and that the site carries no hard-coded metrics.
Zero external dependencies (Python standard library only).
"""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"


def _tokens(theme="light"):
    css = (WEB / "styles.css").read_text(encoding="utf-8")
    start = css.index(':root[data-theme="dark"] {') if theme == "dark" else css.index(":root {")
    block = css[start:css.index("}", start)]
    return dict(re.findall(r"--((?:color|btn|code)-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", block))


def _luminance(hex_color):
    def channel(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(fg, bg):
    a, b = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


class TestSiteContrast(unittest.TestCase):
    def test_dark_theme_redefines_every_light_color(self):
        light, dark = _tokens("light"), _tokens("dark")
        missing = [k for k in light if k.startswith("color-") and k not in dark]
        self.assertEqual(missing, [], "dark theme leaves these light-only")

    def test_text_tokens_meet_wcag_aa(self):
        pairs = [
            ("color-text", "color-bg"), ("color-text", "color-surface"),
            ("color-text-soft", "color-bg"), ("color-text-soft", "color-surface"),
            ("color-text-muted", "color-bg"), ("color-text-muted", "color-surface"),
            ("color-accent-700", "color-bg"), ("color-accent-700", "color-surface"),
            ("color-accent-800", "color-accent-100"), ("color-accent-2-800", "color-accent-2-100"),
            ("color-neutral-800", "color-neutral-200"),
            ("color-pass", "color-pass-bg"), ("color-warn", "color-warn-bg"), ("color-fail", "color-fail-bg"),
            ("color-text", "color-accent-100"), ("color-text", "color-accent-2-100"),
            ("color-code-fg", "color-code-bg"),
        ]
        for theme in ("light", "dark"):
            t = _tokens(theme)
            for fg, bg in pairs:
                with self.subTest(theme=theme, fg=fg, bg=bg):
                    self.assertGreaterEqual(contrast(t[fg], t[bg]), 4.5, f"{theme}: {fg} on {bg}")

    def test_white_on_button_fills_meets_aa(self):
        for theme in ("light", "dark"):
            t = _tokens(theme)
            for fill in ("btn-bg", "btn-bg-hover", "btn-bg-active"):
                with self.subTest(theme=theme, fill=fill):
                    self.assertGreaterEqual(contrast("#ffffff", t[fill]), 4.5)

    def test_focus_ring_visible_against_background(self):
        for theme in ("light", "dark"):
            t = _tokens(theme)
            self.assertGreaterEqual(contrast(t["color-accent"], t["color-bg"]), 3.0, theme)

    def test_terminal_text_readable_in_both_themes(self):
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        code = dict(re.findall(r"--(code-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css))
        for theme in ("light", "dark"):
            bg = _tokens(theme)["color-code-bg"]
            for name in ("code-muted", "code-accent", "code-accent-2", "code-warn"):
                with self.subTest(theme=theme, token=name):
                    self.assertGreaterEqual(contrast(code[name], bg), 4.5)

    def test_white_text_only_sits_on_button_fills(self):
        css = (WEB / "styles.css").read_text(encoding="utf-8")
        for rule in re.findall(r"\{[^}]*color: #fff[^}]*\}", css):
            with self.subTest(rule=rule):
                self.assertRegex(rule, r"var\(--btn-bg(-hover|-active)?\)")


class TestSiteData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("node") is None:
            raise unittest.SkipTest("node is not installed")
        subprocess.run(["node", str(WEB / "build-data.js")], check=True, capture_output=True)
        text = (WEB / "data.js").read_text(encoding="utf-8")
        cls.data = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))

    def test_counts_match_repository(self):
        skills = [p for p in (ROOT / "skills").iterdir() if (p / "skill.json").exists()]
        vendored = [p for p in (ROOT / "vendor" / "skills").iterdir() if p.is_dir()]
        self.assertEqual(self.data["counts"]["skills"], len(skills))
        self.assertEqual(self.data["counts"]["vendoredSkills"], len(vendored))
        self.assertEqual(self.data["counts"]["agents"], len(list((ROOT / "agents").rglob("agent.json"))))

    def test_every_skill_is_grouped_once(self):
        ids = [k["id"] for g in self.data["skillGroups"] for k in g["skills"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), self.data["counts"]["skills"] + self.data["counts"]["vendoredSkills"])

    def test_validation_numbers_come_from_report(self):
        report = json.loads((ROOT / "validation" / "reports" / "master_validation_report.json").read_text())
        self.assertEqual(self.data["validation"]["totalRun"], report["totalRun"])

    def test_sessions_come_from_memory(self):
        files = sorted(p.name for p in (ROOT / "memory" / "council-briefs").glob("*.json"))
        self.assertEqual(sorted(Path(s["path"]).name for s in self.data["sessions"]), files)

    def test_demo_plans_come_from_the_dispatcher(self):
        from core.orchestrator.dispatch import dispatch
        for sc in self.data["demo"]:
            for turn in sc["turns"]:
                with self.subTest(task=turn["task"]):
                    live = dispatch(turn["task"], council=turn.get("council"), include=turn.get("include"))
                    if turn.get("sessionId"):
                        record = json.loads((ROOT / "memory" / "council-briefs" / f"{turn['sessionId']}.json").read_text())
                        planned = [m["personaId"] for m in live["sessions"][0]["convened"]] if live.get("sessions") else []
                        if record["councilId"] == (live["councils"] or [None])[0]:
                            self.assertEqual(sorted(planned), sorted(m["personaId"] for m in record["convened"]),
                                             "the demo plan must convene the same personas as the recorded session")
                    self.assertEqual(turn["plan"]["tier"], live["tier"])
                    self.assertEqual(turn["plan"]["councils"], live["councils"])
                    if turn.get("sessionId"):
                        self.assertTrue((ROOT / "memory" / "council-briefs" / f"{turn['sessionId']}.json").exists())

    def test_install_commands_use_the_repository_cli(self):
        self.assertEqual(self.data["install"]["init"], "npx -y @sahasbelbase/project-intelligence init")
        self.assertEqual(self.data["install"]["plugin"]["install"], "claude plugin install project-intelligence@sahasbelbase")
        self.assertNotIn("npx project-intelligence", json.dumps(self.data["install"]))


class TestAdvisorFacts(unittest.TestCase):
    """The advisor must only state things that exist in the repository."""

    def test_no_invented_paths_gates_or_placeholders(self):
        src = (WEB / "app.js").read_text(encoding="utf-8")
        for bad in ["contracts/${gId", "Next lifecycle gate", "G7", "contracts/g0/", "'$ /"]:
            with self.subTest(pattern=bad):
                self.assertNotIn(bad, src)

    def test_every_gate_has_a_real_contract_path(self):
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        subprocess.run(["node", str(WEB / "build-data.js")], check=True, capture_output=True)
        text = (WEB / "data.js").read_text(encoding="utf-8")
        data = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
        for gate in data["gates"]:
            with self.subTest(gate=gate["id"]):
                self.assertIsNotNone(gate.get("contract"))
                self.assertTrue((ROOT / gate["contract"]["path"]).exists(), gate["contract"]["path"])


class TestNoHardcodedClaims(unittest.TestCase):
    def test_site_source_has_no_fixed_metrics_or_slogans(self):
        source = "\n".join((WEB / f).read_text(encoding="utf-8") for f in ("index.html", "app.js", "styles.css"))
        for pattern in [r"\d+/\d+ Tests", r"82\.4%", "Zero Hallucination", "Zero Guesswork", "cdn.tailwindcss.com", r"onclick="]:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, source, re.I), pattern)


if __name__ == "__main__":
    unittest.main()
