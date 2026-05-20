# Voice & Brand Guidelines
## Natal Chart Synthesis — All Copy

---

## The Voice in One Line

Credible, funny, sharp, wise. The friend who actually knows what they're talking about
and doesn't need you to know that they know.

---

## Core Principles

**Dry wit over warmth.** Not cold — there's genuine care here. But the warmth earns its
place. It doesn't lead. A wise friend leans in and tells you something real; they don't
hug you first to soften it.

**Specific over cosmic.** Never use vague spiritual language as a substitute for an
actual observation. "You have a gift for seeing beneath surfaces" beats "your soul radiates
ancient wisdom." The first is true. The second means nothing.

**Short sentences at the key moments.** The wit lands when it has room. Don't bury the
good line in a dependent clause.

**Earned gravity.** The reading covers serious material. The tone earns the right to go
deep by not being precious about it. Occasional dry humor is not disrespectful — it's
the signal that the reader isn't being handled.

**No exclamation points. Ever.**

**No vague cosmic language.** Banned phrases include (but are not limited to):
- "your soul's journey"
- "the universe is calling you to..."
- "shine your light"
- "you are exactly where you need to be"
- "ancient wisdom"
- "the cosmos have aligned"
- anything that sounds like it belongs on a wellness Instagram

---

## Do / Don't

| Do | Don't |
|----|-------|
| "Your authority is Emotional. Sleep on it." | "You are blessed with deep emotional intelligence!" |
| "Three systems agree on this. That's not coincidence." | "The universe is confirming your path." |
| "The fortress was useful. It's also become a habit." | "You have built walls around your heart." |
| "This is the chapter for going inward." | "It's time to embrace your inner journey." |
| "You feel what's actually happening before anyone says it." | "You are highly intuitive and spiritually gifted." |
| "Solid outside. Volcanic inside. Most people only see one." | "You are a complex and multi-faceted individual." |

---

## UI Copy

### Tagline / Header
> "Six systems. One synthesis. A lot of existential clarity you probably weren't ready for."

### Onboarding / Subhead
> "Enter your birth data. We'll handle the rest — Western astrology, Human Design, Vedic,
> BaZi, numerology, Gene Keys, and one Sabian Symbol that will probably make you pause."

### Loading States

**During calculation (JS, pre-API call):**
> "Running your chart across six systems. This takes a moment. The planets were doing
> their thing long before instant gratification existed."

**During API stream (synthesis writing):**
> "Writing your reading. This is the long part. Worth it."

**On completion:**
> "Done."

### Form Field Labels & Tooltips

**Birth time — "Time unknown" toggle:**
> "No birth time? No problem — you'll lose the Ascendant and houses, but the rest holds."

**Human Design API key:**
> "Optional but recommended. Free tier gives you 100 charts/month. Your design data gets
> pulled directly from the source rather than estimated."
> *(link: Get a free key →)*

**Enneagram field:**
> "Self-identified only. If you're not sure, skip it — a wrong type does more damage than
> a missing one."

**Anthropic API key:**
> "Your key stays in your browser. It never touches our servers because we don't have any."

### Error States

**Geocoding failed:**
> "Couldn't find that city. Try adding the country, or use coordinates."

**HD API error:**
> "Human Design API returned an error. Check your key, or enter your HD data manually below."

**Claude API error:**
> "The synthesis didn't complete. This is usually an API key issue or a timeout on a
> long response. Try again."

**No birth time entered:**
> "Birth time is empty. If you don't know it, use the toggle above — don't guess."

### Section Intros (for Deep Dive accordion headers — optional flavor text beneath title)

These are short. One line. They set the stakes without over-explaining.

| Section | Intro line |
|---------|-----------|
| Core Energetic Signature | "What you actually are, underneath the persona." |
| Central Psychological Architecture | "The tension that runs everything." |
| Decision-Making & Mental Style | "How you're wired to choose. And where it goes wrong." |
| Moon Deep Dive | "The interior life. The part most people don't see." |
| Natural Gifts & Gene Keys | "What you're actually good at, and why." |
| Shadow Patterns & Growth Edges | "The contracted form of the gift." |
| Relationship Dynamics | "What you bring. What you draw in. What the growth edge is." |
| Ideal Work & Creative Expression | "What the work has to mean." |
| Family, Ancestry & Roots | "Where you came from and what it left in you." |
| Nervous System & Body | "Not wellness advice. Specific to this chart." |
| Vedic Mahadasha Context | "The chapter you're in and how long it runs." |
| Living in Alignment | "The five practices. Specific to this chart." |
| The Seal on the Sun | "The archetypal image on your exact solar degree." |

### Glossary Header
> "Everything above is the synthesis. This is the map behind it — every placement,
> every system, what each one means for you. Come back here when you want to know
> where a specific insight came from."

### Copy Button
- Default: **"Copy full reading"**
- On success: **"Copied"** *(2 seconds, then revert)*

---

## Synthesis Writing Voice

The synthesis itself follows the same principles. The approved benchmark is
`references/synthesis-voice-sample.md` — the Jamie v2 reading. Use it as the living
proof of what this sounds like when it's right.

The two non-negotiable rules (carried forward from v2):

**1. Less describing the system, more describing the implication.**
Don't say "Gate 27 is the nurturance gate which in Human Design represents care."
Say "you have an almost supernatural ability to sense what people actually need,
not what they're asking for." Earn the system reference. Don't lead with it.

**2. Wise but relatable, not lofty.**
Sounds like a wise friend who happens to know all these systems — talking *to* you,
leaning in, direct. Not an analyst presenting findings. Short paragraphs. More "you"
and less "this placement." Occasional dry wit is not just permitted — it's part of the
voice when the material earns it.

---

## What This Voice Is Not

Not a horoscope. Not a wellness brand. Not a therapist. Not a life coach.
Not trying to be liked.

It's trying to be true.
