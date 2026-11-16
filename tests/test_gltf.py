"""Tests for scripts/layout_to_gltf.py. Standard library only."""
import base64
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "residential-space-designer"
sys.path.insert(0, str(SKILL / "scripts"))
import layout_to_gltf as gl  # noqa: E402

LAYOUTS = sorted((SKILL / "examples").glob("*.json")) + sorted((SKILL / "evals" / "runs").glob("*.json"))


def example(name):
    return json.loads((SKILL / "examples" / name).read_text())


def read_glb(data):
    """Split a .glb into its JSON and binary chunks, checking the container format."""
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF" and version == 2 and length == len(data)
    jlen, jtype = struct.unpack_from("<I4s", data, 12)
    assert jtype == b"JSON" and jlen % 4 == 0
    gltf = json.loads(data[20:20 + jlen])
    blen, btype = struct.unpack_from("<I4s", data, 20 + jlen)
    assert btype == b"BIN\0" and blen % 4 == 0
    return gltf, data[28 + jlen:28 + jlen + blen]


class TestGltf(unittest.TestCase):
    def check_model(self, gltf, buf):
        """Internal consistency every glTF loader relies on."""
        self.assertEqual(gltf["asset"]["version"], "2.0")
        self.assertGreaterEqual(len(buf), gltf["buffers"][0]["byteLength"])
        for bv in gltf["bufferViews"]:
            self.assertLessEqual(bv["byteOffset"] + bv["byteLength"], gltf["buffers"][0]["byteLength"])
        size = {"VEC3": 12, "SCALAR": 2}
        for acc in gltf["accessors"]:
            bv = gltf["bufferViews"][acc["bufferView"]]
            self.assertEqual(acc["count"] * size[acc["type"]], bv["byteLength"])
        idx = gltf["accessors"][2]
        indices = struct.unpack_from(f"<{idx['count']}H", buf, gltf["bufferViews"][2]["byteOffset"])
        self.assertLess(max(indices), gltf["accessors"][0]["count"])
        for n in gltf["nodes"]:
            if "mesh" in n:
                self.assertLess(n["mesh"], len(gltf["meshes"]))
                self.assertTrue(all(s > 0 for s in n["scale"]), n["name"])
        for scene_node in gltf["scenes"][0]["nodes"]:
            self.assertLess(scene_node, len(gltf["nodes"]))

    def test_every_shipped_layout_exports(self):
        for f in LAYOUTS:
            L = json.loads(f.read_text())
            for state in (L.get("states") or [None]):
                with self.subTest(layout=f.name, state=state):
                    gltf, buf = read_glb(gl.to_glb(*gl.build(L, state)))
                    self.check_model(gltf, buf)

    def test_elements_placed_at_real_size(self):
        L = example("twins-offset-loft.json")
        gltf, _ = gl.build(L)
        e = next(e for e in L["elements"] if e["id"] == "bed_upper")
        node = next(n for n in gltf["nodes"] if n.get("extras", {}).get("id") == "bed_upper")
        # glTF is Y-up: layout x → X, z → Y, layout y → −Z
        self.assertAlmostEqual(node["translation"][0], e["x"] + e["w"] / 2, places=3)
        self.assertAlmostEqual(node["translation"][1], e["z"] + e["h"] / 2, places=3)
        self.assertAlmostEqual(node["translation"][2], -(e["y"] + e["d"] / 2), places=3)
        self.assertEqual(node["scale"], [e["w"], e["h"], e["d"]])

    def test_walls_have_openings(self):
        L = example("twins-offset-loft.json")
        gltf, _ = gl.build(L)
        walls = [n for n in gltf["nodes"] if n["name"].startswith("wall_")]
        glass = [n for n in gltf["nodes"] if n["name"].startswith("glass_")]
        doors = [o for o in L["room"]["openings"] if o["type"] == "door"]
        windows = [o for o in L["room"]["openings"] if o["type"] != "door"]
        self.assertEqual(len(glass), len(windows))
        # 4 solid walls + 1 lintel per door + sill and lintel per window + 1 extra piece per opening
        self.assertEqual(len(walls), 4 + 2 * len(doors) + 3 * len(windows))
        # nothing solid in the door gap below the door head
        door = doors[0]
        for n in walls:
            x, y, _ = n["translation"]
            sx, sy, _ = n["scale"]
            if door["wall"] == "S" and abs(n["translation"][2]) < 0.2 and y - sy / 2 < door.get("height", gl.DOOR_H) - 0.01:
                self.assertTrue(x + sx / 2 <= door["offset"] + 1e-6 or x - sx / 2 >= door["offset"] + door["width"] - 1e-6)

    def test_entry_node_inside_the_door(self):
        L = example("studio-apartment.json")
        gltf, _ = gl.build(L)
        entry = next(n for n in gltf["nodes"] if n["name"] == "entry")
        door = L["room"]["openings"][0]
        self.assertAlmostEqual(entry["translation"][0], door["offset"] + door["width"] / 2)
        self.assertEqual(entry["extras"]["facing"], [0, 1])

    def test_routes_are_not_modelled(self):
        L = example("studio-apartment.json")
        L["elements"].append({"id": "path", "type": "route", "x": 1, "y": 1, "z": 0, "w": 0.9, "d": 1, "h": 0.01})
        gltf, _ = gl.build(L)
        self.assertFalse(any(n.get("extras", {}).get("id") == "path" for n in gltf["nodes"]))

    def test_text_gltf_round_trip(self):
        gltf, buf = gl.build(example("galley-kitchen.json"))
        text = json.loads(gl.to_gltf_text(gltf, buf))
        data = base64.b64decode(text["buffers"][0]["uri"].split(",", 1)[1])
        self.assertEqual(data, buf)
        self.assertNotIn("uri", gltf["buffers"][0])  # the original dict is untouched

    def test_command_line(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "room.glb"
            r = subprocess.run([sys.executable, str(SKILL / "scripts" / "layout_to_gltf.py"),
                                str(SKILL / "examples" / "studio-apartment.json"), str(out), "--state", "day"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            read_glb(out.read_bytes())
            r = subprocess.run([sys.executable, str(SKILL / "scripts" / "layout_to_gltf.py"),
                                str(SKILL / "examples" / "studio-apartment.json"), str(out), "--state", "noon"],
                               capture_output=True, text=True)
            self.assertIn("Unknown state", r.stderr)


if __name__ == "__main__":
    unittest.main()
