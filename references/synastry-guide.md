# Synastry Guide — Composite + Inter-Aspects

> How the Western layer reads two charts as one relationship. Two techniques:
> inter-aspects (the chemistry between the two people) and the composite chart
> (the relationship as its own third entity). Receipts live in the relational
> Deep Dive; the relational Blueprint reports the verdict jargon-free.
>
> Computed now: Western synastry + composite (below), plus BaZi Day Master
> interaction, Numerology Life Path interaction, and the Vedic/lunar nodal axis
> (§4, contributed through the `SYNASTRY_CONTRIBUTORS` registry). HD connection
> theory is the remaining later phase — see `relationship-feature-spec.md`.

---

## 1. Inter-aspects (the chemistry)

Compare each of person A's planets against each of person B's planets. An
inter-aspect is a recognized angular relationship between two longitudes:

| Aspect | Angle | Orb (slice) | Feel |
|---|---|---|---|
| Conjunction | 0° | 8° | fusion, intensity, blended — energizing or overwhelming |
| Opposition | 180° | 7° | magnetism + tension; the see-saw, attraction across a gap |
| Trine | 120° | 6° | ease, flow, things that just work between them |
| Square | 90° | 6° | friction, growth-through-grind, the productive irritation |
| Sextile | 60° | 4° | gentle opportunity, low-effort support |

**Which contacts matter most for which theme:**
- **Attraction / magnetism:** Sun–Moon, Venus–Mars, Sun–Venus, Moon–Mars contacts.
- **Emotional rhythm:** Moon–Moon, Moon–Sun, Moon–Venus.
- **Mental fit:** Mercury–Mercury, Mercury–Moon.
- **Friction / heat:** squares and oppositions involving Mars, or to either Sun/Moon.
- **Easy ground:** trines and sextiles among the personal planets.

A single contact is a single-system observation. Several contacts pointing at
the same theme is a convergence — state it once, in the Blueprint, jargon-free.

---

## 2. The composite chart (the third entity)

The composite is built by the **midpoint method**: for each body, take the
nearer circular midpoint of A's and B's longitudes. The result is a chart that
belongs to neither person — it is the relationship itself.

- **Composite Sun** — what the relationship is *for*; its core identity and purpose.
- **Composite Moon** — its emotional baseline; how it feels to be inside it.
- **Composite Venus / Mars** — how affection and drive move through it.
- **Composite Ascendant** (only if both birth times are known) — how the pair
  presents to the outside world.
- **Composite Sun's sign element/modality** — the relationship's constitutional
  temperament (earthy and durable, airy and verbal, watery and merged, fiery and
  volatile).

The composite is what makes a relational reading feel like a third thing rather
than two readings stapled together. Lead the "what this is, underneath" beat
from the composite Sun + Moon, not from either person's chart.

---

## 3. Discipline

- **No score.** Synastry has a long tradition of compatibility points
  (Ashtakoota, etc.). Do not use it. The reading is weather, not a verdict.
- **Orbs are honest.** If two planets are 9° apart, they are not in aspect — do
  not round them into one. Report only contacts within the orbs above.
- **Time-unknown charts.** Without a birth time, the Moon longitude is computed
  at local noon (it can drift up to ~6°) and there is no Ascendant. Moon-based
  contacts are approximate; say so rather than overreaching, and omit composite
  Ascendant.
- **The convergence is the insight.** When inter-aspects and the composite agree
  on a theme, that agreement — stated once — is the Blueprint line.

---

## 4. Cross-system relational layers

These plug into the synastry engine through the `SYNASTRY_CONTRIBUTORS` registry
and add their signals to the relational convergence hints. They are receipts for
the Deep Dive; the Blueprint still reports the verdict jargon-free. None of them
produce a score.

### BaZi — Day Master interaction
Compare the two Day Master elements through the Five-Element cycle:
- **Same element →** resonance: instant recognition and sameness, with the risk of
  one note and no counterbalance.
- **Generating (one feeds the next: Wood→Fire→Earth→Metal→Water→Wood) →** one-way
  support: the feeding element naturally nourishes and energizes the other; watch
  for the giver running dry.
- **Controlling (one checks the next two along: Wood→Earth→Water→Fire→Metal→Wood) →**
  one-way control: the controlling element disciplines or contains the other;
  steadying in small doses, controlling in large ones.
The dynamic is **directional** — name who feeds or checks whom, not a verdict.

### Numerology — Life Path interaction
Light touch, one line, and only when it converges: if both walk the same Life
Path, name the shared road (deep mutual understanding plus a shared blind spot).
Otherwise it stays in the receipts, not the Blueprint.

### Vedic — lunar nodal axis (Rahu / Ketu)
Using the mean lunar node, flag where one person's North or South Node lands on
the other's Sun, Moon, Venus, or Mars (within 6°). Nodal contacts read as a
*fated, sticky* quality — the relationship feels less optional than chosen and
carries a pull toward growth. This is nodal **synastry**, not Ashtakoota scoring;
the no-score discipline still holds.
