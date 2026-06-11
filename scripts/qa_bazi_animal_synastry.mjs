// QA harness for the cross-chart BaZi Earthly-Branch (Chinese zodiac animal) synastry
// contributors. Extracts the REAL code from app.html, evals it, and cross-checks every
// one of the 144 animal pairings — for BOTH the Year-animal and Day-branch (Spouse
// Palace) layers — against an independent reimplementation of the branch tables in
// scripts/calculate_bazi.py. Run: node scripts/qa_bazi_animal_synastry.mjs
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../app.html', import.meta.url), 'utf8');

function extract(re, label) {
  const m = html.match(re);
  if (!m) throw new Error(`QA setup failure: could not find ${label} in app.html`);
  return m[0];
}

// Pull the actual definitions out of the shipped file so we test the real code.
const pieces = [
  extract(/const BAZI_ANIMALS\s*=\s*\[[^\]]*\];/, 'BAZI_ANIMALS'),
  extract(/const BAZI_SIX_COMBINATIONS\s*=\s*\[[\s\S]*?\];/, 'BAZI_SIX_COMBINATIONS'),
  extract(/const BAZI_THREE_HARMONY\s*=\s*\[[\s\S]*?\];/, 'BAZI_THREE_HARMONY'),
  extract(/function baziBranchPairing\(a, b\)\{[\s\S]*?\n\}/, 'baziBranchPairing'),
  extract(/function baziAnimalInteraction\(chartA, chartB\)\{[\s\S]*?\n\}/, 'baziAnimalInteraction'),
  extract(/function baziDayAnimalInteraction\(chartA, chartB\)\{[\s\S]*?\n\}/, 'baziDayAnimalInteraction'),
];

const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(`${pieces.join('\n')}\nthis.yearFn = baziAnimalInteraction; this.dayFn = baziDayAnimalInteraction; this.ANIMALS = BAZI_ANIMALS;`, sandbox);
const { yearFn, dayFn, ANIMALS } = sandbox;

// ── Independent reimplementation of calculate_bazi.py branch tables (source of truth) ──
const IDX = { Rat:0, Ox:1, Tiger:2, Rabbit:3, Dragon:4, Snake:5, Horse:6, Goat:7, Monkey:8, Rooster:9, Dog:10, Pig:11 };
const PY_SIX = [['Rat','Ox'],['Tiger','Pig'],['Rabbit','Dog'],['Dragon','Rooster'],['Snake','Monkey'],['Horse','Goat']].map(p => p.map(x=>IDX[x]));
const PY_TRINE = [['Monkey','Rat','Dragon'],['Pig','Rabbit','Goat'],['Tiger','Horse','Dog'],['Snake','Rooster','Ox']].map(g => g.map(x=>IDX[x]));

function expectedCategory(a, b) {
  if (a === b) return 'RESONANCE';
  if ((a + 6) % 12 === b) return 'CLASH';
  if (PY_SIX.some(([x,y]) => (x===a&&y===b)||(x===b&&y===a))) return 'SIX-COMBINATION';
  if (PY_TRINE.some(g => g.includes(a) && g.includes(b))) return 'THREE-HARMONY';
  return 'NONE';
}
function actualCategory(res) {
  const h = res && res.hints && res.hints[0];
  if (!h) return 'NONE';
  for (const c of ['RESONANCE','CLASH','SIX-COMBINATION','THREE-HARMONY']) if (h.includes(c)) return c;
  return 'UNKNOWN';
}

let pass = 0, fail = 0;
const failures = [];
const ok = (cond, msg) => { if (cond) pass++; else { fail++; failures.push(msg); } };

// Each layer: its chart-field, the hint prefix that proves the right framing fired, and
// the fact-line marker that proves the right receipt fired.
const LAYERS = [
  { name: 'Year',  fn: yearFn, field: 'animal',    prefix: 'ANIMAL',       factMark: 'Year animals' },
  { name: 'Day',   fn: dayFn,  field: 'dayAnimal', prefix: 'PARTNER-SEAT', factMark: 'Day-branch animals' },
];
const mk = (field, animal) => ({ bazi: { [field]: animal } });

for (const L of LAYERS) {
  const counts = { RESONANCE:0, CLASH:0, 'SIX-COMBINATION':0, 'THREE-HARMONY':0, NONE:0 };

  // 1) Exhaustive 12×12: category matches the Python-derived truth table.
  for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
    const res = L.fn(mk(L.field, ANIMALS[a]), mk(L.field, ANIMALS[b]));
    const exp = expectedCategory(a, b);
    const act = actualCategory(res);
    ok(exp === act, `[${L.name}] pair (${ANIMALS[a]}, ${ANIMALS[b]}): expected ${exp}, got ${act}`);
    counts[act]++;
    // Fact line must always name both animals and carry this layer's marker.
    const fact = res && res.facts && res.facts[0];
    ok(fact && fact.includes(ANIMALS[a]) && fact.includes(ANIMALS[b]) && fact.includes(L.factMark),
       `[${L.name}] pair (${ANIMALS[a]}, ${ANIMALS[b]}): fact malformed`);
    // Any emitted hint must carry this layer's framing prefix (no Year/Day mix-up).
    const hint = res && res.hints && res.hints[0];
    ok(!hint || hint.startsWith(L.prefix), `[${L.name}] pair (${ANIMALS[a]}, ${ANIMALS[b]}): wrong hint prefix`);
  }

  // 2) Symmetry: category is order-independent.
  for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
    ok(actualCategory(L.fn(mk(L.field, ANIMALS[a]), mk(L.field, ANIMALS[b]))) ===
       actualCategory(L.fn(mk(L.field, ANIMALS[b]), mk(L.field, ANIMALS[a]))),
       `[${L.name}] asymmetry at (${ANIMALS[a]}, ${ANIMALS[b]})`);
  }

  // 3) Category counts over the full 144-cell grid (incl. both orderings + diagonal).
  ok(counts.RESONANCE === 12, `[${L.name}] RESONANCE count ${counts.RESONANCE} ≠ 12`);
  ok(counts.CLASH === 12, `[${L.name}] CLASH count ${counts.CLASH} ≠ 12`);
  ok(counts['SIX-COMBINATION'] === 12, `[${L.name}] SIX count ${counts['SIX-COMBINATION']} ≠ 12`);
  ok(counts['THREE-HARMONY'] === 24, `[${L.name}] TRINE count ${counts['THREE-HARMONY']} ≠ 24`);
  ok(counts.NONE === 84, `[${L.name}] NONE count ${counts.NONE} ≠ 84`);

  // 4) Mutual exclusivity: no pairing emits more than one hint.
  for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
    const res = L.fn(mk(L.field, ANIMALS[a]), mk(L.field, ANIMALS[b]));
    ok(!res || res.hints.length <= 1, `[${L.name}] pair (${ANIMALS[a]}, ${ANIMALS[b]}) emitted ${res.hints.length} hints`);
  }

  // 5) Guard rails: missing / invalid animal → null (so the registry skips it cleanly).
  ok(L.fn(mk(L.field, 'Rat'), mk(L.field, undefined)) === null, `[${L.name}] missing animal should yield null`);
  ok(L.fn(mk(L.field, 'Wolf'), mk(L.field, 'Rat')) === null, `[${L.name}] invalid animal should yield null`);
  ok(L.fn({ bazi: null }, mk(L.field, 'Rat')) === null, `[${L.name}] missing bazi should yield null`);
}

// 6) Layer independence: the Day contributor must read dayAnimal, not animal (and vice
//    versa). Feed only the OTHER field and confirm the contributor returns null.
ok(dayFn({ bazi: { animal: 'Rat' } }, { bazi: { animal: 'Ox' } }) === null, 'Day layer must not read the Year field');
ok(yearFn({ bazi: { dayAnimal: 'Rat' } }, { bazi: { dayAnimal: 'Ox' } }) === null, 'Year layer must not read the Day field');

// 7) Spot checks on famous pairs (Year layer) + Day-layer framing.
ok(actualCategory(yearFn(mk('animal','Tiger'), mk('animal','Monkey'))) === 'CLASH', 'Tiger–Monkey should clash');
ok(/PARTNER-SEAT CLASH/.test(dayFn(mk('dayAnimal','Rat'), mk('dayAnimal','Horse')).hints[0]), 'Day Rat–Horse should be a partner-seat clash');
ok(/PARTNER-SEAT SIX-COMBINATION/.test(dayFn(mk('dayAnimal','Rat'), mk('dayAnimal','Ox')).hints[0]), 'Day Rat–Ox should be a partner-seat six-combination');

// 8) Chart pipeline wiring: dayAnimal is persisted, and the contributor is registered.
ok(/dayAnimal:\s*dayPillar\.animal/.test(html), 'dayAnimal not persisted onto chart.bazi');
ok(/SYNASTRY_CONTRIBUTORS\.push\([^)]*baziDayAnimalInteraction[^)]*\)/.test(html), 'baziDayAnimalInteraction not registered');
ok(/SYNASTRY_CONTRIBUTORS\.push\([^)]*baziAnimalInteraction[^)]*\)/.test(html), 'baziAnimalInteraction not registered');

console.log(`\nBaZi animal-synastry QA (Year + Day-branch): ${pass} passed, ${fail} failed`);
if (fail) { console.error('\nFAILURES:\n  ' + failures.slice(0, 20).join('\n  ')); process.exit(1); }
console.log('All checks passed. ✔');
