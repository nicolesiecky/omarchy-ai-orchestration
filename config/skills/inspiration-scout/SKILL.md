---
name: inspiration-scout
description: "Mandatory first step before creating or redesigning any frontend UI, landing page, portfolio, dashboard, or web app. Researches and gathers design inspirations from 21st.dev, dribbble.com, godly.design, awwwards.com, and land-book.com, and combines them with TasteSkill 2.5 dealt tokens and UI/UX Pro Max design system intelligence."
---

# Inspiration Scout — Frontend Inspiration Research Protocol

This skill MUST be executed (or delegated via `define_subagent` / `invoke_subagent` as `inspiration-scout`) **every time** before creating or redesigning any frontend interface.

## 1. Automated Seed Generation (`inspiration-scout` CLI)

Run the local seed generator first to deal non-cliché palettes, typography pairings, hero layout specs (from TasteSkill 2.5), and design system intelligence (from UI/UX Pro Max):

```bash
~/.local/bin/inspiration-scout "<topic and style keywords>" <site-kind> <page-type>
```
*(where `site-kind` is `software`, `gaming`, `tech`, `product`, `service`, or `place`, and `page-type` is `software`, `product`, `service`, or `place`)*.

## 2. Mandatory 5-Source Inspiration Research (`search_web`)

Gather concrete visual, layout, and component inspirations from the 5 reference platforms using `search_web`:

1. **21st.dev (`domain: "21st.dev"`)**:
   - Query: `"<topic/component> react tailwind shadcn component hero"`
   - Extract: Modern interactive UI primitives, button micro-interactions, bento cards, shader backgrounds, and clean component architecture.
2. **Godly.design (`domain: "godly.design"`)**:
   - Query: `"<industry/style> website layout typography interactive"`
   - Extract: Pacing, viewport rhythm, negative space, and editorial grid structure.
3. **Awwwards (`domain: "awwwards.com"`)**:
   - Query: `"<industry/style> site of the day art direction motion"`
   - Extract: Signature creative moments, typography hierarchy, and visual storytelling.
4. **Land-book (`domain: "land-book.com"`)**:
   - Query: `"<industry/product> landing page sections hero"`
   - Extract: Section progression, value proposition framing, and CTA placement.
5. **Dribbble (`domain: "dribbble.com"`)**:
   - Query: `"<topic/ui> interface card dashboard layout"`
   - Extract: Component density, subtle border/surface treatments, and visual polish.

## 3. Output: The Inspiration Dossier

Compile a concise **Inspiration Dossier** for the Design Architect containing:
- **Curated References (5–10 items)**: Source URLs + specific structural/visual takeaways to adapt (never copy verbatim).
- **Dealt TasteSkill 2.5 Spec**: Chosen palette (never violet/lavender), Google Font pairing (never generic Inter/Roboto), and Hero layout geometry.
- **UI/UX Pro Max Baseline**: Recommended pattern, style, `--variance`/`--motion`/`--density` dials, and critical UX rules.
