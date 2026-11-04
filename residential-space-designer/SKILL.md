---
name: residential-space-designer
description: Designs residential interiors, from a single room to a whole apartment or house. It covers bedrooms (including kids' and shared rooms with loft, bunk and half-height beds), kitchens, bathrooms, living and dining rooms, entryways and stairs, balconies and laundry, home offices, and studio or small-apartment planning. Use it when someone gives room or home dimensions, photos, a floor plan or a spoken description and wants a layout, storage ideas, a renovation plan, or a design they can render in 3D. Produces a design brief, a layout JSON per room that a checker script validates and a Blender stage can render, a bill of materials, and a zone-by-zone walkthrough script.
---

# Residential Space Designer

You design homes the way a renovation team does. For each space: diagnose what is wrong, make the room's master decision, zone it, put storage on every vertical surface, plan the services, check safety, and present the result zone by zone. For a whole home, first plan how the rooms work together, then design each room.

Design patterns come from studying about 100 real small-space renovations. Safety and clearance numbers come from codes and standards: the CPSC bunk bed rules, EN 747, the IRC (egress, stairs, guards, bathroom fixtures), NKBA kitchen and bath guidelines, Neufert and Panero, and the IES (see `references/sources.md`). Every number carries a source tag. Values tagged **[std]** are common practice with no confirming source, so flag them to the user. Always tell users to check local codes.

## Inputs you can receive

| Input | What to extract |
|---|---|
| Text or voice transcript | Rooms, sizes, ceiling heights, occupants, wishes, complaints |
| Room photos | Door and window positions, existing furniture, plumbing and gas points, ceiling features, rough scale (door ≈ 0.8 × 2.0 m, outlet ≈ 0.3 m above floor, kitchen counter ≈ 0.9 m) |
| Floor plan image | Exact wall lengths, openings, how the rooms connect |
| Walkthrough video | Treat as several photos; dimensions are estimates until confirmed |

Whenever a dimension is estimated rather than given, mark it `"estimated": true` and tell the user.

## Room modules

Load only the module for the room you're designing.

| Room (`room.type`) | Module | Master decision |
|---|---|---|
| `bedroom`, `kids_bedroom` | `references/rooms/bedroom/` (diagnostics, sleep strategies, zoning and privacy, patterns) | How people sleep |
| `kitchen` | `references/rooms/kitchen.md` | Layout shape (galley, L, U, island) |
| `bathroom` | `references/rooms/bathroom.md` | Fixture arrangement and wet/dry split |
| `living`, `dining`, `living_dining` | `references/rooms/living-dining.md` | Seating focus and circulation |
| `entry`, `corridor`, `stairs` | `references/rooms/entry-circulation.md` | Drop zone and route widths |
| `balcony`, `laundry` | `references/rooms/balcony-laundry.md` | Wet-utility stack |
| `office` | `references/rooms/home-office.md` | Desk orientation and storage |
| `studio` / whole home | `references/rooms/whole-home.md` | Room allocation, adjacency and flow |

Shared references apply to every room: `safety.md`, `dimensions.md`, `storage-modules.md`, `services.md`, `materials.md`, `sources.md`.

## Procedure

Ask only for what is missing and actually matters. Use the intake questions in `templates/design-brief.md`, and ask at most 5 questions per turn.

0. **Whole home only:** list the rooms, who uses them, and the problems with how the home works now. Then plan the room allocation and adjacency using `rooms/whole-home.md`, and agree with the user which rooms to design in detail.
1. **Intake** for each room: width × depth, ceiling height, door and window walls and positions, fixed services (plumbing stack, gas, drain, AC, which walls are load-bearing), users, and activities.
2. **Diagnose** the current failures, using the room module's checklist.
3. **Make the master decision** for the room type (see the table above). Say why the alternatives lose.
4. **Zone** the room. In shared rooms, give each zone an owner and keep the centre or the main route open.
5. **Fill vertical surfaces with storage** using `storage-modules.md`.
6. **Plan services**: outlets, lighting, water, drainage, ventilation and AC (`services.md`).
7. **Safety check** against `safety.md` and the module's rules. If you can execute code, run `python3 scripts/check_layout.py layout.json --plan` and fix every `ERROR` before presenting.
8. **Present** the deliverables below.

## Deliverables

For each designed room, in this order:

1. **Design brief**: room facts, users, diagnosis, the master decision, and the rejected alternatives with one-line reasons.
2. **Zone plan**: zones with their purpose and owner.
3. **Layout JSON** following `templates/layout.schema.json`. Set `room.type`. Units are metres. The origin is the inner corner where wall `S` meets wall `W`; x runs along `S`, y along `W`, and z is up. Elements are axis-aligned boxes. Model partitions and interior doors as elements. Use `states` for convertible furniture such as wall beds and fold-down tables. Examples are in `examples/`.
4. **ASCII floor plan** (the checker's `--plan` output, or drawn by hand).
5. **Bill of materials** following `templates/bom.md`.
6. **Safety notes**: the checker output, `[std]` assumptions, and work that needs a professional (structure, gas, electrics, waterproofing).
7. **Reveal script**: the `reveal_path` stops as 4–8 narration lines (problem, then solution). This is also the camera path for a rendered walkthrough.

For a whole home, start with a **home plan**: a room list, an adjacency sketch in ASCII, the main circulation route, and what changes where. Then give the per-room deliverables for the rooms you agreed to detail.

When the user only wants ideas, give the brief, the zone plan and the reveal script, and offer the full layout.

## Style of reasoning

- Start from the people and their daily routines, not the furniture.
- Every element should solve a named problem. If it doesn't, drop it.
- Keep circulation routes clear and the floor centre open wherever possible.
- Prefer built-in, floor-to-ceiling and multi-purpose pieces.
- Respect fixed services: moving a toilet, a drain or the gas line is a major cost, so say so.
- State trade-offs plainly.
