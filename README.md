# Residential Space Designer

[![CI](https://github.com/puvankumarv/residential-space-designer/actions/workflows/ci.yml/badge.svg)](https://github.com/puvankumarv/residential-space-designer/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/puvankumarv/residential-space-designer)](https://github.com/puvankumarv/residential-space-designer/releases/latest)

**Website:** https://puvankumarv.github.io/residential-space-designer/

**One skill for every space in the home.** It's a Claude skill that designs residential interiors, from a single cramped room to a whole apartment or house:

- **Bedrooms:** kids', twin and shared rooms with loft, bunk, half-height and wall beds
- **Kitchens:** galley, L, U and island layouts
- **Bathrooms:** fixture layout and wet/dry split
- **Living and dining rooms**
- **Entryways, corridors and stairs**
- **Balconies and laundry**
- **Home offices**
- **Studios and whole-home planning:** room allocation, adjacency, and the wet-room stack
- **Exterior and site:** car and pedestrian arrival, privacy from the street, courtyards, verandahs and terraces
- **Indian and Western ways of living:** pooja rooms, Vastu if wanted, dry and wet kitchens, elders on the ground floor; or drop zones, open kitchens with sight lines, mudrooms and ensuites

You give it dimensions, photos, a floor plan or a spoken description. For each room it produces:
- a design brief and zone plan,
- a layout JSON (`templates/layout.schema.json`) that the checker validates and a Blender stage can render,
- an ASCII floor plan, a bill of materials and safety notes,
- a zone-by-zone reveal script that doubles as the camera path for a walkthrough video.

For a whole home it first makes a **home plan** (rooms, adjacency, circulation), then designs room by room.

## What's inside

| Path | What it is |
|---|---|
| `residential-space-designer/SKILL.md` | The skill: room modules, procedure, deliverables |
| `residential-space-designer/references/rooms/` | One module per room type: `bedroom/`, `kitchen.md`, `bathroom.md`, `living-dining.md`, `entry-circulation.md`, `balcony-laundry.md`, `home-office.md`, `whole-home.md`, `exterior.md` |
| `residential-space-designer/references/regional/` | `india.md` and `western.md`: room programs, cultural preferences and climate responses |
| `residential-space-designer/references/` | Shared rules with source tags: safety, dimensions, storage, services, materials, sources |
| `residential-space-designer/templates/` | Layout JSON schema, intake questions and brief, BOM |
| `residential-space-designer/scripts/check_layout.py` | Layout checker, standard-library Python |
| `residential-space-designer/examples/` | Twins' loft bedroom, galley kitchen, compact bathroom, studio apartment |
| `residential-space-designer/evals/` | Test scenarios, generated layouts and results |
| `docs/` | Project website (GitHub Pages) |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests |
| `tests/` | Unit tests run by CI |
| `interior-design-research/` | Research notes: existing skills, MCPs and models; small-space case-study notes; whole-home tour notes (`home_tours.md`); draft rules |

## What the checker verifies

- **Every room:** collisions, room bounds, door swings, clearance in front of furniture, outlets near beds and desks, day/night states for convertible furniture.
- **Sleeping areas:** raised-bed guardrails, access and headroom, upper-bed age, lower-bunk headroom, bedside access, an escape window for every sleeping area (including rooms split by partitions).
- **Kitchens:** work-aisle and walkway widths, work-triangle legs and total.
- **Bathrooms:** toilet side and front clearance, basin clearance, shower size and entry clearance.
- **Living rooms:** distance from the sofa to the coffee table.
- **Stairs:** riser, tread, width and headroom.
- **Windows:** fall protection on high floors, and climbable furniture under windows.
- **Structure:** niches in load-bearing walls.

Each rule cites its source: CPSC, EN 747, IRC, NKBA, Neufert/Panero or IES (see `references/sources.md`).

## Install

**Claude Code: plugin (recommended)**
```
/plugin install residential-space-designer --marketplace puvankumarv/residential-space-designer
```
On older Claude Code versions, add the marketplace first:
```
/plugin marketplace add puvankumarv/residential-space-designer
/plugin install residential-space-designer@residential-space-designer
```

**Any agent that supports skills: skills CLI**
```bash
npx skills add puvankumarv/residential-space-designer
```

**Claude app (claude.ai / desktop):** download [`residential-space-designer.zip`](https://github.com/puvankumarv/residential-space-designer/releases/latest/download/residential-space-designer.zip) from the latest release and upload it under Settings → Capabilities → Skills, where custom skills are available on your plan.

**Manual:** copy the skill folder into your skills directory:
```bash
git clone https://github.com/puvankumarv/residential-space-designer.git
cp -r residential-space-designer/residential-space-designer ~/.claude/skills/
```

Then describe your room or home ("my twins share a 3.4 × 3.4 m room…", "plan our 30×40 Vastu house…") and the skill loads automatically.

## Check a layout

```bash
python3 residential-space-designer/scripts/check_layout.py residential-space-designer/examples/studio-apartment.json --plan
```

Add `--json` to get the result as one JSON object (`errors`, `warnings`, `ok`, and `plans` with `--plan`) for scripts and other tools. The exit code is 1 when there are errors.

## Development

```bash
python3 -m unittest discover -s tests -v
```
CI runs these tests on every push: checker rules, every shipped layout, and the skill and plugin manifests. Pushing a `v*` tag that matches `.claude-plugin/plugin.json` builds the ZIP and publishes a GitHub release. See [CHANGELOG.md](CHANGELOG.md).

## Status

v1. Code values are minimums. NKBA and design-guide values are recommendations. Values tagged `[std]` are common practice and must be confirmed. Always check local building codes, and have structure, gas, electrics and waterproofing done or signed off by professionals.

Design patterns were studied from public renovation videos and written up in our own words. The case-study notes in `interior-design-research/` are paraphrased summaries, not transcripts.

## Roadmap

1. Blind test of the skill on the scenarios in `evals/scenarios.md`.
2. MCP v1: `validate_layout` and `floor_plan_svg` tools.
3. Blender stage via blender-orchestrator: layout JSON to scene to walkthrough video.
4. Inputs: photo to dimensions, voice (Whisper), video to 3D reconstruction.
5. Multi-room home layouts in a single file.

## License

[MIT](LICENSE) © 2026 Puvan Kumar V. The research notes in `interior-design-research/` summarise public videos in our own words. The videos themselves belong to their creators.
