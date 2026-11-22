# Contributing

Thanks for helping. This project is a Claude skill, a layout checker and an MCP server, all in plain Python 3 with no dependencies. The one rule that matters most: **every number needs a source.**

## Run the tests

```bash
python3 -m unittest discover -s tests
```

CI runs the same suite on Python 3.10 and 3.13, checks every example layout, and makes sure the generated scenario layouts match the committed files.

## Ways to help

| You want to… | Where it goes |
|---|---|
| Report a layout the checker gets wrong | Open a **Layout problem** issue with the layout JSON and what you expected |
| Add or fix a design rule | The room module in `residential-space-designer/references/rooms/`, with a source tag |
| Add a check to the checker | `residential-space-designer/scripts/check_layout.py`, plus a test in `tests/test_checker.py` |
| Add a regional practice | `references/regional/india.md` or `western.md` |
| Add an example room | `residential-space-designer/examples/`, a layout that passes `check_layout.py` with no errors |
| Improve the 3D or plan drawings | `scripts/furniture.py`, `layout_to_gltf.py`, `plan_drawing.py` |

## Sourcing rules

- Every dimension or safety value carries a tag from `references/sources.md`, such as `[IRC]`, `[NKBA]` or `[EN747]`.
- A new source gets a row in that table: what it is, a link, what it supplies and how strong it is (law, code, standard, guideline, rule of thumb).
- If two sources disagree, use the stricter value and say so.
- If nothing confirms a value, tag it `[std]`; the skill flags those to the user.
- Case studies (`[DI]`, `[HT]`) supply patterns only, never dimensions. Paraphrase them; don't copy text.

## Code style

- Standard library only, so the skill and server run anywhere with Python 3.
- Checker constants carry their source tag: either on a comment above a group (`# Kitchen [NKBA]`) or at the end of the line (`RAIL_MIN = 0.13  # [CPSC]`).
- Keep error messages short and actionable: what is wrong, by how much, and the source.
- Run the tests before opening a pull request.

## Safety

This tool gives starting layouts, not certified designs. Changes must not weaken a safety check (raised beds, escape windows, stairs, window falls) without a stronger source that says so.
