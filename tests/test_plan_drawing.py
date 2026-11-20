"""Tests for scripts/plan_drawing.py (architectural SVG plans). Standard library only."""
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "residential-space-designer"
sys.path.insert(0, str(SKILL / "scripts"))
import plan_drawing as pd  # noqa: E402
import mcp_server  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"
LAYOUTS = (sorted((SKILL / "examples").glob("*.json")) + sorted((SKILL / "evals" / "runs").glob("*.json"))
           + sorted((SKILL / "evals" / "blind").glob("*.json")))


def example(name):
    return json.loads((SKILL / "examples" / name).read_text())


def groups(svg):
    root = ET.fromstring(svg)
    return {g.get("data-id"): g for g in root.iter(NS + "g") if g.get("data-id")}


class TestPlanDrawing(unittest.TestCase):
    def test_every_layout_draws_valid_svg(self):
        for f in LAYOUTS:
            L = json.loads(f.read_text())
            if "room" not in L:
                continue
            for state in (L.get("states") or [None]):
                with self.subTest(layout=f.name, state=state):
                    root = ET.fromstring(pd.render(L, state))
                    self.assertTrue(root.tag.endswith("svg"))

    def test_one_group_per_element_with_size_title(self):
        L = example("studio-apartment.json")
        g = groups(pd.render(L, "night"))
        ids = {e["id"] for e in L["elements"]}
        self.assertEqual(set(g), ids)
        title = g["sofa"].find(NS + "title").text
        self.assertIn("0.90 × 2.00 m", title)

    def test_state_hides_the_wall_bed(self):
        self.assertNotIn("bed", groups(pd.render(example("studio-apartment.json"), "day")))

    def test_raised_items_are_dashed_overhead(self):
        g = groups(pd.render(example("twins-offset-loft.json")))
        upper = g["bed_upper"]
        self.assertTrue(any(r.get("class") == "d-dash" for r in upper.iter(NS + "rect")))
        lower = g["bed_lower"]
        self.assertFalse(any(r.get("class") == "d-dash" for r in lower.iter(NS + "rect")))

    def test_symbols(self):
        svg = pd.render(example("galley-kitchen.json"))
        g = groups(svg)
        hob = next(v for k, v in g.items() if "cook" in k or "hob" in k)
        self.assertGreaterEqual(len(list(hob.iter(NS + "circle"))), 8)   # four rings, inner and outer
        bed = groups(pd.render(example("studio-apartment.json"), "night"))["bed"]
        pillows = [r for r in bed.iter(NS + "rect") if r.get("rx") == "4.0"]
        self.assertEqual(len(pillows), 2)                                  # a double bed gets two pillows

    def test_walls_doors_windows_and_dimensions(self):
        L = example("studio-apartment.json")
        svg = pd.render(L)
        self.assertEqual(svg.count('class="d-door"'), 1)
        self.assertEqual(svg.count('class="d-glass"'), 3)                  # one window, three glazing lines
        self.assertIn(">4.00 m<", svg)
        self.assertIn(">6.40 m<", svg)
        self.assertIn("25.6 M²", svg)

    def test_outward_door_gets_room_below_the_wall(self):
        L = example("compact-bathroom.json")
        door = next(o for o in L["room"]["openings"] if o["type"] == "door")
        inward = json.loads(json.dumps(L))
        next(o for o in inward["room"]["openings"] if o["type"] == "door")["swing"] = "in"
        h = lambda svg: float(ET.fromstring(svg).get("viewBox").split()[3])
        if door.get("swing") == "out" and door["wall"] == "S":
            self.assertAlmostEqual(h(pd.render(L)) - h(pd.render(inward)), door["width"] * pd.SCALE, delta=1)

    def test_no_style_leaves_theming_to_the_page(self):
        L = example("twins-offset-loft.json")
        self.assertIn("<style>", pd.render(L))
        self.assertNotIn("<style>", pd.render(L, style=False))

    def test_mcp_styles(self):
        def call(args):
            return mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                      "params": {"name": "floor_plan_svg", "arguments": args}})["result"]
        L = example("studio-apartment.json")
        arch = call({"layout": L})["content"][0]["text"]
        plain = call({"layout": L, "style": "plain"})["content"][0]["text"]
        self.assertIn("d-wall", arch)
        self.assertNotIn("d-wall", plain)
        self.assertTrue(call({"layout": L, "style": "fancy"})["isError"])

    def test_command_line(self):
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "plan_drawing.py"),
                            str(SKILL / "examples" / "twins-offset-loft.json"), "--no-style"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("<style>", r.stdout)
        ET.fromstring(r.stdout)


if __name__ == "__main__":
    unittest.main()
