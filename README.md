# Small-Space Bedroom Designer

A Claude skill for designing small and shared bedrooms: kids' and twin rooms, loft, bunk, half-height and split-level beds, and micro-units under 10 m².

It turns a room description (text, a voice transcript, photos or a floor plan) into:
- a design brief and zone plan,
- a layout JSON (`templates/layout.schema.json`) that a checker can validate and a Blender stage can render,
- an ASCII floor plan, a bill of materials, safety notes,
- a zone-by-zone reveal script that doubles as the camera path for a walkthrough video.

## Layout

| Path | What it is |
|---|---|
| `small-space-bedroom-designer/SKILL.md` | The skill: procedure and deliverables |
| `small-space-bedroom-designer/references/` | Rules with source tags: sleep strategies, zoning, storage, safety (CPSC, EN 747, IRC), dimensions, materials, patterns, sources |
| `small-space-bedroom-designer/templates/` | Layout JSON schema, intake questions and brief, BOM |
| `small-space-bedroom-designer/scripts/check_layout.py` | Layout checker, standard-library Python |
| `small-space-bedroom-designer/examples/` | Worked example (twins, offset loft) |
| `small-space-bedroom-designer/evals/` | 10 test scenarios, generated layouts and results |
| `interior-design-research/` | Research notes: existing skills/MCPs/models, per-video notes, draft rules |

## Using it

Install as a Claude Code skill by copying the folder into your skills directory:

```bash
cp -r small-space-bedroom-designer ~/.claude/skills/
```

Check a layout:

```bash
python3 small-space-bedroom-designer/scripts/check_layout.py small-space-bedroom-designer/examples/twins-offset-loft.json --plan
```

## Status

v1. Safety values come from the cited standards. Values tagged `[std]` are common practice and must be confirmed. Always check local building codes and have structure and electrics signed off by a professional.

The design patterns were studied from public renovation videos and are written in our own words. `interior-design-research/video_notes.md` paraphrases that channel's content, so keep this repository private unless you have the channel owner's permission to publish those notes.

## Roadmap

1. Blind test of the skill on the 10 scenarios.
2. MCP v1: `validate_layout` and `floor_plan_svg` tools.
3. Blender stage via blender-orchestrator: layout JSON to scene to walkthrough video.
4. Inputs: photo to dimensions, voice (Whisper), video to 3D reconstruction.
