#!/usr/bin/env python3
"""MCP server for the Residential Space Designer (stdio, standard library only).

Run:  python3 mcp_server.py

Tools:
  validate_layout   check a layout JSON against the safety and design rules
  floor_plan_svg    draw a layout JSON as an SVG floor plan
  layout_to_gltf    build a 3D model (glTF 2.0) of the room
  get_layout_schema the JSON Schema a layout must follow
  list_references   the skill's reference files and example layouts
  read_reference    read one of those files

Speaks JSON-RPC 2.0 over stdin/stdout, one message per line, as the MCP stdio
transport defines. Logs go to stderr only.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import check_layout as cl  # noqa: E402
import floor_plan_svg as svg  # noqa: E402
import layout_to_gltf as gl  # noqa: E402

SERVER_INFO = {"name": "residential-space-designer", "version": "1.2.0"}  # kept equal to .claude-plugin/plugin.json by the tests
PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"]
READABLE_DIRS = ("references", "templates", "examples")
READABLE_SUFFIXES = (".md", ".json")

LAYOUT_ARG = {
    "description": "The layout, as a JSON object (or a string holding JSON) that follows get_layout_schema.",
    "type": "object",
}

TOOLS = [
    {
        "name": "validate_layout",
        "title": "Validate a room layout",
        "description": (
            "Check a room layout against code minimums and design standards: collisions, door swings, "
            "clearances, raised-bed safety, escape windows, kitchen aisles and work triangle, bathroom "
            "fixture clearances, stairs, window falls, and each day/night state. Returns errors (must fix), "
            "warnings (should review) and ok. Set plan to true to also get ASCII top views."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "layout": LAYOUT_ARG,
                "plan": {"type": "boolean", "description": "Also return ASCII floor and upper-level plans.", "default": False},
            },
            "required": ["layout"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "floor_plan_svg",
        "title": "Draw a floor plan",
        "description": (
            "Draw a room layout as an SVG floor plan, north up, 1 m = 100 px. Floor items are filled, "
            "raised items (loft beds, wall cabinets) dashed; doors show their swing. Returns the SVG markup. "
            "For layouts with states (day/night), pass state to pick one; the first state is the default."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "layout": LAYOUT_ARG,
                "state": {"type": "string", "description": "Which state to draw, e.g. \"day\" or \"night\"."},
            },
            "required": ["layout"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "layout_to_gltf",
        "title": "Build a 3D model",
        "description": (
            "Turn a room layout into a 3D model: glTF 2.0 JSON with the data embedded, so it can be saved "
            "as a .gltf file and opened in Blender, a web glTF viewer or an OS 3D viewer. Walls are cut "
            "around doors and windows, every element is a coloured box at its real height, and an 'entry' "
            "node marks where to stand inside the door. No ceiling, so it can be viewed from above. "
            "scripts/blender_walkthrough.py renders a still or walkthrough video from it."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "layout": LAYOUT_ARG,
                "state": {"type": "string", "description": "Which state to build, e.g. \"day\" or \"night\"."},
            },
            "required": ["layout"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "get_layout_schema",
        "title": "Get the layout schema",
        "description": "Return the JSON Schema for layouts: units (metres), axes, room types, element types and fields.",
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "list_references",
        "title": "List design references",
        "description": (
            "List the skill's design references (room modules, Indian and Western regional modules, "
            "dimensions, safety, storage, services, materials, sources), templates and example layouts."
        ),
        "inputSchema": {"type": "object", "properties": {}},
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "read_reference",
        "title": "Read a design reference",
        "description": "Read one file listed by list_references, e.g. \"references/rooms/kitchen.md\" or \"examples/studio-apartment.json\".",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path relative to the skill folder, as list_references gives it."}},
            "required": ["path"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
]


class ToolError(Exception):
    """A problem with the tool's input, reported back to the model as isError."""


def _layout(args):
    layout = args.get("layout")
    if isinstance(layout, str):
        try:
            layout = json.loads(layout)
        except json.JSONDecodeError as e:
            raise ToolError(f"layout is not valid JSON: {e.msg} (line {e.lineno}, column {e.colno})")
    if not isinstance(layout, dict):
        raise ToolError("layout must be a JSON object")
    return layout


def _readable():
    files = []
    for d in READABLE_DIRS:
        files += [p for p in sorted((SKILL / d).rglob("*")) if p.is_file() and p.suffix in READABLE_SUFFIXES]
    return files


def validate_layout(args):
    layout = _layout(args)
    if not isinstance(layout.get("elements", []), list) or not isinstance(layout.get("room", {}), dict):
        raise ToolError("layout.room must be an object and layout.elements a list")
    layout.setdefault("elements", [])
    try:
        out = cl.result(layout, bool(args.get("plan")))
    except (KeyError, TypeError, ValueError) as e:
        raise ToolError(f"layout is missing or has a malformed field ({type(e).__name__}: {e}); see get_layout_schema")
    return json.dumps(out, ensure_ascii=False, indent=2)


def floor_plan_svg(args):
    layout = _layout(args)
    room = layout.get("room")
    if not isinstance(room, dict) or not all(isinstance(room.get(k), (int, float)) for k in ("width", "depth")):
        raise ToolError("layout.room needs numeric width and depth")
    state = args.get("state")
    if state and state not in (layout.get("states") or []):
        raise ToolError(f"unknown state {state!r}; this layout has {layout.get('states') or 'no states'}")
    layout.setdefault("elements", [])
    try:
        return svg.render(layout, state)
    except (KeyError, TypeError, ValueError) as e:
        raise ToolError(f"layout has a malformed field ({type(e).__name__}: {e}); see get_layout_schema")


def layout_to_gltf(args):
    layout = _layout(args)
    room = layout.get("room")
    if not isinstance(room, dict) or not all(isinstance(room.get(k), (int, float)) for k in ("width", "depth")):
        raise ToolError("layout.room needs numeric width and depth")
    state = args.get("state")
    if state and state not in (layout.get("states") or []):
        raise ToolError(f"unknown state {state!r}; this layout has {layout.get('states') or 'no states'}")
    layout.setdefault("elements", [])
    try:
        return gl.to_gltf_text(*gl.build(layout, state))
    except (KeyError, TypeError, ValueError) as e:
        raise ToolError(f"layout has a malformed field ({type(e).__name__}: {e}); see get_layout_schema")


def get_layout_schema(args):
    return (SKILL / "templates" / "layout.schema.json").read_text()


def list_references(args):
    lines = [str(p.relative_to(SKILL)) for p in _readable()]
    return "Files you can pass to read_reference:\n" + "\n".join(lines)


def read_reference(args):
    rel = str(args.get("path", "")).strip().lstrip("/")
    target = (SKILL / rel).resolve()
    allowed = {p.resolve() for p in _readable()}
    if target not in allowed:
        raise ToolError(f"{rel!r} is not a readable reference; call list_references for the list")
    return target.read_text()


HANDLERS = {
    "validate_layout": validate_layout,
    "floor_plan_svg": floor_plan_svg,
    "layout_to_gltf": layout_to_gltf,
    "get_layout_schema": get_layout_schema,
    "list_references": list_references,
    "read_reference": read_reference,
}


def handle(msg):
    """Return the response dict for one JSON-RPC message, or None for notifications."""
    method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
    if mid is None:  # notification (e.g. notifications/initialized): no reply
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    if method == "initialize":
        asked = params.get("protocolVersion")
        return ok({
            "protocolVersion": asked if asked in PROTOCOLS else PROTOCOLS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": (
                "Tools for designing homes room by room. Get the layout format from get_layout_schema, "
                "write the layout, run validate_layout until it has no errors, then draw it with floor_plan_svg "
                "or build a 3D model with layout_to_gltf. "
                "Design guidance lives in the references (list_references / read_reference)."
            ),
        })
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        if name not in HANDLERS:
            return err(-32602, f"Unknown tool: {name}")
        try:
            text = HANDLERS[name](params.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": text}], "isError": False})
        except ToolError as e:
            return ok({"content": [{"type": "text", "text": str(e)}], "isError": True})
    return err(-32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            try:
                reply = handle(msg) if isinstance(msg, dict) else {
                    "jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
            except Exception as e:  # keep the server alive; report the failure to the client
                print(f"internal error: {e!r}", file=sys.stderr)
                reply = {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32603, "message": "Internal error"}}
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
