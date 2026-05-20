---
name: natal-chart-synthesis-v2
description: >
  Full multi-system natal chart calculator and synthesis engine.
  Triggers on any request for a birth chart reading, astrology interpretation,
  Human Design reading, natal synthesis, or "read my chart" request.
  
  Runs: Western Astrology (Meeus ephemeris) | Human Design (HD Hub API) |
  Vedic/Jyotish (sidereal, Nakshatras, Vimshottari Dasha) | BaZi Four Pillars |
  Numerology (Pythagorean) | Gene Keys (all 64 gates) | Enneagram (if provided) |
  Sabian Symbols (Sun + ASC degree archetypes).
  
  Produces a two-layer output: Blueprint Summary (5-min read) + Deep Dive sections
  + Chart Glossary (all-systems reference card).
  
  Required inputs: birth date, birth time, birth location.
  Optional: full legal birth name (for numerology), HD API key, Enneagram type.
---

# Multi-System Natal Chart Synthesis

## Overview

This skill calculates and synthesizes seven symbolic systems into a unified natal portrait.
The synthesis engine identifies **convergences** — themes that appear across multiple
independent systems — and weights them accordingly. A pattern confirmed by 4+ systems
is near-certain; a pattern from one system alone is noted tentatively.

---

## SYSTEM INVENTORY

| System | What it provides | Calculator |
|--------|-----------------|------------|
| Western Astrology | Character, psychology, aspects | `calculate_chart.py` |
| Human Design | Energy type, decision-making, life design | HD Hub API |
| Gene Keys | Shadow→Gift→Siddhi transformation map | `gene-keys-complete.md` |
| Vedic/Jyotish | Sidereal chart, Nakshatras, Dasha timing | `calculate_vedic.py` |
| BaZi Four Pillars | Elemental constitution, interactions, timing | `calculate_bazi.py` |
| Numerology | Life Path, Expression, Soul Urge, cycles | `calculate_numerology.py` |
| Enneagram | Core wound and ego structure (self-identified) | `enneagram-guide.md` |
| Sabian Symbols | Archetypal image for exact Sun/ASC degree | `sabian-symbols.md` |

---

## STEP 1: COLLECT INPUT

Required:
- Birth date (month/day/year)
- Birth time (as exact as possible; if unknown, note it — time affects ASC/MC/House)
- Birth city and country

Optional but valuable:
- Full legal birth name at birth (enables numerology Expression and Soul Urge numbers)
- Human Design Hub API key (get free at humandesignhub.app/en/developer)
- Enneagram type (e.g. "2w3" or "Type 4, Social subtype")
- Current year (for Personal Year numerology; defaults to 2026)

---

## STEP 2: GEOCODE AND DETERMINE UTC OFFSET

**Common US locations:**
- Scottsdale/Phoenix AZ: lat=33.4942, lng=-111.9261, UTC-7 (Arizona, no DST)
- Los Angeles CA: lat=34.0522, lng=-118.2437, UTC-8 (PST) / UTC-7 (PDT)
- New York NY: lat=40.7128, lng=-74.0060, UTC-5 (EST) / UTC-4 (EDT)
- Chicago IL: lat=41.8781, lng=-87.6298, UTC-6 (CST) / UTC-5 (CDT)
- Denver/Thornton CO: lat=39.7392, lng=-104.9903, UTC-7 (MST) / UTC-6 (MDT)
- Seattle WA: lat=47.6062, lng=-122.3321, UTC-8 (PST) / UTC-7 (PDT)
- Dallas TX: lat=32.7767, lng=-96.7970, UTC-6 (CST) / UTC-5 (CDT)
- Miami FL: lat=25.7617, lng=-80.1918, UTC-5 (EST) / UTC-4 (EDT)

**DST rule (US):** 2nd Sunday March → 1st Sunday November.
Arizona does NOT observe DST (always UTC-7).

---

## STEP 3: RUN ALL CALCULATORS

### 3A. Western Astrology
```bash
python3 scripts/calculate_chart.py \
  --name "NAME" \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --utc_offset OFFSET \
  --lat LAT --lng LNG
```

### 3B. BaZi Four Pillars
```bash
python3 scripts/calculate_bazi.py \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --utc_offset OFFSET
```

### 3C. Vedic / Jyotish
```bash
python3 scripts/calculate_vedic.py \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --utc_offset OFFSET \
  --lat LAT --lng LNG
```

### 3D. Numerology (requires full birth name)
```bash
python3 scripts/calculate_numerology.py \
  --year YYYY --month MM --day DD \
  --name "Full Legal Birth Name" \
  --current_year 2026
```

### OR: Run all at once with the master runner
```bash
python3 scripts/run_full_chart.py \
  --year YYYY --month MM --day DD \
  --hour HH --minute MM \
  --utc_offset OFFSET \
  --lat LAT --lng LNG \
  --name "Display Name" \
  --full_name "Full Legal Birth Name" \
  [--hd_type "Generator"] \
  [--hd_authority "Emotional"] \
  [--hd_profile "3/5"] \
  [--hd_cross "Right Angle Cross of the Unexpected"] \
  [--hd_centers "Sacral,Solar Plexus"] \
  [--hd_channels "27-50,28-38"] \
  [--hd_gates "27,28,41,31,50"] \
  [--enneagram "2w3"] \
  [--enneagram_instinct "SP"]
```

### 3E. Human Design Hub API (call from browser/fetch, not bash — network restricted)
```
POST https://api.humandesignhub.app/v1/bodygraph
Header: X-API-KEY: {user's key}
Body: {"datetime": "YYYY-MM-DDTHH:MM:SS±HH:MM"}
```
Cost: 1 credit (100/month free). Returns: type, strategy, authority, profile,
definition, incarnation_cross, centers, undefined_centers, channels_short, gates.

---

## STEP 4: READ REFERENCE FILES

Before writing synthesis, read these files:
- `references/voice-guide.md` — brand voice, tone rules, banned phrases (read first)
- `references/synthesis-guide-v2.md` — section structure, tone, convergence weighting
- `references/synthesis-guide-addendum-v2.1.md` — Section 13 (Sabian Deep Dive) + Glossary instructions
- `references/sabian-symbols.md` — all 360 degrees, symbol names, keywords, lookup convention
- `references/hd-guide.md` — HD types, authorities, profiles, incarnation crosses
- `references/gene-keys-complete.md` — all 64 gates shadow/gift/siddhi
- `references/bazi-guide.md` — Day Master meanings, Ten Gods, clashes
- `references/vedic-guide.md` — Lagna, Nakshatras, Dasha interpretation
- `references/enneagram-guide.md` — types, wings, instincts (if Enneagram provided)
- `references/aspects.md` — key aspect combinations for Western synthesis
- `references/houses.md` — house meanings

---

## STEP 5: IDENTIFY CONVERGENCES

Before writing a single section, scan the full data for cross-system patterns.
The `run_full_chart.py` script auto-generates convergence hints — review these first.

**Convergence checklist:**
□ Does the same element appear in Western Sun/ASC, BaZi Day Master, and Vedic Lagna?
□ Does the North Node direction match across Western and Vedic systems?
□ Does the BaZi Day Master element echo the Western dominant element?
□ Do the Gene Keys primary shadow and Enneagram core wound name the same pattern?
□ Does the Numerology Life Path theme echo the HD Incarnation Cross purpose?
□ Do current timing indicators (Vedic Dasha, Numerology Personal Year) agree?

Weight independent cross-tradition confirmations more heavily than same-tradition ones.

---

## STEP 6: WRITE THE SYNTHESIS

### Two-Layer Format

**Layer 1 — The Blueprint** (~500-700 words):
Four sub-sections: Core Pattern | What You're Here to Do | The Central Challenge | Current Phase
In **Core Pattern**, include one line: the Sabian Symbol for the Sun degree (name + keyword only).
End with the Integrated Alignment Statement (4-6 sentences, first person).

**Layer 2 — The Deep Dive** (13 sections):
1. Core Energetic Signature
2. Central Psychological Architecture
3. Decision-Making & Mental Style
4. Moon Deep Dive
5. Natural Gifts & Gene Keys
6. Shadow Patterns & Growth Edges
7. Relationship Dynamics
8. Ideal Work & Creative Expression
9. Family, Ancestry & Roots
10. Nervous System & Body
11. Vedic Mahadasha Context
12. Living in Alignment
13. The Sabian Symbol ("The Seal on the Sun") — ~300 words, archetypal interpretation
    of the Sun's exact degree, tied back to chart themes

**Closing — Chart Glossary ("Your Chart at a Glance")**
All systems, all key terms, 2–3 sentences each — personalized to this specific chart.
Organized by system: Western → Human Design → Vedic → BaZi → Numerology → Gene Keys → Enneagram.
See `references/synthesis-guide-addendum-v2.1.md` for full structure and tone guidance.

---

## QUALITY STANDARDS

Every statement must trace to a specific placement, gate, number, or pillar.
The cross-system test: does any other system confirm this claim?
The specificity test: could this sentence have been written about a different chart?
The depth test: does this paragraph make the person feel seen, or just catalogued?

---

## EXAMPLE RUN (Apr 24, 1986, 6:10 AM, Scottsdale AZ)

```bash
python3 scripts/run_full_chart.py \
  --year 1986 --month 4 --day 24 \
  --hour 6 --minute 10 --utc_offset -7 \
  --lat 33.4942 --lng -111.9261 \
  --name "Jamie" \
  --full_name "Jane Elizabeth Smith" \
  --hd_type "Generator" \
  --hd_authority "Emotional" \
  --hd_profile "3/5" \
  --hd_cross "Right Angle Cross of the Unexpected" \
  --hd_centers "Sacral,Solar Plexus" \
  --hd_channels "27-50,28-38,41-30" \
  --hd_gates "27,28,41,31,50,38,30" \
  --current_year 2026
```

Key convergences this produces:
- TRIPLE EARTH: Western Taurus Sun + Taurus ASC + BaZi Yang Earth Day Master
- DEPTH: Western Scorpio Moon (H7) + Pluto in H7 + Vedic depth signals
- NODAL: Western NN Aries/SN Libra ↔ Vedic Rahu Aries H1/Ketu Libra H7 (exact match)
- LEADERSHIP: Capricorn MC + HD Gate 31 + Numerology Soul Urge 8
- TIMING: Vedic Mercury mahadasha (2021-2038) + Numerology Personal Year 11 (2026)
