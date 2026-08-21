// End-to-end test of the protocol upload + AI auto-scoring pipeline.
//
// Drives the real page in headless Chromium: uploads a DOCX and a PDF, checks
// that the extracted text reaches the prompt, that all 43 criteria come back
// through the review modal, and that applying them updates the scoring engine.
// The OpenAI call is intercepted and answered locally, so the run needs no API
// key and costs nothing.
//
//   node tests/make-fixtures.js          # once, to build the upload fixtures
//   npx http-server -p 8899 -s &         # serve the repo root
//   node tests/e2e-upload.js                                   # hosted index.html
//   TARGET_PAGE=/offline-bundle/index.html node tests/e2e-upload.js
//
// STUB_CDN=1 serves the offline bundle's vendored libraries in place of the
// CDN ones, for networks (CI sandboxes, hospital VLANs) that block those hosts.

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const FIXTURES = path.join(__dirname, 'fixtures');
const LIB_DIR = path.join(__dirname, '..', 'offline-bundle', 'lib');
const BASE = process.env.BASE_URL || 'http://127.0.0.1:8899';
const TARGET = process.env.TARGET_PAGE || '/index.html';

const results = [];
function check(name, pass, detail) {
  results.push({ name, pass, detail });
  console.log(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
}

for (const f of ['sample-protocol.docx', 'sample-protocol.pdf']) {
  if (!fs.existsSync(path.join(FIXTURES, f))) {
    console.error(`Missing fixture ${f} — run: node tests/make-fixtures.js`);
    process.exit(2);
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();

  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('requestfailed', r => failedRequests.push(`${r.url()} :: ${r.failure()?.errorText}`));

  // Record alert()s rather than blocking on them.
  const alerts = [];
  page.on('dialog', async d => { alerts.push(d.message()); await d.dismiss(); });

  // ── Intercept the OpenAI call, answer with a well-formed synthetic response.
  let capturedPrompt = null;
  let capturedModel = null;
  let itemIds = null;

  await page.route('https://api.openai.com/**', async route => {
    const body = JSON.parse(route.request().postData());
    capturedModel = body.model;
    capturedPrompt = body.messages[0].content;
    const scores = {};
    itemIds.forEach((id, n) => {
      scores[id] = { score: n % 4, rationale: `Mock rationale for ${id}.` };
    });
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ choices: [{ message: { content: JSON.stringify({ scores }) } }] })
    });
  });

  if (process.env.STUB_CDN === '1') {
    const LIB = {
      'cdn.tailwindcss.com': 'tailwind.min.js',
      'chart.umd.min.js': 'chart.umd.min.js',
      'pdf.worker.min.js': 'pdf.worker.min.js',
      'pdf.min.js': 'pdf.min.js',
      'mammoth.browser.min.js': 'mammoth.browser.min.js'
    };
    await page.route(/cdn\.(tailwindcss\.com|jsdelivr\.net)/, async route => {
      const key = Object.keys(LIB).find(k => route.request().url().includes(k));
      if (!key) return route.abort();
      await route.fulfill({
        status: 200,
        contentType: 'application/javascript',
        body: fs.readFileSync(path.join(LIB_DIR, LIB[key]))
      });
    });
  }

  console.log(`\n=== ${BASE}${TARGET} ===\n`);
  await page.goto(BASE + TARGET, { waitUntil: 'networkidle', timeout: 60000 });

  // ── Libraries.
  const libs = await page.evaluate(() => ({
    pdfjs: !!window.pdfjsLib, mammoth: !!window.mammoth, chart: !!window.Chart
  }));
  check('pdf.js loaded', libs.pdfjs, JSON.stringify(libs));
  check('mammoth loaded', libs.mammoth);
  check('Chart.js loaded', libs.chart);

  // ── Scoring inventory, read from the page's own config.
  itemIds = await page.evaluate(() => [...DIMS, DIM6].flatMap(d => d.items.map(i => i.id)));
  check('43 scoring items defined', itemIds.length === 43, `${itemIds.length} items`);

  await page.evaluate(() => sessionStorage.setItem('openai_api_key', 'sk-test-dummy-key'));

  // ── DOCX upload.
  await page.setInputFiles('#file-input', path.join(FIXTURES, 'sample-protocol.docx'));
  const ready = await page.evaluate(() => ({
    name: document.getElementById('upload-filename').textContent,
    enabled: !document.getElementById('analyze-btn').disabled
  }));
  check('DOCX accepted by upload zone',
    ready.name === 'sample-protocol.docx' && ready.enabled, JSON.stringify(ready));

  await page.click('#analyze-btn');
  await page.waitForSelector('#review-modal:not(.hidden)', { timeout: 60000 });
  check('DOCX → analysis → review modal opened', true);

  check('DOCX text extracted into prompt',
    !!capturedPrompt && capturedPrompt.includes('XJ-401') &&
      capturedPrompt.includes('cytokine release syndrome'),
    capturedPrompt ? `prompt ${capturedPrompt.length} chars` : 'no prompt captured');
  check('Prompt enumerates all 43 criteria',
    (capturedPrompt.match(/"criterion"/g) || []).length === 43);
  check('Request names a model', !!capturedModel, `model=${capturedModel}`);
  check('Review modal shows all 43 selects',
    (await page.locator('#review-items-container select').count()) === 43);

  // ── Apply and verify the scores land in the engine.
  await page.click('button:has-text("Apply")');
  await page.waitForSelector('#review-modal.hidden', { state: 'attached', timeout: 10000 });

  const applied = await page.evaluate(() => ({
    core: { ...scores }, supp: { ...scores6 }
  }));
  check('Applied scores to 36 core items', Object.keys(applied.core).length === 36);
  check('Applied scores to 7 supplemental items', Object.keys(applied.supp).length === 7);

  const mismatches = itemIds
    .map((id, n) => ((applied.core[id] ?? applied.supp[id]) === n % 4 ? null : id))
    .filter(Boolean);
  check('Every applied score matches the AI suggestion', mismatches.length === 0,
    mismatches.slice(0, 5).join(', '));

  const gauge = await page.evaluate(() => ({
    num: document.getElementById('gauge-num').textContent.trim(),
    lbl: document.getElementById('gauge-lbl').textContent.trim(),
    breakdown: document.getElementById('score-breakdown').innerText.replace(/\s+/g, ' ')
  }));
  check('Weighted score rendered on gauge',
    /^\d+$/.test(gauge.num) && /Complexity/i.test(gauge.lbl), JSON.stringify(gauge));
  check('Breakdown reports all 36 core items scored', gauge.breakdown.includes('36/36'));

  // ── PDF upload.
  await page.evaluate(() => clearUpload());
  await page.setInputFiles('#file-input', path.join(FIXTURES, 'sample-protocol.pdf'));
  capturedPrompt = null;
  await page.click('#analyze-btn');
  await page.waitForSelector('#review-modal:not(.hidden)', { timeout: 60000 });
  check('PDF text extracted into prompt',
    !!capturedPrompt && capturedPrompt.includes('XJ-401') &&
      capturedPrompt.includes('Lugano') && capturedPrompt.includes('FACT-Lym'),
    capturedPrompt ? `prompt ${capturedPrompt.length} chars` : 'no prompt captured');

  // pdf.js emits one item per text run; without normalization ~19% of the
  // extracted characters are padding, which wastes prompt budget and cost.
  const ws = await page.evaluate(async () => {
    const t = await extractPDF(uploadedFile);
    return { runs: (t.match(/ {2,}/g) || []).length, len: t.length };
  });
  check('PDF text is whitespace-normalized', ws.runs === 0,
    `${ws.runs} multi-space runs in ${ws.len} chars`);
  await page.evaluate(() => closeReviewModal());

  // ── Unsupported file type.
  alerts.length = 0;
  await page.setInputFiles('#file-input', path.join(FIXTURES, 'sample-protocol.txt'));
  await page.waitForTimeout(500);
  check('Unsupported .txt file rejected',
    alerts.some(a => /PDF, DOCX, or DOC/i.test(a)), JSON.stringify(alerts));

  // ── Runtime error surface.
  check('No uncaught page errors', pageErrors.length === 0, pageErrors.join(' | '));
  const realErrors = consoleErrors.filter(e => !/favicon/i.test(e));
  check('No console errors', realErrors.length === 0, realErrors.slice(0, 3).join(' | '));
  const realFailed = failedRequests.filter(r => !/favicon/i.test(r));
  check('No failed network requests', realFailed.length === 0, realFailed.slice(0, 3).join(' | '));

  // ── Degraded mode: the CDN libraries are unreachable.
  // Tailwind supplies .hidden. If it fails to load and nothing else defines
  // .hidden, the three .modal-overlay elements render at display:flex and
  // cover the page, so no control is clickable and the app looks frozen.
  const degraded = await ctx.newPage();
  await degraded.route('**cdn.tailwindcss.com**', r => r.abort());
  await degraded.route('**cdn.jsdelivr.net**', r => r.abort());
  await degraded.goto(BASE + TARGET, { waitUntil: 'domcontentloaded' });
  await degraded.waitForTimeout(1200);

  const overlays = await degraded.evaluate(() =>
    [...document.querySelectorAll('.modal-overlay.hidden')]
      .map(el => ({ id: el.id, display: getComputedStyle(el).display })));
  check('Hidden modals stay hidden without the CDN',
    overlays.every(o => o.display === 'none'), JSON.stringify(overlays));

  await degraded.setInputFiles('#file-input', path.join(FIXTURES, 'sample-protocol.docx'));
  await degraded.locator('#analyze-btn').scrollIntoViewIfNeeded();
  const cover = await degraded.evaluate(() => {
    const btn = document.getElementById('analyze-btn');
    const r = btn.getBoundingClientRect();
    const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return { hit: hit ? (hit.id || hit.tagName) : null, ok: !!hit && (hit === btn || btn.contains(hit)) };
  });
  check('Analyze button is not covered without the CDN', cover.ok,
    `element at button center: ${cover.hit}`);

  let clickOk = true, clickErr = '';
  try {
    await degraded.evaluate(() => sessionStorage.setItem('openai_api_key', 'sk-test-dummy-key'));
    await degraded.click('#analyze-btn', { timeout: 8000 });
  } catch (e) { clickOk = false; clickErr = e.message.split('\n')[0]; }
  check('Analyze button is clickable without the CDN', clickOk, clickErr);

  await browser.close();

  const failed = results.filter(r => !r.pass);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  if (failed.length) {
    console.log('\nFAILURES:');
    failed.forEach(f => console.log(`  - ${f.name}${f.detail ? ': ' + f.detail : ''}`));
    process.exit(1);
  }
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(2); });
