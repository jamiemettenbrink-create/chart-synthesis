# un/charted — Project Handoff

A continuation guide for picking this project up in a fresh thread. Written
2026-06-09. Reflects `main` at the merge of PR #25.

---

## 1. What this project is

A multi-system natal-chart synthesis engine. It calculates seven symbolic
systems (Western astrology, Human Design, Gene Keys, Vedic/Jyotish, BaZi,
Numerology, Enneagram + Sabian symbols) and writes an integrated reading whose
power is **convergence** — when independent systems agree, that agreement is the
insight.

There are two parallel surfaces, and they are **not** kept in lockstep:

- **`app.html`** — the live, deployed web app. Self-contained single file: real
  astronomy in JS, an Anthropic + HD API via a Cloudflare Worker proxy. **This is
  the product and the surface all recent work targets.**
- **The agentic skill** — `SKILL.md` + `scripts/*.py` + `references/*.md`. The
  original path where Claude Code runs Python calculators and writes a reading
  into `outputs/`. Still present; not where the relationship feature was built.
- **`design/`** — a design prototype (`app.js` uses `window.claude`, `index.html`
  holds the locked brand). A reference, **not** the live app.

If those ever conflict, **the real file wins** — and for runtime behavior the
real file is `app.html` (JS), not the Python scripts.

---

## 2. Current state of `main`

Recent history (newest first):

| PR | What |
|----|------|
| #25 | Human Design connection theory (relational) |
| #24 | BaZi + Numerology + Vedic-nodal relational layers |
| #23 | Settle the two relational taste calls (docs) |
| #22 | "Your People" roster screen |
| #21 | Coordinate relationship reading with hybrid Deep Dive generation |
| #20 | Relationship (two-person) reading — vertical slice |
| #19 | Hybrid generation: block on Blueprint, prefetch Deep Dive |
| #18 | Revise Blueprint writing contract: verdict, not evidence |

Net: there is a complete **single-chart** reading and a complete **two-person
relationship** reading, plus a local **roster** to save/edit/read/pair people.

---

## 3. `app.html` map (everything is in one `<script>`)

Rough order, by responsibility:

- **`CONFIG`** — `proxyUrl` (deployed Worker), `hdEnabled`, `model`
  (`claude-sonnet-4-6`), `maxTokens`, `deepDivePrefetch` (4).
- **`el()` / `markEl()`** — DOM builder + the constellation brand mark.
- **Astronomy** — Meeus Sun/Moon, JPL Keplerian inner planets, Ascendant,
  Lahiri ayanamsha (Vedic), Rave wheel (Gene Keys), BaZi pillars, mean lunar
  node. All deterministic from birth data.
- **`SYNTHESIS_SYSTEM`** — the system prompt sent with every LLM call (voice
  rules; rules 5–7 scoped to the Deep Dive; the Blueprint has its own contract).
- **`state`** — `form`, `form2`, `relationship{enabled,type}`, `mode`
  (`'single'|'relational'`), `chart`, `chartB`, `synastry`, `reading`,
  `relReading`.
- **Roster data model** (localStorage) — see §4.
- **`REL_TYPE_CONFIG` / `REL_TYPE_ORDER`** — the five relationship types; mirrors
  `references/relationship-type-config.md` (canonical).
- **`computeChart(form, hdApiData)`** — returns the full chart object
  (`western{…, northNode, southNode}`, `vedic`, `bazi`, `numerology`, `geneKeys`,
  `humanDesign|null`, `enneagram`).
- **`chartFacts` / `blueprintPrompt` / `deepDivePrompt` / `glossaryPrompt`** —
  single-chart prompt builders.
- **Synastry engine** — `computeSynastry`, `SYNASTRY_CONTRIBUTORS` registry, the
  contributors (`baziInteraction`, `lifePathInteraction`, `nodalOverlap`,
  `hdConnection`), `relationalFacts`, `relBlueprintPrompt`, `relDeepDivePrompt`.
- **Render + lifecycle** — `renderForm`, `startReading`, `renderReading`,
  `streamBlueprint`; the mode-aware Deep Dive job system (`ddJobs`,
  `ensureDeepDive`, `prefetchDeepDive`, `deepDiveAccordion`,
  `activeDeepDiveSections`/`ddPromptFor`/`ddStore`); `startRelationalReading`,
  `renderRelationalReading`, `streamRelBlueprint`; the roster (§4).
- **Boot** — opens the roster if people are saved, else the form.

---

## 4. The relationship feature (the bulk of recent work)

**Principle (non-negotiable):** the reading describes the relationship as a
*third entity*. **No score, no percentage, no "should you" verdict.** It answers
"what's the weather between these two, and how do you move through it." If any
change trends toward a score, stop.

### Data model (localStorage)
- `Person` — `{id, display_name, full_legal_name, birth_date, birth_time,
  time_known, birth_place{lat,lng,display,city}, enneagram?, added_by, added_at}`.
- `DerivedChart` — a deterministic, recomputable cache (`derivedCache`, keyed by
  person id). HD is attached best-effort on top (`enrichHD`).
- `Relationship` — computed on demand, **never stored**. Store inputs + derived
  charts; treat the reading as a render.
- "You" identity — a `SELF_KEY` pointer; the form-filler becomes "you" on first
  reading (`upsertSelf`). `savedOthers()` = everyone else.
- Key fns: `loadRoster/upsertPerson/upsertSelf/updatePerson/deletePerson/
  clearRoster/getSelf/personToForm/derivedChartFor`. Deletion is complete
  (record + cache + self-pointer).

### Synastry (Western, built in)
- Inter-aspects across Sun/Moon/Mercury/Venus/Mars (+ Rising when both timed),
  honest orbs; composite chart via nearer circular midpoint; relational
  convergence hints.

### Cross-system contributors (`SYNASTRY_CONTRIBUTORS` registry)
Each is `(chartA, chartB) => {facts:[], hints:[]} | null`. To add a system,
write one function and `push` it — no other wiring.
- **BaZi** — Day Master Five-Element interaction (resonance / one-way feeds /
  one-way checks), directional.
- **Numerology** — Life Path interaction (light touch; only on a shared path).
- **Vedic** — lunar-nodal overlap (one chart's node axis on the other's
  Sun/Moon/Venus/Mars ≤6° → "fated/sticky").
- **HD** — `hdConnection` classifies all 36 channels into electromagnetic /
  companionship / dominance / compromise. Needs HD for both people (see below).

### HD for two people
`enrichHD(chart, form)` does a best-effort second bodygraph fetch (reuses
`fetchHD` → Worker `/hd`) and attaches `humanDesign` to the cached chart. No-op
without a birth time or the HD service, so the reading degrades gracefully.

### Output
`relationalFacts()` assembles the facts block (reader = "you" = the form-filler;
person B = the framing word). The relational Blueprint applies the single-chart
Blueprint contract verbatim (no system names on the surface; the relationship is
the subject; write to convergence; specific over comprehensive). Deep Dive
sections come from `REL_TYPE_CONFIG[type].sections` and hold the receipts.

### Roster screen ("Your People")
`renderRoster` — you pinned at top (editable, where birth-time correction lives),
saved people below with **Read / With you / Forget**, plus **New reading** and
**Forget everyone**. `readWithYou` → `pickRelTypeModal` ("Who is X to you?") →
relational reading. `editPersonModal` overwrites a stored record in place. Built
entirely from the existing design system — no new design files.

### Hybrid generation (#19/#21)
Single and relational Deep Dives share one job system: prefetch the first
`CONFIG.deepDivePrefetch` sections in display order, lazy-load the rest on
expand, dedup in-flight requests, fill open-and-waiting sections in the
background, surface errors only on expand. Mode is routed by
`activeDeepDiveSections`/`ddPromptFor`/`ddStore`.

---

## 5. Decisions locked this session (don't relitigate without reason)

- **Build surface:** `app.html` only. The Python skill + `design/` were *not*
  updated for the relationship feature (synastry lives in JS, not a
  `calculate_synastry.py`). This was a deliberate "real file wins" call.
- **Persistence:** browser `localStorage` (the app has no backend). Complete
  deletion is a hard requirement (third-party birth data).
- **Reader = form-filler** for child/parent direction; relational Blueprint
  headings final ("What this is, underneath / Where the current runs / Where it
  snags / How to move through it"). Both recorded as DECIDED in
  `references/relationship-type-config.md`.
- **No score / no verdict.** Ever.

---

## 6. Known limitations & untested surfaces

- **Only verifiable in the deployed app:** live LLM streaming/rendering, and the
  two-person HD API fetch (needs the Worker proxy + `HD_API_KEY` secret). All the
  math, data model, routing, and prompt assembly are validated offline.
- **`outputs/*.md`** are historical generated readings using the *old* Blueprint
  headings. Left as dated records; not regenerated (would need the live pipeline).
- **Lunar nodes** are now computed on every chart but used only relationally —
  an easy win is to surface them in the single-chart synthesis too.
- **`design/app.js`** still mirrors an older prompt shape; it's a prototype, not
  the product. Don't assume it matches `app.html`.
- **Privacy posture** is "fine for a friends beta." Revisit if it widens (you're
  storing third parties' birth data locally).

---

## 7. How to validate without the deployed app

The script is browser-only, but pure logic is testable in Node by extracting the
`<script>` and stubbing the few browser globals:

```bash
node -e "const fs=require('fs');const m=fs.readFileSync('app.html','utf8').match(/<script>([\\s\\S]*)<\\/script>/);fs.writeFileSync('/tmp/app.js',m[1]);"
node --check /tmp/app.js   # syntax
```

Then prepend stubs (`document` with `createElement/createElementNS/createTextNode/
addEventListener/querySelector`, an in-memory `localStorage`, `navigator`,
`window`, `fetch`, `requestAnimationFrame`, `alert/confirm`), append the script,
and call `computeChart` / `computeSynastry` / contributor functions directly.
`computeChart` and `computeSynastry` need no DOM; render functions need the
element stub above. Known-good anchor: Jamie (1986-04-24, 06:10, Scottsdale)
→ Taurus Sun 4.1°, North Node 29.8° Aries.

---

## 8. Suggested next steps (deferred, demand-gated)

In rough priority:

1. **Eyeball a live relational reading** in the deployed app (LLM + two-person
   HD). This is the one thing that hasn't been seen end to end.
2. **Type-branching / weight tuning** on real beta pairs — the convergence
   weighting and per-type ordering are first-pass; tune on real output.
3. **Surface lunar nodes (and HD) in the single-chart reading** — the data now
   exists; `chartFacts` doesn't yet include nodes.
4. **Step-3 "return-to" navigation** (home / recent-updates / relationship detail
   pages) — only if beta usage shows people returning. A retention bet; don't
   build on spec.
5. **Reader-selectable child/parent direction** — wire-ready; the synthesis is
   direction-agnostic underneath, only framing/UX would change.
6. **Privacy hardening** if the audience widens beyond friends.

---

## 9. Workflow notes

- **Branch/PR:** develop on `claude/chart-synthesis-revision-y8q5lm`, squash-merge
  to `main`. (This session realigned that branch to `main` before each new PR and
  force-pushed — fine because each prior PR was already squash-merged.)
- **APIs:** the browser never holds keys. `CONFIG.proxyUrl` → Cloudflare Worker
  (`proxy/worker.js`) with `/anthropic` (SSE streaming) and `/hd` routes;
  `ANTHROPIC_API_KEY` and `HD_API_KEY` are Worker secrets.
- **GitHub:** use the `mcp__github__*` tools (no `gh` CLI). Scope is this repo.
- **Identity in artifacts:** don't put model identifiers in commits/PRs/code.

---

## 10. File map

| Path | Role |
|------|------|
| `app.html` | The live app — all runtime logic (calc, synastry, roster, render) |
| `SKILL.md` | The agentic skill instructions (Python path) |
| `scripts/*.py` | Python calculators for the skill path (not used by `app.html`) |
| `references/synthesis-guide-v2.md` | Single-chart structure + Blueprint contract |
| `references/synthesis-guide-addendum-v2.1.md` | Sabian Deep Dive + Glossary |
| `references/relationship-type-config.md` | **Canonical** relationship type table (mirrored by `REL_TYPE_CONFIG`) |
| `references/synastry-guide.md` | Composite + inter-aspects + cross-system layers |
| `references/hd-connection-theory.md` | The four HD channel-connection types |
| `references/relationship-convergence-checklist.md` | Relational convergence checklist |
| `references/voice-guide.md`, `synthesis-voice-sample.md` | House voice + worked example |
| `design/`, `design-brief.md` | Design prototype + brief (locked brand) |
| `proxy/` | Cloudflare Worker (API proxy) + deploy README |
| `outputs/` | Historical generated readings (dated records) |
