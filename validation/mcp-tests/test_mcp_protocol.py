"""
Project Intelligence — MCP Protocol-Level Wire Smoke Tests
Executes end-to-end stdio JSON-RPC 2.0 communication against adapters/mcp/server.py
using standard library subprocess and pipes.
Verifies protocol initialization, notifications, tool discovery, tool invocation,
error handling, and clean EOF teardown.
Uses Python standard library with zero external dependencies.
"""

import unittest
from pathlib import Path
import sys
import subprocess
import json
import time

project_root = Path(__file__).resolve().parents[2]


class TestMCPProtocolSmoke(unittest.TestCase):
    def setUp(self):
        # Spawn the server as a background subprocess over stdio
        self.proc = subprocess.Popen(
            [sys.executable, "adapters/mcp/server.py"],
            cwd=str(project_root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )

    def tearDown(self):
        if self.proc.stdin:
            try:
                self.proc.stdin.close()
            except Exception:
                pass
        if self.proc.stdout:
            try:
                self.proc.stdout.close()
            except Exception:
                pass
        if self.proc.stderr:
            try:
                self.proc.stderr.close()
            except Exception:
                pass
        if self.proc.poll() is None:
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()

    def _send_and_receive(self, request_dict: dict, timeout_seconds: float = 5.0) -> dict:
        """Sends a JSON-RPC request line and reads the response line."""
        req_line = json.dumps(request_dict) + "\n"
        self.proc.stdin.write(req_line)
        self.proc.stdin.flush()

        # Read line from stdout
        resp_line = self.proc.stdout.readline()
        if not resp_line:
            stderr_out = self.proc.stderr.read()
            raise RuntimeError(f"Server closed connection unexpectedly. Stderr: {stderr_out}")

        return json.loads(resp_line.strip())

    def test_full_protocol_wire_lifecycle(self):
        """Test full JSON-RPC 2.0 wire lifecycle over stdio."""
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "test-runner", "version": "1.0.0"},
            },
        }
        init_resp = self._send_and_receive(init_req)
        self.assertEqual(init_resp.get("jsonrpc"), "2.0")
        self.assertEqual(init_resp.get("id"), 1)
        res = init_resp.get("result", {})
        self.assertEqual(res.get("serverInfo", {}).get("name"), "project-intelligence")
        self.assertIn("tools", res.get("capabilities", {}))

        # 2. Notification (notifications/initialized)
        # Server should NOT reply to notifications
        notif_req = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        self.proc.stdin.write(json.dumps(notif_req) + "\n")
        self.proc.stdin.flush()

        # 3. Ping
        ping_req = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
        ping_resp = self._send_and_receive(ping_req)
        self.assertEqual(ping_resp.get("id"), 2)
        self.assertEqual(ping_resp.get("result"), {})

        # 4. Tools list
        list_req = {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}
        list_resp = self._send_and_receive(list_req)
        tools = list_resp.get("result", {}).get("tools", [])
        self.assertEqual(len(tools), 11, f"Expected 11 tools, got {len(tools)}")
        tool_names = [t["name"] for t in tools]
        self.assertIn("project_status", tool_names)
        self.assertIn("run_project_checks", tool_names)

        # 5. Tools call: project_status
        call_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "project_status", "arguments": {}},
        }
        call_resp = self._send_and_receive(call_req)
        self.assertEqual(call_resp.get("id"), 4)
        call_result = call_resp.get("result", {})
        self.assertFalse(call_result.get("isError"))
        content = call_result.get("content", [])
        self.assertTrue(len(content) > 0)
        parsed_status = json.loads(content[0]["text"])
        with open(project_root / "memory" / "execution-state.json", "r", encoding="utf-8") as f:
            live_gate = json.load(f)["currentGate"]
        self.assertEqual(parsed_status["lifecycle"]["currentGate"], live_gate)

        # 6. Tools call: unknown tool -> Method/Tool Not Found Error (-32601)
        bad_tool_req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "non_existent_tool", "arguments": {}},
        }
        bad_tool_resp = self._send_and_receive(bad_tool_req)
        self.assertEqual(bad_tool_resp.get("id"), 5)
        self.assertIn("error", bad_tool_resp)
        self.assertEqual(bad_tool_resp["error"]["code"], -32601)

        # 7. Tools call: missing required arguments -> -32602
        missing_args_req = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "advance_lifecycle_gate", "arguments": {}},
        }
        missing_args_resp = self._send_and_receive(missing_args_req)
        self.assertEqual(missing_args_resp.get("id"), 6)
        self.assertIn("error", missing_args_resp)
        self.assertEqual(missing_args_resp["error"]["code"], -32602)

        # 8. Malformed JSON -> -32700
        self.proc.stdin.write("INVALID JSON NOT A DICT\n")
        self.proc.stdin.flush()
        parse_err_resp = json.loads(self.proc.stdout.readline().strip())
        self.assertEqual(parse_err_resp.get("error", {}).get("code"), -32700)

        # 9. Clean shutdown on stdin close
        self.proc.stdin.close()
        exit_code = self.proc.wait(timeout=3)
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
