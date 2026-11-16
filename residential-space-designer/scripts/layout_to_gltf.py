#!/usr/bin/env python3
"""Turn a layout JSON into a 3D model (glTF 2.0) of the room.

Usage: python3 layout_to_gltf.py layout.json out.glb [--state night]
       python3 layout_to_gltf.py layout.json out.gltf      (text glTF, data embedded)

The model has a floor, walls cut around doors and windows (glass in the
windows), and every element as a coloured box at its real position and height.
There is no ceiling, so a viewer can look in from above. Open the file in
Blender (File → Import → glTF), Windows 3D Viewer, macOS Quick Look, or any
web glTF viewer; scripts/blender_walkthrough.py renders a video from it.

Axes: glTF is Y-up, so layout x → X, height z → Y, and layout y (towards the
N wall) → −Z. Units stay metres. Standard library only.
"""
import base64
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_layout as cl  # noqa: E402
from floor_plan_svg import FILL, DEFAULT_FILL  # noqa: E402

WALL_T = 0.12          # wall thickness drawn outside the room
FLOOR_T = 0.05
DOOR_H = 2.1           # default door height [std]
WINDOW_H = 1.2         # default window height if the layout gives none [std]
SKIP = {"route", "niche"}   # routes are rules, not objects; niches are recesses in the wall
MIN_SIZE = 0.02

FIXED_COLOURS = {"_wall": "#f2efe9", "_floor": "#c8b291", "_glass": "#9cc8e6"}


def _linear(hex_colour, alpha=1.0):
    """sRGB hex to the linear RGBA factors glTF expects."""
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return [round(c, 4) for c in lin] + [alpha]


def _cube():
    """Unit cube centred on the origin: positions, normals and indices, one quad per face."""
    faces = [((1, 0, 0), (0, 1, 0)), ((-1, 0, 0), (0, 1, 0)), ((0, 1, 0), (0, 0, -1)),
             ((0, -1, 0), (0, 0, 1)), ((0, 0, 1), (0, 1, 0)), ((0, 0, -1), (0, 1, 0))]
    pos, nrm, idx = [], [], []
    for n, up in faces:
        # right = up × n, so (right, up, n) is right-handed and the quad faces outward
        right = (up[1] * n[2] - up[2] * n[1], up[2] * n[0] - up[0] * n[2], up[0] * n[1] - up[1] * n[0])
        base = len(pos)
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pos.append(tuple(0.5 * (n[i] + su * right[i] + sv * up[i]) for i in range(3)))
            nrm.append(n)
        idx += [base, base + 1, base + 2, base, base + 2, base + 3]
    return pos, nrm, idx


def _box(x0, x1, y0, y1, z0, z1):
    """Layout-space box → glTF (translation, scale)."""
    w, d, h = max(x1 - x0, MIN_SIZE), max(y1 - y0, MIN_SIZE), max(z1 - z0, MIN_SIZE)
    return [round((x0 + x1) / 2, 4), round((z0 + z1) / 2, 4), round(-(y0 + y1) / 2, 4)], [round(w, 4), round(h, 4), round(d, 4)]


def _wall_boxes(room):
    """Boxes for the four walls with holes for openings, plus glass panes for windows."""
    W, D, H = room["width"], room["depth"], room.get("height", 2.7)
    T = WALL_T
    walls, glass = [], []
    spans = {"S": (-T, W + T), "N": (-T, W + T), "W": (0, D), "E": (0, D)}
    for wall, (a0, a1) in spans.items():
        ops = sorted((o for o in room.get("openings", []) if o.get("wall") == wall), key=lambda o: o["offset"])

        def piece(a, b, z0, z1, into=walls, inset=0.0):
            if b - a < 1e-3 or z1 - z0 < 1e-3:
                return
            t0, t1 = (-T + inset, -inset) if wall in ("S", "W") else (inset, T - inset)
            if wall in ("S", "N"):
                y0, y1 = (t0, t1) if wall == "S" else (D + t0, D + t1)
                into.append((a, b, y0, y1, z0, z1))
            else:
                x0, x1 = (t0, t1) if wall == "W" else (W + t0, W + t1)
                into.append((x0, x1, a, b, z0, z1))

        cursor = a0
        for o in ops:
            o0, o1 = max(o["offset"], a0), min(o["offset"] + o["width"], a1)
            piece(cursor, o0, 0, H)
            if o["type"] == "door":
                piece(o0, o1, min(o.get("height", DOOR_H), H), H)
            else:
                sill = o.get("sill", 0.9)
                top = min(sill + o.get("height", WINDOW_H), H - 0.05)
                piece(o0, o1, 0, sill)
                piece(o0, o1, top, H)
                piece(o0, o1, sill, top, into=glass, inset=T * 0.45)
            cursor = max(cursor, o1)
        piece(cursor, a1, 0, H)
    return walls, glass


def _entry(room, step_in=0.6):
    """Layout (x, y) just inside the first door, and the (dx, dy) direction into the room."""
    doors = [o for o in room.get("openings", []) if o.get("type") == "door"]
    if not doors:
        return None
    o = doors[0]
    W, D = room["width"], room["depth"]
    mid = o["offset"] + o["width"] / 2
    return {"S": ((mid, step_in), (0, 1)), "N": ((mid, D - step_in), (0, -1)),
            "W": ((step_in, mid), (1, 0)), "E": ((W - step_in, mid), (-1, 0))}[o["wall"]]


def build(layout, state=None):
    """Return (gltf_dict, binary_buffer) for one state of the layout."""
    if state is None and layout.get("states"):
        state = layout["states"][0]
    view = cl.apply_state(layout, state)
    room = view["room"]
    W, D = room["width"], room["depth"]

    pos, nrm, idx = _cube()
    buf = bytearray()
    for v in pos:
        buf += struct.pack("<3f", *v)
    n_off = len(buf)
    for v in nrm:
        buf += struct.pack("<3f", *v)
    i_off = len(buf)
    for i in idx:
        buf += struct.pack("<H", i)
    while len(buf) % 4:
        buf += b"\0"

    gltf = {
        "asset": {"version": "2.0", "generator": "residential-space-designer layout_to_gltf.py"},
        "scene": 0,
        "scenes": [{"name": room.get("name", "Room") + (f" ({state})" if state else ""), "nodes": []}],
        "nodes": [], "meshes": [], "materials": [],
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": n_off, "target": 34962},
            {"buffer": 0, "byteOffset": n_off, "byteLength": i_off - n_off, "target": 34962},
            {"buffer": 0, "byteOffset": i_off, "byteLength": len(idx) * 2, "target": 34963},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3",
             "min": [-0.5, -0.5, -0.5], "max": [0.5, 0.5, 0.5]},
            {"bufferView": 1, "componentType": 5126, "count": len(nrm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5123, "count": len(idx), "type": "SCALAR"},
        ],
    }
    mesh_for = {}

    def mesh(key):
        if key not in mesh_for:
            colour = FIXED_COLOURS.get(key) or FILL.get(key, DEFAULT_FILL)
            mat = {"name": key.lstrip("_"), "pbrMetallicRoughness": {
                "baseColorFactor": _linear(colour, 0.35 if key == "_glass" else 1.0),
                "metallicFactor": 0.0, "roughnessFactor": 0.1 if key == "_glass" else 0.85}}
            if key == "_glass":
                mat["alphaMode"] = "BLEND"
                mat["doubleSided"] = True
            gltf["materials"].append(mat)
            gltf["meshes"].append({"name": key.lstrip("_"), "primitives": [{
                "attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2,
                "material": len(gltf["materials"]) - 1}]})
            mesh_for[key] = len(gltf["meshes"]) - 1
        return mesh_for[key]

    def node(name, key, box, extras=None):
        t, s = _box(*box)
        n = {"name": name, "mesh": mesh(key), "translation": t, "scale": s}
        if extras:
            n["extras"] = extras
        gltf["nodes"].append(n)
        gltf["scenes"][0]["nodes"].append(len(gltf["nodes"]) - 1)

    node("floor", "_floor", (-WALL_T, W + WALL_T, -WALL_T, D + WALL_T, -FLOOR_T, 0))
    walls, glass = _wall_boxes(room)
    for k, b in enumerate(walls):
        node(f"wall_{k}", "_wall", b)
    for k, b in enumerate(glass):
        node(f"glass_{k}", "_glass", b)
    entry = _entry(room)
    if entry:
        (ex, ey), (fx, fy) = entry
        # an empty node a viewer or blender_walkthrough.py can stand at: just inside the first door
        gltf["nodes"].append({"name": "entry", "translation": [round(ex, 4), 1.6, round(-ey, 4)],
                              "extras": {"facing": [fx, fy]}})
        gltf["scenes"][0]["nodes"].append(len(gltf["nodes"]) - 1)
    for e in view.get("elements", []):
        if e["type"] in SKIP:
            continue
        x0, x1, y0, y1 = cl.rect(e)
        z0 = e.get("z", 0)
        node(e.get("label") or e["id"], e["type"], (x0, x1, y0, y1, z0, z0 + e.get("h", MIN_SIZE)),
             {"id": e["id"], "type": e["type"]})
    return gltf, bytes(buf)


def to_glb(gltf, buf):
    """Pack glTF JSON and its buffer into one binary .glb."""
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    buf += b"\0" * (-len(buf) % 4)
    total = 12 + 8 + len(js) + 8 + len(buf)
    return (struct.pack("<4sII", b"glTF", 2, total)
            + struct.pack("<I4s", len(js), b"JSON") + js
            + struct.pack("<I4s", len(buf), b"BIN\0") + buf)


def to_gltf_text(gltf, buf):
    """A single .gltf JSON file with the buffer embedded as a data URI."""
    out = json.loads(json.dumps(gltf))
    out["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(buf).decode()
    return json.dumps(out, indent=1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    state = None
    if "--state" in sys.argv:
        i = sys.argv.index("--state")
        state = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        args = [a for a in args if a != state]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    src, dst = args
    try:
        layout = json.loads(Path(src).read_text())
    except OSError as e:
        sys.exit(f"Can't open {src}: {e.strerror}")
    except json.JSONDecodeError as e:
        sys.exit(f"{src} is not valid JSON: {e.msg} (line {e.lineno}, column {e.colno})")
    if state and state not in (layout.get("states") or []):
        sys.exit(f"Unknown state {state!r}; this layout has {layout.get('states') or 'no states'}")
    gltf, buf = build(layout, state)
    if dst.endswith(".gltf"):
        Path(dst).write_text(to_gltf_text(gltf, buf))
    else:
        Path(dst).write_bytes(to_glb(gltf, buf))
    print(f"wrote {dst}: {len(gltf['nodes'])} objects")


if __name__ == "__main__":
    main()
