# Changelog

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
