"""Tests for the skill package and scripts/check_layout.py. Standard library only.

Run from the repository root:  python3 -m unittest discover -s tests -v
"""
import copy
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "residential-space-designer"

spec = importlib.util.spec_from_file_location("check_layout", SKILL / "scripts" / "check_layout.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)

# Layouts allowed to carry warnings, and why.
EXPECTED_WARNINGS = {
    "04-couple.json": "intended bedside trade-off: one sleeper gets in from the foot",
}


def load(rel):
    return json.loads((SKILL / rel).read_text())


def el(layout, eid):
    return next(e for e in layout["elements"] if e["id"] == eid)


def run(layout):
    return cl.check_all(layout)


def has(msgs, text):
    return any(text in m for m in msgs)


class TestShippedLayouts(unittest.TestCase):
    """Every example and scenario layout must pass the checker."""

    def test_all_layouts_have_no_errors(self):
        files = sorted((SKILL / "examples").glob("*.json")) + sorted((SKILL / "evals" / "runs").glob("*.json"))
        self.assertGreater(len(files), 10)
        for f in files:
            with self.subTest(layout=f.name):
                rep = run(json.loads(f.read_text()))
                self.assertEqual(rep.errors, [], f"{f.name}: {rep.errors}")
                if f.name not in EXPECTED_WARNINGS:
                    self.assertEqual(rep.warns, [], f"{f.name}: {rep.warns}")

    def test_layouts_use_schema_types(self):
        schema = load("templates/layout.schema.json")
        room_types = set(schema["properties"]["room"]["properties"]["type"]["enum"])
        el_types = set(schema["properties"]["elements"]["items"]["properties"]["type"]["enum"])
        for f in list((SKILL / "examples").glob("*.json")) + list((SKILL / "evals" / "runs").glob("*.json")):
            L = json.loads(f.read_text())
            with self.subTest(layout=f.name):
                self.assertIn(L["room"].get("type", "bedroom"), room_types)
                for e in L["elements"]:
                    self.assertIn(e["type"], el_types, f"{f.name}: {e['id']}")

    def test_plan_renders(self):
        L = load("examples/studio-apartment.json")
        plan = cl.ascii_plan(cl.apply_state(L, "night"), upper=False)
        self.assertIn("bed", plan)


class TestSleepingRules(unittest.TestCase):
    def setUp(self):
        self.twins = load("examples/twins-offset-loft.json")

    def test_raised_bed_needs_guardrail(self):
        el(self.twins, "bed_upper")["guardrail"] = False
        self.assertTrue(has(run(self.twins).errors, "without guardrails"))

    def test_raised_bed_needs_access(self):
        el(self.twins, "steps_a")["serves"] = "nothing"
        self.assertTrue(has(run(self.twins).errors, "no steps/ladder"))

    def test_upper_bed_minimum_age(self):
        self.twins["occupants"][0]["age"] = 4
        self.assertTrue(has(run(self.twins).errors, "upper beds need age"))

    def test_headroom_above_mattress(self):
        self.twins["room"]["height"] = 2.45
        self.assertTrue(has(run(self.twins).errors, "headroom 0.65"))

    def test_desk_under_low_loft(self):
        el(self.twins, "bed_upper")["z"] = 1.2
        el(self.twins, "steps_a")["h"] = 1.2
        el(self.twins, "wardrobe_a")["h"] = 1.1
        self.assertTrue(has(run(self.twins).errors, "desk_a under bed_upper"))

    def test_lower_bunk_headroom(self):
        L = load("evals/runs/03-three-kids.json")
        el(L, "bed8")["z"] = 1.1
        self.assertTrue(has(run(L).errors, "above lower mattress"))

    def test_egress_per_partitioned_area(self):
        L = load("evals/runs/06-siblings-partition.json")
        L["room"]["openings"] = [o for o in L["room"]["openings"] if o["id"] != "win_b"]
        self.assertTrue(has(run(L).errors, "no egress window"))

    def test_double_bed_side_access(self):
        L = load("evals/runs/04-couple.json")
        self.assertTrue(has(run(L).warns, "double bed with 1 accessible"))


class TestGeneralRules(unittest.TestCase):
    def test_door_swing(self):
        L = load("examples/twins-offset-loft.json")
        el(L, "desk_b")["y"] = 0.2
        self.assertTrue(has(run(L).errors, "blocks the swing of door"))

    def test_niche_in_load_bearing_wall(self):
        L = load("examples/twins-offset-loft.json")
        L["elements"].append({"id": "niche1", "type": "niche", "wall": "N",
                              "x": 0.2, "y": 3.3, "z": 0.6, "w": 0.4, "d": 0.1, "h": 0.3})
        self.assertTrue(has(run(L).errors, "load-bearing wall N"))

    def test_states_checked_separately(self):
        L = load("evals/runs/10-micro-unit.json")
        el(L, "desk")["states"]["day"]["x"] = 0.3
        self.assertTrue(has(run(L).errors, "[day]"))


class TestRoomTypeRules(unittest.TestCase):
    def test_kitchen_aisle(self):
        L = load("examples/galley-kitchen.json")
        for i in ("pantry", "counter_e1", "cooktop", "counter_e2"):
            el(L, i)["x"] = 1.4
        el(L, "pantry")["y"] = 2.3
        el(L, "pantry")["d"] = 0.9
        el(L, "counter_e2")["y"] = 2.0
        el(L, "counter_e2")["d"] = 0.3
        for i in ("hood", "uppers_e"):
            el(L, i)["x"] = 1.55
        self.assertTrue(has(run(L).warns, "walkway"))

    def test_kitchen_triangle(self):
        L = load("examples/galley-kitchen.json")
        L["room"]["depth"] = 5.5
        el(L, "fridge")["y"] = 4.7
        self.assertTrue(has(run(L).warns, "work triangle total"))

    def test_bathroom_toilet_and_shower(self):
        L = load("examples/compact-bathroom.json")
        el(L, "toilet")["y"] = 0.1
        el(L, "shower")["w"] = 0.7
        el(L, "shower")["x"] = 1.0
        msgs = run(L).errors
        self.assertTrue(has(msgs, "centreline to left"))
        self.assertTrue(has(msgs, "below 0.76"))

    def test_coffee_table_distance(self):
        L = load("examples/studio-apartment.json")
        el(L, "coffee")["x"] = 1.7
        self.assertTrue(has(run(L).warns, "from sofa"))

    def test_stair_geometry(self):
        L = load("examples/studio-apartment.json")
        L["elements"].append({"id": "stair", "type": "stairs", "x": 2.6, "y": 4.2, "z": 0,
                              "w": 0.8, "d": 1.5, "h": 2.7, "rise": 0.22, "tread": 0.22, "headroom": 1.9})
        msgs = run(L).errors
        for text in ("riser", "tread", "stair width", "headroom"):
            self.assertTrue(has(msgs, text), text)

    def test_window_fall_protection(self):
        L = load("examples/studio-apartment.json")
        L["room"]["openings"][1]["sill"] = 0.5
        self.assertTrue(has(run(L).warns, "fall protection"))

    def test_climbable_under_window(self):
        L = load("evals/runs/20-sloping-hosting-level.json")
        el(L, "sofa")["x"] = 0.0
        self.assertTrue(has(run(L).warns, "climbable"))



class TestBlindTestFixes(unittest.TestCase):
    """Checks added after the blind test (evals/results.md, run 4)."""

    def test_route_must_stay_clear(self):
        L = load("examples/studio-apartment.json")
        L["elements"].append({"id": "path", "type": "route", "x": 1.0, "y": 1.0, "z": 0,
                              "w": 0.9, "d": 1.5, "h": 0.01})
        self.assertTrue(has(run(L).errors, "blocks route path"))

    def test_multi_sided_island(self):
        L = load("evals/runs/19-london-terrace-kitchen-diner.json")
        el(L, "island_s")["front"] = ["+x", "-x"]
        el(L, "island_s")["clearance"] = 1.4
        self.assertTrue(has(run(L).errors, "(-x)"))

    def test_restrictor_silences_fall_warnings(self):
        L = load("evals/runs/20-sloping-hosting-level.json")
        el(L, "sofa")["x"] = 0.0
        self.assertTrue(has(run(L).warns, "climbable"))
        L["room"]["openings"][2]["restrictor"] = True
        self.assertFalse(has(run(L).warns, "climbable"))

    def test_tall_furniture_over_window(self):
        L = load("examples/compact-bathroom.json")
        el(L, "tall_cab")["h"] = 2.0
        self.assertTrue(has(run(L).warns, "covers window"))

    def test_step_rise(self):
        L = load("examples/twins-offset-loft.json")
        el(L, "steps_a")["rise"] = 0.30
        self.assertTrue(has(run(L).errors, "step rise"))
        el(L, "steps_a")["rise"] = 0.24
        el(L, "steps_a")["tread"] = 0.20
        self.assertTrue(has(run(L).warns, "steep steps"))

    def test_upper_plan_shows_full_height_items(self):
        L = load("examples/twins-offset-loft.json")
        self.assertIn("wardrobe_b", cl.ascii_plan(L, upper=True))

class TestCommandLine(unittest.TestCase):
    """The checker reports bad input clearly instead of crashing."""

    def cli(self, *args):
        import subprocess, sys
        return subprocess.run([sys.executable, str(SKILL / "scripts" / "check_layout.py"), *args],
                              capture_output=True, text=True)

    def test_help(self):
        r = self.cli("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Usage", r.stdout)

    def test_missing_file(self):
        r = self.cli("no-such-layout.json")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Can't open", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_invalid_json(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{not json")
        r = self.cli(f.name)
        self.assertIn("not valid JSON", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_plan_flag_before_file(self):
        r = self.cli("--plan", str(SKILL / "examples" / "studio-apartment.json"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("FLOOR LEVEL", r.stdout)


class TestSkillPackage(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()
        self.fm = self.text.split("---")[1]

    def test_frontmatter(self):
        name = re.search(r"^name: (.+)$", self.fm, re.M).group(1).strip()
        desc = re.search(r"^description: (.+)$", self.fm, re.M).group(1).strip()
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertEqual(name, SKILL.name)
        self.assertLessEqual(len(desc), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"`((?:references|templates|scripts|examples|evals)/[^`*]+?\.(?:md|json|py))`", self.text))
        self.assertGreater(len(refs), 5)
        for ref in refs:
            with self.subTest(ref=ref):
                self.assertTrue((SKILL / ref).exists(), ref)

    def test_plugin_manifests(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(plugin["name"], SKILL.name)
        for path in plugin["skills"]:
            self.assertTrue((ROOT / path / "SKILL.md").exists(), path)
        self.assertIn(plugin["name"], [p["name"] for p in market["plugins"]])


if __name__ == "__main__":
    unittest.main()
