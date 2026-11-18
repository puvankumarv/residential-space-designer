# MCP server research (November 2026)

What we looked at before building MCP server v2, and what we took from it.

## 1. The protocol

| Revision | What matters for a small stdio server | What we did |
|---|---|---|
| 2025-06-18 | `title` on tools; `outputSchema` + `structuredContent` (with the same JSON as text for older clients); `resource_link` and embedded resources in results; image content | Structured output on the four data tools; PNG image content from `floor_plan_png` |
| 2025-11-25 | Icons on servers, tools, prompts; `description` on the server's `Implementation`; input-validation problems should be **tool execution errors** (`isError: true`) so the model can correct itself; JSON Schema 2020-12 as the default dialect; stdio servers may log anything to stderr | Server icon, title, description; all input problems are `isError` results; logs only to stderr |
| 2026-07-28 | Stateless: no `initialize` handshake, every request carries `_meta["io.modelcontextprotocol/protocolVersion"]`; servers **must** implement `server/discover`; every result has `resultType: "complete"`; list and read results carry `ttlMs` and `cacheScope`; unsupported version → error `-32022` with `supported` and `requested`; "resource not found" moves from `-32002` to `-32602`; `ping` and `logging/setLevel` removed; Roots, Sampling and Logging deprecated | Dual-era server: legacy clients use `initialize`, modern clients are served per request. Real Claude Code connects as modern (2026-07-28) |

Sources: the official changelogs for [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/changelog) and [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools), [versioning](https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle) and [server/discover](https://modelcontextprotocol.io/specification/2026-07-28/server/discover).

Not adopted, on purpose: Sampling, Roots and Logging (deprecated), tasks (nothing here runs long), elicitation (the prompts ask in chat instead), Streamable HTTP (the plugin runs locally over stdio).

## 2. Other design MCP servers

From directory listings and READMEs (Nov 2026); we did not run them.

- **architecture-mcp** (npm): `create_floor_plan` (positions, SVG, compliance warnings), `interior_design` (mood board, palette, furniture layout), `material_palette`, `lighting_analysis`, `cost_estimate`; walkthroughs and contractor specs behind a paid plan.
- **Sweet Home 3D MCP**: about 40 tools driving the desktop app: walls, rooms, furniture, PNG/SVG plan export, ray-traced renders.
- **Skopia**: `build_a_room`, text to a validated layout and a rendered plan.
- **parti-mcp**: blueprint-style SVG floor and site plans.
- **Roomvana**: style and photo restyling; does not change layouts.

What they suggested for us: models need to **see** plans (PNG, not just SVG text), to get **numbers** back (areas, compliance), and to iterate cheaply. What we kept out: prices and cost estimates (no sourced data), and invented product catalogues.

## 3. What v2 added, and why

| Addition | Why |
|---|---|
| `floor_plan_png` | Models read images, not SVG markup. A plain PNG (standard-library zlib) with numbered elements and a text legend lets Claude look at what it designed. Verified: Claude Code read the twins' plan and described the loft, steps, desks and door correctly |
| `room_metrics` | Turns a layout into the numbers a brief asks about: free floor, storage volume, hanging rail, sleeping places, seats, worktop run, glazing ratio. The daylight check uses IRC R303.1, glazing ≥ 8% of floor area |
| `edit_layout` | One call applies a fix and re-checks, instead of rewriting the whole JSON and calling `validate_layout` again. Stateless by design (2026-07-28 moves cross-call state into explicit arguments), so the layout goes in and the new layout comes out |
| `compare_layouts` | Briefs often have two good answers. The ranking is errors, then warnings, then free floor, then storage, and it says it is not a verdict on taste |
| Resources + template | References become `@`-attachable in Claude Code and readable by any client, with path completion |
| Prompts | `design_room` packs the procedure plus the right room module, regional module and safety rules; `review_layout` runs check → metrics → look → fix |
| Plugin config in `plugin.json` | The root `.mcp.json` was also loaded as a project server inside a clone, where `${CLAUDE_PLUGIN_ROOT}` is unset, so a broken second copy appeared next to the working one |

A finding from the new metrics: the studio example's glazing is 6.6% of its floor area, under the IRC's 8%. The window is fine for egress, but a bigger window or a glazed door would be needed to meet the daylight rule.
