# Multi-agent evaluation

Score a multi-agent run on what it cost, how long it took, and whether the agents told each other things the record actually supports. It reads plain JSON traces, so it works with any framework (LangGraph, AutoGen, CrewAI, a hand-written loop) and needs only Python 3.10+. No model is called and nothing leaves your machine.

## Try it in two minutes

```bash
npx -y @sahasbelbase/project-intelligence eval core/eval/examples
# from a clone: python3 -m core.eval core/eval/examples
```

The folder holds two runs of the same task. `clean-run` scores clean. `planted-problems` has a handoff that cites a file nobody saw, a function nobody mentioned, test and file counts nothing supports, and missing required fields. The report lists each one.

## What you get

| Metric | Meaning |
|---|---|
| Tokens in/out, cost | Provider-reported when the trace has them. Otherwise estimated at about 4 characters per token and marked `estimated` (`*` in the table). Pass `--price-in` and `--price-out` (dollars per million tokens) for cost. |
| Time | Sum of step durations, and wall clock when steps carry `startedAt` and `endedAt`. |
| Unsupported-claim rate | Unsupported claims divided by claims checked across all handoffs. `n/a` when a run has no claims, never a misleading 0%. |
| Handoff fidelity | Share of a handoff's `requiredFields` that arrived non-empty. |
| Task success | Whether the final output contains every string in `expected.finalContains`. |

Results are grouped by `model`, so two models on the same task suite compare side by side.

## Trace format

```json
{
  "runId": "run-1",
  "task": "Fix the null check in src/parser.py",
  "model": "my-model",
  "workspace": "/path/the/agents/worked/in",
  "expected": { "finalContains": ["tests pass"] },
  "steps": [
    {
      "stepId": "s1", "agent": "explorer", "durationMs": 2100, "tokensIn": 1200, "tokensOut": 260,
      "toolOutputs": [{ "tool": "grep", "output": "src/parser.py:42: if value == None:" }],
      "output": "The bug is in src/parser.py line 42.",
      "handoff": { "to": "s2", "requiredFields": ["file", "line"], "payload": { "file": "src/parser.py", "line": "42" } },
      "claims": [{ "text": "bug is at line 42", "evidence": ["src/parser.py:42"] }]
    }
  ]
}
```

Only `steps`, and `stepId` and `agent` on each step, are required. A `.jsonl` file holds one run per line. Bad traces fail with a message naming the field.

## How a claim is checked

For each handoff the checker finds claims two ways: the ones the step lists explicitly with quoted `evidence`, and the ones it extracts from the handoff payload (file paths, `backticked` identifiers, and counts with a unit such as `12 passed` or `3 files`).

A claim is supported when it appears in what the sender could have seen: the task, every earlier step's output, and every tool output up to and including the sender's step. The sender's own output does not count as evidence for itself. A cited file is also supported if it exists inside `--workspace`; a path that escapes the workspace does not count.

## Limits, stated plainly

- **Unsupported is not fabricated.** It means nothing in the trace backs the claim. An agent may have read something the trace did not record. Treat the rate as a review flag.
- **It checks literals, not meaning.** A claim worded differently from its evidence reads as unsupported, and a true-looking number that happens to appear elsewhere reads as supported.
- **Only handoffs are checked.** Text an agent keeps to itself is not scored.
- **Estimated tokens are rough.** Use provider-reported counts for anything you publish.
- **Not yet included:** live execution of agents, an optional model-as-judge, and holdout task suites. Traces come from your own runs.

## CI use

`--max-unsupported 0.1` exits 1 when any run's unsupported-claim rate is above 10%. Exit 2 means the traces could not be read. `--format json` and `--out report.json` are there for scripts.
