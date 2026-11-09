# Interior Design Skill / MCP — Research Notes

Collected 2026-11-03. Sources are listed inline.

## 1. Source channel: Dreamy Interior (@DreamyInterior)

- 508k subscribers, 105 videos. 100 listed in [`dreamy_interior_videos.md`](dreamy_interior_videos.md).
- **98 are Shorts (60–105 s); 2 are long-form (~4 min).**
- **Shorts have spoken narration** (auto-captions, English). Example, "Stunning Bedroom Renovation For Two Kids In One Room" (k9P027Hktzg):
  > Problem: twins outgrow a standard bunk bed; a big wardrobe blocks door opening; two side-by-side desks waste space.
  > Solution: frame built from galvanized square steel, clad in eco-friendly wood panels + gypsum board to create separate zones. Upper bunk gets a sliding window for natural light and small curtains for privacy. L-shaped wardrobe built beneath the second bed; coat hooks on the side...
- Every Short follows the same **problem → constraint → build → zone-by-zone reveal** script. That pattern is exactly the reasoning a skill should encode.
- **Long-form videos have no narration** (only [music], [laughter]), so their content is visual only.
- Topic mix: ~80% small/kids/shared bedrooms (bunk, loft, split-level, hidden bed, walk-in closet), plus bathrooms, balconies, shoe cabinets, window seats, tiny homes.

### Transcripts: done
Each video was opened in the browser and the captions its player loaded were read. **96 of 100 have narration**, and per-video notes are in [`video_notes.md`](video_notes.md). The rules distilled from them are in [`design_rules.md`](design_rules.md). Four videos have no narration (the 2 long-form plus 2 Shorts) and need key-frame screenshots.

### Copyright
The videos belong to the channel owner. It's fine to **watch them and write your own general design rules** (dimensions, layout patterns, problem→solution pairs). Don't copy transcripts or frames into a product, and don't fine-tune a model on them, without the owner's permission.

## 2. Existing skills & MCPs

### Claude Skills (all written, none "trained")
A skill is a `SKILL.md` plus reference files (rule tables, templates, scripts) that Claude reads when it's relevant. Nothing is trained; the quality comes entirely from how good the written rules are.

| Skill | What it covers | Source |
|---|---|---|
| interior-design-expert (erichowens / curiositech) | Space planning, anthropometrics, IES lighting, Munsell/NCS color, styles. ~261★ | [skills.sh](https://skills.sh/erichowens/some_claude_skills/interior-design-expert), [claudemarketplaces](https://claudemarketplaces.com/skills/erichowens/some_claude_skills/interior-design-expert) |
| interior-design | Space planning, materials, documentation | [claudskills.com](https://claudskills.com/skills/interior-design/) |
| interior-design-visualizer (SamurAIGPT) | Generate/furnish/redesign room images | [claudskills.com](https://claudskills.com/skills/interior-design-visualizer/) |
| interior-design-ideator | Ideas, palettes, layout, budget | [claudskills.com](https://claudskills.com/skills/interior-design-ideator/) |

**Gap:** none of these cover small-space / bunk / loft / split-level bedrooms, which is this channel's niche and your differentiator.

### MCP servers (tools that do real work)
| Server | What it does | Notes |
|---|---|---|
| [blender-orchestrator](https://github.com/mlolson/blender-orchestrator) | `create_room_bounds`, a database of real-world dimensions and clearances for 55+ objects, collision-free placement, ASCII floor plans, Cycles/EEVEE renders, Poly Haven CC0 assets, text/image→3D via Meshy | MIT. **Best base for the 3D/render stage.** |
| [blender-mcp (ahujasid)](https://playbooks.com/mcp/ahujasid-blender) | General Claude↔Blender bridge | The most popular option; generic, not interior-specific |
| [Sweet Home 3D MCP](https://mcpservers.org/fr/servers/grimashevich/sweethome3d-mcp-server) | 42 tools: walls, furniture, textures, 2D plan PNG/SVG, ray-traced renders | Interior-specific; easiest floor-plan tool |
| [architecture-mcp](https://www.pkgstats.com/pkg:architecture-mcp) | `create_floor_plan` with compliance warnings (minimum areas, corridor widths), mood boards, budgets | npm |
| [Planner 5D WebMCP](https://ai.planner5d.com/webmcp) | Hosted floor plan → 2D/3D | Commercial |
| Survey | [DEV.to: interior & architecture MCP servers](https://dev.to/grove_chatforest/interior-design-architecture-mcp-servers-blender-autocad-rhino-freecad-revit-and-more-4cp) | |

### Actually trained models (research)
These are the only "trained" options: LLMs fine-tuned on 3D room datasets such as 3D-FRONT.
- **OptiScene** ([arXiv 2506.07570](https://arxiv.org/pdf/2506.07570v2)): open LLM fine-tuned for indoor layout; dataset 3D-SynthPlace.
- **LLplace** ([arXiv 2406.03866](https://arxiv.org/html/2406.03866v1)): Llama 3 + LoRA; room type + object list → layout.
- **HLG** ([arXiv 2508.17832](https://arxiv.org/pdf/2508.17832)), Holodeck, LayoutGPT, InstructScene; dataset **M3DLayout** ([arXiv 2509.23728](https://arxiv.org/html/2509.23728v2)).
- Overview: [SFU text-to-scene lecture 2026](https://angelxuanchang.github.io/nlp-class/assets/lecture-slides/2026-03-30_CMPT-413_03_text-to-scene.pdf).

Recommendation: **don't train a model at first.** Claude + a good skill + Blender MCP gets you most of the way. Fine-tune only if you later collect hundreds of your own validated layouts.

### Video → 3D (your "if a video is provided" input)
Pipeline: frames → COLMAP structure-from-motion → Gaussian splatting (.ply) → measure the room and extract walls → rebuild in Blender → furnish → render.
- [nerfstudio](https://www.markaicode.com/3d-gaussian-splatting-video-to-3d-environments/) (`ns-process-data video`), [vid2scene](https://replicate.com/kfarr/vid2scene) (Apache 2.0), [gaussian-reconstruction](https://pypi.org/project/gaussian-reconstruction).
- Caveats: blank white walls, mirrors, and moving people reconstruct badly ([2026 write-up](https://the-homepage.pages.dev/posts/2026-02-15-3dgs-room-modeling-mobile-camera-2026)).

## 3. People already doing this (YouTube)
| Video | Why it's useful |
|---|---|
| [I Built a 3D Walkthrough From a Floor Plan in One Night (Claude + Blender)](https://www.youtube.com/watch?v=l4OtqWGKFos) | Closest to your end goal: floor plan → walkthrough video |
| [Design a Room using Blender-MCP and Claude AI demo](https://www.youtube.com/watch?v=wxgQmjm9wfM) | Room build via MCP, step by step |
| [Claude Opus 5.5 Recreates a Midjourney Interior in Blender](https://www.youtube.com/watch?v=bILKJ8u5ERE) | Image → 3D interior (your "image input") |
| [I connected Claude AI to Blender 3D (MCP)](https://www.youtube.com/watch?v=r7H60u0kHRA) | Setup + limits of blender-mcp (380k views) |
| [Can an AI Agent Model a Whole House in Blender? 3D-Agent](https://www.youtube.com/watch?v=E9hC-EG7oMU) | One-prompt whole house |
| [Staging my entire house with AI — Claude Code + Nano Banana skill](https://www.youtube.com/watch?v=UES10EP6GuA) | A Claude Code skill for photo → staged images |
| [How to Build AI Interior Design Agent (Step by Step)](https://www.youtube.com/watch?v=k2aRIGoV_i8) | Agent architecture tutorial |
| [img2interior v2.2 — Open-Source Image to 3D Interior](https://www.youtube.com/watch?v=m4dDK7nOp9Y) | Open-source image→3D (Three.js) |
| [2D Floor Plan to 3D Render, Photorealistic Walkthrough (BuildFlow)](https://www.youtube.com/watch?v=iHxicHnGw_Y) | Commercial benchmark for output quality |
| [MCP vs Skills (IBM)](https://www.youtube.com/watch?v=goU9VIXA8II) | When to use which |

## 4. Proposed architecture

```
Inputs: text | voice (speech-to-text) | room photos | walkthrough video | floor plan
            │
   ┌────────▼─────────┐
   │ 1. SKILL          │  residential-space-designer/
   │  (knowledge)      │   SKILL.md          — intake questions, design procedure
   │                   │   references/        — dimensions, clearances, bunk/loft/split-level
   │                   │                       patterns, problem→solution catalog (from the Shorts),
   │                   │                       materials, safety (guardrails, ladder angle, headroom)
   │                   │   templates/         — design brief, layout JSON schema, BOM
   └────────┬─────────┘
            │ structured layout JSON
   ┌────────▼─────────┐
   │ 2. MCP (tools)    │  validate_layout (clearance/collision/headroom), floor_plan_svg,
   │                   │  bom_and_cost, + bridge to Blender (blender-orchestrator)
   └────────┬─────────┘
   ┌────────▼─────────┐
   │ 3. Render         │  Blender: build room → furnish → materials/HDRI → camera path
   │                   │  → Cycles stills + animated walkthrough MP4
   └──────────────────┘
   Video input path: frames → COLMAP → Gaussian splat → room dimensions → stage 3
```

### Build order
1. **Skill v1:** write the rules and the problem→solution catalog from the Shorts, plus a layout JSON schema.
2. **Test** the skill on 5–10 scenarios (single bed, twins bunk, 3 kids, couple in 8 m², split-level).
3. **MCP v1:** `validate_layout` + `floor_plan_svg` (pure Python, no Blender yet).
4. **Blender stage:** install blender-orchestrator and map layout JSON → scene → render a camera-path video.
5. **Inputs:** add photo→dimensions, voice (Whisper), then video→3D reconstruction.

## 5. Whole-home tours (added 2026-11-09)
To widen the skill from small rooms to whole houses, 14 full home tours were read: 8 Indian (Buildofy, Zenden, Homely by LBB and a budget-build channel) and 6 Western (Never Too Small, The Local Project, Living Big in a Tiny House). Paraphrased notes and cross-cutting patterns are in [`home_tours.md`](home_tours.md). They feed `references/regional/india.md`, `references/regional/western.md`, `references/rooms/exterior.md` and the patterns section of `references/rooms/whole-home.md`.
