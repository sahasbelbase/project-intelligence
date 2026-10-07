"""
Project Intelligence — Model Context Protocol (MCP) Server
Main entrypoint providing stdio JSON-RPC 2.0 communication.
Exposes the 10 canonical Project Intelligence tools.
Conformance: Python 3.10+ standard library.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys
from typing import Any, Callable, Dict, List, Optional

# Ensure standard IO streams are in unbuffered UTF-8 mode
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Direct all diagnostic logs to stderr only (stdout is strictly JSON-RPC messages)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [project-intelligence-mcp]: %(message)s",
)
logger = logging.getLogger("project_intelligence_mcp")

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from adapters.mcp.security import SecretScrubber, SecurityError
from adapters.mcp.tools import ProjectIntelligenceTools


class MCPServer:
    """Specification-compliant Model Context Protocol Server (stdio transport)."""

    PROTOCOL_VERSIONS = ["2024-11-05", "2025-03-26"]

    def __init__(
        self,
        workspace_root: Optional[pathlib.Path] = None,
        name: str = "project-intelligence",
        version: str = "1.0.0",
    ):
        self.name = name
        self.version = version
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.tools_handler = ProjectIntelligenceTools(self.workspace_root)
        self.is_initialized = False

        self.tools_registry: Dict[str, Dict[str, Any]] = {}
        self._register_canonical_tools()

    def _register_canonical_tools(self) -> None:
        """Registers the 10 canonical tools with schemas and handler callbacks."""

        # 1. project_status
        self.register_tool(
            name="project_status",
            description="Return the verified lifecycle gate, task state, blockers, and available next actions using actual repository data.",
            schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=lambda: self.tools_handler.project_status(),
            is_read_only=True,
        )

        # 2. inspect_project
        self.register_tool(
            name="inspect_project",
            description="Inspect a caller-specified project root within an explicitly authorized workspace boundary. Return a bounded summary of relevant repository structure, project instructions, and Git state.",
            schema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Optional directory path within authorized workspace boundary (defaults to workspace root)",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum directory traversal depth (default 2, max 4)",
                        "default": 2,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.inspect_project(**kwargs),
            is_read_only=True,
        )

        # 3. get_next_action
        self.register_tool(
            name="get_next_action",
            description="Use the actual lifecycle engine and contract state to identify the next valid action, its prerequisites, and required approvals.",
            schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=lambda: self.tools_handler.get_next_action(),
            is_read_only=True,
        )

        # 4. validate_contract
        self.register_tool(
            name="validate_contract",
            description="Validate a specified contract using existing schemas and validation logic. Return structured errors and actual validation result.",
            schema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Workspace-relative path to contract file, e.g. contracts/project/contract.json",
                    },
                    "contract_type": {
                        "type": "string",
                        "enum": [
                            "project",
                            "requirements",
                            "design",
                            "architecture",
                            "implementation",
                            "quality",
                            "release",
                        ],
                        "description": "Contract type shorthand",
                    },
                    "contract_data": {
                        "type": "object",
                        "description": "In-memory contract JSON object to validate directly",
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.validate_contract(**kwargs),
            is_read_only=True,
        )

        # 5. evaluate_quality
        self.register_tool(
            name="evaluate_quality",
            description="Invoke the existing quality evaluator where supported. Return selected profile, checks performed (anti-slop, verification honesty), check statuses, and evidence.",
            schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Text or code snippet to scan for anti-slop violations",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Workspace-relative file path to scan for anti-slop",
                    },
                    "profile_name": {
                        "type": "string",
                        "enum": [
                            "PROTOTYPE",
                            "STANDARD",
                            "PRODUCTION_READY",
                            "SECURITY_SENSITIVE",
                            "DESIGN_INTENSIVE",
                        ],
                        "description": "Target quality profile name",
                        "default": "STANDARD",
                    },
                    "verification_suites": {
                        "type": "array",
                        "description": "Array of verification suite check results to test for verification honesty",
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.evaluate_quality(**kwargs),
            is_read_only=True,
        )

        # 6. get_project_memory
        self.register_tool(
            name="get_project_memory",
            description="Read selected durable knowledge, execution state, and backlog records with bounded retrieval.",
            schema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": [
                            "summary",
                            "all",
                            "durable_knowledge",
                            "execution_state",
                            "backlog",
                        ],
                        "description": "Target memory section",
                        "default": "summary",
                    },
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of items to return per section (default 10, max 50)",
                        "default": 10,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.get_project_memory(**kwargs),
            is_read_only=True,
        )

        # 7. create_work_plan
        self.register_tool(
            name="create_work_plan",
            description="Create a proposed work breakdown structure plan based on approved requirements. Keep result in draft form unless explicitly authorizing persistence.",
            schema={
                "type": "object",
                "required": [
                    "workstream_id",
                    "title",
                    "assigned_agent_role",
                    "phases",
                    "tasks",
                    "file_ownership",
                ],
                "properties": {
                    "workstream_id": {
                        "type": "string",
                        "description": "Workstream ID, e.g. WS-08",
                    },
                    "title": {
                        "type": "string",
                        "description": "Plan title",
                    },
                    "assigned_agent_role": {
                        "type": "string",
                        "description": "Role of the executing agent",
                    },
                    "phases": {
                        "type": "array",
                        "description": "List of phases with phaseNumber, name, goal",
                    },
                    "tasks": {
                        "type": "array",
                        "description": "List of tasks conforming to implementation contract schema",
                    },
                    "file_ownership": {
                        "type": "array",
                        "description": "List of pathPattern and exclusiveOwnerRole mappings",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, validates and returns plan without writing to disk (default true)",
                        "default": True,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.create_work_plan(**kwargs),
            is_read_only=False,
        )

        # 8. advance_lifecycle_gate
        self.register_tool(
            name="advance_lifecycle_gate",
            description="Request a transition through the existing lifecycle engine. Enforces prerequisites, valid transitions, required approvals, and contract validation.",
            schema={
                "type": "object",
                "required": ["target_gate", "condition"],
                "properties": {
                    "target_gate": {
                        "type": "string",
                        "enum": ["G0", "G1", "G2", "G3", "G4", "G5", "G6"],
                        "description": "Target lifecycle gate to advance to",
                    },
                    "condition": {
                        "type": "string",
                        "description": "Transition condition name matching FSM (e.g. G0_APPROVED)",
                    },
                    "approved_by": {
                        "type": "string",
                        "description": "Name or identifier of human approving transition when required",
                    },
                    "is_exempt": {
                        "type": "boolean",
                        "description": "Set true if formally exempting G2 (Design)",
                        "default": False,
                    },
                    "exemption_justification": {
                        "type": "string",
                        "description": "Documented justification for G2 exemption (min 10 chars)",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, simulates transition without persisting state (default true)",
                        "default": True,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.advance_lifecycle_gate(**kwargs),
            is_read_only=False,
        )

        # 9. reconcile_project_memory
        self.register_tool(
            name="reconcile_project_memory",
            description="Reconcile Git status and execution memory using existing reconciler. Supports preview/dry-run mode before persisting changes. Preserves uncommitted human work and never stores secrets.",
            schema={
                "type": "object",
                "properties": {
                    "update_mode": {
                        "type": "boolean",
                        "description": "If true, persists reconciled git commit and state to memory/execution-state.json (default false)",
                        "default": False,
                    },
                    "repair_mode": {
                        "type": "boolean",
                        "description": "If true, repairs missing or damaged execution state from template",
                        "default": False,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.reconcile_project_memory(**kwargs),
            is_read_only=False,
        )

        # 10. run_project_checks
        self.register_tool(
            name="run_project_checks",
            description="Run approved, project-configured verification commands using an explicit allowlist, bounded output, timeouts, and safe working-directory rules.",
            schema={
                "type": "object",
                "properties": {
                    "check_type": {
                        "type": "string",
                        "enum": [
                            "all_tests",
                            "schemas",
                            "lifecycle",
                            "quality",
                            "memory",
                            "adapters",
                            "reconciler",
                        ],
                        "description": "Configured verification check identifier",
                        "default": "all_tests",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum execution timeout in seconds (default 30, max 60)",
                        "default": 30,
                    },
                },
                "additionalProperties": False,
            },
            handler=lambda **kwargs: self.tools_handler.run_project_checks(**kwargs),
            is_read_only=False,
        )

    def register_tool(
        self,
        name: str,
        description: str,
        schema: Dict[str, Any],
        handler: Callable[..., Any],
        is_read_only: bool = True,
    ) -> None:
        """Registers a tool with metadata and callback handler."""
        self.tools_registry[name] = {
            "name": name,
            "description": description,
            "inputSchema": schema,
            "handler": handler,
            "isReadOnly": is_read_only,
        }
        logger.debug(f"Registered MCP tool: {name} (read_only={is_read_only})")

    def send_response(self, response: Dict[str, Any]) -> None:
        """Serializes and flushes a single JSON-RPC response to stdout."""
        serialized = json.dumps(response, ensure_ascii=False) + "\n"
        sys.stdout.write(serialized)
        sys.stdout.flush()

    def handle_message(self, line: str) -> Optional[Dict[str, Any]]:
        """Processes a single line-delimited JSON-RPC 2.0 message."""
        line = line.strip()
        if not line:
            return None

        try:
            req = json.loads(line)
        except json.JSONDecodeError as err:
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(err)}",
                },
            }
            self.send_response(resp)
            return resp

        if not isinstance(req, dict):
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: root must be a JSON object",
                },
            }
            self.send_response(resp)
            return resp

        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Notifications (no id field)
        if msg_id is None:
            if method == "notifications/initialized":
                self.is_initialized = True
                logger.info("Client initialization handshake completed.")
            elif method == "notifications/cancelled":
                logger.info(f"Client cancelled operation: {params}")
            return None

        # Request Handling
        if method == "initialize":
            client_proto = params.get("protocolVersion", "2024-11-05")
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": client_proto,
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version,
                    },
                },
            }
            self.send_response(resp)
            return resp

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            self.send_response(resp)
            return resp

        elif method == "tools/list":
            tools_list = [
                {
                    "name": t_name,
                    "description": t_info["description"],
                    "inputSchema": t_info["inputSchema"],
                }
                for t_name, t_info in sorted(self.tools_registry.items())
            ]
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": tools_list},
            }
            self.send_response(resp)
            return resp

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name or tool_name not in self.tools_registry:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found",
                    },
                }
                self.send_response(resp)
                return resp

            tool_entry = self.tools_registry[tool_name]
            handler = tool_entry["handler"]

            # Validate required arguments
            schema = tool_entry["inputSchema"]
            required_args = schema.get("required", [])
            missing = [r for r in required_args if r not in arguments]
            if missing:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32602,
                        "message": f"Missing required arguments for tool '{tool_name}': {missing}",
                    },
                }
                self.send_response(resp)
                return resp

            try:
                result_payload = handler(**arguments)
                text_content = (
                    json.dumps(result_payload, indent=2, ensure_ascii=False)
                    if isinstance(result_payload, (dict, list))
                    else str(result_payload)
                )
                clean_content = SecretScrubber.redact_secrets(text_content)

                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": clean_content}],
                        "isError": False,
                    },
                }
                self.send_response(resp)
                return resp

            except Exception as exc:
                clean_err = SecretScrubber.sanitize_error(exc)
                logger.warning(f"Tool execution exception in '{tool_name}': {clean_err}")
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {clean_err}"}],
                        "isError": True,
                    },
                }
                self.send_response(resp)
                return resp

        else:
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not supported: '{method}'",
                },
            }
            self.send_response(resp)
            return resp

    def run(self) -> None:
        """Main stdio read loop."""
        logger.info(f"Starting {self.name} v{self.version} MCP server on stdio transport...")
        try:
            for line in sys.stdin:
                self.handle_message(line)
        except KeyboardInterrupt:
            logger.info("Server terminated by signal.")
        except Exception as exc:
            logger.exception(f"Fatal exception in stdio loop: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project Intelligence Model Context Protocol (MCP) Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--workspace-root",
        type=pathlib.Path,
        default=WORKSPACE_ROOT,
        help="Path to authorized workspace repository root",
    )
    parser.add_argument(
        "--test-smoke",
        action="store_true",
        help="Run protocol self-test smoke verification and exit",
    )

    args = parser.parse_args()

    server = MCPServer(workspace_root=args.workspace_root)

    if args.test_smoke:
        # Run in-process handshake smoke test
        print("Running in-process MCP server smoke test...", file=sys.stderr)
        init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}})
        resp1 = server.handle_message(init_req)
        assert resp1 and resp1.get("result", {}).get("serverInfo", {}).get("name") == "project-intelligence"

        list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        resp2 = server.handle_message(list_req)
        tools = resp2.get("result", {}).get("tools", [])
        assert len(tools) == 10, f"Expected 10 tools, found {len(tools)}"

        status_req = json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "project_status", "arguments": {}}})
        resp3 = server.handle_message(status_req)
        assert resp3 and not resp3.get("result", {}).get("isError")

        print(f"Smoke test PASSED! Verified {len(tools)} tools registered.", file=sys.stderr)
        return 0

    server.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
