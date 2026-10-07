# Project Intelligence — Model Context Protocol (MCP) Adapter

This adapter exposes the canonical capabilities of Project Intelligence—deterministic lifecycle gates (G0–G6), JSON contract validation, anti-slop and verification quality evaluations, Git-aware 3-tier memory, and allowlisted check execution—to AI coding assistants and IDEs via the **Model Context Protocol (MCP)**.

---

## 1. Architectural Overview

The MCP adapter is designed as a **thin, zero-trust reference monitor** around the core framework:
- **Core Stays Canonical**: All state transitions (`core/lifecycle/engine.py`), quality rules (`core/quality/evaluator.py`), memory reconciliation (`memory/reconciliation-rules/reconciler.py`), and schemas (`core/schemas/`) remain strictly in the core engine.
- **Adapter Responsibilities**: Validates client requests, enforces workspace boundaries (SR-001/002), sanitizes outputs against secret leakage (SR-003), restricts Git operations to read-only queries (SR-004), caps subprocess execution to an explicit allowlist (SR-005/006), and formats JSON-RPC 2.0 messages.
- **Zero Runtime Dependencies**: Written entirely using the Python 3.10+ standard library. While compatible with the official `mcp` Python SDK when installed, it operates independently with zero pip dependencies on environments (such as Python 3.14) where binary wheels may be unavailable.

```
┌────────────────────────────────────────────────────────┐
│                   MCP Client / Host                    │
│   (Claude Desktop, Claude Code, Cursor, Cline, etc.)   │
└───────────────────────────┬────────────────────────────┘
                            │ stdio (JSON-RPC 2.0)
                            ▼
┌────────────────────────────────────────────────────────┐
│             adapters/mcp/server.py                     │
│  - Protocol Handshake & Dispatch                       │
│  - Zero-Dependency stdio Engine                        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────┼────────────────────────────┐
│ adapters/mcp/security.py  │ adapters/mcp/validator.py  │
│  - Path Traversal Guard   │  - Contract Envelopes      │
│  - Secret Scrubber        │  - Payload Validation      │
│  - Safe Subprocess Runner │  - DAG Acyclicity Checker  │
└───────────────────────────┼────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             adapters/mcp/tools.py                      │
│     (10 Canonical Project Intelligence Tools)          │
└───────────┬───────────────┬────────────────┬───────────┘
            │               │                │
            ▼               ▼                ▼
     core/lifecycle/   core/quality/      memory/
```

---

## 2. Supported Tools and Permissions

The server registers 10 canonical tools categorized into **6 Read-Only Tools** and **4 Proposed-Action Tools**:

| Tool Name | Type | Description | Disk / Git Side Effects |
|---|---|---|---|
| `project_status` | **Read-Only** | Returns verified lifecycle gate, task state, blockers, and git alignment. | **None** |
| `inspect_project` | **Read-Only** | Returns bounded summary of repository layout, standing instructions, and Git status. | **None** |
| `get_next_action` | **Read-Only** | Evaluates current gate and contract status to identify next required action and transitions. | **None** |
| `validate_contract` | **Read-Only** | Validates contract files or in-memory JSON envelopes against core schemas. | **None** |
| `evaluate_quality` | **Read-Only** | Scans code for anti-slop violations (placeholders, emojis) and checks verification honesty. | **None** |
| `get_project_memory` | **Read-Only** | Bounded retrieval of durable knowledge, execution state, or backlog with secrets redacted. | **None** |
| `create_work_plan` | **Proposed-Action** | Validates WBS implementation plan and DAG acyclicity; preview in `dry_run=True`, atomic write to `contracts/implementation/contract.json` when `dry_run=False`. | Atomic file creation in `contracts/implementation/` |
| `advance_lifecycle_gate` | **Proposed-Action** | Requests FSM gate advance; validates contract prerequisites and human approvals; atomic update to `memory/execution-state.json` when `dry_run=False`. | Atomic update to `memory/execution-state.json` |
| `reconcile_project_memory`| **Proposed-Action** | Inspects Git status/log and reconciles execution state; preview mode when `update_mode=False`, atomic write preserving human edits when `update_mode=True`. | Atomic update to `memory/execution-state.json` |
| `run_project_checks` | **Proposed-Action** | Executes allowlisted verification checks (`all_tests`, `schemas`, `lifecycle`, `quality`, `memory`, `adapters`, `reconciler`) with timeouts. | Executes test suite subprocess |

---

## 3. Security Invariants (SR-001 through SR-008)

1. **SR-001: Workspace Boundary Invariance**: All file operations resolve strictly within the canonical `workspace_root`. Traversals (`../`), root escapes (`/etc/passwd`), or path resets raise `PathTraversalError`.
2. **SR-002: Symlink Containment**: Symlinks pointing outside the authorized workspace are rejected immediately.
3. **SR-003: Zero Secret Leakage**: All responses pass through `SecretScrubber` scanning for 12 token patterns (Google, OpenAI, Anthropic, GitHub, AWS, Slack, Private Keys, etc.). Detected secrets are replaced with `[REDACTED:<PATTERN>]` without revealing edge characters.
4. **SR-004: Read-Only Git Policy**: Git interaction is restricted to query commands (`status`, `diff`, `log`, `rev-parse`, `show`). Destructive commands (`reset`, `clean`, `commit`, `push`, `checkout`) raise `SecurityError`.
5. **SR-005: Allowlisted Subprocess Execution**: Subprocess commands are strictly mapped from pre-approved enum identifiers. Arbitrary shell strings and `shell=True` are strictly prohibited.
6. **SR-006: Subprocess Bounds**: Every subprocess is bound by a maximum timeout (default 30s) and bounded output buffer (50,000 characters).
7. **SR-007: Writable Confinement**: Write operations are strictly confined to designated mutable locations (`memory/`, `contracts/`). Immutable assets (`core/schemas/`, `instructions/`) are locked.
8. **SR-008: Sanitized Error Messages**: Exceptions are sanitized of paths and secret patterns before serialization to the client.

---

## 4. Local Installation and Startup

### Prerequisites
- Python 3.10+ (Python 3.10, 3.11, 3.12, 3.13, 3.14+).
- Git installed and on PATH.

### Installation
Because the server is written with standard library Python, no external package installation is required:
```bash
# Verify Python version
python3 --version
```

*(Optional)* If you wish to use the official `mcp` SDK package in environments where binary wheels are available:
```bash
pip install "mcp>=1.2.0"
```

### Protocol Smoke Verification
Run the built-in self-test smoke verification:
```bash
python3 adapters/mcp/server.py --test-smoke
```
Expected output:
```
Smoke test PASSED! Verified 10 tools registered.
```

### Running the Server
The server communicates over standard input/output (`stdio`):
```bash
python3 adapters/mcp/server.py --workspace-root /path/to/project-intelligence
```

---

## 5. Client Configuration Examples

### 5.1 Claude Desktop
Add to `claude_desktop_config.json`:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "project-intelligence": {
      "command": "python3",
      "args": [
        "/path/to/project-intelligence/adapters/mcp/server.py",
        "--workspace-root",
        "/path/to/project-intelligence"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 5.2 Claude Code (Anthropic CLI)
In the project root:
```bash
claude mcp add --transport stdio --scope project project-intelligence python3 adapters/mcp/server.py
```
Or create `.mcp.json` in the project root:
```json
{
  "mcpServers": {
    "project-intelligence": {
      "command": "python3",
      "args": [
        "adapters/mcp/server.py"
      ]
    }
  }
}
```

### 5.3 Cursor
Add to `.cursor/mcp.json` in your workspace root:
```json
{
  "mcpServers": {
    "project-intelligence": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/adapters/mcp/server.py",
        "--workspace-root",
        "${workspaceFolder}"
      ]
    }
  }
}
```

### 5.4 Cline / Roo Code (VS Code Extension)
In `cline_mcp_settings.json`:
```json
{
  "mcpServers": {
    "project-intelligence": {
      "command": "python3",
      "args": [
        "/path/to/project-intelligence/adapters/mcp/server.py",
        "--workspace-root",
        "/path/to/project-intelligence"
      ],
      "disabled": false,
      "autoApprove": [
        "project_status",
        "inspect_project",
        "get_next_action",
        "validate_contract",
        "evaluate_quality",
        "get_project_memory"
      ]
    }
  }
}
```

### 5.5 Zed Editor
In `~/.config/zed/settings.json`:
```json
{
  "context_servers": {
    "project-intelligence": {
      "command": {
        "path": "python3",
        "args": [
          "/path/to/project-intelligence/adapters/mcp/server.py",
          "--workspace-root",
          "/path/to/project-intelligence"
        ]
      }
    }
  }
}
```

---

## 6. Verification and Test Suite

Execute the master framework validation runner (includes all 5 canonical test suites and the new MCP test suite):
```bash
python3 validation/test_runner.py
```

Run MCP-specific test suites directly:
```bash
python3 -m unittest discover -s validation/mcp-tests -p "test_*.py" -v
```

---

## 7. Troubleshooting & Diagnostics

1. **"Method not found (-32601)" on Client Connect**:
   Verify that your client sends `"method": "tools/list"` and `"method": "tools/call"`. Confirm the server was initialized via `initialize`.
2. **Client Hangs During Handshake**:
   Ensure no `print()` statements write to `sys.stdout`. The MCP `stdio` wire is strictly line-delimited JSON. All diagnostic logging is routed to `sys.stderr`.
3. **"Security Violation: Path escapes authorized workspace"**:
   Paths passed to `inspect_project` or `validate_contract` must reside within the `--workspace-root`. Ensure symlinks do not target directories outside the repository.
4. **"Transition blocked: requires explicit human approval"**:
   Certain lifecycle transitions (such as G0 -> G1 or G3 -> G4) require human sign-off per ADR-0002. Provide the `approved_by` argument when invoking `advance_lifecycle_gate`.

---

## 8. Remote ChatGPT & Cloud Readiness (Phase 2)

While the initial integration operates over local `stdio`, the MCP server architecture is fully portable for future remote deployment:
- **Transport**: Remote deployment requires upgrading to **Streamable HTTP** (or HTTP+SSE) using Starlette/Uvicorn.
- **Authentication**: Requires OAuth 2.0 authorization server integration or signed bearer tokens (`Authorization: Bearer <token>`).
- **Authorization**: Tool-level role-based access control (RBAC) to restrict proposed-action tools (`advance_lifecycle_gate`, `create_work_plan`) to authorized human identities.
- **Hosting & Tunneling**: Secure HTTPS termination via Cloudflare Tunnel, GCP Cloud Run, or AWS Lambda with session management (`Mcp-Session-Id`).
- **Tool Risk Review**: Cloud exposure requires pre-execution human confirmation webhooks for mutating operations.
