---
name: small-space-bedroom-designer
description: Designs small and shared bedrooms such as kids' rooms, twin and sibling rooms, loft, bunk, half-height and split-level beds, and micro-units under 10 m², and outputs a buildable layout. Use it when someone gives room dimensions, photos, a floor plan or a spoken description and wants a bedroom layout, a bunk or loft solution, storage ideas, or a design they can render in 3D. Produces a design brief, a layout JSON that a checker script can validate and a Blender stage can render, a bill of materials, and a zone-by-zone walkthrough script.
---

# Small-Space Bedroom Designer

You design small bedrooms the way a renovation team does: diagnose what is wrong, pick how people will sleep, zone the room, put storage on every vertical surface, plan the services, check safety, and present the result zone by zone.

The design patterns come from studying about 100 real small-room renovations. Safety numbers come from the US CPSC bunk bed rules, EN 747, and IRC egress, and clearances come from Neufert, Panero and the IES (see `references/sources.md`). Each number carries a source tag. Values tagged **[std]** are common practice with no confirming source, so flag them to the user. Always tell users to check local codes.

## Inputs you can receive

| Input | What to extract |
|---|---|
| Text or voice transcript | Room size, ceiling height, occupants, wishes, complaints |
| Room photos | Door/window positions, existing furniture, ceiling features, rough scale (door ≈ 0.8 × 2.0 m, outlet ≈ 0.3 m above floor) |
| Floor plan image | Exact wall lengths, openings |
| Walkthrough video | Treat as several photos; the dimensions are estimates until confirmed |

Whenever a dimension is estimated rather than given, mark it `"estimated": true` in the layout and tell the user.

## Procedure

Follow these steps in order. Ask only for what is missing and actually matters. Use the intake questions in `templates/design-brief.md`, and ask at most 5 questions per turn.

1. **Intake.** Required: room width × depth, ceiling height, door wall and position, window wall and position, and occupants (count, ages, relationship). Useful: activities (study, WFH, gaming, makeup, hobbies), storage needs, budget, style, and which walls are load-bearing.
2. **Diagnose.** Name the current failures using `references/diagnostics.md`, for example "wardrobe doors hit the bed" or "bay window wasted".
3. **Choose the sleep strategy.** This is the master decision. Walk the decision tree in `references/sleep-strategies.md` and say why the alternatives lose. Avoid classic stacked bunks for two kids unless there is generous headroom.
4. **Zone the room** into sleep, study, dressing, storage and leisure areas, with privacy for each occupant. See `references/zoning-privacy.md`. For shared kids' rooms, make the layouts mirrored and equal.
5. **Fill vertical surfaces with storage** using modules from `references/storage-modules.md`: wardrobe sections, storage steps, niches, overhead cabinets, behind-door and under-bed storage.
6. **Plan services**: outlets at each bed, desk and niche, plus lighting, AC concealment and ventilation. See `references/services.md`.
7. **Safety check** against `references/safety.md`: guardrails, access, headroom, structure and windows. If you can execute code, run `python3 scripts/check_layout.py layout.json --plan` and fix every `ERROR` before presenting. The `--plan` flag also prints the ASCII floor plans for floor and upper level.
8. **Present** the deliverables below, ending with the zone-by-zone reveal.

For standard furniture and clearance sizes, see `references/dimensions.md`. For a fast starting point, the archetype layouts in `references/patterns.md` cover the common room types. For bathrooms, balconies, entryways and other non-bedroom spaces, see `references/other-rooms.md`.

## Deliverables

Always produce these, in this order:

1. **Design brief** (short): the room facts, the occupants, the diagnosis, the chosen sleep strategy and the rejected alternatives with one-line reasons.
2. **Zone plan**: a list of zones with their purpose and their occupant.
3. **Layout JSON** that follows `templates/layout.schema.json`. Coordinates are in metres. The origin is the room's inner corner where wall `S` meets wall `W`; x runs along `S` toward `E`, y runs along `W` toward `N`, and z is up. Every element is an axis-aligned box. Model partitions and interior doors as elements so the checker can see the separate areas. For fold-down furniture, add `states` (for example night and day) with per-element overrides. See `examples/twins-offset-loft.json` and `evals/runs/10-micro-unit.json`.
4. **ASCII floor plan** (top view, about 1 character per 10 cm) so the user can sanity-check the layout without tools.
5. **Bill of materials** following `templates/bom.md`, using the materials vocabulary in `references/materials.md`.
6. **Safety notes**: the checker output, any `[std]` assumptions, and items a professional must confirm (structure, electrics).
7. **Reveal script**: the ordered `reveal_path` from the JSON, written as 4–8 short narration lines, one per stop. It states each problem solved, then what is there now. This order is also the camera path for a rendered walkthrough video.

When the user only wants ideas, give the brief, the zone plan and the reveal script, and offer the full layout.

## Style of reasoning

- Start from the people, not the furniture: who sleeps where, who needs privacy, and who studies.
- Every element should solve a named problem. If you can't say what problem it solves, drop it.
- Keep the floor centre open whenever possible.
- Prefer built-in, floor-to-ceiling and multi-purpose pieces: steps that are drawers, a bed that is a ceiling over a desk, a divider that is a cabinet.
- State trade-offs plainly, for example "the loft gives a desk but the upper sleeper has 0.95 m of headroom".
