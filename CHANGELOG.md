# Changelog

## Unreleased

- **`find_design_patterns` covers bedrooms and diagnostics:** it now also reads the "Symptom → Usual fix" tables (bedroom, kitchen, bathroom, living) and the bedroom archetype layouts, and links the 100 renovation Shorts (`[DI n]`, "Seen in" lists) to YouTube. 104 entries in all, each tagged `pattern`, `fix` or `archetype`.
- **Checker:** warns when a fridge sits in the middle of a worktop run, splitting it in two `[YT-K1]`.
- **`design_room` prompt:** points Claude to `find_design_patterns` for specific problems.
- **New research: 10 room-specific YouTube videos** (`interior-design-research/youtube_room_notes.md`, tag `[YT]`): kitchens (an architect's layout mistakes; Indian modular kitchens), bathrooms, living rooms (an architect's eight-step method), home offices, a utility balcony and two small flats. Paraphrased, with each creator's strength noted; numbers kept only where a code agrees, otherwise `[std]`.
- **Room modules updated** with "Patterns from room videos": kitchen (fridge at a run end, the kitchen as a corridor, a second station, modular widths, storage from a list), bathroom (WC out of the door view, niches off the shower-head wall, mirror cabinet depth), living (paths first, faces before the screen, rug and TV rules), home office (command position), utility (dishwasher orientation, door width before buying), and small flats (guest WC by the entrance, borrowed light).
- **MCP `find_design_patterns`** (`scripts/design_patterns.py`): searches every pattern table in the references and links each cited video to YouTube via `references/video_sources.json`.
- **Architectural floor plans** (`scripts/plan_drawing.py`, standard library): hatched walls, door leaves and swings, glazed windows, furniture as plan symbols (beds with pillows and a turned-down duvet, sofas with arms and cushions, hob rings, sink and toilet bowls, wardrobe rails, stair treads with an UP arrow), loft beds and wall cabinets dashed as overhead, a light tint per use, dimension lines, a north arrow and a scale bar. Each item has a hover title with its size. `floor_plan_svg` now draws this by default; `style: "plain"` keeps the old boxes.
- **Website:** rebuilt in the style of MCP product sites (dark-first blueprint theme, install command up front, a product window with layout JSON, plan and tool calls, a tool table), using the new architectural plans.
- **Furniture shapes in 3D** (`scripts/furniture.py`): elements are modelled by type instead of as plain boxes. Beds get a frame, mattress, duvet and pillows at the end nearest a wall, plus a guardrail with a gap by the steps on lofts. Sofas get arms and cushions; cabinets and wardrobes get plinths, doors or drawers and handles (sliding doors on two tracks); counters get stone worktops, a sink bowl and a hob; and there are appliances, sanitaryware, glass shower screens on the open sides, stairs, shelves and pleated curtains. Every part stays inside the element's box, so sizes match what the checker tested.
- **Materials:** wood, fabric, metal, ceramic, stone and black glass, with metallic and roughness values. An element's `material` field (steel, wood, veneer) picks the frame material.
- **MCP server v2**, after researching the 2025-11-25 and 2026-07-28 MCP revisions and other design MCP servers (notes in `interior-design-research/mcp_research.md`):
  - New tools: `room_metrics`, `edit_layout` (apply fixes and re-check in one call), `compare_layouts`, and `floor_plan_png`, a picture of the plan the model can see, with a numbered legend (`scripts/plan_png.py`, standard library).
  - `validate_layout`, `room_metrics`, `edit_layout` and `compare_layouts` return `structuredContent` with an `outputSchema`.
  - Resources (`rsd://skill/<path>`) with a resource template, prompts (`design_room`, `review_layout`) that embed the right room and regional modules, and completions.
  - Dual-era protocol: `initialize` for 2024-11-05 to 2025-11-25, and stateless 2026-07-28 with `server/discover`, per-request `_meta`, `resultType` and cache hints. Server icon, title and description.
  - The MCP server is now declared in `.claude-plugin/plugin.json`. The root `.mcp.json` was removed because Claude Code also loaded it as a project server inside a clone, where it failed to start.
- **Metrics CLI:** `python3 scripts/layout_tools.py metrics layout.json` and `compare a.json b.json`.
- 3D shapes for `bathtub`, `closet` and `dryer`; elements whose `front` lists several sides use the first.
- `--boxes` on `layout_to_gltf.py` and `boxes: true` on the MCP `layout_to_gltf` tool keep the old one-box-per-element model.

## v1.3.0 (2026-11-17)

- **3D models** (`scripts/layout_to_gltf.py`, standard-library Python): any layout becomes a glTF 2.0 model (.glb or .gltf) with walls cut around doors and windows, glass, every element at its real size and height, and an `entry` node just inside the door.
- **Blender walkthroughs** (`scripts/blender_walkthrough.py`): renders the model as a still or MP4, orbiting from above or standing in the doorway. Tested with Blender 5.0 (bpy 5.0.1).
- **MCP:** new `layout_to_gltf` tool.
- **Website:** a [3D viewer](https://puvankumarv.github.io/residential-space-designer/viewer.html) for the example rooms or your own .glb.

## v1.2.0 (2026-11-15)

- **MCP server** (`scripts/mcp_server.py`, standard-library Python): `validate_layout`, `floor_plan_svg`, `get_layout_schema`, `list_references` and `read_reference` tools. The Claude Code plugin registers it through `.mcp.json`; other MCP clients can point at the script.
- **SVG floor plans** (`scripts/floor_plan_svg.py`): north-up plans with door swings, windows, routes, and raised items dashed over floor items.
- **Checker:** `--help` prints usage, and a missing file or invalid JSON gives a one-line error instead of a Python traceback. `--plan` can come before the file name.
- **Checker:** `--json` prints errors, warnings and (with `--plan`) the ASCII plans as one JSON object for other tools to read.
- **CI:** tests run on Python 3.10 and 3.13 (3.9 is end-of-life and gone from GitHub's Ubuntu 26.04 runners); actions updated to their Node 24 versions.

## v1.1.0 (2026-11-11)

Fixes from the blind test (see `residential-space-designer/evals/results.md`, run 4):
- **Checker:**
  - `route` elements that must stay clear
  - multi-sided `front` for islands and dining tables
  - window `restrictor`
  - tall-furniture-over-window warning
  - step rise and tread checks
  - the upper-level plan shows full-height items
- **Skill:**
  - defaults when the user can't answer
  - when to load secondary modules
  - a low-ceiling den branch
  - Pattern H puts the window beside the screen
  - two step types and wall-bed sizes
  - NBC and UK code pointers
- **Layout format:** new zone purposes (cooking, dining, wet, worship, laundry, work, play); `route`, `mirror` and `guard` element types; `estimated` and `restrictor` on openings; `room.north`.
- **Examples:** the bathroom example's linen cabinet is lowered below the window sill.
- **Blind test:** outputs and a scoring script added.

## v1.0.0 (2026-11-10)

First public release.

- **Skill:** a 10-step design procedure (region and culture → whole-home plan → intake → diagnose → master decision → zone → storage → services → safety → present).
- **Room modules:** bedrooms (kids', shared, loft, bunk, half-height, wall beds), kitchens, bathrooms, living/dining, entry/corridors/stairs, balcony/laundry, home office, whole home and studios, exterior and site.
- **Regional modules:** Indian homes (pooja rooms, optional Vastu, dry and wet kitchens, utility, elders, climate) and Western homes (drop zones, open kitchens, transformable living, mudrooms, tiny houses).
- **Layout checker** (`scripts/check_layout.py`, standard-library Python):
  - **Every room:** collisions, door swings, clearances, day/night states, outlets, ASCII plans.
  - **Sleeping:** raised-bed safety, headroom, bedside access, an escape window per sleeping area.
  - **Room types:** kitchen aisles and work triangle; toilet, basin and shower clearances; sofa-to-table distance; stairs.
  - **Windows and walls:** window falls, load-bearing niches.
- **Sources:** every number is tagged (CPSC, EN 747, IRC, NKBA, Neufert/Panero, IES, case studies).
- **Examples and tests:** 4 examples, 20 test scenarios with results, and unit tests run by CI on every push.
- **Install options:** Claude Code plugin, `npx skills add`, or this ZIP for the Claude app.
