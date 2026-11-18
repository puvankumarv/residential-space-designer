"""Tests for scripts/mcp_server.py and scripts/floor_plan_svg.py. Standard library only."""
import base64
import json
import struct
import subprocess
import sys
import unittest
import zlib
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
        self.assertEqual(names, {"validate_layout", "room_metrics", "edit_layout", "compare_layouts", "floor_plan_png",
                                 "floor_plan_svg", "layout_to_gltf", "get_layout_schema", "list_references", "read_reference"})
        self.assertEqual(replies[2]["result"], {})

    def test_unknown_protocol_gets_latest(self):
        r = self.session({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(r[0]["result"]["protocolVersion"], mcp_server.LEGACY[0])

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
        cfg = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["mcpServers"]["residential-space-designer"]
        script = cfg["args"][0].replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT))
        self.assertTrue(Path(script).exists(), script)
        # no root .mcp.json: Claude Code would also load it as a project server, where ${CLAUDE_PLUGIN_ROOT} is unset
        self.assertFalse((ROOT / ".mcp.json").exists())


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


def rpc(method, params=None, meta_version=None):
    params = dict(params or {})
    if meta_version:
        params["_meta"] = {"io.modelcontextprotocol/protocolVersion": meta_version,
                           "io.modelcontextprotocol/clientInfo": {"name": "t", "version": "0"},
                           "io.modelcontextprotocol/clientCapabilities": {}}
    return mcp_server.handle({"jsonrpc": "2.0", "id": 7, "method": method, "params": params})


class TestModernProtocol(unittest.TestCase):
    """2026-07-28: no handshake, version in _meta, server/discover."""

    def test_discover(self):
        r = rpc("server/discover", meta_version="2026-07-28")["result"]
        self.assertEqual(r["resultType"], "complete")
        self.assertIn("2026-07-28", r["supportedVersions"])
        self.assertIn("2025-11-25", r["supportedVersions"])
        self.assertIn("tools", r["capabilities"])
        self.assertEqual(r["_meta"]["io.modelcontextprotocol/serverInfo"]["name"], "residential-space-designer")
        self.assertIn("ttlMs", r)

    def test_stateless_tool_call_without_initialize(self):
        r = rpc("tools/call", {"name": "validate_layout", "arguments": {"layout": example("galley-kitchen.json")}},
                meta_version="2026-07-28")["result"]
        self.assertEqual(r["resultType"], "complete")
        self.assertTrue(r["structuredContent"]["ok"])
        self.assertIn("io.modelcontextprotocol/serverInfo", r["_meta"])

    def test_lists_are_cacheable(self):
        r = rpc("tools/list", meta_version="2026-07-28")["result"]
        self.assertEqual(r["cacheScope"], "public")
        self.assertGreater(r["ttlMs"], 0)

    def test_unsupported_version(self):
        e = rpc("tools/list", meta_version="1900-01-01")["error"]
        self.assertEqual(e["code"], -32022)
        self.assertEqual(e["data"]["requested"], "1900-01-01")
        self.assertIn("2026-07-28", e["data"]["supported"])

    def test_legacy_results_stay_plain(self):
        r = rpc("tools/list")["result"]
        self.assertNotIn("resultType", r)
        self.assertNotIn("ttlMs", r)

    def test_legacy_initialize_offers_2025_11_25(self):
        r = rpc("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}})["result"]
        self.assertEqual(r["protocolVersion"], "2025-11-25")
        for cap in ("tools", "resources", "prompts", "completions"):
            self.assertIn(cap, r["capabilities"])
        self.assertTrue(r["serverInfo"]["icons"][0]["src"].startswith("data:image/svg+xml;base64,"))


class TestNewTools(unittest.TestCase):
    def test_structured_output_matches_text(self):
        res = call("validate_layout", {"layout": example("studio-apartment.json")})
        self.assertEqual(json.loads(res["content"][0]["text"]), res["structuredContent"])
        schema = next(t for t in mcp_server.TOOLS if t["name"] == "validate_layout")["outputSchema"]
        for key in schema["required"]:
            self.assertIn(key, res["structuredContent"])

    def test_every_output_schema_is_an_object(self):
        for t in mcp_server.TOOLS:
            if "outputSchema" in t:
                self.assertEqual(t["outputSchema"]["type"], "object", t["name"])

    def test_room_metrics(self):
        m = call("room_metrics", {"layout": example("twins-offset-loft.json")})["structuredContent"]
        self.assertEqual(m["floor_area_m2"], 11.56)
        self.assertEqual(m["sleeping_places"], 2)
        self.assertTrue(0 < m["free_floor_pct"] < 100)
        self.assertGreater(m["storage_volume_m3"], 1)
        self.assertTrue(m["meets_irc_glazing_8pct"])
        self.assertTrue(m["check"]["ok"])

    def test_metrics_follow_the_state(self):
        L = example("studio-apartment.json")
        day = call("room_metrics", {"layout": L, "state": "day"})["structuredContent"]
        night = call("room_metrics", {"layout": L, "state": "night"})["structuredContent"]
        self.assertGreater(day["free_floor_pct"], night["free_floor_pct"])  # the wall bed folds away by day
        self.assertGreater(night["sleeping_places"], day["sleeping_places"])

    def test_edit_layout_moves_and_rechecks(self):
        L = example("galley-kitchen.json")
        fridge = next(e for e in L["elements"] if e["type"] == "fridge")
        res = call("edit_layout", {"layout": L, "operations": [{"op": "move", "id": fridge["id"], "dx": 1.0}]})
        self.assertFalse(res["isError"])
        out = res["structuredContent"]
        moved = next(e for e in out["layout"]["elements"] if e["id"] == fridge["id"])
        self.assertAlmostEqual(moved["x"], fridge["x"] + 1.0)
        self.assertFalse(out["check"]["ok"])            # pushed into the aisle and the other run
        self.assertEqual(fridge["x"], next(e for e in L["elements"] if e["id"] == fridge["id"])["x"])  # input untouched

    def test_edit_rotate_add_remove_set(self):
        L = example("studio-apartment.json")
        ops = [{"op": "rotate", "id": "sofa"}, {"op": "remove", "id": "coffee"},
               {"op": "add", "element": {"id": "lamp", "type": "other", "x": 3.5, "y": 3.5, "z": 0, "w": 0.3, "d": 0.3, "h": 1.5}},
               {"op": "set", "id": "lamp", "fields": {"label": "Floor lamp"}}]
        ids = {e["id"] for e in L["elements"]}
        if not {"sofa", "coffee"} <= ids:
            self.skipTest("example ids changed")
        out = call("edit_layout", {"layout": L, "operations": ops})["structuredContent"]
        sofa = next(e for e in out["layout"]["elements"] if e["id"] == "sofa")
        old = next(e for e in L["elements"] if e["id"] == "sofa")
        self.assertEqual((sofa["w"], sofa["d"]), (old["d"], old["w"]))
        self.assertEqual(sofa["front"], "+y")
        self.assertNotIn("coffee", {e["id"] for e in out["layout"]["elements"]})
        self.assertEqual(next(e for e in out["layout"]["elements"] if e["id"] == "lamp")["label"], "Floor lamp")
        self.assertEqual(len(out["changes"]), 4)

    def test_edit_errors_are_tool_errors(self):
        L = example("studio-apartment.json")
        for ops in ([{"op": "move", "id": "nope", "x": 1}], [{"op": "explode", "id": "sofa"}],
                    [{"op": "resize", "id": "sofa", "w": -1}], [{"op": "set", "id": "sofa", "fields": {"id": "x"}}], []):
            with self.subTest(ops=ops):
                res = call("edit_layout", {"layout": L, "operations": ops})
                self.assertTrue(res["isError"])

    def test_compare_layouts(self):
        good = example("galley-kitchen.json")
        bad, _ = mcp_server.lt.edit(good, [{"op": "move", "id": next(e["id"] for e in good["elements"] if e["type"] == "fridge"), "dx": 1.0}])
        out = call("compare_layouts", {"options": [{"name": "B", "layout": bad}, {"name": "A", "layout": good}]})["structuredContent"]
        self.assertEqual(out["ranking"][0], "A")
        self.assertIn("A ranks first", out["summary"])
        self.assertTrue(call("compare_layouts", {"options": [{"layout": good}]})["isError"])

    def test_floor_plan_png(self):
        res = call("floor_plan_png", {"layout": example("twins-offset-loft.json")})
        self.assertFalse(res["isError"])
        img, legend = res["content"]
        self.assertEqual(img["mimeType"], "image/png")
        data = base64.b64decode(img["data"])
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        w, h = struct.unpack(">II", data[16:24])
        self.assertEqual(w, h)  # a square room
        self.assertIn("1. ", legend["text"])
        self.assertIn("raised", legend["text"])
        self.assertTrue(call("floor_plan_png", {"layout": example("twins-offset-loft.json"), "scale": 5})["isError"])

    def test_png_decodes_and_has_the_room_colours(self):
        png = mcp_server.plan_png.render(example("galley-kitchen.json"))
        raw, pos = b"", 8
        while pos < len(png):
            n, kind = struct.unpack(">I4s", png[pos:pos + 8])
            if kind == b"IHDR":
                w, h = struct.unpack(">II", png[pos + 8:pos + 16])
            if kind == b"IDAT":
                raw += png[pos + 8:pos + 8 + n]
            pos += 12 + n
        pixels = zlib.decompress(raw)
        self.assertEqual(len(pixels), h * (1 + 3 * w))
        self.assertIn(bytes([0xf0, 0xdc, 0xc9]), pixels)   # counter colour

    def test_bad_layouts_are_tool_errors(self):
        for name in ("room_metrics", "floor_plan_png", "edit_layout", "validate_layout"):
            with self.subTest(tool=name):
                res = call(name, {"layout": {"room": {"width": "wide"}}, "operations": [{"op": "remove", "id": "x"}]})
                self.assertTrue(res["isError"])


class TestResourcesPromptsCompletions(unittest.TestCase):
    def test_resources_list_and_read(self):
        res = rpc("resources/list")["result"]["resources"]
        uris = {r["uri"] for r in res}
        self.assertIn("rsd://skill/references/rooms/kitchen.md", uris)
        self.assertIn("rsd://skill/templates/layout.schema.json", uris)
        kitchen = next(r for r in res if r["uri"].endswith("kitchen.md"))
        self.assertEqual(kitchen["mimeType"], "text/markdown")
        body = rpc("resources/read", {"uri": "rsd://skill/references/rooms/kitchen.md"})["result"]["contents"][0]
        self.assertEqual(body["text"], (SKILL / "references/rooms/kitchen.md").read_text())

    def test_resource_read_refuses_outside_paths(self):
        for uri in ("rsd://skill/../.claude-plugin/plugin.json", "rsd://skill/scripts/mcp_server.py", "file:///etc/passwd"):
            with self.subTest(uri=uri):
                e = rpc("resources/read", {"uri": uri})["error"]
                self.assertEqual(e["code"], -32002)
        self.assertEqual(rpc("resources/read", {"uri": "rsd://skill/nope.md"}, meta_version="2026-07-28")["error"]["code"], -32602)

    def test_resource_templates(self):
        t = rpc("resources/templates/list")["result"]["resourceTemplates"][0]
        self.assertEqual(t["uriTemplate"], "rsd://skill/{path}")

    def test_prompts(self):
        names = {p["name"] for p in rpc("prompts/list")["result"]["prompts"]}
        self.assertEqual(names, {"design_room", "review_layout"})
        r = rpc("prompts/get", {"name": "design_room", "arguments": {
            "room_type": "kitchen", "size": "2.4 x 3.2 m", "region": "indian"}})["result"]
        uris = [m["content"]["resource"]["uri"] for m in r["messages"] if m["content"]["type"] == "resource"]
        self.assertIn("rsd://skill/references/rooms/kitchen.md", uris)
        self.assertIn("rsd://skill/references/regional/india.md", uris)
        self.assertIn("rsd://skill/references/safety.md", uris)
        self.assertIn("validate_layout", r["messages"][0]["content"]["text"])
        kids = rpc("prompts/get", {"name": "design_room", "arguments": {"room_type": "kids_bedroom", "size": "3 x 3 m"}})["result"]
        self.assertTrue(any("sleep-strategies" in m["content"].get("resource", {}).get("uri", "") for m in kids["messages"]))
        self.assertEqual(rpc("prompts/get", {"name": "design_room", "arguments": {}})["error"]["code"], -32602)
        review = rpc("prompts/get", {"name": "review_layout", "arguments": {"layout": "{}"}})["result"]
        self.assertIn("edit_layout", review["messages"][0]["content"]["text"])

    def test_completions(self):
        r = rpc("completion/complete", {"ref": {"type": "ref/prompt", "name": "design_room"},
                                        "argument": {"name": "room_type", "value": "kit"}})["result"]["completion"]
        self.assertEqual(r["values"][0], "kitchen")
        r = rpc("completion/complete", {"ref": {"type": "ref/resource", "uri": "rsd://skill/{path}"},
                                        "argument": {"name": "path", "value": "bathroom"}})["result"]["completion"]
        self.assertIn("references/rooms/bathroom.md", r["values"])
        r = rpc("completion/complete", {"ref": {"type": "ref/prompt", "name": "nope"},
                                        "argument": {"name": "x", "value": ""}})["result"]["completion"]
        self.assertEqual(r["values"], [])
