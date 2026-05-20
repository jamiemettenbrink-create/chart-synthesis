# Session Handoff — Natal Chart Synthesis Skill
## Where We Left Off · May 2026 (v2.1)

---

## Project Summary

A multi-system natal chart synthesis engine built as a skill for the Claude AI assistant.
Takes birth data and produces a deeply personalized reading across 8 symbolic systems,
synthesized into a two-layer output (Blueprint + Deep Dive) plus a Chart Glossary.

---

## What Was Added This Session (v2.1)

Building on the v2 skill (7 systems + master runner), this session added:

### 1. Sabian Symbols — 8th System
Sabian Symbols are 360 archetypal images (one per degree of the zodiac), channeled in 1925
by Elsie Wheeler and Marc Edmund Jones. Used in synthesis to add poetic/archetypal depth
to the Sun's exact degree placement.

**New files produced this session (in `/skill-update-v2.1/`):**

- `references/sabian-symbols.md` — Complete reference: all 360 symbols + keywords,
  organized by sign, with lookup convention (always round UP to next whole degree)

- `scripts/sabian_lookup.py` — Python module with:
  - `get_sabian(sign, degree, minute)` — returns symbol dict
  - `get_sabian_from_longitude(longitude)` — accepts raw ecliptic longitude (0–360°)
  - Integration instructions in file comments (how to wire into `run_full_chart.py`)
  - Test confirmed: Jamie's Sun 4°11' Taurus → Taurus 5° · "A widow at an open grave" · Reorientation ✓

- `references/synthesis-guide-addendum-v2.1.md` — Writing instructions for:
  - **Blueprint update**: one-line Sabian seal added to Core Pattern sub-section
  - **Deep Dive Section 13**: "The Seal on the Sun" (~300 words, archetypal interpretation
    tied back to chart themes) — includes good/bad examples
  - **Chart Glossary**: full structure for all 7 systems (see below)

- `SKILL.md` — Updated root skill file reflecting all changes

### 2. Chart Glossary — New Closing Section
A structured reference card at the end of every reading: every key term from the chart,
organized by system, with 2–3 sentences of *personalized* meaning per term.

**Structure:** Western Astrology → Human Design → Vedic/Jyotish → BaZi Four Pillars →
Numerology → Gene Keys → Enneagram

**Tone rule:** Each entry is written directly to the person ("Your Taurus Sun in House 1...")
not as a generic definition. 2–3 sentences firm limit per term. The synthesis above is
where depth lives; the glossary is the annotated map behind it.

Full template with field-by-field instructions is in `synthesis-guide-addendum-v2.1.md`.

---

## Complete File Checklist — What Goes Where

### New files from this session → add to skill directory:

**Into `/references/`:**
- [ ] `sabian-symbols.md` *(new)*
- [ ] `synthesis-guide-addendum-v2.1.md` *(new — extends synthesis-guide-v2.md)*

**Into `/scripts/`:**
- [ ] `sabian_lookup.py` *(new — integrate into run_full_chart.py per inline instructions)*

**Root:**
- [ ] `SKILL.md` *(replace existing — updated for 8 systems, 13 Deep Dive sections, glossary)*

### Files from prior session (v2) still needed — should already be in skill directory:
*(If migrating fresh, these need to come from prior session outputs or be rebuilt)*

**`/scripts/`:**
- [ ] `calculate_chart.py` — Western astrology (Meeus ephemeris)
- [ ] `calculate_bazi.py` — BaZi Four Pillars
- [ ] `calculate_vedic.py` — Vedic/Jyotish
- [ ] `calculate_numerology.py` — Pythagorean numerology
- [ ] `run_full_chart.py` — Master runner (needs sabian_lookup integration)

**`/references/`:**
- [ ] `synthesis-guide-v2.md` — 12-section synthesis guide (v2.1 addendum extends this)
- [ ] `synthesis-voice-sample.md` — Approved voice/tone benchmark (Jamie v2 reading)
- [ ] `hd-guide.md` — Human Design types, authorities, profiles, crosses
- [ ] `gene-keys-complete.md` — All 64 gates shadow/gift/siddhi
- [ ] `bazi-guide.md` — Day Masters, Ten Gods, clashes, element psychology
- [ ] `vedic-guide.md` — Lagna, Nakshatras, Dasha interpretation
- [ ] `enneagram-guide.md` — All 9 types, wings, instinctual variants
- [ ] `aspects.md` — Key Western aspect combinations
- [ ] `houses.md` — House meanings

---

## Next Build: The HTML Artifact

The main outstanding work is building a browser-based artifact that does everything
the Python scripts do, but fully client-side (no bash — network is restricted in the
skill runner), with a Claude API call to stream the synthesis.

### Artifact Requirements

**1. Input Form**
- Birth date (date picker)
- Birth time (time input; "unknown" toggle that disables ASC/MC/houses)
- Birth city — geocoded via Nominatim (OpenStreetMap, free, no key)
- Full legal birth name (for numerology)
- HD API key (user-provided; link to humandesignhub.app/en/developer)
- Enneagram type (dropdown: Type 1–9, wing, instinct variant)
- Current year (defaults to 2026)

**2. Calculation Layer (JavaScript)**
All of the following need to run client-side in the browser:
- Ephemeris math (Meeus algorithms) → Sun, Moon, planets, ASC, MC, houses
- **Sabian Symbol lookup** (port `sabian_lookup.py` to JS — straightforward array lookup)
- BaZi Four Pillars (stems, branches, Day Master, Ten Gods)
- Vedic sidereal positions (subtract ~23.85° ayanamsha from tropical), Nakshatras, Dasha
- Numerology (Life Path, Expression, Soul Urge, Personality, Birthday, Maturity, PY)
- Cross-system convergence detection
- HD Hub API call (browser fetch, not bash)
- Timezone lookup via timeapi.io

*Note: The ephemeris math was already ported to JS in an earlier widget prototype session —
retrieve from that conversation history if available.*

**3. Human Design API Call**
```
POST https://api.humandesignhub.app/v1/bodygraph
Header: X-API-KEY: {user's key}
Body: {"datetime": "YYYY-MM-DDTHH:MM:SS±HH:MM"}
```
Returns: type, strategy, authority, profile, definition, incarnation_cross,
centers, undefined_centers, channels_short, gates.
Cost: 1 credit (100/month free tier).

**4. Claude API Call**
```javascript
POST https://api.anthropic.com/v1/messages
Model: claude-sonnet-4-20250514
Max tokens: 8000 (synthesis is long)
Stream: true
```

Prompt structure:
```
System: You are writing an integrated natal chart synthesis.
        [full content of synthesis-guide-v2.md]
        [full content of synthesis-guide-addendum-v2.1.md]

        Voice reference — this is the approved tone:
        [first 500 words of synthesis-voice-sample.md]

User: Here is the full chart data for [Name]:
      [JSON output from all calculators]

      Write the full synthesis in three parts:
      Part 1 — The Blueprint (~600 words, 4 sections + alignment statement,
               include Sabian Symbol one-liner in Core Pattern)
      Part 2 — The Deep Dive (13 sections, ~300-400 words each,
               Section 13 = Sabian Symbol deep dive)
      Part 3 — Chart Glossary ("Your Chart at a Glance")
               All 7 systems, all key placements, 2-3 sentences each,
               written directly to the person
```

**5. Output Display**
- Blueprint: visible immediately, full-width, no toggle
- Deep Dive: 13 collapsible/expandable sections (accordion), all collapsed by default
- Glossary: collapsible by system (7 accordions), collapsed by default
- Streaming: render text as it arrives, don't wait for full response
- "Copy full reading" button

**6. Design Direction**
Dark, refined aesthetic. Parchment/ink/gold palette. Not generic. Not purple gradients.
Reference: the partial HTML artifact started in an earlier session — retrieve from
conversation history if available. Key design tokens used:
- Background: near-black (#0d0d0d or similar)
- Text: warm off-white (#e8e0d0 or similar)
- Accent: muted gold (#c9a96e or similar)
- Font: serif for headings (Georgia or similar), sans for body
- Section dividers: thin gold rules

---

## Test Chart (use this to verify everything end-to-end)

```
Name: Jamie Mettenbrink
Birth name: Jamie Rae Mettenbrink
Date: April 24, 1986
Time: 6:10 AM
Location: Scottsdale, AZ
Coordinates: lat=33.4942, lng=-111.9261
UTC offset: -7 (Arizona, no DST)
HD: Generator · Emotional Authority · 3/5 Profile
    Cross of the Unexpected · Channels: 27-50, 28-38, 41-30
Enneagram: 8w7 SP
```

Expected key outputs:
| System | Expected |
|--------|----------|
| Western | Taurus Sun/ASC (H1), Scorpio Moon/Pluto (H7), Capricorn MC, NN Aries 29°59' H12 |
| Sabian (Sun) | Taurus 5° · "A widow at an open grave" · Reorientation |
| Sabian (ASC) | Taurus 1° · "A clear mountain stream" · Endowment |
| BaZi | Yang Earth Day Master (Strong), Tiger-Monkey clash, missing Fire |
| Vedic | Aries Lagna, Swati Moon (Pada 2), Mercury dasha current |
| Numerology | LP 7 (KD16), Expression 4 (KD13), Soul Urge 4, Personality 9, Maturity 11✦, PY 2026 = 11✦ |
| Convergences | Triple Earth · Depth/Scorpio · Nodal match · Double 11 timing |

---

## Two Core Voice Rules (from v2 session — carry forward always)

1. **Less describing the system, more describing the implication.** Don't say "Gate 27 is
   the nurturance gate which in Human Design represents..." — say "you have an almost
   supernatural ability to sense what people actually need, not what they're asking for."
   Earn the system reference; don't lead with it.

2. **Wise but relatable, not lofty.** Sounds like a wise friend who happens to know all
   these systems — talking *to* you, leaning in, direct. Not an analyst presenting findings.
   Short paragraphs. More "you" and less "this placement." Occasional dry wit is fine.

The `synthesis-voice-sample.md` (Jamie v2 reading) is the living proof of what this
sounds like when it's right. Include it in the Claude API prompt.

---

## Skill Location

Skill lives at: `/mnt/skills/user/natal-chart-synthesis-v2/`
Skill description file: `SKILL.md` (root of skill directory)
Scripts: `scripts/`
References: `references/`

All new files from this session are in the outputs folder delivered with this handoff.
