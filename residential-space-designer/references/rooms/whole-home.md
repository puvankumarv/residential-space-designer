# Whole home and studio planning

Use this before designing individual rooms when the request covers a whole apartment, a house or a studio.

## 1. Room allocation
List each household member's daily routine: sleep, work or study, cooking, guests, hobbies. Then assign rooms:
- The biggest or brightest room goes to the activity that uses it most hours, not automatically to the "master bedroom".
- Kids sharing a room: see `rooms/bedroom/sleep-strategies.md`. Teens of different sexes usually need separation.
- Work-from-home: a dedicated corner with a door or a closable cabinet beats the dining table.

## 2. Zoning: public, private and service
| Zone | Rooms | Rule |
|---|---|---|
| Public | Entry, living, dining, kitchen | Close to the front door |
| Private | Bedrooms, study | Away from the entry; quieter side |
| Service | Bathroom, laundry, balcony | **Stack wet rooms** along the existing plumbing; a bathroom near the bedrooms |

## 3. Adjacency and flow
- Kitchen next to dining and reasonably close to the entry (groceries).
- A bathroom reachable without walking through a bedroom.
- Laundry near the bathroom or balcony (water and drainage).
- Keep corridors short. Every metre of corridor is storage or living space lost. Corridors need ≥ 0.91 m clear (`entry-circulation.md`).
- **Every sleeping room needs its own escape window** [IRC]. ✔ (the checker enforces this per area)
- Sketch the main route from the front door to each room. It should not cross the seating group or the kitchen work triangle.

## 4. Studios and micro-flats
- Split the single room into zones with height, not walls: a raised sleeping platform with storage under it, a loft, or a half-height partition [DI 12, 23, 32].
- Choose dividers that keep the daylight: glass, slatted screens, open shelving, curtains.
- Convertible furniture: a wall bed plus a fold-down desk or table. Model it with `states` and check each one. ✔
- Keep kitchen fumes away from the sleeping zone: a ducted hood, or place the kitchen near the entry.

## 5. Deliverable: the home plan
1. A room list with users and main activities.
2. An ASCII adjacency sketch of rooms, doors and the main route.
3. What moves or changes, with a cost flag for plumbing and structural moves.
4. The order to design or renovate the rooms in.
5. Then a layout JSON for each room (one file per room, with the right `room.type`).
