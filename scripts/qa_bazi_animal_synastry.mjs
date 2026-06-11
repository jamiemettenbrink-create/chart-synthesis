// QA harness for the cross-chart BaZi Earthly-Branch (Chinese zodiac animal) synastry
// contributor. Extracts the REAL code from app.html, evals it, and cross-checks every
// one of the 144 animal pairings against an independent reimplementation of the branch
// tables in scripts/calculate_bazi.py. Run: node scripts/qa_bazi_animal_synastry.mjs
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../app.html', import.meta.url), 'utf8');

function extract(re, label) {
  const m = html.match(re);
  if (!m) throw new Error(`QA setup failure: could not find ${label} in app.html`);
  return m[0];
}

// Pull the actual definitions out of the shipped file so we test the real code.
const animalsConst = extract(/const BAZI_ANIMALS\s*=\s*\[[^\]]*\];/, 'BAZI_ANIMALS');
const sixConst     = extract(/const BAZI_SIX_COMBINATIONS\s*=\s*\[[\s\S]*?\];/, 'BAZI_SIX_COMBINATIONS');
const triConst     = extract(/const BAZI_THREE_HARMONY\s*=\s*\[[\s\S]*?\];/, 'BAZI_THREE_HARMONY');
const fnDef        = extract(/function baziAnimalInteraction\(chartA, chartB\)\{[\s\S]*?\n\}/, 'baziAnimalInteraction');

const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(`${animalsConst}\n${sixConst}\n${triConst}\n${fnDef}\nthis.fn = baziAnimalInteraction; this.ANIMALS = BAZI_ANIMALS;`, sandbox);
const { fn, ANIMALS } = sandbox;

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
const mk = (animal) => ({ bazi: { animal } });

let pass = 0, fail = 0;
const failures = [];
const ok = (cond, msg) => { if (cond) pass++; else { fail++; failures.push(msg); } };

// 1) Exhaustive 12×12: category matches the Python-derived truth table.
const counts = { RESONANCE:0, CLASH:0, 'SIX-COMBINATION':0, 'THREE-HARMONY':0, NONE:0 };
for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
  const res = fn(mk(ANIMALS[a]), mk(ANIMALS[b]));
  const exp = expectedCategory(a, b);
  const act = actualCategory(res);
  ok(exp === act, `pair (${ANIMALS[a]}, ${ANIMALS[b]}): expected ${exp}, got ${act}`);
  counts[act]++;
  // Fact line must always name both animals.
  const fact = res && res.facts && res.facts[0];
  ok(fact && fact.includes(ANIMALS[a]) && fact.includes(ANIMALS[b]), `pair (${ANIMALS[a]}, ${ANIMALS[b]}): fact missing an animal`);
}

// 2) Symmetry: category is order-independent.
for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
  ok(actualCategory(fn(mk(ANIMALS[a]), mk(ANIMALS[b]))) === actualCategory(fn(mk(ANIMALS[b]), mk(ANIMALS[a]))),
     `asymmetry at (${ANIMALS[a]}, ${ANIMALS[b]})`);
}

// 3) Category counts over the full 144-cell grid (incl. both orderings + diagonal).
//    Diagonal RESONANCE = 12. CLASH = 12 (6 unordered ×2). SIX = 12. TRINE = 12 pairs ×2 = 24. NONE = rest.
ok(counts.RESONANCE === 12, `RESONANCE count ${counts.RESONANCE} ≠ 12`);
ok(counts.CLASH === 12, `CLASH count ${counts.CLASH} ≠ 12`);
ok(counts['SIX-COMBINATION'] === 12, `SIX count ${counts['SIX-COMBINATION']} ≠ 12`);
ok(counts['THREE-HARMONY'] === 24, `TRINE count ${counts['THREE-HARMONY']} ≠ 24`);
ok(counts.NONE === 84, `NONE count ${counts.NONE} ≠ 84`); // 144 - 12 - 12 - 12 - 24

// 4) Spot checks on the famous pairs.
ok(actualCategory(fn(mk('Rat'), mk('Horse'))) === 'CLASH', 'Rat–Horse should clash');
ok(actualCategory(fn(mk('Tiger'), mk('Monkey'))) === 'CLASH', 'Tiger–Monkey should clash');
ok(actualCategory(fn(mk('Rat'), mk('Ox'))) === 'SIX-COMBINATION', 'Rat–Ox six-combination');
ok(actualCategory(fn(mk('Monkey'), mk('Dragon'))) === 'THREE-HARMONY', 'Monkey–Dragon trine (Water)');
ok(actualCategory(fn(mk('Rat'), mk('Tiger'))) === 'NONE', 'Rat–Tiger neutral');

// 5) Guard rails: missing / invalid animal → null (so the registry skips it cleanly).
ok(fn(mk('Rat'), mk(undefined)) === null, 'missing animal should yield null');
ok(fn(mk('Wolf'), mk('Rat')) === null, 'invalid animal should yield null');
ok(fn({ bazi: null }, mk('Rat')) === null, 'missing bazi should yield null');

// 6) Mutual exclusivity: no pairing emits more than one hint.
for (let a = 0; a < 12; a++) for (let b = 0; b < 12; b++) {
  const res = fn(mk(ANIMALS[a]), mk(ANIMALS[b]));
  ok(!res || res.hints.length <= 1, `pair (${ANIMALS[a]}, ${ANIMALS[b]}) emitted ${res.hints.length} hints`);
}

// 7) Registry wiring: contributor is actually pushed into SYNASTRY_CONTRIBUTORS.
ok(/SYNASTRY_CONTRIBUTORS\.push\([^)]*baziAnimalInteraction[^)]*\)/.test(html), 'baziAnimalInteraction not registered in SYNASTRY_CONTRIBUTORS');

console.log(`\nBaZi animal-synastry QA: ${pass} passed, ${fail} failed`);
if (fail) { console.error('\nFAILURES:\n  ' + failures.slice(0, 20).join('\n  ')); process.exit(1); }
console.log('All checks passed. ✔');
