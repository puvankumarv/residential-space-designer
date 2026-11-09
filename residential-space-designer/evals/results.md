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

# Run 2: residential scope (2026-11-04)

The skill was widened from bedrooms to every residential space. New room modules: kitchen, bathroom, living/dining, entry/circulation and stairs, balcony/laundry, home office, whole home and studio.

| # | Scenario | Result | Checker |
|---|---|---|---|
| 11 | Galley kitchen | ✅ `examples/galley-kitchen.json`: 1.2 m aisle, triangle legs about 2 m | 0/0 |
| 12 | Compact bathroom | ✅ `examples/compact-bathroom.json`: toilet front 1.0 m, sides 0.6/0.9 m, 0.92 m shower with 0.78 m entry | 0/0 |
| 13 | Studio, WFH | ✅ `examples/studio-apartment.json`: wall bed with day/night states, one-wall kitchen, sofa 0.40 m from the coffee table | 0/0 |
| 14–16 | Whole-home plan, living room, stair | ⏸ not run yet | — |

**New checks, each tested with a broken layout:**
- **Kitchen:** an aisle squeezed to 0.8 m gives walkway warnings on every work element. Stretching the fridge to the far end gives `cooktop–fridge 3.78 m` and `total 8.24 m > 7.9 m`.
- **Bathroom:** a toilet 0.30 m from the side wall, with the vanity pushed into its front zone and a 0.70 m shower, gives 4 errors.
- **Living:** a coffee table 0.80 m from the sofa gives a warning.
- **Window falls:** a 0.5 m sill with a 15 m drop, and a daybed under the window, give 2 warnings.
- **Stairs:** a 0.22 m riser, 0.22 m tread, 0.8 m width and 1.9 m headroom give 4 errors.
- **States:** messages that are the same in every state are now printed once instead of once per state.

All 10 layouts (4 examples and 6 bedroom runs) pass with 0 errors. The only warning is #4's intended bedside trade-off.

# Run 3: regional scenarios 17–20 (2026-11-09)

**How this was run:** I followed SKILL.md with the regional and exterior modules, as in runs 1–2, and I'm also the author. Whole-home scenarios get a home plan (below) plus layouts for the rooms the skill chose to detail. Layouts are in `runs/` (regenerate with `python3 evals/build_regional.py`).

## 17: Vastu house, 30×40 ft east-facing plot, Bengaluru, G+1
**Intake the skill would ask first:** How strictly do you follow Vastu (fixed rules or preferences)? Who uses the pooja room daily? Do the parents manage stairs? Is there household help? What are the setbacks under the local bye-laws?

**Home plan** (assumed setbacks: front 1.5 m, rear 1.0 m, sides 0.9 m; to be confirmed locally):
```
GROUND FLOOR  (N up · road on the EAST)
 W                                                      E
 +-------------+--------------------+------------------+
 | Parents'    |  Living, double    |  Foyer  + POOJA  |  ← pedestrian gate
 | bath        |  height, faces N   |  (NE)   ENTRY    |    (NE corner)
 +-------------+---------+----------+------------------+
 | Parents'    | Dining + |  Stair  |  Dry kitchen     |  CAR PORCH
 | bedroom SW  | wash     |  (S)    |  (SE), hob → E   |  (front setback)
 | sit-out (W) | basin    |         +------------------+
 +-------------+----------+---------+  Utility (S)     |
   ~~~ south side setback: drying yard, service door ~~~~

FIRST FLOOR
 +-------------+--------------------+------------------+
 | Child (NW)  |  Void over living  |  Open terrace    |
 | + study     |  + library landing |  (NE, light)     |
 +-------------+---------+----------+------------------+
 | Master (SW) | Family   |  Stair  | Bath  | Covered  |
 | + walk-in   | lounge   |  (S)    | (SE)  | terrace  |
 +-------------+----------+---------+-------+----------+
```
- **Vastu placements used:** entry and pooja NE; kitchen SE; parents' bedroom SW (ground floor) and master SW (first floor); child NW; stair S; no toilet in the NE.
- **Trade-offs stated:** the NE pooja takes the best morning-light corner from the living room, so the double-height void and the NE terrace bring that light back. A strict SW master on both floors stacks the two biggest bedrooms, which suits the structure.
- **Exterior:** separate pedestrian gate (NE) and car porch (front, south half); the porch roof doubles as the covered terrace.
- **Detailed rooms:** `17a-vastu-kitchen-utility.json` (SE dry kitchen + utility to the south setback, hob on the east wall, deep drawers, corner carousel) and `17b-parents-bedroom.json` (ground floor, no steps, low bed reachable from both sides, outward-opening bath door, near the pooja room).

## 18: Pune 3BHK flat, daily Indian cooking, maid twice a day
- **Brief:** keep the parallel kitchen and the **utility balcony**; give the maid a route main door → dining → kitchen → utility that never passes the bedrooms; put a **pooja unit** on the NE wall of the living/dining; lofts above the wardrobes and kitchen.
- **Detailed room:** `18-pune-flat-kitchen-utility.json`: 1.4 m aisle; triangle legs 2.06/2.70/1.50 m; deep drawers by the hob; lofts; utility with washer, low vessel-washing tap and ceiling drying rack, behind a sliding glass door.

## 19: Victorian terrace, London, two kids, see them while cooking
- **Brief:** knock the dark back rooms into one kitchen-diner-family room facing the garden; **island sink facing the family zone and garden**; keep the original hall tiles, cornices and stair; drop zone in the hall; under-stair cupboard as pantry or utility; boot bench by the garden doors.
- **Detailed room:** `19-london-terrace-kitchen-diner.json`: E-wall run plus island (1.2 m aisle), sofa 0.40 m from the coffee table, low toy storage, table by the sliding doors. Party walls are flagged load-bearing (structural engineer and party wall agreement needed).

## 20: Sloping site, family of five, love hosting
**Home plan (section, street to valley):**
```
 STREET (east, high)                                   VALLEY (west, low)
 Level  0 │ garage · entry → HOSTING: living | island kitchen | dining for 10 → DECK
 Level −1 │ KIDS: 3 bedrooms around a shared lounge, bath, side garden
 Level −2 │ MASTER SUITE (most private) + guest/den, opens onto the lawn
```
- **Privacy by floor:** hosting at street level, kids in the middle, parents lowest and quietest, with the garden. A courtyard or lightwell at level −1 brings daylight into the slope.
- **Detailed room:** `20-sloping-hosting-level.json`: an island kitchen (1.2 m aisle, triangle well inside limits), a table for 10 opening onto the deck, two sofas facing the valley view, and a stair down (riser 0.175 m, tread 0.28 m, width 1.0 m, headroom 2.4 m: all pass).

## Results
| # | Expectation | Result |
|---|---|---|
| 17 | Ask about Vastu strictness; parents downstairs near the pooja room; SE kitchen, NE pooja or trade-offs; dry kitchen + utility; site sketch | ✅ all present; 17a and 17b pass with 0/0 |
| 18 | Utility balcony; deep drawers; pooja unit; lofts; maid route avoids bedrooms | ✅ 0/0 |
| 19 | Sight lines; original features kept; drop zone; under-stair storage | ✅ 0/0 |
| 20 | Split levels; privacy by floor; hosting level; deck; site sketch | ✅ 0/0 after one fix |

## What the run found and what changed
1. **Blind corners:** the first 17a draft modelled the L-corner as a counter with a front, and the checker reported 0 m free in front. That's correct, because it's a blind corner. The kitchen module now says to model corners as a `cabinet` (carousel), and 17a uses one.
2. **Fall risk caught:** the first 20 draft put the sofa against the view window with a 3.5 m drop outside. The checker warned that it was climbable, so the seating moved 0.7 m off the window wall.
3. **Open-plan kitchens are checked:** kitchen aisle and triangle checks now also run for `living_dining` and `dining` rooms that contain a sink or hob (scenarios 19 and 20 rely on this).

## Still not checked automatically
Home-plan rules (Vastu placements, elders near the pooja room, the maid's route, privacy by floor, adjacency) are judged by reading the plan, not by the checker, which works one room at a time. A multi-room home-plan checker is on the roadmap ("multi-room home layouts in a single file").
