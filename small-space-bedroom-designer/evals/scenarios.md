# Test scenarios (build-order step 2)

Run each prompt through the skill. A pass means the layout JSON gets 0 checker errors and the stated expectation holds.

| # | Prompt | Expect |
|---|---|---|
| 1 | "My 10-year-old's room is 2.6 × 3.0 m with a 2.75 m ceiling. He needs a desk, and the wardrobe door hits the bed." | Loft over a desk (pattern A), sliding wardrobe, diagnosis names the door clash |
| 2 | "Twins aged 9, room 3.4 × 3.4 m, ceiling 2.8 m. They fight over the bunk bed." | Offset or side-by-side layout, not a stacked bunk; mirrored storage |
| 3 | "Three kids aged 5, 8 and 12 in a 4 × 3.5 m room, ceiling 2.9 m." | Multi-bed system; the 5-year-old is not on an upper bed |
| 4 | "Couple in a 3 × 3.2 m bedroom. She needs a vanity, he works from home." | Platform with split step drawers; split desk; niches instead of nightstands |
| 5 | "Teen girl, 2.4 m ceiling, 2.8 × 2.9 m room, wants a hideout to game in." | Recognizes a loft over a desk won't fit; half-height bed or den with ≥ 1.0 clear; asks about window/door |
| 6 | "Brother 14 and sister 11 share 3.2 × 4.2 m." | A partition with a door or frosted glass; equal zones |
| 7 | Photo only (no numbers) | Estimates from the door, marks `estimated: true`, asks to confirm the width and ceiling |
| 8 | "Make a niche in the wall behind the bed" (structure unknown) | Asks about load-bearing; the checker errors until it's confirmed |
| 9 | Voice-style ramble: "uh so it's like a small room maybe three metres, two boys, they need desks" | Pulls out the facts; asks at most 5 focused questions |
| 10 | "4 m² micro-room, can't even lie flat" | Fold-up or pull-out bed; any structural extension is flagged for an engineer |
