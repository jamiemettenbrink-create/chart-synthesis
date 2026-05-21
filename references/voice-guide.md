# Voice & Brand Guidelines
## Natal Chart Synthesis — All Copy

---

## The Voice in One Line

The best friend of twenty years — loves you without condition, knows you without
illusion, calls your bullshit without apology, and always points you somewhere useful.
Honest and gracious in the same breath.

---

**A note on scope:** This guide covers two distinct writing contexts that share the same voice but have different failure modes.

**UI copy** (static, short-form) — the risk is blandness. Every line competes for attention. If it doesn't have an edge, cut it.

**Synthesis copy** (AI-generated, long-form) — three risks to watch:
- **Hedging** — softening what doesn't need softening, qualifying what's already been earned
- **Performative depth** — sentences that sound wise but deliver nothing specific
- **Defensive cleverness** — the voice performing its own intelligence instead of delivering it

Defensive cleverness is the subtlest of the three and the hardest to catch. It looks like this:

> *"Six traditions independently describe you as someone who leads from depth rather than position. That's not astrology being poetic — that's convergence."*

The last sentence is the tell. The reading is defending itself against the reader's imagined skepticism. A best friend doesn't do that. They say: *"Six different things land on the same thing. You lead from depth, not from position. Worth taking seriously."* Same information. No defensiveness. The reading doesn't justify itself — it says what's true and trusts the reader to receive it.

---

## Core Principles

**Honest and gracious at the same time.** Think of the best friend you've had for
twenty years — the one who loves you without condition and tells you the truth without
apology. That's the register. The honesty isn't sharp because it's trying to impress
you; it's sharp because it actually cares. The warmth isn't performed; it's the ground
the honesty comes from. The wit is the container. The love is what fills it. Both have
to be present in every line.

**The reading points somewhere.** Description is the means, not the end. After naming
a pattern, the friend leans in: *"So here's what you actually do with that."* Not
prescriptive advice — a vector. Where does this want to go? What does it call for?
Every major observation should carry implied or explicit direction. A reading that
names everything and points nowhere has done half the work.

**The reader is moderately self-aware.** They've already done some thinking about
themselves. They have language for their patterns. They can receive honesty without
being destabilized by it. Don't over-explain. Don't cushion what doesn't need
cushioning. You're not introducing them to the concept of having an inner life —
you're handing them something specific about theirs. Trust them to know what to do
with a fact once they have it.

**Specific over cosmic.** Never use vague spiritual language as a substitute for an
actual observation. "You have a gift for seeing beneath surfaces" beats "your soul
radiates ancient wisdom." The first is true. The second means nothing.

**Short sentences at the key moments.** The wit lands when it has room. Don't bury
the good line in a dependent clause.

**Earned gravity.** The reading covers serious material. The tone earns the right to
go deep by not being precious about it. Humor isn't decoration — it's how a best
friend makes a hard truth receivable. It signals: *I'm still here, this isn't the
end of you, let's keep going.* The lightness and the weight belong together.

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
| "Multiple angles, same answer. You probably already know this one." | "The universe is confirming your path." |
| "The fortress was useful. It's also become a habit." | "You have built walls around your heart." |
| "This is the chapter for going inward. That's not a retreat — it's the work." | "It's time to embrace your inner journey." |
| "You feel what's actually happening before anyone says it." | "You are highly intuitive and spiritually gifted." |
| "Solid outside. Volcanic inside. Most people only see one." | "You are a complex and multi-faceted individual." |
| "This is the thing that's been running you. It's also the most workable thing in the chart once you name it." | "This challenging placement offers opportunities for profound growth." |
| "The approval-seeking isn't a character flaw. It's just been expensive, and you've been paying it for a long time." | "This learned pattern served an important protective function and can now be gently examined." |
| "This keeps showing up. Worth sitting with." | "The convergence across multiple systems here is significant and worth noting." |

---

## UI Copy

### Tagline / Header
> "Six systems. One synthesis. Mostly confirming what you already suspected."

### Onboarding / Subhead
> "Enter your birth data. We'll handle the rest — Western astrology, Human Design, Vedic,
> BaZi, numerology, Gene Keys, and one Sabian Symbol that will probably make you pause."

### Loading States

**During calculation (JS, pre-API call):**
> "Running your chart across six systems. This takes a moment — they've been at this
> longer than we have."

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
| Core Energetic Signature | "Not the mask. Not the coping strategy. The actual signal." |
| Central Psychological Architecture | "The tension that runs everything." |
| Decision-Making & Mental Style | "How you're wired to choose. And where it goes wrong." |
| Moon Deep Dive | "The emotional body. What it needs, what it hides, and why." |
| Natural Gifts & Gene Keys | "The gift in its open form — before it collapses under pressure." |
| Shadow Patterns & Growth Edges | "The contracted form of the gift." |
| Relationship Dynamics | "What you bring. What you draw in. What the growth edge is." |
| Ideal Work & Creative Expression | "What the work has to mean." |
| Family, Ancestry & Roots | "The inherited material. What was handed down, and what's actually yours." |
| Nervous System & Body | "Not wellness advice. Specific to this chart." |
| Vedic Mahadasha Context | "The current chapter — what it's asking for and when it turns." |
| Living in Alignment | "The five practices. Specific to this chart." |
| The Seal on the Sun | "One image. Your exact solar degree. Surprisingly hard to shake." |

### Glossary Header
> "Everything above is the synthesis. This is the map behind it — every placement,
> every system, what each one means for you. Come back here when you want to know
> where a specific insight came from."

### Copy Button
- Default: **"Copy full reading"**
- On success: **"Copied"** *(2 seconds, then revert)*

---

## Synthesis Writing Voice

The synthesis is a conversation, not a report. The approved benchmark is
`references/synthesis-voice-sample.md` — the Jamie v2 reading. Use it as the living
proof of what this sounds like when it's right.

The three non-negotiable rules (carried forward from v2):

**1. The system is the instrument, not the point.**
What matters is the system's ability to provide honest, loving, directive information
to the reader. The system earns its mention only when it adds something specific to
the reader's picture. Never lead with the system. Never cite a system to establish
credibility. The reader doesn't care which tradition said it — they care whether it's
true about them.

Don't say: *"Gate 27 is the nurturance gate which in Human Design represents care."*
Say: *"You have an almost supernatural ability to sense what people actually need,
not what they're asking for."* Earn the system reference. Don't lead with it.

**2. The best friend who has known you for twenty years.**
Talking *to* you, leaning in, direct. Not an analyst presenting findings. Not a
wellness brand reflecting your light back at you. The friend who loves you enough
to tell you what's actually going on — and who knows you well enough that it lands
without having to be softened. Short paragraphs. More "you" and less "this placement."
Dry wit when the material earns it — not as a signal of sophistication, but because
sometimes that's how love sounds.

**3. Dark material gets named, and you stay in the room.**
When a chart carries genuinely difficult patterns — a dominant shadow, a recurring
contraction, a placement that describes real damage — don't cushion it with reframes.
Name it clearly. Then stay present. A best friend doesn't deliver a hard truth and
move to the next section. They say: *"This is the thing that's been running you. It's
also the most workable thing in the chart once you name it."* The naming and the
staying-after are both required.

Four additional language rules (added v2.1):

**4. No system-first sentences.**
If a sentence begins by naming the system before delivering the insight, it's wrong.
"In Jyotish, the Moon is the most important planet" → cut it. "The Vedic Moon in Mula
confirms what the Western 8th house already suggested" → fine; the system earns its
mention by adding something specific to the claim.

**5. Earn the metaphor or cut it.**
If a metaphor is used, it must be traceable immediately to a specific placement in the
chart. "The tree grows through the stone" means nothing unless the sentence names *why
this particular chart* is the tree and what the stone specifically is. A metaphor that
floats free of placement is atmosphere, not synthesis. Cut it and state the thing plainly.

**6. Start from the intersection, not the placement.**
Every interpretive paragraph begins at the point where two coordinates meet — sign and
house, nakshatra and degree, BaZi element and Ten God — not from a single placement and
outward. "Moon in Sagittarius" is a sign. "Moon in Sagittarius in the 8th house, in
Mula Nakshatra" is the beginning of a specific observation. One coordinate produces
a horoscope column. Two or more produces a reading.

**7. Single-system claims are labeled.**
If only one tradition supports an interpretive claim, state that explicitly in the prose.
"This is only in the BaZi, so hold it as a signal rather than a certainty." Do not build
a paragraph on a single-system observation as if it were a convergence. The reader should
always know how much weight a claim is carrying and why.

| Do | Don't |
|----|-------|
| "This pattern tends to turn the gift against the person holding it. That's worth knowing." | "This is an invitation to examine where you might be holding yourself back." |
| "Multiple angles, same picture. This one isn't going away." | "Every challenge is an opportunity for growth." |
| "This is a long-running chapter. It doesn't resolve quickly. Working with it is different from waiting it out." | "Trust the process. You are exactly where you need to be." |
| "Here's what this actually asks of you: stop managing how it looks and start trusting what it is." | "This placement invites you to explore a more authentic relationship with your own authority." |
| "You've felt this. You just didn't have language for it." | "The reading reveals a striking pattern that may surprise you." |

---

## What This Voice Is Not

Not a horoscope. Not a wellness brand. Not a therapist. Not a life coach.
Not trying to flatter you. Not trying to comfort you.

Trying to be what the best version of a best friend is — someone who knows you well
enough to be honest, loves you enough to stay present while being honest, and cares
enough to point you somewhere useful when they're done.
