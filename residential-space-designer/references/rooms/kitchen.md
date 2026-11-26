# Kitchen

Source tags are explained in `../sources.md`. ✔ means `scripts/check_layout.py` checks it (with `room.type: "kitchen"`).

## Master decision: layout shape
| Shape | Fits when | Watch out for |
|---|---|---|
| **One-wall** | Room ≤ 2 m wide, or a studio | No real triangle; add a mobile island or a fold-down table |
| **Galley** (two parallel runs) | 2.1–3.0 m wide | Aisle 1.07–1.22 m; no through traffic if possible |
| **L-shape** | Corner room, open plan | Use corner carousels or a diagonal corner sink [DI 66] |
| **U-shape** | ≥ 2.4 m wide and ≥ 2.4 m deep | The aisle between the legs must still meet the minimum |
| **Island / peninsula** | Open plan with ≥ 1.07 m on all working sides | Seating clearance behind the stools |

## Diagnostics
| Symptom | Usual fix |
|---|---|
| Fridge door hits a wall or blocks the aisle | Move the fridge to a run end; reverse the door hinge |
| No landing space beside the cooktop or sink | Shift appliances; add a pull-out board |
| Through traffic crosses the work triangle | Reorient the runs; move the doorway or island |
| Upper cabinets out of reach and wasted | Pull-down racks, open shelves, full-height pantry |
| Window sill too high to extend the counter | Lower the sill and run the counter under it [DI 66] |
| Corner cabinets unusable | Corner carousel or diagonal corner sink [DI 66] |

**Modelling L and U corners:** give the corner unit its own element as a `cabinet` (carousel or magic corner), not a counter with a `front`. Otherwise the checker correctly reports "0 m free in front" for a blind corner.

## Rules
| Rule | Value | Source | Checked |
|---|---|---|---|
| Work aisle, one cook | ≥ 1.07 m (42 in) | [NKBA] | ✔ warns on the front clearance of counters, sink, cooktop, fridge and island; give an island every working side, e.g. `"front": ["+x", "-x"]` |
| Work aisle, two or more cooks | ≥ 1.22 m (48 in) | [NKBA] | |
| Walkway past a kitchen (not a work aisle) | ≥ 0.91 m (36 in) | [NKBA] | ✔ warns below 0.91 m |
| Work triangle (sink, cooktop, fridge): total of the three legs | ≤ 7.9 m (26 ft) | [NKBA] | ✔ |
| Each triangle leg | 1.2–2.7 m (4–9 ft) | [NKBA] | ✔ |
| Sink landing area | 0.61 m on one side, 0.46 m on the other | [NKBA] | |
| Cooktop landing area | 0.30 m on one side, 0.38 m on the other | [NKBA] | |
| Fridge landing area, handle side | 0.38 m | [NKBA] | |
| Seat width per diner at a counter or table | 0.61 m | [NKBA] | |
| Clearance behind seated diners | 0.81 m with no traffic; 0.91 m to edge past; 1.12 m to walk past | [NKBA] | |
| Counter height | about 0.90 m | [std] | |
| Upper cabinets above the counter | 0.45–0.50 m | [std] | |
| Hood above cooktop | Follow the manufacturer, typically 0.65–0.75 m | [std] | |

- Don't put the cooktop under a window with curtains, or right beside a doorway.
- Gas, hob and electrical connections are professional work.
- Ventilation: a ducted hood where possible. In small flats, keep the kitchen's air separate from the bedrooms.

## Regional notes
- **Indian kitchens:** daily heavy cooking calls for a ducted chimney, **deep drawers for pressure cookers and kadai**, a tall pantry beside the cooktop, and often a separate **wet kitchen or utility** for vessel washing and the washing machine. Plan storage from the family's utensil list [HT-I4, I6]. See `../regional/india.md`.
- **Western small kitchens:** toe-kick drawers, open glass shelves in front of windows, a rolling trolley, task lights in front of the cook [HT-W1]. See `../regional/western.md`.

## Storage moves
Full-height pantry with pull-out baskets [DI 66]; stacked drawer bases instead of doors; a rail system on the backsplash; a toe-kick drawer; appliance garages; an over-fridge cabinet for rarely used items.

## Patterns from room videos
| Pattern | How | Source |
|---|---|---|
| **Fridge at a run end, near the way in** | Never mid-run: it splits the worktop into two short pieces and puts snack traffic through the work zone. ✔ The checker warns when worktop touches the fridge on both sides | [YT-K1] |
| **The kitchen is also a corridor** | Trace routes to the garden, utility, bins and table; if one crosses the sink–hob–fridge strip, move the access, not the units | [YT-K1] |
| **Draw every swing on one sheet** | Appliance doors, drawers and corner cupboards; check the bin drawer opens with the dishwasher down | [YT-K1] |
| **Room width decides the layout** | Island only from about 3.6 m of room width with 1.0–1.2 m clear on the working side; galleys under about 2.4 m are poor | [YT-K1], agrees with [NKBA] |
| **A view from the sink** | You stand there longest: face a window or the room, not a blank wall; avoid gloss worktops facing low west sun | [YT-K1] |
| **Services fix the sink and hob** | Sink near the stack with enough fall; hood on or near an external wall with a short, straight duct | [YT-K1], [YT-K2] |
| **A second station** | Somewhere for the second person: about 800 mm of worktop with a socket away from hob and sink (island end or short return) | [YT-K1] |
| **Indian: hob on the longest counter** | Room for the rolling board and everything around it; the drain point fixes the sink | [YT-K2] |
| **Modular widths** | Cabinets in 300 / 450 / 600 / 750 / 900 mm so standard baskets, trays and shutters fit; odd widths leave dead pockets | [YT-K2] |
| **Storage from a list** | List dals and pulses (shallow drawers sized to canisters), atta, rice and sugar (grain trolley), oils, ladles; then pick a pantry type | [YT-K2], [HT-I6] |
| **Appliance garage** | Rolling shutter (450 / 600 / 900 mm) with daily appliances on shelves and sockets behind, so nothing is unplugged and moved | [YT-K2] |
| **Round corner trays** | A swing-out corner unit with round trays for kadais and pressure cookers | [YT-K2] |

## Reveal order
Entry view → the main run and triangle → landing and prep space → storage reveal (pantry, drawers) → seating or island → wide shot.
