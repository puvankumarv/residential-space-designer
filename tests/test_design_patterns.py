"""Tests for scripts/design_patterns.py, the video source map and the find_design_patterns tool."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "residential-space-designer"
REFS = SKILL / "references"
sys.path.insert(0, str(SKILL / "scripts"))
import design_patterns as dp  # noqa: E402
import mcp_server  # noqa: E402


def call(args):
    return mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                              "params": {"name": "find_design_patterns", "arguments": args}})["result"]


class TestPatterns(unittest.TestCase):
    def test_every_cited_video_has_a_link(self):
        videos = json.loads((REFS / "video_sources.json").read_text())["videos"]
        cited = set()
        for f in REFS.rglob("*.md"):
            cited |= set(dp.video_ids(f.read_text()))
        self.assertTrue(cited)
        self.assertEqual(sorted(cited - set(videos)), [])

    def test_video_map_matches_the_research_notes(self):
        """Every video in the notes tables is in the skill's map, with the same YouTube id."""
        videos = json.loads((REFS / "video_sources.json").read_text())["videos"]
        for notes in ("home_tours.md", "youtube_room_notes.md"):
            for vid_id, yt in re.findall(r"\|\s*((?:HT|YT)-[A-Z]\d+)\s*\|\s*\[([\w-]{11})\]",
                                         (ROOT / "interior-design-research" / notes).read_text()):
                with self.subTest(vid_id=vid_id):
                    self.assertEqual(videos[vid_id]["video"], yt)
                    self.assertEqual(videos[vid_id]["url"], f"https://youtu.be/{yt}")

    def test_shorthand_ids(self):
        self.assertEqual(dp.video_ids("[HT-I1, I2, W4]"), ["HT-I1", "HT-I2", "HT-W4"])
        self.assertEqual(dp.video_ids("[YT-K1], agrees with [NKBA]"), ["YT-K1"])

    def test_loads_patterns_for_each_room(self):
        rooms = {r["room"] for r in dp.load()}
        for room in ("kitchen", "bathroom", "living", "office", "utility", "whole-home"):
            self.assertIn(room, rooms)

    def test_search_ranks_the_obvious_match_first(self):
        hits = dp.search("fridge position", room="kitchen", limit=3)
        self.assertTrue(all("ridge" in h["pattern"] for h in hits[:2]), [h["pattern"] for h in hits])
        run_end = next(h for h in hits if "run end" in h["pattern"])
        self.assertEqual(run_end["videos"][0]["url"], "https://youtu.be/Bx5tm2m4320")
        top = dp.search("toilet seen from the door", room="bathroom")[0]
        self.assertIn("WC", top["pattern"])

    def test_bedroom_fixes_and_archetypes(self):
        fix = dp.search("wardrobe doors can't open", room="bedroom")[0]
        self.assertEqual(fix["kind"], "fix")
        self.assertTrue(fix["videos"] and all(v["id"].startswith("DI-") for v in fix["videos"]))
        kinds = {r["kind"] for r in dp.load() if r["room"] == "bedroom"}
        self.assertEqual(kinds, {"fix", "archetype"})
        twins = dp.search("twins loft", room="bedroom")[0]
        self.assertEqual(twins["kind"], "archetype")

    def test_room_filter(self):
        self.assertTrue(all(r["room"] == "utility" for r in dp.search("", room="utility")))
        with self.assertRaises(ValueError):
            dp.search("x", room="garage")

    def test_mcp_tool(self):
        res = call({"query": "dishwasher in a narrow balcony"})
        self.assertFalse(res["isError"])
        out = res["structuredContent"]
        self.assertGreater(out["count"], 0)
        self.assertEqual(out["patterns"][0]["room"], "utility")
        self.assertEqual(json.loads(res["content"][0]["text"]), out)
        self.assertTrue(call({"room": "garage"})["isError"])
        self.assertTrue(call({"limit": 0})["isError"])

    def test_yt_source_tag_is_documented(self):
        self.assertIn("**[YT]**", (REFS / "sources.md").read_text())


if __name__ == "__main__":
    unittest.main()
