# Living and dining

Source tags are explained in `../sources.md`. ✔ means `scripts/check_layout.py` checks it (with `room.type` of `living`, `dining` or `living_dining`).

## Master decision: seating focus and circulation
Pick the focus first: TV, a view or window, or conversation. Seating faces the focus. The main circulation route runs **behind or beside** the seating group, never through it.

| Layout | Fits when |
|---|---|
| Sofa facing the TV wall | Narrow rooms; the classic layout |
| L-sofa in a corner | Small rooms; frees the centre. A corner platform sofa with drawers saves more [DI 26] |
| Two sofas facing each other | Conversation-first rooms; needs width |
| Dining at the window, lounge at the back | Open plan; daylight for meals |
| Fold-down or extendable dining | Studios and micro-flats |

## Diagnostics
| Symptom | Usual fix |
|---|---|
| People walk between the sofa and the TV | Re-route the path behind the sofa; float the sofa off the wall |
| Coffee table too far away or blocking legs | 0.36–0.46 m from the sofa front |
| Loose furniture, no storage | A full TV wall of cabinets; platform sofa with drawers [DI 26] |
| Dining chairs hit walls | Use a bench on the wall side; round table in tight spots |

## Rules
| Rule | Value | Source | Checked |
|---|---|---|---|
| Sofa front to coffee table | 0.36–0.46 m (14–18 in) | [RET-L] | ✔ warns outside the range |
| Main walkway | ≥ 0.9 m; small-room minimum 0.6 m | [BO] [IDE] | ✔ via front clearances |
| TV viewing distance | About 1.5–2.5 × the screen diagonal | [std] | |
| Dining: width per diner | 0.61 m | [NKBA] | |
| Dining: clearance behind a chair | 0.81 m (no traffic) to 1.12 m (people walk behind) | [NKBA] | ✔ give the table `front` as a list of the sides with chairs, e.g. `["+y", "-y"]` |
| **Main route stays clear** | Draw the path (front door → inner door, door → balcony) as a `route` element ≥ 0.9 m wide | [BO] | ✔ error if anything stands on it |
| General lighting | 50–150 lux, plus task lamps at seats | [IES] | |

## Storage moves
A TV wall with closed cabinets and open display niches; window-seat storage; platform seating with drawers [DI 26]; a sideboard that doubles as a room divider in open plan.

## Patterns from room videos
| Pattern | How | Source |
|---|---|---|
| **Paths first** | Map the routes people will take before placing anything; seating goes in the quiet pockets left over, dining in the next one, desks or shelves on slim edges | [YT-L1] |
| **Path around, not through** | Main path about 0.9 m, kept to the edge of the seating group so nobody walks between two chairs | [YT-L2], agrees with [NKBA] walkway |
| **Align to an axis** | Centre the seating on a window, fireplace or wall, and the table on a window or light point; loosen once it works | [YT-L1] |
| **First view and seat views** | From the entrance, show the seating group, not the TV or kitchen; from the sofa, look at a window or calm wall, not the kitchen or WC door | [YT-L1] |
| **Faces first, screen second** | Seats in a U or loose circle within conversation distance; mix chair types; dining chairs can join for guests | [YT-L1], [YT-L2] |
| **Pull the sofa off the wall** | 20–30 cm off the wall in small rooms; float it with a console behind in large rooms | [YT-L2] `[std]` |
| **Anchor and enclose** | Coffee table in the middle, side tables and lamps beside seats so each seat feels enclosed | [YT-L1] |
| **Rug holds the group** | At least the front legs of every main seat on the rug | [YT-L1], [YT-L2] |
| **TV at seated eye level** | Centre of the screen near seated eye height; a screen filling about 30° of view puts a 50-inch TV within about 2.1 m | [YT-L2] (SMPTE guidance) |
| **Vary heights and light** | Mix tall and low pieces; layer lamps instead of one ceiling light | [YT-L2] |

## Reveal order
Entry view → seating focus → storage wall → dining → wide shot.
