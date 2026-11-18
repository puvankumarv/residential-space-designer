"""Tests for scripts/mcp_server.py and scripts/floor_plan_svg.py. Standard library only."""
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "residential-space-designer"
SERVER = SKILL / "scripts" / "mcp_server.py"
sys.path.insert(0, str(SKILL / "scripts"))
import floor_plan_svg  # noqa: E402
import mcp_server  # noqa: E402


def example(name):
    return json.loads((SKILL / "examples" / name).read_text())


def call(name, arguments=None):
    reply = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                               "params": {"name": name, "arguments": arguments or {}}})
    return reply["result"]


class TestProtocol(unittest.TestCase):
    """Drive the real process over stdio, as an MCP client would."""

    def session(self, *messages):
        lines = "\n".join(json.dumps(m) for m in messages) + "\n"
        r = subprocess.run([sys.executable, str(SERVER)], input=lines, capture_output=True, text=True, timeout=30)
        return [json.loads(l) for l in r.stdout.splitlines()]

    def test_handshake_and_tool_list(self):
        replies = self.session(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
        )
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])  # no reply to the notification
        init = replies[0]["result"]
        self.assertEqual(init["protocolVersion"], "2025-06-18")
        self.assertIn("tools", init["capabilities"])
        names = {t["name"] for t in replies[1]["result"]["tools"]}
        self.assertEqual(names, {"validate_layout", "floor_plan_svg", "layout_to_gltf", "get_layout_schema",
                                 "list_references", "read_reference"})
        self.assertEqual(replies[2]["result"], {})

    def test_unknown_protocol_gets_latest(self):
        r = self.session({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(r[0]["result"]["protocolVersion"], mcp_server.PROTOCOLS[0])

    def test_bad_input_does_not_kill_the_server(self):
        r = subprocess.run([sys.executable, str(SERVER)], capture_output=True, text=True, timeout=30,
                           input='not json\n{"jsonrpc":"2.0","id":7,"method":"nope"}\n{"jsonrpc":"2.0","id":8,"method":"ping"}\n')
        replies = [json.loads(l) for l in r.stdout.splitlines()]
        self.assertEqual(replies[0]["error"]["code"], -32700)
        self.assertEqual(replies[1]["error"]["code"], -32601)
        self.assertEqual(replies[2]["result"], {})

    def test_server_version_matches_plugin(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(mcp_server.SERVER_INFO["version"], plugin["version"])

    def test_plugin_registers_server(self):
        cfg = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["residential-space-designer"]
        script = cfg["args"][0].replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT))
        self.assertTrue(Path(script).exists(), script)


class TestTools(unittest.TestCase):
    def test_validate_ok(self):
        res = call("validate_layout", {"layout": example("galley-kitchen.json")})
        self.assertFalse(res["isError"])
        out = json.loads(res["content"][0]["text"])
        self.assertTrue(out["ok"])
        self.assertEqual(out["errors"], [])

    def test_validate_finds_errors_and_plans(self):
        L = example("twins-offset-loft.json")
        next(e for e in L["elements"] if e["id"] == "bed_upper")["guardrail"] = False
        out = json.loads(call("validate_layout", {"layout": L, "plan": True})["content"][0]["text"])
        self.assertFalse(out["ok"])
        self.assertTrue(any("without guardrails" in m for m in out["errors"]))
        self.assertIn("FLOOR LEVEL", out["plans"]["default"]["floor"])

    def test_validate_accepts_json_string(self):
        res = call("validate_layout", {"layout": json.dumps(example("galley-kitchen.json"))})
        self.assertTrue(json.loads(res["content"][0]["text"])["ok"])

    def test_validate_bad_input_is_tool_error(self):
        for bad in ("{oops", 42, {"room": {"width": 3}, "elements": [{"id": "x"}]}):
            with self.subTest(bad=bad):
                res = call("validate_layout", {"layout": bad})
                if res["isError"]:
                    self.assertTrue(res["content"][0]["text"])
                else:  # a partial layout is reported through the checker's own errors
                    self.assertFalse(json.loads(res["content"][0]["text"])["ok"])

    def test_floor_plan_svg(self):
        res = call("floor_plan_svg", {"layout": example("studio-apartment.json"), "state": "day"})
        self.assertFalse(res["isError"])
        root = ET.fromstring(res["content"][0]["text"])  # well-formed XML
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("day", res["content"][0]["text"])

    def test_layout_to_gltf(self):
        res = call("layout_to_gltf", {"layout": example("studio-apartment.json"), "state": "day"})
        self.assertFalse(res["isError"])
        g = json.loads(res["content"][0]["text"])
        self.assertEqual(g["asset"]["version"], "2.0")
        self.assertTrue(g["buffers"][0]["uri"].startswith("data:application/octet-stream;base64,"))
        self.assertTrue(call("layout_to_gltf", {"layout": example("studio-apartment.json"), "state": "x"})["isError"])
        shaped = json.loads(call("layout_to_gltf", {"layout": example("studio-apartment.json")})["content"][0]["text"])
        plain = json.loads(call("layout_to_gltf", {"layout": example("studio-apartment.json"), "boxes": True})["content"][0]["text"])
        self.assertGreater(len(shaped["nodes"]), len(plain["nodes"]))

    def test_floor_plan_unknown_state(self):
        res = call("floor_plan_svg", {"layout": example("studio-apartment.json"), "state": "noon"})
        self.assertTrue(res["isError"])

    def test_schema_and_references(self):
        schema = json.loads(call("get_layout_schema")["content"][0]["text"])
        self.assertIn("elements", schema["properties"])
        listing = call("list_references")["content"][0]["text"]
        self.assertIn("references/rooms/kitchen.md", listing)
        self.assertIn("examples/studio-apartment.json", listing)
        text = call("read_reference", {"path": "references/safety.md"})["content"][0]["text"]
        self.assertGreater(len(text), 200)

    def test_read_reference_stays_inside_the_skill(self):
        for path in ("../../.git/config", "/etc/passwd", "scripts/mcp_server.py", "SKILL.md",
                     "references/../../README.md"):
            with self.subTest(path=path):
                self.assertTrue(call("read_reference", {"path": path})["isError"])

    def test_unknown_tool(self):
        reply = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "rm"}})
        self.assertEqual(reply["error"]["code"], -32602)


class TestSvgRenderer(unittest.TestCase):
    def test_every_shipped_layout_renders(self):
        files = sorted((SKILL / "examples").glob("*.json")) + sorted((SKILL / "evals" / "runs").glob("*.json"))
        for f in files:
            L = json.loads(f.read_text())
            for state in (L.get("states") or [None]):
                with self.subTest(layout=f.name, state=state):
                    ET.fromstring(floor_plan_svg.render(L, state))

    def test_labels_fit(self):
        self.assertIsNone(floor_plan_svg._fit("anything", 200, 5))
        text, size, rotate = floor_plan_svg._fit("Lower bed with 3 wheeled drawers", 90, 400)
        self.assertTrue(rotate)
        self.assertGreaterEqual(size, floor_plan_svg.MIN_FONT)
        text, size, rotate = floor_plan_svg._fit("A very long label for a small box", 60, 40)
        self.assertTrue(text.endswith("…"))


if __name__ == "__main__":
    unittest.main()
