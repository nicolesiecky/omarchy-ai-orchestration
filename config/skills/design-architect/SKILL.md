---
name: design-architect
description: "Unified Frontend Design Architect skill. Orchestrates Inspiration Scout (21st.dev, Dribbble, Godly, Awwwards, Land-book), Impeccable (modes, craft-floor, detector), TasteSkill 2.5 (figma.com/x.ai bar, 9 house rules, dealt tokens, browser checks), UI/UX Pro Max (80 styles, 192 palettes, 119 UX guidelines, 22 stacks), Figma MCP, and Higgsfield MCP into one seamless frontend creation pipeline."
---

# Design Architect — Unified Frontend & UI/UX Pipeline

Use this skill whenever designing, building, or refactoring any frontend UI. It fuses **Inspiration Scout**, **Impeccable (v4.8.0)**, **TasteSkill (v2.5.0)**, **UI/UX Pro Max (v2.15.0)**, **Figma MCP**, and **Higgsfield MCP** so they reinforce each other without conflict.

---

## Phase 1: Inspiration & Seed Harvesting (`inspiration-scout`)

Before designing or writing code, spawn the `inspiration-scout` subagent (or run the `inspiration-scout` protocol):
1. Run `~/.local/bin/inspiration-scout "<query>" <site-kind> <page-type>`.
2. Query `21st.dev`, `godly.design`, `awwwards.com`, `land-book.com`, and `dribbble.com` via `search_web`.
3. Produce the **Inspiration Dossier**.

---

## Phase 2: How Impeccable + TasteSkill + UI/UX Pro Max Work Together

Each skill owns a distinct layer of the design stack:

### Layer A — Strategic Mode & Anti-Slop Floor (**Impeccable**)
- Run `impeccable context` and read `~/.gemini/skills/impeccable/reference/craft-floor.md`.
- Select the **Surface Mode**:
  - `Persuade` (Landing pages, marketing, SaaS homepages)
  - `Operate` (Dashboards, trading desks, admin panels, tools)
  - `Read` (Docs, blogs, editorial)
  - `Experience` (Portfolios, showcases, creative galleries)
- Persist durable product/design decisions in `PRODUCT.md` and `DESIGN.md`.

### Layer B — Art Direction, Layout Geometry & House Rules (**TasteSkill 2.5**)
- Read `~/.gemini/skills/design-taste-frontend/SKILL.md` (`figma.com` and `x.ai` are the quality bar).
- **Deal Tokens, Never Guess by Habit**:
  - Use `taste-skill start deal --page <kind>` and `taste-skill start css --page <kind> --palette <id> --type <id> --radius <sharp|soft|round>`.
  - Use `taste-skill deal-hero --type <page-type> --has <photo,ui,object,film>` for hero geometry.
- **Enforce the 9 House Rules**:
  1. **No captions/apologies under visuals**; credits go in one footer line.
  2. **Every visual renders** at `1440, 1024, 768, 390` — never an empty ground.
  3. **One section per screen**: Hero alone on screen 1; every section 1 or 2 screens tall at `1440×900`, no neighbor heading peeking in.
  4. **Equal left and right content edges** (`.wrap` alignment).
  5. **Tactile hover micro-animations**: linked card lifts `2px`, photo zooms `1.02–1.03` inside frame, buttons step on hover and press on click, underlines draw. **Never** use 3D card tilt, timed carousels, or scroll-jacking card reveals.
  6. **Authentic visuals**: real photographs, live HTML product UI inside `app-frame` (never fake empty dashboard boxes), real full-color brand icons (`taste-skill icons`), pulsing SVG diagrams. Shader/WebGL effects ONLY on `software`, `gaming`, or `tech` pages.
  7. **Plain, high-signal copy**: noun in every heading, verb+object in buttons, 60–80 words per screen outside UI mocks.
  8. **Zero AI Violet**: Never use violet or lavender in the page's own palette.

### Layer C — Empirical UX Rules, Dials & Stack Ergonomics (**UI/UX Pro Max**)
- Query domain & stack specifics via `uipro-search`:
  - `uipro-search "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10> --persist -p "<Project>" --output-dir "<root>"`
  - `uipro-search "<concern>" --domain <ux|style|color|typography|landing|chart|gsap|icons>`
  - `uipro-search "<pattern>" --stack <react|nextjs|astro|vue|svelte|html-tailwind|shadcn|threejs>`
- Enforce Priority 1–10 UX checks: WCAG 4.5:1 contrast, 44×44px touch targets, CLS < 0.1, visible `:focus-visible` rings, `prefers-reduced-motion` support.

### Layer D — External Design & Media MCPs (**Figma** + **Higgsfield**)
- **Figma MCP (`Figma`)**: If the user provides a Figma link or file, extract exact design tokens, components, and layout trees via `get_design_context` and `get_screenshot`.
- **Higgsfield MCP (`Higgsfield`)**: Use `Higgsfield` MCP tools when generating custom AI video loops, hero motion backgrounds, or visual renders.

---

## Phase 3: Mandatory Dual Verification Gate

Before reporting completion on any frontend task, run BOTH deterministic checks:

1. **Impeccable Anti-Slop & Quality Detector**:
   ```bash
   impeccable detect --json <changed-files-or-url>
   ```
   *(Must achieve 0 primary findings: no `side-tab`, `border-accent-on-rounded`, `overused-font`, `flat-type-hierarchy`, `gradient-text`, or `ai-color-palette`.)*

2. **TasteSkill Real-Browser & Viewport Verification**:
   ```bash
   taste-skill consistency <entry.html-or-url> --widths 1440,1024,820,768,390 --rhythm-widths 1440,820,768,390 --page <kind>
   taste-skill check --url <entry.html-or-url> --sizes 1440x900,1024x768,820x1180,768x1024,390x844
   ```
   *(Fix any overflow, broken edge alignment, or rhythm failure before finishing.)*
