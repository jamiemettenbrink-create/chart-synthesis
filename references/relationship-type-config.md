# Relationship Type Config — Source of Truth

> The single source of truth for relationship-type branching in the relational
> reading. One table feeds both the Deep Dive section ordering and the framing
> word injected into the synthesis prompt. No branching logic should be
> scattered anywhere else.
>
> **Implementation note (app.html slice):** app.html is a static single file and
> cannot read this markdown at runtime, so the `REL_TYPE_CONFIG` object in
> app.html mirrors this table verbatim. This file is canonical; keep the two in
> sync. (Deviation from the handoff's "read from the file" instruction — the
> real file is JS-only, so we mirror instead of read.)

---

## The type table

| Type | Framing word | Blueprint leads with | Deep Dive section order (top 4) | First-person-plural alignment statement |
|---|---|---|---|---|
| Romantic | partner | magnetism + emotional rhythm | Attraction · Emotional weather · Long-term friction · Repair | yes |
| Child | your child | who they are vs. who you assume | Their nature · Where you clash · What they need from you · Letting go | yes |
| Parent | your parent | inherited patterns + the old role | Inherited patterns · The old dynamic · Triggers · Re-meeting as adults | yes |
| Coworker | colleague | who initiates vs. sustains | Decision friction · Complementary energy · How you clash · Trust | no (reads odd for co-founders) |
| Friend | friend | ease vs. effort | Natural ease · What recharges vs. drains · Loyalty shape · Drift risk | no |

Computation is identical across all five types. Type only reorders the Deep
Dive and reframes the surface — it never changes the underlying synastry math.

---

## Blueprint structure (all types)

Four beats, reworded per type via the framing word. Apply the single-chart
Blueprint contract verbatim: no system names on the surface, the
person/relationship is the grammatical subject, write to the convergence, be
specific over comprehensive, dry-credible voice.

1. **What this is, underneath** — the one dynamic everything circles back to
2. **Where the current runs** — the pull / chemistry / ease, stated plainly
3. **Where it snags** — the recurring friction, named without judgment or verdict
4. **How to move through it** — practical, non-prescriptive navigation

End with a short first-person-plural alignment statement ("We tend to…") — only
for the types marked yes above (romantic, child, parent).

> **DECIDED (Jamie, final):** these four beat headings are confirmed as written —
> "What this is, underneath" / "Where the current runs" / "Where it snags" /
> "How to move through it." No change.

---

## Directionality (child / parent)

The same pair read from opposite ends is the same computation framed two ways.
The framing word keys off **which direction the reader is looking**.

> **DECIDED (Jamie, final):** the reader is the form-filler. Person A (the primary
> chart, the form) is addressed as "you." Person B (the added second person) is
> the relation named by the framing word — "your child," "your parent," etc.
> One fixed direction, confirmed — no reader-selectable direction. (If that
> changes later, it's a new task; the synthesis is direction-agnostic underneath,
> so only the framing/UX would need wiring.)

---

## The non-negotiable principle

The reading describes the relationship as a **third entity**. No score, no
percentage, no "should you" verdict. It answers "what is the weather between
these two and how do you move through it," never "does this work." If any
implementation choice trends toward a score or a verdict, stop and flag it.
