"""Project Intelligence - Eval Report: JSON and Markdown output, plus the CLI (python3 -m core.eval)."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.eval.metrics import evaluate_trace, summarize  # noqa: E402
from core.eval.trace import TraceError, load_traces  # noqa: E402


def _fmt(value: Any, suffix: str = "", pct: bool = False) -> str:
    if value is None:
        return "n/a"
    if pct:
        return f"{value * 100:.1f}%"
    return f"{value:,.1f}{suffix}" if isinstance(value, float) else f"{value:,}{suffix}"


def render_markdown(results: List[Dict[str, Any]], summary: Dict[str, Dict[str, Any]]) -> str:
    lines = ["# Multi-agent evaluation", "", "## By model", "",
             "| Model | Runs | Mean tokens | Mean cost (USD) | Mean time (ms) | Unsupported claims | Handoff fidelity | Task success |",
             "|---|---|---|---|---|---|---|---|"]
    for model, s in summary.items():
        flag = " *" if s["anyTokensEstimated"] else ""
        lines.append(f"| {model} | {s['runs']} | {_fmt(s['meanTokensTotal'])}{flag} | {'n/a' if s['meanCostUsd'] is None else '$%.4f' % s['meanCostUsd']} | {_fmt(s['meanWallClockMs'])} | "
                     f"{_fmt(s['unsupportedClaimRate'], pct=True)} | {_fmt(s['meanHandoffFidelity'], pct=True)} | {_fmt(s['taskSuccessRate'], pct=True)} |")
    if any(s["anyTokensEstimated"] for s in summary.values()):
        lines += ["", "\\* Some token counts are estimated (about 4 characters per token), not provider-reported."]
    lines += ["", "## Runs", ""]
    for r in results:
        lines.append(f"### {r['runId']} ({r['model'] or 'unknown model'})")
        lines.append(f"- Tokens: {r['tokensTotal']:,} ({r['tokensIn']:,} in, {r['tokensOut']:,} out){' estimated' if r['tokensEstimated'] else ''}")
        lines.append(f"- Time: step total {_fmt(r['stepTimeMs'], ' ms')}, wall clock {_fmt(r['wallClockMs'], ' ms')}")
        lines.append(f"- Handoff claims: {r['handoffClaims']} checked, {r['unsupportedClaims']} unsupported ({_fmt(r['unsupportedClaimRate'], pct=True)})")
        lines.append(f"- Handoff fidelity: {_fmt(r['handoffFidelity'], pct=True)}; task success: {r['taskSuccess'] if r['taskSuccess'] is not None else 'n/a'}")
        for h in r["handoffs"]:
            for c in h["unsupported"]:
                lines.append(f"  - {h['from']} -> {h['to'] or '?'}: unsupported {c['kind']} `{c['text']}`")
            for f in h["missingFields"]:
                lines.append(f"  - {h['from']} -> {h['to'] or '?'}: missing required field `{f}`")
        lines.append("")
    lines += ["Unsupported means nothing in the trace backs the claim. It is a flag to review, not proof of fabrication."]
    return "\n".join(lines)


def run(paths: List[Path], workspace: Optional[Path], price_in: Optional[float], price_out: Optional[float]) -> Dict[str, Any]:
    traces = [t for p in paths for t in load_traces(p)]
    results = []
    for t in traces:
        ws = workspace or (Path(t["workspace"]) if t.get("workspace") else None)
        results.append(evaluate_trace(t, ws if ws and ws.is_dir() else None, price_in, price_out))
    return {"results": results, "summary": summarize(results)}


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m core.eval", description="Score multi-agent run traces: tokens, time, handoff claims, fidelity, success.")
    parser.add_argument("traces", nargs="+", type=Path, help="Trace .json/.jsonl files or folders of them")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--workspace", type=Path, help="Folder the agents worked in, so cited files can be confirmed to exist")
    parser.add_argument("--price-in", type=float, help="Dollars per million input tokens")
    parser.add_argument("--price-out", type=float, help="Dollars per million output tokens")
    parser.add_argument("--max-unsupported", type=float, help="Exit 1 if the unsupported-claim rate of any run exceeds this (0 to 1)")
    parser.add_argument("--out", type=Path, help="Write the report to this file instead of printing it")
    args = parser.parse_args(argv)
    try:
        report = run(args.traces, args.workspace, args.price_in, args.price_out)
    except TraceError as err:
        print(str(err), file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2) if args.format == "json" else render_markdown(report["results"], report["summary"])
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.max_unsupported is not None:
        over = [r["runId"] for r in report["results"] if (r["unsupportedClaimRate"] or 0) > args.max_unsupported]
        if over:
            print(f"Unsupported-claim rate above {args.max_unsupported} in: {', '.join(over)}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
