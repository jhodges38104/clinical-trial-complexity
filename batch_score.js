// Batch scorer for the HEM Protocol Complexity & Workload Tool.
//
// Loads the REAL app.js from the scoring-tool repo against a stub DOM (the same
// indirect-eval pattern tests/invariants.js uses) so the arithmetic is the
// shipped tool's, not a transcription. Reads a JSON batch, writes results JSON.
//
//   jsc batch_score.js -- <repo_dir> <input.json> <output.json>
//
// Input:  { "protocols": [ { "id","pi","phase","capacity",
//                            "items": {...37 ids...},
//                            "participants": {...status ids...} } ] }
//
// A protocol whose `items` does not carry ALL 37 ids is NOT scored — it comes
// back with scored:false and the missing ids listed. Blank means blank: the
// tool's own applyState() treats an absent item as 0, which is a migration
// convention, not a scoring one, and silently understates a total.
// Participants may be omitted; Part B is then reported as null, not zero.

// jsc exposes post-`--` args as `arguments`; Node uses process.argv.
const args = (typeof scriptArgs !== 'undefined') ? scriptArgs
           : (typeof arguments !== 'undefined') ? Array.prototype.slice.call(arguments)
           : (typeof process !== 'undefined' ? process.argv.slice(2) : []);
const [REPO, INFILE, OUTFILE] = args;
if (!REPO || !INFILE || !OUTFILE) { throw new Error('usage: batch_score.js <repo_dir> <in.json> <out.json>'); }

const log = (typeof console !== 'undefined' && console.log) ? console.log.bind(console) : print;
function readText(p) {
  if (typeof require === 'function') return require('fs').readFileSync(p, 'utf8');
  if (typeof readFile === 'function') return readFile(p);
  if (typeof read === 'function') return read(p);
  throw new Error('no file-reading primitive');
}
function writeText(p, s) {
  if (typeof require === 'function') return require('fs').writeFileSync(p, s);
  if (typeof writeFile === 'function') return writeFile(p, s); // jsc
  throw new Error('no file-writing primitive in this runtime');
}

// ── stub host (mirrors tests/invariants.js) ──────────────────────────────
const elements = new Map();
function stubEl(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id, value: '', textContent: '', innerHTML: '', hidden: true, disabled: false,
      classList: (() => { const s = new Set(); return {
        add: (...c) => c.forEach(x => s.add(x)), remove: (...c) => c.forEach(x => s.delete(x)),
        contains: c => s.has(c), toggle: (c, f) => { const on = f === undefined ? !s.has(c) : !!f; if (on) s.add(c); else s.delete(c); return on; } }; })(),
      addEventListener() {}, appendChild() {}, removeChild() {}, click() {}, focus() {},
      setAttribute() {}, style: {},
    });
  }
  return elements.get(id);
}
globalThis.document = { getElementById: stubEl, addEventListener() {},
  createElement: () => ({ style: {}, click() {}, setAttribute() {}, appendChild() {} }),
  body: { appendChild() {}, removeChild() {} } };
globalThis.window = { print() {} };
let lsStore = {};
globalThis.localStorage = { getItem: k => (k in lsStore ? lsStore[k] : null),
  setItem: (k, v) => { lsStore[k] = String(v); }, removeItem: k => { delete lsStore[k]; } };
globalThis.Blob = function Blob() {};
globalThis.URL = { createObjectURL: () => 'blob:stub', revokeObjectURL() {} };
if (typeof setTimeout !== 'function') globalThis.setTimeout = () => 0;

const NAMES = ['DOMAINS','PART_A_MAX','TIERS','STATIC_WU','STATUS_ROWS','PHASE_MULTIPLIERS',
  'DATA_VOLUME_ITEMS','DATA_VOLUME_MAX','DATA_VOLUME_FACTOR_RANGE','RUBRIC_VERSION',
  'TOOL_VERSION','tierFor','computeAll','setVal','DEFAULT_PHASE','resolvePhase',
  'capacityIsImplausible','repeatedParticipantCounts'];
(0, eval)(readText(REPO + '/app.js') + '\n;globalThis.APP = { ' + NAMES.join(', ') + ' };');
const APP = globalThis.APP;

const ALL_ITEMS = APP.DOMAINS.flatMap(d => d.items.map(it => it.id));
const STATUS_IDS = APP.STATUS_ROWS.map(r => r.id);

function scoreOne(p) {
  const items = p.items || {};
  const missing = ALL_ITEMS.filter(id => items[id] === undefined || items[id] === null || items[id] === '');
  if (missing.length) {
    return { id: p.id, scored: false, missingItems: missing,
             itemsPresent: ALL_ITEMS.length - missing.length, itemsRequired: ALL_ITEMS.length };
  }
  for (const d of APP.DOMAINS) for (const it of d.items) APP.setVal('item_' + it.id, items[it.id]);
  const hasP = p.participants && Object.keys(p.participants).length > 0;
  for (const r of APP.STATUS_ROWS) APP.setVal('p_' + r.id, hasP ? (p.participants[r.id] ?? 0) : 0);
  APP.setVal('phaseSelect', p.phase || APP.DEFAULT_PHASE);
  APP.setVal('capacityConstant', p.capacity != null ? p.capacity : '');
  const c = APP.computeAll();

  const out = {
    id: p.id, pi: p.pi || '', scored: true,
    partA: c.total, partAMax: APP.PART_A_MAX,
    tier: c.tier ? (c.tier.tier ?? c.tier.label ?? String(c.tier)) : null,
    tierLabel: c.tier ? (c.tier.label ?? '') : '',
    domains: {}, dataVolumeFactor: c.dataVolumeFactor ?? null,
    phase: (APP.resolvePhase ? APP.resolvePhase(p.phase || APP.DEFAULT_PHASE).id : (p.phase || APP.DEFAULT_PHASE)),
  };
  for (const ds of c.domainScores) out.domains[ds.domain.id] = { raw: ds.raw, capped: ds.capped, max: ds.domain.max };
  if (hasP) {
    out.partB = { staticWU: c.staticWU ?? null, participantSubtotal: c.participantSubtotal ?? null,
                  monthlyWU: c.monthlyWU ?? c.totalWU ?? null, fte: c.fte ?? null,
                  participantTotal: c.participantTotal ?? null };
  } else {
    out.partB = null;
    out.partBNote = 'no participant counts supplied - WU/FTE not computable';
  }
  return out;
}

const batch = JSON.parse(readText(INFILE));
const results = (batch.protocols || []).map(scoreOne);
const scored = results.filter(r => r.scored).length;
writeText(OUTFILE, JSON.stringify({
  rubricVersion: APP.RUBRIC_VERSION, toolVersion: APP.TOOL_VERSION,
  partAMax: APP.PART_A_MAX, itemCount: ALL_ITEMS.length, statusRows: STATUS_IDS,
  generated: batch.generated || null, results,
}, null, 2));
log('scored ' + scored + ' of ' + results.length + ' protocols (' + ALL_ITEMS.length +
    ' items required each); rubric ' + APP.RUBRIC_VERSION + ', tool ' + APP.TOOL_VERSION +
    ', Part A max ' + APP.PART_A_MAX);
