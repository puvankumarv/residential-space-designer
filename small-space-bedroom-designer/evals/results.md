# Scenario run 1 (2026-11-04)

**How this was run:** I wrote each layout myself by following SKILL.md. I'm also the skill's author, so this tests whether the rules and checker produce sound designs. It does **not** test how a fresh Claude session would behave with only the skill loaded. That needs a separate blind run.

Layouts are in `runs/` and are regenerated with `python3 evals/build_runs.py`. Check them with `python3 scripts/check_layout.py runs/<file> --plan`.

| # | Scenario | Result | Design | Checker |
|---|---|---|---|---|
| 1 | Boy 10, 2.6×3.0×2.75, door hits bed | ✅ pass | Loft over desk + stair cabinet, sliding wardrobe | 1st try: **WARN, the wardrobe blocked the escape window**. Moved it. Now 0/0 |
| 2 | Twins 9, 3.4×3.4×2.8 | ✅ pass | Offset L-loft (`examples/twins-offset-loft.json`) | 0/0 |
| 3 | Kids 5/8/12, 4.0×3.5×2.9 | ✅ pass | Loft + desk for k12; bunk with k5 on the floor bed and k8 up; window desk row; 3-section wardrobe | 1st try: **ERROR, the steps sat in the desk chair zone**. Shortened the desk. Now 0/0 |
| 4 | Couple, 3.0×3.2×2.6, vanity + WFH | ⚠ pass with trade-off | Platform with split drawers, headboard cabinet, split desk at the window | 0/0. The left partner has no side access (gets in from the foot); the checker doesn't detect this |
| 5 | Teen, 2.4 m ceiling, gaming hideout | ✅ pass | Rejected loft-over-desk (needs ≈2.6 m); half-loft at 1.0 m over a den, 1.15 m headroom | 0/0 |
| 6 | Brother 14 + sister 11, 3.2×4.2×2.7 | ⚠ pass with assumption | Partition + frosted sliding door; sister on a floor bed, brother on a loft | 0/0, but only because I **assumed two windows**. The checker doesn't verify each partitioned room keeps an escape window |
| 7 | Photo only | ⏸ not run | — | Needs a real room photo |
| 8 | Niche, structure unknown | ✅ pass | — | Checker errors on an unknown wall and passes once `load_bearing: false` is confirmed |
| 9 | Rambling voice input | ✅ pass (simulated) | Extracted: ~3 m room, 2 boys, desks needed. Asked 5 questions: exact width × depth, ceiling, door/window walls, ages, main complaint | — |
| 10 | 4 m² micro-room | ✅ pass | Fold-down wall bed (night state), sliding door, overhead shelf; extension rejected | 0/0 |

## What the run found and what changed

1. **The checker caught 2 real mistakes in my own designs** (#1 and #3). That's good evidence it's worth running before presenting.
2. **Gap fixed:** the checker didn't check headroom for a lower bunk under an upper bed. It now flags less than 0.76 m as an error and less than 0.84 m as a warning, and `safety.md` has been updated. Tested: raising the lower mattress to leave a 0.65 m gap produces an error.

## Gaps fixed after run 1
- **Bedside access:** the checker now warns when a floor bed has no long side with a free strip 0.6 m deep and 0.9 m long, and when a double bed lacks this on both sides. #4 now shows the trade-off as a warning, which is the intended outcome since the brief has to state it. Tested: a desk blocking the open side makes it report 0 sides.
- **Escape window per partitioned area:** partitions and interior `door` elements split the floor into areas, and every bed's area must reach an egress window. Tested: removing #6's north window gives `loft_b: its area … has no egress window`.
- **Day and night states:** layouts can list `states`, and elements carry per-state overrides (`hidden` removes the element in that state). Each state is checked and drawn separately. #10 now models the bed folded away and the desk open for day. Tested: pushing the day desk into the bed housing gives 3 `[day]` errors.
- **Door element type:** `door` was added to the schema, and #6's sliding door uses it.
- **ASCII plan:** elements are drawn wherever they touch a cell, so thin boards and doors now show.

After the fixes, all 7 layouts have 0 errors. The one remaining warning is #4's bedside trade-off, which is intended.

## Still open
- **A blind run:** a fresh session given only the skill folder, on scenarios 1–10.
- **Scenario 7** needs a real room photo.
