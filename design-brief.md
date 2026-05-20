# Natal Chart Synthesis — HTML Page Design Brief

## What This Is

A single-page web app where a user enters birth data and receives a fully personalized
multi-system natal chart synthesis, streamed in real time from the Claude API.

The page does two things: collects input, and displays a long-form synthesis reading.
Both need to work beautifully on mobile. There is no backend — all calculation happens
client-side in JavaScript, and the synthesis is generated via a direct Claude API call
from the browser.

---

## Aesthetic Direction

**Dark, refined, unhurried.** Think old leather, ink, candlelight, gold leaf on black.
Not mystical-kitschy (no stars-and-moons clip art, no purple gradients). Not sterile-tech
(no white cards, no Material UI). The closest reference: a beautifully typeset private
document — something that feels like it was made specifically for one person.

**Design tokens:**

| Token | Value |
|-------|-------|
| Background | `#0d0d0d` (near-black) |
| Surface (cards, input fields) | `#141414` |
| Text primary | `#e8e0d0` (warm off-white) |
| Text secondary | `#a09880` (muted warm gray) |
| Accent / gold | `#c9a96e` (muted gold) |
| Accent hover | `#dbbf85` (slightly brighter gold) |
| Divider | 1px `#c9a96e` at 30% opacity |
| Error | `#c97a6e` |

**Typography:**

- Headings: Georgia, serif — warm, classic, not trendy
- Body: system-ui or Inter, sans-serif — readable at length on mobile
- Section labels / metadata: small caps or spaced uppercase, muted gold
- No web font dependencies — keep it self-contained

**Spacing:** Generous. This is a long reading. Give it room to breathe. Sections should
feel like turning pages, not scrolling through a feed.

---

## Page Structure

```
┌─────────────────────────────┐
│         HEADER              │  Logo/title — minimal, centered
├─────────────────────────────┤
│         INPUT FORM          │  Collapsible after submission
├─────────────────────────────┤
│      [ Generate Button ]    │
├─────────────────────────────┤
│         BLUEPRINT           │  Always visible, full-width
│   (streams in on generate)  │
├─────────────────────────────┤
│      DEEP DIVE              │  13 collapsible sections
│   ▶ Section 1               │  All collapsed by default
│   ▶ Section 2               │  Smooth expand/collapse
│   ...                       │
│   ▶ Section 13              │
├─────────────────────────────┤
│      CHART GLOSSARY         │  7 collapsible system sections
│   ▶ Western Astrology       │  All collapsed by default
│   ▶ Human Design            │
│   ...                       │
├─────────────────────────────┤
│    [ Copy Full Reading ]    │  Copies complete text to clipboard
└─────────────────────────────┘
```

---

## Input Form

All fields visible on load. Form collapses (or fades to a compact summary bar) after
the user hits Generate, so the reading takes over the screen.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| Full legal birth name | Text | For numerology; labeled "name at birth" |
| Birth date | Date picker | |
| Birth time | Time input | Include "Time unknown" toggle — disables ASC/MC/houses when checked |
| Birth city | Text with autocomplete | Geocoded via Nominatim (OpenStreetMap, no API key needed) |
| Human Design API key | Password input | Optional; link: humandesignhub.app/en/developer; "What's this?" tooltip |
| Enneagram type | Dropdown | Format: "Type 1", "Type 2" ... "Type 9"; second dropdown for wing (optional); third for instinct SP/SX/SO (optional) |
| Current year | Number | Defaults to current year; used for numerology Personal Year |
| Anthropic API key | Password input | Required for synthesis generation; stored in sessionStorage only |

**Form UX notes:**
- API key fields should have a show/hide toggle
- "Time unknown" toggle should visually disable the time field
- City field should show a subtle loading state while geocoding
- Form validation inline, not on submit — gold underline for active field, red for error
- On mobile, fields stack single-column; labels above fields (not floating)

---

## Generate Button

- Full-width on mobile, centered with generous padding on desktop
- Gold background (`#c9a96e`), dark text, no border radius (or very slight — 2px max)
- Label: **"Generate Reading"**
- Loading state: label changes to "Calculating..." during JS calculations, then
  "Writing your reading..." during API stream
- Disabled state while already generating

---

## Output: The Blueprint

- Appears immediately when streaming begins — don't wait for the full response
- Full-width, no accordion — this is the primary deliverable, always visible
- Blueprint heading in gold, small caps
- Four sub-sections rendered as they stream: **The Core Pattern**, **What You're Here to Do**,
  **The Central Challenge**, **Right Now**
- Sabian Symbol one-liner (in Core Pattern) in italics, slightly indented
- Integrated Alignment Statement at the end: set apart visually — centered, slightly larger
  text, a thin gold rule above and below
- A blinking cursor at the stream position while generating

---

## Output: The Deep Dive

13 sections, all collapsed by default when they arrive.

**Accordion behavior:**
- Section header: gold chevron (▶) + section title; full row is tappable
- Chevron rotates 90° on expand (smooth CSS transition, ~200ms)
- Content expands with a smooth height transition — not a jump
- Multiple sections can be open simultaneously
- Section titles (from the synthesis):
  1. The Mountain and the River
  2. The Tension That Runs Everything
  3. How You Actually Make Decisions
  4. The Interior Life You Don't Show Much
  5. What You're Actually Good At
  6. The Patterns Worth Naming
  7. Relationships
  8. Work and Purpose
  9. Where You Came From
  10. The Body and How to Regulate It
  11. The Chapter You're In
  12. How to Actually Live This
  13. The Seal on the Sun *(Sabian Symbol)*

**Section header design:**
- Thin gold rule above each section
- Section number in muted gold, small and right-aligned
- Title in warm off-white, Georgia serif

---

## Output: The Chart Glossary

Same accordion pattern as Deep Dive, but grouped by system (7 accordions):

1. Western Astrology
2. Human Design
3. Vedic / Jyotish
4. BaZi Four Pillars
5. Numerology
6. Gene Keys
7. Enneagram

Within each open system section, entries are formatted:

```
**Sun 4° Taurus, House 1** — One to two sentences of personalized meaning.

**Moon 4° Scorpio, House 7** — One to two sentences of personalized meaning.
```

Term in bold/gold, em-dash, then the sentence(s) in regular weight.

---

## Copy Button

- Appears below the Glossary once the full reading has streamed
- Label: **"Copy Full Reading"**
- On click: copies Blueprint + all Deep Dive sections + Glossary as plain text
- Confirmation: button label briefly changes to "Copied ✓" for 2 seconds
- Same styling as Generate button but secondary — outlined gold, not filled

---

## Streaming Behavior

- Start rendering Blueprint text as soon as the first token arrives
- Parse section breaks in the stream to know when to create a new accordion item
- Deep Dive sections appear as collapsed headers as their content streams in
- Glossary sections appear the same way
- A subtle "writing..." indicator (animated ellipsis or blinking cursor) at the active
  stream position
- On completion: "writing..." disappears, Copy button appears

---

## Mobile-First Requirements

- Designed for 390px viewport width first (iPhone 14 base)
- Touch targets minimum 44px height
- Accordion headers especially need generous tap area
- Form fields full-width on mobile
- Blueprint text: 16px minimum (no smaller — this is a long read)
- Deep Dive section content: comfortable line length (max ~70 characters on larger screens)
- No horizontal scroll at any breakpoint

---

## What This Is NOT

- Not a dashboard — no charts, graphs, or data visualizations
- Not a SaaS product — no accounts, no saved readings, no pricing
- Not generic — the output is deeply personal; the design should feel the same way
- Not responsive-as-afterthought — mobile is the primary target

---

## Sample Content

For the static mockup, use the Jamie Mettenbrink reading as placeholder content.
Blueprint and all 13 Deep Dive sections + Glossary are in `references/synthesis-voice-sample.md`
and the v2.1 additions (Section 13 + Glossary) are in `references/synthesis-guide-addendum-v2.1.md`.

Use realistic content lengths — the Blueprint is ~600 words, each Deep Dive section
is ~300-400 words, the Glossary entries are 1-2 sentences each. The design needs to
handle this comfortably, not just look good with two lines of Lorem Ipsum.

---

## Technical Constraints

- Single self-contained HTML file (HTML + CSS + JS, no build step)
- No external CSS frameworks (no Bootstrap, no Tailwind CDN)
- No external JS libraries except: optionally a lightweight markdown renderer
- Nominatim for geocoding (free, no key)
- timeapi.io for timezone lookup
- Human Design Hub API for HD data (user provides key)
- Anthropic Messages API for synthesis (user provides key, streamed via fetch)
- All API keys stay in sessionStorage only — never logged, never sent anywhere except
  their respective APIs

---

## Deliverable for the Design Step

A single static HTML file with:
- Full visual design implemented in CSS
- All input form fields present and styled (non-functional)
- Sample Blueprint content visible (hardcoded)
- All 13 Deep Dive accordions present with hardcoded section titles and sample content
- All 7 Glossary accordions present with hardcoded sample entries
- Working accordion expand/collapse behavior (JS)
- Copy button present (non-functional in mockup)
- Mobile-responsive layout

No calculation logic, no API calls. Design only.
