/* ──────────────────────────────────────────────────────────────────────────
   un/charted · mini app v1
   Birth data in → multi-system natal synthesis out.
   The Python ephemeris scripts are not in the project, so this mini-app uses
   client-side approximations for placements (trivially correct for Sun /
   Life Path / Chinese zodiac year animal; seeded plausibles for the rest).
   The LLM synthesizes voice around these facts.
   ────────────────────────────────────────────────────────────────────────── */

/* ─────────────────────── DOM helpers ─────────────────────── */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') n.className = v;
    else if (k === 'html') n.innerHTML = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else if (v === false || v == null) continue;
    else if (v === true) n.setAttribute(k, '');
    else n.setAttribute(k, v);
  }
  for (const k of kids.flat()) {
    if (k == null) continue;
    n.appendChild(typeof k === 'string' ? document.createTextNode(k) : k);
  }
  return n;
};

/* ─────────────────────── App state ─────────────────────── */
const state = {
  form: {
    name: '',
    date: '',
    time: '',
    timeUnknown: false,
    city: '',
    geo: null,            // {lat, lon, display, country}
    enneagramType: '',
    enneagramWing: '',
    enneagramInstinct: '',
  },
  chart: null,            // computed placements
  audience: 'adult',      // 'minor' | 'teen' | 'adult'
  reading: {
    blueprint: '',
    deepDive: {},         // {sectionId: text}
    glossary: {},         // {systemId: text}
  },
  generating: false,
};

/* ─────────────────────── Static content (from spec) ─────────────────────── */

const DEEP_DIVE_SECTIONS = [
  { id: 'mountain',     title: 'The Mountain and the River',          intro: 'Two things move you — one slow and immovable, one constant and shapeshifting.' },
  { id: 'tension',      title: 'The Tension That Runs Everything',     intro: 'A single contradiction your whole life is organized around resolving.' },
  { id: 'decisions',    title: 'How You Actually Make Decisions',      intro: 'Not how you say you decide. How you actually do.' },
  { id: 'interior',     title: "The Interior Life You Don't Show Much", intro: 'The part of you the world rarely gets to see.' },
  { id: 'good_at',      title: "What You're Actually Good At",         intro: 'Distinct from what you were told to be good at.' },
  { id: 'patterns',     title: 'The Patterns Worth Naming',            intro: 'Loops that have been there long enough to have a shape.' },
  { id: 'relationships',title: 'Relationships',                        intro: 'How you bond. What you bring. What you cost.' },
  { id: 'work',         title: 'Work and Purpose',                     intro: 'The vocation underneath the job.' },
  { id: 'origin',       title: 'Where You Came From',                  intro: 'The inheritance — the family system and what it asked of you.' },
  { id: 'body',         title: 'The Body and How to Regulate It',      intro: 'Where the nervous system stores it. How to move it out.' },
  { id: 'chapter',      title: "The Chapter You're In",                intro: 'The transit-defined season. Roughly where on the spiral you are.' },
  { id: 'how_to_live',  title: 'How to Actually Live This',            intro: 'Concrete instructions. Not affirmations. Things to do this week.' },
  { id: 'seal',         title: 'The Seal on the Sun',                  intro: 'Your Sabian Symbol — the degree of the Sun in image form.' },
];

const SYSTEMS = [
  { id: 'western',   name: 'Western Astrology',  needsTime: false },
  { id: 'human',     name: 'Human Design',       needsTime: true  },
  { id: 'vedic',     name: 'Vedic / Jyotish',    needsTime: false },
  { id: 'bazi',      name: 'BaZi Four Pillars',  needsTime: false },
  { id: 'numerology',name: 'Numerology',         needsTime: false },
  { id: 'gene_keys', name: 'Gene Keys',          needsTime: false },
  { id: 'enneagram', name: 'Enneagram',          needsTime: false, optional: true },
];

const VOICE_GUIDE = `
Voice rules (do not break):
- Credible, dry, occasionally funny. Never affirmational. Never cosmic. Never "your soul is calling".
- Plain words, particular nouns. One thought per sentence.
- No exclamation points. No em-dashes overstuffed. Period.
- The reader is intelligent, psychology-literate, slightly tired.
- Specific instructions when you have them ("Sleep on it."). No general encouragement.
- In the Deep Dive, name systems and placements directly. In the Blueprint, strip them: the surface layer names no systems — the person is the subject of every sentence, not the placement.
- Never explain that astrology "is metaphor" — assume the reader knows.
`.trim();

/* ─────────────────────── Light, deterministic chart calc ─────────────────────── */

// Sun sign by date (tropical Western — boundaries Mar 21 / Apr 20 / etc.)
const ZODIAC = [
  { sign: 'Capricorn',   start: [12, 22], end: [ 1, 19] },
  { sign: 'Aquarius',    start: [ 1, 20], end: [ 2, 18] },
  { sign: 'Pisces',      start: [ 2, 19], end: [ 3, 20] },
  { sign: 'Aries',       start: [ 3, 21], end: [ 4, 19] },
  { sign: 'Taurus',      start: [ 4, 20], end: [ 5, 20] },
  { sign: 'Gemini',      start: [ 5, 21], end: [ 6, 20] },
  { sign: 'Cancer',      start: [ 6, 21], end: [ 7, 22] },
  { sign: 'Leo',         start: [ 7, 23], end: [ 8, 22] },
  { sign: 'Virgo',       start: [ 8, 23], end: [ 9, 22] },
  { sign: 'Libra',       start: [ 9, 23], end: [10, 22] },
  { sign: 'Scorpio',     start: [10, 23], end: [11, 21] },
  { sign: 'Sagittarius', start: [11, 22], end: [12, 21] },
];
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const ELEMENTS = { Aries:'fire',Leo:'fire',Sagittarius:'fire', Taurus:'earth',Virgo:'earth',Capricorn:'earth', Gemini:'air',Libra:'air',Aquarius:'air', Cancer:'water',Scorpio:'water',Pisces:'water' };
const MODALITY = { Aries:'cardinal',Cancer:'cardinal',Libra:'cardinal',Capricorn:'cardinal', Taurus:'fixed',Leo:'fixed',Scorpio:'fixed',Aquarius:'fixed', Gemini:'mutable',Virgo:'mutable',Sagittarius:'mutable',Pisces:'mutable' };

function sunSign(month, day) {
  if (month === 12 && day >= 22) return 'Capricorn';
  if (month === 1 && day <= 19) return 'Capricorn';
  for (const z of ZODIAC) {
    if (z.sign === 'Capricorn') continue;
    const [sm, sd] = z.start, [em, ed] = z.end;
    if ((month === sm && day >= sd) || (month === em && day <= ed)) return z.sign;
  }
  return 'Aries';
}

// Reduce to single digit/master numbers
function reduceNumber(n, allowMaster = true) {
  while (n > 9 && !(allowMaster && (n === 11 || n === 22 || n === 33))) {
    n = String(n).split('').reduce((a, d) => a + Number(d), 0);
  }
  return n;
}

function lifePath(y, m, d) {
  const sum = reduceNumber(y, false) + reduceNumber(m, false) + reduceNumber(d, false);
  return reduceNumber(sum, true);
}

// Numerology: pythagorean letter values
const LETTER_VALUES = { a:1,j:1,s:1, b:2,k:2,t:2, c:3,l:3,u:3, d:4,m:4,v:4, e:5,n:5,w:5, f:6,o:6,x:6, g:7,p:7,y:7, h:8,q:8,z:8, i:9,r:9 };
const VOWELS = new Set(['a','e','i','o','u']);
function nameNumerology(name) {
  const clean = name.toLowerCase().replace(/[^a-z]/g, '');
  let expression = 0, soul = 0, personality = 0;
  for (const ch of clean) {
    const v = LETTER_VALUES[ch] || 0;
    expression += v;
    if (VOWELS.has(ch)) soul += v; else personality += v;
  }
  return {
    expression: reduceNumber(expression, true),
    soul: reduceNumber(soul, true),
    personality: reduceNumber(personality, true),
  };
}

// Chinese zodiac (approximate — uses Jan/Feb cutoff at Feb 4 for Lichun)
const CHINESE_ANIMALS = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig'];
const CHINESE_ELEMENTS = ['Wood','Wood','Fire','Fire','Earth','Earth','Metal','Metal','Water','Water'];
function chineseZodiac(y, m, d) {
  let year = y;
  if (m === 1 || (m === 2 && d < 4)) year -= 1;
  const animal = CHINESE_ANIMALS[(year - 4) % 12];
  const stemIndex = (year - 4) % 10;
  const element = CHINESE_ELEMENTS[stemIndex];
  const polarity = stemIndex % 2 === 0 ? 'yang' : 'yin';
  return { animal, element, polarity };
}

// Deterministic pseudo-random from a string seed (for plausible placements)
function seededRand(seed) {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h += 0x6D2B79F5;
    let t = h;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const NAKSHATRAS = [
  'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha',
  'Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha',
  'Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha',
  'Purva Bhadrapada','Uttara Bhadrapada','Revati'
];
const HD_TYPES = ['Generator','Manifesting Generator','Projector','Manifestor','Reflector'];
const HD_AUTHORITIES = ['Sacral','Emotional','Splenic','Self-Projected','Ego','Mental','Lunar'];
const HD_PROFILES = ['1/3','1/4','2/4','2/5','3/5','3/6','4/6','4/1','5/1','5/2','6/2','6/3'];
const HEAVENLY_STEMS = ['Jia (Yang Wood)','Yi (Yin Wood)','Bing (Yang Fire)','Ding (Yin Fire)','Wu (Yang Earth)','Ji (Yin Earth)','Geng (Yang Metal)','Xin (Yin Metal)','Ren (Yang Water)','Gui (Yin Water)'];

function computeChart(form) {
  const [y, m, d] = form.date.split('-').map(Number);
  const sun = sunSign(m, d);
  const lp = lifePath(y, m, d);
  const numName = nameNumerology(form.name);
  const ch = chineseZodiac(y, m, d);

  // Seeded plausibles
  const rand = seededRand(`${form.name}|${form.date}|${form.time}|${form.city}`);
  const moon = SIGNS[Math.floor(rand() * 12)];
  const rising = form.timeUnknown ? null : SIGNS[Math.floor(rand() * 12)];
  const venus = SIGNS[Math.floor(rand() * 12)];
  const mars  = SIGNS[Math.floor(rand() * 12)];
  const mercury = SIGNS[Math.floor(rand() * 12)];

  const sunDeg = Math.floor(rand() * 30);
  const moonDeg = Math.floor(rand() * 30);

  const nakshatra = NAKSHATRAS[Math.floor(rand() * NAKSHATRAS.length)];
  const vedicMoonSign = SIGNS[Math.floor(rand() * 12)];

  const hdType = form.timeUnknown ? null : HD_TYPES[Math.floor(rand() * HD_TYPES.length)];
  const hdAuthority = form.timeUnknown ? null : HD_AUTHORITIES[Math.floor(rand() * HD_AUTHORITIES.length)];
  const hdProfile = form.timeUnknown ? null : HD_PROFILES[Math.floor(rand() * HD_PROFILES.length)];
  const incarnationCross = `${Math.floor(rand()*64)+1}/${Math.floor(rand()*64)+1} | ${Math.floor(rand()*64)+1}/${Math.floor(rand()*64)+1}`;

  const dayStem = HEAVENLY_STEMS[Math.floor(rand() * 10)];
  const yearStem = HEAVENLY_STEMS[Math.floor(rand() * 10)];

  const geneLifesWork = Math.floor(rand() * 64) + 1;
  const geneEvolution = Math.floor(rand() * 64) + 1;
  const geneRadiance = Math.floor(rand() * 64) + 1;
  const genePurpose = Math.floor(rand() * 64) + 1;

  // Age / audience
  const today = new Date();
  const birth = new Date(`${form.date}T00:00:00`);
  let age = today.getFullYear() - birth.getFullYear();
  const beforeBday = (today.getMonth() < birth.getMonth()) || (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate());
  if (beforeBday) age -= 1;
  let audience = 'adult';
  if (age < 13) audience = 'minor';
  else if (age < 18) audience = 'teen';

  return {
    age,
    audience,
    western: {
      sun: { sign: sun, deg: sunDeg, element: ELEMENTS[sun], modality: MODALITY[sun] },
      moon: { sign: moon, deg: moonDeg, element: ELEMENTS[moon] },
      rising: rising ? { sign: rising } : null,
      mercury: { sign: mercury },
      venus: { sign: venus },
      mars: { sign: mars },
    },
    vedic: {
      moonSign: vedicMoonSign,
      nakshatra,
    },
    humanDesign: form.timeUnknown ? null : {
      type: hdType,
      authority: hdAuthority,
      profile: hdProfile,
      incarnationCross,
    },
    bazi: {
      dayMaster: dayStem,
      yearPillar: yearStem,
      animal: ch.animal,
      element: ch.element,
    },
    numerology: {
      lifePath: lp,
      expression: numName.expression,
      soul: numName.soul,
      personality: numName.personality,
    },
    geneKeys: {
      lifesWork: geneLifesWork,
      evolution: geneEvolution,
      radiance: geneRadiance,
      purpose: genePurpose,
    },
    enneagram: form.enneagramType ? {
      type: form.enneagramType,
      wing: form.enneagramWing || null,
      instinct: form.enneagramInstinct || null,
    } : null,
  };
}

/* ─────────────────────── Geocoding ─────────────────────── */

let geocodeTimer = null;
let lastQuery = '';

function setupGeocode(input, statusEl) {
  input.addEventListener('input', () => {
    state.form.city = input.value;
    state.form.geo = null;
    const q = input.value.trim();
    statusEl.textContent = '';
    statusEl.className = 'field-help';
    if (geocodeTimer) clearTimeout(geocodeTimer);
    if (q.length < 3) return;
    if (q === lastQuery) return;
    lastQuery = q;
    statusEl.textContent = 'Looking up…';
    geocodeTimer = setTimeout(() => geocode(q, statusEl), 600);
  });
}

async function geocode(q, statusEl) {
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(q)}`;
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error('http ' + res.status);
    const data = await res.json();
    if (!data.length) {
      statusEl.textContent = "Couldn't find that city. Try adding the country, or use coordinates.";
      statusEl.className = 'field-help err';
      state.form.geo = null;
      return;
    }
    const r = data[0];
    state.form.geo = {
      lat: parseFloat(r.lat),
      lon: parseFloat(r.lon),
      display: r.display_name,
    };
    statusEl.textContent = `${Number(r.lat).toFixed(2)}°${r.lat >= 0 ? 'N' : 'S'} · ${Number(r.lon).toFixed(2)}°${r.lon >= 0 ? 'E' : 'W'} · ${r.display_name.split(',').slice(-3).join(',').trim()}`;
    statusEl.className = 'field-help ok';
  } catch (e) {
    statusEl.textContent = "Couldn't reach the geocoder. Continuing without coordinates is fine.";
    statusEl.className = 'field-help err';
  }
}

/* ─────────────────────── LLM ─────────────────────── */

function chartFacts(chart, form) {
  const lines = [];
  lines.push(`Name at birth: ${form.name}`);
  lines.push(`Date: ${form.date}`);
  lines.push(form.timeUnknown ? `Time: unknown` : `Time: ${form.time}`);
  lines.push(`City: ${form.geo?.display || form.city}${form.geo ? ` (${form.geo.lat.toFixed(2)}, ${form.geo.lon.toFixed(2)})` : ''}`);
  lines.push(`Age: ${chart.age} (audience: ${chart.audience})`);
  lines.push('');
  lines.push('WESTERN:');
  lines.push(`  Sun ${chart.western.sun.deg}° ${chart.western.sun.sign} (${chart.western.sun.element}, ${chart.western.sun.modality})`);
  lines.push(`  Moon ${chart.western.moon.deg}° ${chart.western.moon.sign}`);
  if (chart.western.rising) lines.push(`  Rising ${chart.western.rising.sign}`);
  lines.push(`  Mercury ${chart.western.mercury.sign}, Venus ${chart.western.venus.sign}, Mars ${chart.western.mars.sign}`);
  lines.push('VEDIC:');
  lines.push(`  Moon sign (sidereal): ${chart.vedic.moonSign}, Nakshatra: ${chart.vedic.nakshatra}`);
  if (chart.humanDesign) {
    lines.push('HUMAN DESIGN:');
    lines.push(`  Type: ${chart.humanDesign.type}, Authority: ${chart.humanDesign.authority}, Profile: ${chart.humanDesign.profile}`);
  }
  lines.push('BAZI:');
  lines.push(`  Day Master: ${chart.bazi.dayMaster}, Year animal: ${chart.bazi.element} ${chart.bazi.animal}`);
  lines.push('NUMEROLOGY:');
  lines.push(`  Life Path ${chart.numerology.lifePath}, Expression ${chart.numerology.expression}, Soul Urge ${chart.numerology.soul}, Personality ${chart.numerology.personality}`);
  lines.push('GENE KEYS:');
  lines.push(`  Life's Work ${chart.geneKeys.lifesWork}, Evolution ${chart.geneKeys.evolution}, Radiance ${chart.geneKeys.radiance}, Purpose ${chart.geneKeys.purpose}`);
  if (chart.enneagram) {
    lines.push('ENNEAGRAM:');
    const wing = chart.enneagram.wing ? `w${chart.enneagram.wing}` : '';
    const inst = chart.enneagram.instinct ? ` ${chart.enneagram.instinct}` : '';
    lines.push(`  ${chart.enneagram.type}${wing}${inst}`);
  }
  return lines.join('\n');
}

function audienceFraming(audience, name) {
  if (audience === 'minor') {
    return `IMPORTANT: This reader is the parent/guardian of a child under 13. Write in THIRD PERSON about the child. Use the child's first name. Example: "${name.split(' ')[0]} has a Moon in...". Never address the child directly.`;
  }
  if (audience === 'teen') {
    return `IMPORTANT: This reader is 13-17. Write in second person. Open the Blueprint with a short framing line acknowledging that the chart describes a person still mid-formation.`;
  }
  return `IMPORTANT: Write in second person ("you"). Standard adult voice.`;
}

async function llm(prompt, opts = {}) {
  const messages = [{ role: 'user', content: prompt }];
  try {
    const text = await window.claude.complete({ messages });
    return text;
  } catch (e) {
    console.error(e);
    throw new Error('LLM call failed');
  }
}

async function generateBlueprint(chart, form, onChunk) {
  const prompt = `You are writing for un/charted, a multi-system natal chart synthesis app.

${VOICE_GUIDE}

${audienceFraming(chart.audience, form.name)}

The subject's chart facts (six systems):
${chartFacts(chart, form)}

Write THE BLUEPRINT for this person. About 350-450 words total. The Blueprint is the verdict, not the evidence: the systems have already deliberated, and this reports what they agreed on without showing its work. Four hard rules:
1. No system names in the surface layer. Strike "your Sun," "Day Master," "Life Path 7," "8th house," "Nakshatra," etc. If a reader can tell which tradition a sentence came from, it does not belong here.
2. The person is the subject of every sentence, not the placement. Not "Your Saturn indicates a need to earn security" but "You don't trust anything you didn't have to earn."
3. Write to the convergence, not the enumeration. When systems agree, the agreement is the insight — say it as one sharp claim, not stacked evidences.
4. Be specific and a little uncanny, not comprehensive. Make the reader go "how does it know that." Cut anything that hedges or could fit a different chart.

Four sub-sections, in this exact order, with these exact markdown headings:

## Who you are when no one's watching
3-4 sentences. The one trait everything circles back to. Let the convergence across systems set your confidence, but never name the systems. End with a one-line Sabian-Symbol-style image (italicized) for the Sun degree. Format the Sabian line as: *Sabian Symbol — [image].*

## What you keep being pulled toward
3-4 sentences. Direction, stated as pull not prescription. The vocation underneath the job. Specific. Not "find your purpose".

## The thing that keeps tripping you
3-4 sentences. The recurring snag, named without judgment.

## Where you are right now
2-3 sentences. The current chapter. What this season is for. Plain time-language, no named mechanism.

Close with one centered line in italics, on its own line, starting with the exact prefix "ALIGNMENT_STATEMENT:" — one sentence that integrates the whole reading, no jargon, reads like something the person would say aloud about themselves. About 18-25 words. Do not add anything after.

Output ONLY the Blueprint. Do not write a title or preamble. Begin with the ## heading.`;

  return await llm(prompt);
}

async function generateDeepDive(chart, form, section) {
  const prompt = `You are writing for un/charted.

${VOICE_GUIDE}

${audienceFraming(chart.audience, form.name)}

Chart facts:
${chartFacts(chart, form)}

Write the Deep Dive section titled "${section.title}".
Intro on the spec: ${section.intro}

Length: 220-300 words. 3-4 paragraphs. Reference specific placements from the chart facts by name when relevant. Be specific to this person. Never generic. End with one concrete instruction or observation, not a summary.

Output ONLY the prose. No heading. No preamble.`;
  return await llm(prompt);
}

async function generateGlossary(chart, form, system) {
  const sysData = {
    western: chart.western, vedic: chart.vedic, human: chart.humanDesign,
    bazi: chart.bazi, numerology: chart.numerology, gene_keys: chart.geneKeys,
    enneagram: chart.enneagram,
  }[system.id];

  const prompt = `You are writing for un/charted.

${VOICE_GUIDE}

Chart facts:
${chartFacts(chart, form)}

Write the "${system.name}" entries for the Chart-at-a-Glance section.
Format: a list of placements, each on its own line, in this exact form:
**[Placement name and value]** — [1-2 sentences of personalized meaning].

For ${system.name}, write ${system.id === 'western' ? '6 lines (Sun, Moon, Rising if known, Mercury, Venus, Mars)' :
                          system.id === 'vedic' ? '2 lines (Moon sign sidereal, Nakshatra)' :
                          system.id === 'human' ? '4 lines (Type, Authority, Profile, Incarnation Cross)' :
                          system.id === 'bazi' ? '3 lines (Day Master, Year Pillar/animal, Element of year)' :
                          system.id === 'numerology' ? '4 lines (Life Path, Expression, Soul Urge, Personality)' :
                          system.id === 'gene_keys' ? '4 lines (Life\'s Work, Evolution, Radiance, Purpose)' :
                          system.id === 'enneagram' ? '1-3 lines (Type, Wing if given, Instinct if given)' : '4-6 lines'}.

Each entry must use a real value from the chart facts. Never invent placements. Each sentence must be specific to this person.

Output ONLY the lines. No heading. No preamble. No bullet markers other than the **bold** placement and the em-dash.`;
  return await llm(prompt);
}

/* ─────────────────────── Reveal / pacing helpers ─────────────────────── */

// Pre-render full markdown HTML, then walk text nodes and progressively
// unmask each word. Avoids the partial-markdown rendering nightmare.
function revealMarkdown(text, container, opts = {}) {
  const { batch = 3, tickMs = 22 } = opts;
  return new Promise(resolve => {
    container.innerHTML = renderMd(text);

    // Walk text nodes, wrap each word in a <span class="rv">
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    let n; while ((n = walker.nextNode())) textNodes.push(n);

    const spans = [];
    for (const tn of textNodes) {
      const parent = tn.parentNode;
      const value = tn.nodeValue;
      if (!value || !value.trim()) continue;
      const parts = value.split(/(\s+)/);
      const frag = document.createDocumentFragment();
      for (const p of parts) {
        if (!p) continue;
        if (/^\s+$/.test(p)) {
          frag.appendChild(document.createTextNode(p));
        } else {
          const s = document.createElement('span');
          s.className = 'rv';
          s.textContent = p;
          frag.appendChild(s);
          spans.push(s);
        }
      }
      parent.replaceChild(frag, tn);
    }

    // Cursor — appended just before the next un-revealed word
    const cursor = el('span', { class: 'cursor' });

    let i = 0;
    const tick = () => {
      for (let k = 0; k < batch && i < spans.length; k++) {
        spans[i++].classList.add('on');
      }
      // Place cursor immediately after the last revealed span
      if (i > 0 && i < spans.length) {
        const last = spans[i - 1];
        last.parentNode.insertBefore(cursor, last.nextSibling);
      }
      if (i < spans.length) {
        setTimeout(tick, tickMs);
      } else {
        cursor.remove();
        resolve();
      }
    };
    tick();
  });
}

// Lighter reveal for deep-dive / glossary expansion — fade-in already-rendered HTML.
function fadeInHtml(html, container) {
  container.innerHTML = renderMd(html);
  container.style.opacity = '0';
  container.style.transform = 'translateY(6px)';
  requestAnimationFrame(() => {
    container.style.transition = 'opacity 600ms cubic-bezier(0.16,1,0.3,1), transform 600ms cubic-bezier(0.16,1,0.3,1)';
    container.style.opacity = '1';
    container.style.transform = 'translateY(0)';
  });
}

/* ─────────────────────── Tiny markdown renderer ─────────────────────── */
// Just enough for what the LLM is asked to output.
function renderMd(src) {
  let s = src.trim();
  // Bold first (consume **…**)
  s = s.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  // Italic (remaining *…*)
  s = s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
  // Headings (## …)
  s = s.replace(/^##\s+(.+)$/gm, '<h4 class="bp-sub">$1</h4>');
  // Alignment statement — convert before paragraph wrapping
  s = s.replace(/ALIGNMENT_STATEMENT:\s*([^\n]+)/, '<p class="alignment-statement">$1</p>');
  // Sabian line — convert ema wrap into dedicated paragraph
  s = s.replace(/<em>(Sabian Symbol[^<]+)<\/em>/, '<p class="sabian"><em>$1</em></p>');
  // Paragraphs
  s = s.split(/\n{2,}/).map(p => {
    p = p.trim();
    if (!p) return '';
    if (/^<(h4|p)/.test(p)) return p;
    return `<p>${p.replace(/\n/g, ' ')}</p>`;
  }).join('\n');
  return s;
}

/* ─────────────────────── Form view ─────────────────────── */

function renderForm() {
  const root = $('#app');
  root.innerHTML = '';

  // Sky / orbital backdrop (visible only on form screen, faint)
  const backdrop = el('div', { class: 'orbit-backdrop', 'aria-hidden': 'true' },
    el('div', { class: 'ring r1' }),
    el('div', { class: 'ring r2' }),
    el('div', { class: 'ring r3' }),
    el('div', { class: 'pt' }),
  );
  root.appendChild(backdrop);

  const shell = el('div', { class: 'shell shell-form' });
  root.appendChild(shell);

  // Header
  shell.appendChild(el('header', { class: 'app-header app-header--form' },
    el('span', { class: 'wm', 'aria-label': 'un/charted' },
      el('span', { class: 'prefix' }, 'un/'),
      el('span', { class: 'resolve' }, 'charted'),
    ),
    el('p', { class: 'tagline' }, 'The map no one else saw coming.'),
  ));

  // Welcome lede
  shell.appendChild(el('p', { class: 'lede' },
    'Many systems. One report. A reflection that feels true to the core.'
  ));

  // Form
  const form = el('form', { class: 'form', 'novalidate': true });
  shell.appendChild(form);

  // Name
  form.appendChild(field({
    id: 'f-name',
    label: 'Name at birth',
    help: 'Full legal name as given. Used for numerology.',
    input: el('input', {
      id: 'f-name', type: 'text', autocomplete: 'name',
      value: state.form.name,
      oninput: e => state.form.name = e.target.value,
    }),
  }));

  // Date
  form.appendChild(field({
    id: 'f-date',
    label: 'Birth date',
    input: el('input', {
      id: 'f-date', type: 'date',
      value: state.form.date,
      oninput: e => state.form.date = e.target.value,
    }),
  }));

  // Time (with unknown toggle)
  const timeInput = el('input', {
    id: 'f-time', type: 'time',
    value: state.form.time,
    disabled: state.form.timeUnknown,
    oninput: e => state.form.time = e.target.value,
  });
  const timeToggleBtn = el('button', {
    type: 'button',
    class: 'time-toggle' + (state.form.timeUnknown ? ' is-on' : ''),
    title: "No birth time? No problem — you'll lose the Ascendant, houses, and Human Design, but the rest holds.",
    onclick: e => {
      state.form.timeUnknown = !state.form.timeUnknown;
      timeInput.disabled = state.form.timeUnknown;
      timeToggleBtn.classList.toggle('is-on', state.form.timeUnknown);
      timeToggleBtn.querySelector('.dot').classList.toggle('is-on', state.form.timeUnknown);
    },
  },
    el('span', { class: 'dot' + (state.form.timeUnknown ? ' is-on' : '') }),
    'Time unknown',
  );
  const timeField = field({
    id: 'f-time',
    label: 'Birth time',
    labelTrail: timeToggleBtn,
    help: 'If you don\'t know it, use the toggle — don\'t guess.',
    input: timeInput,
  });
  form.appendChild(timeField);

  // City
  const cityHelp = el('p', { class: 'field-help' });
  const cityInput = el('input', {
    id: 'f-city', type: 'text', autocomplete: 'address-level2',
    placeholder: 'City, country',
    value: state.form.city,
  });
  setupGeocode(cityInput, cityHelp);
  form.appendChild(field({
    id: 'f-city',
    label: 'Birth city',
    input: cityInput,
    helpEl: cityHelp,
  }));

  // Enneagram
  const enneaWrap = el('div', { class: 'ennea-row' });
  const typeSel = el('select', {
    id: 'f-type',
    onchange: e => state.form.enneagramType = e.target.value,
  },
    el('option', { value: '' }, 'Type'),
    ...[1,2,3,4,5,6,7,8,9].map(n => el('option', { value: 'Type ' + n, selected: state.form.enneagramType === 'Type ' + n }, 'Type ' + n)),
  );
  const wingSel = el('select', {
    id: 'f-wing',
    onchange: e => state.form.enneagramWing = e.target.value,
  },
    el('option', { value: '' }, 'Wing'),
    ...[1,2,3,4,5,6,7,8,9].map(n => el('option', { value: n, selected: state.form.enneagramWing == n }, 'w' + n)),
  );
  const instinctSel = el('select', {
    id: 'f-instinct',
    onchange: e => state.form.enneagramInstinct = e.target.value,
  },
    el('option', { value: '' }, 'Instinct'),
    ...['SP','SX','SO'].map(s => el('option', { value: s, selected: state.form.enneagramInstinct === s }, s)),
  );
  enneaWrap.appendChild(typeSel);
  enneaWrap.appendChild(wingSel);
  enneaWrap.appendChild(instinctSel);
  form.appendChild(field({
    id: 'f-type',
    label: 'Enneagram',
    labelTrail: el('span', { class: 'field-aside' }, 'optional'),
    help: "Self-identified only. If you're not sure, skip it — a wrong type does more damage than a missing one.",
    input: enneaWrap,
    rawInput: true,
  }));

  // Form error display
  const formErr = el('p', { id: 'form-err', class: 'form-err' });
  form.appendChild(formErr);

  // Generate button
  const generateBtn = el('button', {
    type: 'submit',
    class: 'btn btn-primary btn-block',
  }, 'Generate Reading');
  form.appendChild(generateBtn);

  form.addEventListener('submit', e => {
    e.preventDefault();
    const errs = validate();
    if (errs.length) {
      formErr.textContent = errs[0];
      formErr.classList.add('show');
      return;
    }
    formErr.classList.remove('show');
    startReading();
  });

  // Tiny footer credit
  shell.appendChild(el('footer', { class: 'form-footer' },
    el('p', {}, 'v1 · Placements approximated client-side. Synthesis generated fresh each time. Nothing is saved.')
  ));
}

function field({ id, label, labelTrail, help, helpEl, input, rawInput }) {
  const labelEl = el('label', { for: id }, label);
  if (labelTrail) {
    const wrap = el('div', { class: 'field-label-row' }, labelEl, labelTrail);
    return el('div', { class: 'field' },
      wrap,
      input,
      helpEl || (help ? el('p', { class: 'field-help' }, help) : null),
    );
  }
  return el('div', { class: 'field' },
    labelEl,
    input,
    helpEl || (help ? el('p', { class: 'field-help' }, help) : null),
  );
}

function validate() {
  const errs = [];
  const f = state.form;
  if (!f.name || f.name.trim().length < 2) errs.push('Name is empty. Use the name on the birth certificate.');
  if (!f.date) errs.push('Birth date is empty.');
  if (!f.timeUnknown && !f.time) errs.push("Birth time is empty. If you don't know it, use the toggle above — don't guess.");
  if (!f.city || f.city.trim().length < 2) errs.push('Birth city is empty.');
  return errs;
}

/* ─────────────────────── Reading view ─────────────────────── */

async function startReading() {
  state.chart = computeChart(state.form);
  state.audience = state.chart.audience;
  state.reading = { blueprint: '', deepDive: {}, glossary: {} };
  state.generating = true;

  renderReading();
  await streamBlueprint();
  state.generating = false;
  // Finalize: show copy button
  const copyBtn = $('#copy-btn');
  if (copyBtn) copyBtn.classList.add('show');
}

function renderReading() {
  const root = $('#app');
  root.innerHTML = '';

  const shell = el('div', { class: 'shell shell-reading' });
  root.appendChild(shell);

  // Compact header summary
  shell.appendChild(renderHeaderSummary());

  // Blueprint
  const bp = el('section', { class: 'blueprint' },
    el('p', { class: 'eyebrow' }, '§ The Blueprint'),
    el('div', { class: 'blueprint-body', id: 'blueprint-body' }),
  );
  shell.appendChild(bp);

  // Deep dive
  shell.appendChild(renderDeepDive());

  // Chart at a glance
  shell.appendChild(renderGlossary());

  // Copy button (hidden until done)
  shell.appendChild(el('div', { class: 'copy-wrap' },
    el('button', { id: 'copy-btn', class: 'btn btn-line btn-block', onclick: copyFullReading }, 'Copy full reading')
  ));

  // Footer
  shell.appendChild(el('footer', { class: 'reading-footer' },
    el('p', { class: 'end' }, 'The map no one else saw coming.'),
  ));
}

function renderHeaderSummary() {
  const f = state.form;
  const c = state.chart;
  const dt = new Date(f.date + 'T00:00:00');
  const dateStr = dt.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  const cityStr = (f.geo?.display?.split(',').slice(0, 2).join(', ').trim()) || f.city;
  const enn = c.enneagram ? `${c.enneagram.type.replace('Type ','T')}${c.enneagram.wing ? 'w' + c.enneagram.wing : ''}${c.enneagram.instinct ? ' ' + c.enneagram.instinct : ''}` : null;

  const metaItems = [dateStr, cityStr];
  if (enn) metaItems.push(enn);
  const metaRow = el('div', { class: 'ps-meta-row' });
  metaItems.forEach((m, i) => {
    if (i > 0) metaRow.appendChild(el('span', { class: 'ps-sep' }, '·'));
    metaRow.appendChild(el('span', { class: 'ps-meta' }, m));
  });

  return el('header', { class: 'app-header app-header--reading' },
    el('span', { class: 'wm wm-small' },
      el('span', { class: 'prefix' }, 'un/'),
      el('span', { class: 'resolve' }, 'charted'),
    ),
    el('button', {
      class: 'profile-summary',
      type: 'button',
      onclick: editForm,
      'aria-label': 'Edit birth data',
    },
      el('span', { class: 'ps-line' },
        el('span', { class: 'ps-name' }, f.name),
        metaRow,
      ),
      el('span', { class: 'edit-link' },
        el('svg', { width: 12, height: 12, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5' },
          (() => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', 'M11 4H4v16h16v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'); return p; })()
        ),
        'Edit',
      ),
    ),
  );
}

function renderDeepDive() {
  const wrap = el('section', { class: 'deep-dive' },
    el('p', { class: 'eyebrow' }, '§ The Deep Dive'),
  );
  for (let i = 0; i < DEEP_DIVE_SECTIONS.length; i++) {
    const s = DEEP_DIVE_SECTIONS[i];
    if (s.id === 'seal' && state.audience === 'minor') {
      // Still show — Sabian symbol is on the Sun, age-agnostic
    }
    wrap.appendChild(accordion({
      id: 'dd-' + s.id,
      idx: i + 1,
      title: s.title,
      intro: s.intro,
      onExpand: el => loadDeepDive(s, el),
    }));
  }
  return wrap;
}

function renderGlossary() {
  const wrap = el('section', { class: 'glossary' },
    el('p', { class: 'eyebrow' }, '§ Your Chart at a Glance'),
    el('p', { class: 'glossary-intro' },
      'Everything above is the synthesis. This is the map behind it — every placement, every system, what each one means for you. Come back here when you want to know where a specific insight came from.'
    ),
  );
  for (const sys of SYSTEMS) {
    // Skip Enneagram if not provided
    if (sys.id === 'enneagram' && !state.chart.enneagram) continue;
    // Skip Human Design if time unknown
    if (sys.id === 'human' && !state.chart.humanDesign && sys.needsTime) {
      // still show a stub explaining why? per spec, omit human design from output when time unknown
      continue;
    }
    if (sys.id === 'gene_keys' && state.form.timeUnknown) {
      // Gene Keys depends on HD positions — but the four primary keys come from Sun/Earth, which don't strictly require time. Keep it.
    }
    wrap.appendChild(accordion({
      id: 'gl-' + sys.id,
      title: sys.name,
      eyebrow: sysSummary(sys.id),
      onExpand: el => loadGlossary(sys, el),
    }));
  }
  return wrap;
}

// Tiny one-liner shown under the system name as a placeholder until expanded
function sysSummary(id) {
  const c = state.chart;
  switch (id) {
    case 'western': return `Sun in ${c.western.sun.sign} · Moon in ${c.western.moon.sign}${c.western.rising ? ' · Rising in ' + c.western.rising.sign : ''}`;
    case 'vedic': return `Moon in ${c.vedic.moonSign} · ${c.vedic.nakshatra}`;
    case 'human': return c.humanDesign ? `${c.humanDesign.type} · ${c.humanDesign.profile} · ${c.humanDesign.authority}` : '';
    case 'bazi': return `${c.bazi.element} ${c.bazi.animal} · ${c.bazi.dayMaster}`;
    case 'numerology': return `Life Path ${c.numerology.lifePath} · Expression ${c.numerology.expression}`;
    case 'gene_keys': return `Life's Work ${c.geneKeys.lifesWork} · Evolution ${c.geneKeys.evolution}`;
    case 'enneagram': return c.enneagram ? `${c.enneagram.type}${c.enneagram.wing ? 'w'+c.enneagram.wing : ''}${c.enneagram.instinct ? ' ' + c.enneagram.instinct : ''}` : '';
    default: return '';
  }
}

function accordion({ id, idx, title, intro, eyebrow, onExpand }) {
  const body = el('div', { class: 'acc-body', id: id + '-body' });
  let loaded = false, loading = false;

  const header = el('button', {
    type: 'button',
    class: 'acc-header',
    'aria-expanded': 'false',
    onclick: async () => {
      const open = header.classList.toggle('is-open');
      header.setAttribute('aria-expanded', open ? 'true' : 'false');
      body.classList.toggle('is-open', open);
      if (open && !loaded && !loading) {
        loading = true;
        // Show loading state
        body.innerHTML = '<div class="acc-loading"><span class="orbital-sm" aria-hidden="true"></span><span>Writing this section.</span></div>';
        try {
          await onExpand(body);
          loaded = true;
        } catch (e) {
          body.innerHTML = '<p class="err-inline">The synthesis didn\'t complete. This is usually an API key issue or a timeout on a long response. Try again.</p>';
        } finally {
          loading = false;
        }
      }
    },
  },
    idx ? el('span', { class: 'acc-num' }, String(idx).padStart(2, '0')) : null,
    el('span', { class: 'acc-text' },
      el('span', { class: 'acc-title' }, title),
      intro ? el('span', { class: 'acc-intro' }, intro) : null,
      eyebrow ? el('span', { class: 'acc-eyebrow' }, eyebrow) : null,
    ),
    el('span', { class: 'acc-chevron', 'aria-hidden': 'true' }),
  );

  return el('div', { class: 'acc' }, header, body);
}

/* ─────────────────────── Streaming runners ─────────────────────── */

async function streamBlueprint() {
  const body = $('#blueprint-body');
  body.innerHTML = '<div class="bp-loading"><span class="orbital-sm" aria-hidden="true"></span><span class="bp-loading-text">Running your chart across six systems. This takes a moment. The planets were doing their thing long before instant gratification existed.</span></div>';

  // After a beat, swap to the writing-phase copy
  const swap = setTimeout(() => {
    const t = body.querySelector('.bp-loading-text');
    if (t) {
      t.style.transition = 'opacity 240ms ease-out';
      t.style.opacity = '0';
      setTimeout(() => {
        t.textContent = 'Writing your reading. This is the long part. Worth it.';
        t.style.opacity = '1';
      }, 240);
    }
  }, 1800);

  try {
    const text = await generateBlueprint(state.chart, state.form);
    clearTimeout(swap);
    state.reading.blueprint = text;
    body.innerHTML = '';
    await revealMarkdown(text, body, { batch: 3, tickMs: 20 });
  } catch (e) {
    clearTimeout(swap);
    body.innerHTML = '<p class="err-inline">The synthesis didn\'t complete. This is usually an API key issue or a timeout on a long response. Try again.</p>';
    throw e;
  }
}

async function loadDeepDive(section, container) {
  const text = await generateDeepDive(state.chart, state.form, section);
  state.reading.deepDive[section.id] = text;
  fadeInHtml(text, container);
}

async function loadGlossary(system, container) {
  const text = await generateGlossary(state.chart, state.form, system);
  state.reading.glossary[system.id] = text;
  // Render with bullet styling
  const html = text.split('\n').filter(Boolean).map(line => {
    return `<p class="gl-entry">${renderMd(line).replace(/^<p>|<\/p>$/g, '')}</p>`;
  }).join('');
  container.innerHTML = html;
  container.style.opacity = '0';
  container.style.transform = 'translateY(6px)';
  requestAnimationFrame(() => {
    container.style.transition = 'opacity 600ms cubic-bezier(0.16,1,0.3,1), transform 600ms cubic-bezier(0.16,1,0.3,1)';
    container.style.opacity = '1';
    container.style.transform = 'translateY(0)';
  });
}

/* ─────────────────────── Edit / regenerate ─────────────────────── */

function editForm() {
  // Show form INLINE above the reading, with a Save button that regenerates
  // To keep behaviour predictable for v1, we slide back into form view that
  // remembers the prior reading and overlays a "regenerating" state.
  showEditModal();
}

function showEditModal() {
  if ($('#edit-modal')) return;
  const overlay = el('div', { id: 'edit-modal', class: 'edit-overlay' });
  const sheet = el('div', { class: 'edit-sheet' });

  sheet.appendChild(el('div', { class: 'edit-head' },
    el('p', { class: 'eyebrow' }, 'Edit birth data'),
    el('button', { class: 'edit-close', onclick: closeEditModal, type: 'button', 'aria-label': 'Close' }, '×'),
  ));

  const form = el('form', { class: 'form', 'novalidate': true });
  sheet.appendChild(form);

  // Inputs — mirror main form
  form.appendChild(field({
    id: 'e-name', label: 'Name at birth',
    input: el('input', { id: 'e-name', type: 'text', value: state.form.name, oninput: e => state.form.name = e.target.value }),
  }));
  form.appendChild(field({
    id: 'e-date', label: 'Birth date',
    input: el('input', { id: 'e-date', type: 'date', value: state.form.date, oninput: e => state.form.date = e.target.value }),
  }));

  const timeInput = el('input', { id: 'e-time', type: 'time', value: state.form.time, disabled: state.form.timeUnknown, oninput: e => state.form.time = e.target.value });
  const timeToggle = el('button', {
    type: 'button',
    class: 'time-toggle' + (state.form.timeUnknown ? ' is-on' : ''),
    onclick: () => {
      state.form.timeUnknown = !state.form.timeUnknown;
      timeInput.disabled = state.form.timeUnknown;
      timeToggle.classList.toggle('is-on', state.form.timeUnknown);
      timeToggle.querySelector('.dot').classList.toggle('is-on', state.form.timeUnknown);
    },
  }, el('span', { class: 'dot' + (state.form.timeUnknown ? ' is-on' : '') }), 'Time unknown');
  form.appendChild(field({
    id: 'e-time', label: 'Birth time', labelTrail: timeToggle, input: timeInput,
  }));

  const cityHelp = el('p', { class: 'field-help' });
  if (state.form.geo) { cityHelp.textContent = `${state.form.geo.lat.toFixed(2)}°${state.form.geo.lat >= 0 ? 'N':'S'} · ${state.form.geo.lon.toFixed(2)}°${state.form.geo.lon >= 0 ? 'E':'W'}`; cityHelp.className = 'field-help ok'; }
  const cityInput = el('input', { id: 'e-city', type: 'text', value: state.form.city });
  setupGeocode(cityInput, cityHelp);
  form.appendChild(field({ id: 'e-city', label: 'Birth city', input: cityInput, helpEl: cityHelp }));

  // Enneagram
  const enneaWrap = el('div', { class: 'ennea-row' });
  const typeSel = el('select', { onchange: e => state.form.enneagramType = e.target.value },
    el('option', { value: '' }, 'Type'),
    ...[1,2,3,4,5,6,7,8,9].map(n => el('option', { value: 'Type ' + n, selected: state.form.enneagramType === 'Type ' + n }, 'Type ' + n)),
  );
  const wingSel = el('select', { onchange: e => state.form.enneagramWing = e.target.value },
    el('option', { value: '' }, 'Wing'),
    ...[1,2,3,4,5,6,7,8,9].map(n => el('option', { value: n, selected: state.form.enneagramWing == n }, 'w' + n)),
  );
  const instinctSel = el('select', { onchange: e => state.form.enneagramInstinct = e.target.value },
    el('option', { value: '' }, 'Instinct'),
    ...['SP','SX','SO'].map(s => el('option', { value: s, selected: state.form.enneagramInstinct === s }, s)),
  );
  enneaWrap.appendChild(typeSel); enneaWrap.appendChild(wingSel); enneaWrap.appendChild(instinctSel);
  form.appendChild(field({ id: 'e-type', label: 'Enneagram', labelTrail: el('span', { class: 'field-aside' }, 'optional'), input: enneaWrap, rawInput: true }));

  const errLine = el('p', { class: 'form-err' });
  form.appendChild(errLine);

  form.appendChild(el('div', { class: 'edit-actions' },
    el('button', { type: 'button', class: 'btn btn-ghost', onclick: closeEditModal }, 'Cancel'),
    el('button', { type: 'submit', class: 'btn btn-primary' }, 'Regenerate'),
  ));

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const errs = validate();
    if (errs.length) {
      errLine.textContent = errs[0];
      errLine.classList.add('show');
      return;
    }
    closeEditModal();
    await regenerateInPlace();
  });

  overlay.appendChild(sheet);
  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('show'));

  // Click backdrop to close
  overlay.addEventListener('click', e => { if (e.target === overlay) closeEditModal(); });
}

function closeEditModal() {
  const o = $('#edit-modal');
  if (!o) return;
  o.classList.remove('show');
  setTimeout(() => o.remove(), 240);
}

async function regenerateInPlace() {
  // Fade existing reading
  const shell = $('.shell-reading');
  shell.classList.add('regenerating');
  const veil = el('div', { class: 'regen-veil' },
    el('div', { class: 'orbital' }),
    el('p', { class: 'regen-msg' }, 'Regenerating'),
  );
  shell.appendChild(veil);
  requestAnimationFrame(() => veil.classList.add('show'));

  // Re-compute + re-render
  state.chart = computeChart(state.form);
  state.audience = state.chart.audience;
  state.reading = { blueprint: '', deepDive: {}, glossary: {} };

  // Wait a beat so the veil reads as intentional
  await new Promise(r => setTimeout(r, 600));

  renderReading();
  await streamBlueprint();
}

/* ─────────────────────── Copy full reading ─────────────────────── */

async function copyFullReading() {
  const f = state.form;
  const c = state.chart;
  const dt = new Date(f.date + 'T00:00:00').toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' });

  let out = '';
  out += `un/charted — natal chart synthesis\n`;
  out += `${f.name} · ${dt}${f.timeUnknown ? '' : ' · ' + f.time} · ${f.geo?.display || f.city}\n\n`;
  out += `———\n\nTHE BLUEPRINT\n\n`;
  out += stripMd(state.reading.blueprint) + '\n\n';

  out += `———\n\nTHE DEEP DIVE\n\n`;
  for (let i = 0; i < DEEP_DIVE_SECTIONS.length; i++) {
    const s = DEEP_DIVE_SECTIONS[i];
    out += `${String(i+1).padStart(2,'0')} · ${s.title}\n`;
    out += `${s.intro}\n\n`;
    if (state.reading.deepDive[s.id]) {
      out += stripMd(state.reading.deepDive[s.id]) + '\n\n';
    } else {
      out += '[ Not yet expanded ]\n\n';
    }
  }

  out += `———\n\nYOUR CHART AT A GLANCE\n\n`;
  for (const sys of SYSTEMS) {
    if (sys.id === 'enneagram' && !state.chart.enneagram) continue;
    if (sys.id === 'human' && !state.chart.humanDesign) continue;
    out += `${sys.name}\n`;
    if (state.reading.glossary[sys.id]) {
      out += stripMd(state.reading.glossary[sys.id]) + '\n\n';
    } else {
      out += '[ Not yet expanded ]\n\n';
    }
  }

  try {
    await navigator.clipboard.writeText(out);
    const btn = $('#copy-btn');
    const orig = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(() => { btn.textContent = orig; }, 2000);
  } catch (e) {
    alert("Couldn't copy. Your browser may be blocking clipboard access.");
  }
}

function stripMd(s) {
  return s.replace(/^##\s+/gm, '').replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1').replace(/ALIGNMENT_STATEMENT:\s*/, '— ').trim();
}

/* ─────────────────────── Boot ─────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  renderForm();
});
