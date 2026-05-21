# Natal Chart Synthesis — HTML Page Specification

## What This Is

A single-page web app where a user enters birth data and receives a fully personalized
multi-system natal chart synthesis, streamed in real time from the Claude API.

The page does two things: collects input, and displays a long-form synthesis reading.
Both need to work beautifully on mobile. There is no backend — all calculation happens
client-side in JavaScript, and the synthesis is generated via a direct Claude API call
from the browser.

---

## Page Structure

**Before first generation:**
```
┌─────────────────────────────┐
│         HEADER              │  Logo/title — minimal, centered
├─────────────────────────────┤
│         INPUT FORM          │  All fields visible
├─────────────────────────────┤
│      [ Generate Button ]    │
└─────────────────────────────┘
```

**After generation (reading state):**
```
┌─────────────────────────────┐
│  HEADER + PROFILE SUMMARY   │  Name · date · city · Enneagram (if set) · ✏ Edit
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
│  YOUR CHART AT A GLANCE    │  6–7 collapsible system sections
│   ▶ Western Astrology       │  All collapsed by default
│   ▶ Human Design            │
│   ...                       │
├─────────────────────────────┤
│    [ Copy Full Reading ]    │  Copies complete text to clipboard
└─────────────────────────────┘
```

---

## Input Form

All fields visible on load. After the user hits Generate, the form collapses into the
header as a compact profile summary, so the reading takes over the screen.

**Collapsed state (header):**
- Displays: name · birth date · birth city · Enneagram type (if provided)
- A small edit affordance (pencil icon or "Edit" link) sits at the right edge
- Tapping anywhere on the summary re-expands the full form above the reading
- The Generate button reappears when the form is expanded; hidden otherwise
- Transition: form slides up and fades into the header; smooth, not abrupt

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| Full legal birth name | Text | For numerology; labeled "name at birth" |
| Birth date | Date picker | |
| Birth time | Time input | Include "Time unknown" toggle — disables ASC/MC/houses and omits Human Design from output when checked |
| Birth city | Text with autocomplete | Geocoded via Nominatim (OpenStreetMap, no API key needed) |
| Enneagram type | Dropdown | Optional. Format: "Type 1" ... "Type 9"; second dropdown for wing (optional); third for instinct SP/SX/SO (optional). If left blank, Enneagram section is omitted from output entirely. |

**Form UX notes:**
- "Time unknown" toggle should visually disable the time field; tooltip reads: "No birth time? No problem — you'll lose the Ascendant, houses, and Human Design, but the rest holds."
- City field should show a subtle loading state while geocoding
- Enneagram field tooltip: "Self-identified only. If you're not sure, skip it — a wrong type does more damage than a missing one."
- Form validation inline, not on submit — highlight active field, red for error
- On mobile, fields stack single-column; labels above fields (not floating)

---

## Generate Button

- Full-width on mobile, centered with generous padding on desktop
- Label: **"Generate Reading"**
- Loading state (calculation phase): "Running your chart across six systems. This takes a moment. The planets were doing their thing long before instant gratification existed."
- Loading state (API stream phase): "Writing your reading. This is the long part. Worth it."
- On completion: "Done."
- Disabled state while already generating
- Hidden after first generation; reappears only when the form is re-expanded via Edit

**Regeneration behavior (when user edits and re-submits):**
- Existing reading fades to 50% opacity
- A centered "Regenerating..." graphic overlays the faded content
- New content streams in, replacing the old reading in place
- Reading returns to full opacity on completion

---

## Output: Audience Detection

Birth date is used to detect if the chart subject is a minor. This changes the synthesis output — no UI flag is needed; detection is automatic from the birth date.

| Age at generation | Output mode |
|---|---|
| Under 13 | Third person, addressed to the parent/guardian ("Leo has a Moon in…") |
| 13–17 | Second person with a brief framing note at the top of the reading |
| 18+ | Standard second person, no age-specific modification |

---

## Output: The Blueprint

- Appears immediately when streaming begins — don't wait for the full response
- Full-width, no accordion — this is the primary deliverable, always visible
- Four sub-sections rendered as they stream: **The Core Pattern**, **What You're Here to Do**,
  **The Central Challenge**, **Right Now**
- Sabian Symbol one-liner (in Core Pattern) slightly indented; optional second line for Ascendant degree if birth time is known
- Integrated Alignment Statement at the end: set apart visually — centered, slightly larger text
- A blinking cursor at the stream position while generating

---

## Output: The Deep Dive

13 sections, all collapsed by default when they arrive.

**Accordion behavior:**
- Section header: chevron (▶) + section title; full row is tappable
- Chevron rotates 90° on expand
- Content expands with a smooth height transition — not a jump
- Multiple sections can be open simultaneously
- Each section header optionally shows a one-line intro beneath the title (see `references/voice-guide.md` — "Section Intros" for the approved copy per section)
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

---

## Output: Your Chart at a Glance

Section header copy: "Everything above is the synthesis. This is the map behind it — every placement, every system, what each one means for you. Come back here when you want to know where a specific insight came from."

Same accordion pattern as Deep Dive, but grouped by system (6–7 accordions):

1. Western Astrology
2. Human Design
3. Vedic / Jyotish
4. BaZi Four Pillars
5. Numerology
6. Gene Keys
7. Enneagram *(only rendered if Enneagram type was entered)*

Within each open system section, entries are formatted:

```
**Sun 4° Taurus, House 1** — One to two sentences of personalized meaning.

**Moon 4° Scorpio, House 7** — One to two sentences of personalized meaning.
```

Term in bold, em-dash, then the sentence(s) in regular weight.

---

## Copy Button

- Appears below the Glossary once the full reading has streamed
- Label: **"Copy full reading"**
- On click: copies Blueprint + all Deep Dive sections + Glossary as plain text
- Confirmation: button label briefly changes to "Copied" for 2 seconds, then reverts

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

## Error States

All error messages inline, no modal. Copy from `references/voice-guide.md`.

| Trigger | Message |
|---|---|
| Geocoding fails | "Couldn't find that city. Try adding the country, or use coordinates." |
| Human Design API error | "Human Design API returned an error. Check your key, or enter your HD data manually below." |
| Claude API error | "The synthesis didn't complete. This is usually an API key issue or a timeout on a long response. Try again." |
| Time field empty on submit | "Birth time is empty. If you don't know it, use the toggle above — don't guess." |

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
- Not generic — the output is deeply personal
- Not responsive-as-afterthought — mobile is the primary target

---

## Sample Content

For reference, use the Jamie Mettenbrink reading as placeholder content.
Blueprint and all 13 Deep Dive sections + Glossary are in `references/synthesis-voice-sample.md`
and the v2.1 additions (Section 13 + Glossary) are in `references/synthesis-guide-addendum-v2.1.md`.

Use realistic content lengths — the Blueprint is ~500–700 words, each Deep Dive section
is ~300-400 words, the Glossary entries are 1-2 sentences each. The app needs to
handle this comfortably, not just minimal placeholder content.

---

## Technical Constraints

- Single self-contained HTML file (HTML + CSS + JS, no build step)
- No external CSS frameworks (no Bootstrap, no Tailwind CDN)
- No external JS libraries except: optionally a lightweight markdown renderer
- All calculation logic implemented in JavaScript. The Python scripts in `/scripts/` (calculate_chart.py, calculate_bazi.py, calculate_vedic.py, calculate_numerology.py, sabian_lookup.py) are the canonical reference implementation to port from — they define the expected inputs, outputs, and calculation logic for each system
- Nominatim for geocoding (free, no key)
- timeapi.io for timezone lookup
- Human Design Hub API for HD data (key pre-configured in source — not entered by user)
- Anthropic Messages API for synthesis (key pre-configured in source, streamed via fetch)
- Current year auto-detected from the browser — not entered by user
- App is private/personal use; keys are hardcoded for simplicity

