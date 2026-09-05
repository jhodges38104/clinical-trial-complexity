// Builds the DOCX and PDF upload fixtures from fixtures/sample-protocol.txt,
// plus a "long" variant that pads the same protocol past the app's
// 80,000-character prompt cap (see buildPrompt() in index.html) so the
// truncation path can be exercised end-to-end, and a "hem-cohort" variant —
// a distinct non-interventional protocol (fixtures/sample-protocol-hem-cohort.txt)
// that exercises the supplemental Dimension 6 / HEM CTM addendum content
// (retrospective chart abstraction, biobanking, PROs, qualitative substudy)
// the oncology fixture never touches.
//
// The binaries aren't committed — they're generated, so they can't drift from
// the text they're built out of. Run this once before `e2e-upload.js`.
//
//   node tests/make-fixtures.js
//
// PLAYWRIGHT_CHROMIUM_PATH points at a pre-installed Chromium binary, for
// sandboxes that ship a browser whose revision doesn't match the installed
// playwright package's expected download.

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const FIXTURES = path.join(__dirname, 'fixtures');
const SOURCE = path.join(FIXTURES, 'sample-protocol.txt');
const text = fs.readFileSync(SOURCE, 'utf8');
const hemCohortText = fs.readFileSync(path.join(FIXTURES, 'sample-protocol-hem-cohort.txt'), 'utf8');

// The real protocol content is ~4.3k chars — comfortably under the app's
// 80,000-character prompt cap. Pad it with clearly-labeled filler past that
// cap, then land a canary marker at the very end: if the canary ever reaches
// the captured prompt, the truncation in buildPrompt() has regressed.
const CANARY = 'QR-BEYOND-CAP-9000';
const FILLER_PARAGRAPH =
  'APPENDIX B: PARTICIPATING SITE ROSTER. This paragraph exists purely to ' +
  'pad the protocol text past the 80,000-character prompt cap so the ' +
  'truncation path can be exercised end-to-end. It carries no clinical ' +
  'content of its own and is repeated verbatim.';

let filler = '';
while (text.length + filler.length < 95000) {
  filler += '\n\n' + FILLER_PARAGRAPH;
}
const longText =
  text + '\n\n' + filler.trim() +
  `\n\nCANARY MARKER ${CANARY}: this text lives after the 80,000-character ` +
  'cutoff and must never reach the AI prompt.';

// ── DOCX ─────────────────────────────────────────────────────────────────────
// A minimal but valid WordprocessingML package. mammoth only needs
// word/document.xml plus the two relationship parts to extract raw text.

function xmlEscape(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Minimal ZIP writer (deflate, no data descriptors, no zip64).
function crc32(buf) {
  let c, crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c = (crc ^ buf[i]) & 0xff;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    crc = (crc >>> 8) ^ c;
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function buildDocx(sourceText) {
  const paragraphs = sourceText
    .split(/\n\s*\n/)
    .map(p => p.split('\n').map(l => l.trim()).filter(Boolean).join(' '))
    .filter(Boolean);

  const documentXml =
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>` +
    paragraphs.map(p => `<w:p><w:r><w:t xml:space="preserve">${xmlEscape(p)}</w:t></w:r></w:p>`).join('') +
    `<w:sectPr><w:pgSz w:w="12240" w:h="15840"/></w:sectPr></w:body></w:document>`;

  const parts = [
    ['[Content_Types].xml',
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>`],
    ['_rels/.rels',
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>`],
    ['word/document.xml', documentXml],
    ['word/_rels/document.xml.rels',
      `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>`]
  ];

  const locals = [];
  const central = [];
  let offset = 0;

  for (const [name, content] of parts) {
    const nameBuf = Buffer.from(name, 'utf8');
    const raw = Buffer.from(content, 'utf8');
    const deflated = zlib.deflateRawSync(raw);
    const crc = crc32(raw);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);           // version needed
    local.writeUInt16LE(0, 6);            // flags
    local.writeUInt16LE(8, 8);            // deflate
    local.writeUInt32LE(0, 10);           // time/date
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(deflated.length, 18);
    local.writeUInt32LE(raw.length, 22);
    local.writeUInt16LE(nameBuf.length, 26);
    local.writeUInt16LE(0, 28);
    locals.push(local, nameBuf, deflated);

    const cd = Buffer.alloc(46);
    cd.writeUInt32LE(0x02014b50, 0);
    cd.writeUInt16LE(20, 4);
    cd.writeUInt16LE(20, 6);
    cd.writeUInt16LE(0, 8);
    cd.writeUInt16LE(8, 10);
    cd.writeUInt32LE(0, 12);
    cd.writeUInt32LE(crc, 16);
    cd.writeUInt32LE(deflated.length, 20);
    cd.writeUInt32LE(raw.length, 24);
    cd.writeUInt16LE(nameBuf.length, 28);
    cd.writeUInt32LE(offset, 42);
    central.push(cd, nameBuf);

    offset += local.length + nameBuf.length + deflated.length;
  }

  const centralBuf = Buffer.concat(central);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(parts.length, 8);
  end.writeUInt16LE(parts.length, 10);
  end.writeUInt32LE(centralBuf.length, 12);
  end.writeUInt32LE(offset, 16);

  return Buffer.concat([...locals, centralBuf, end]);
}

for (const [name, src] of [
  ['sample-protocol.docx', text],
  ['sample-protocol-long.docx', longText],
  ['sample-protocol-hem-cohort.docx', hemCohortText]
]) {
  const docxPath = path.join(FIXTURES, name);
  fs.writeFileSync(docxPath, buildDocx(src));
  console.log('wrote', path.relative(process.cwd(), docxPath));
}

// ── PDF ──────────────────────────────────────────────────────────────────────
// Printed through headless Chromium so the result is a real text-layer PDF,
// which is what pdf.js has to parse in the app.

(async () => {
  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (_) {
    console.error(
      'PDF fixtures skipped: playwright not found.\n' +
      'Install it (npm i -D playwright) and re-run to generate the .pdf fixtures.');
    process.exit(0);
  }

  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined
  });

  async function buildPdf(sourceText, outPath) {
    const html =
      `<!doctype html><meta charset="utf-8">` +
      `<style>body{font-family:monospace;white-space:pre-wrap;font-size:11pt;padding:40px}</style>` +
      `<body>${xmlEscape(sourceText)}</body>`;
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.pdf({
      path: outPath,
      format: 'Letter',
      margin: { top: '0.5in', bottom: '0.5in', left: '0.5in', right: '0.5in' }
    });
    await page.close();
    console.log('wrote', path.relative(process.cwd(), outPath));
  }

  await buildPdf(text, path.join(FIXTURES, 'sample-protocol.pdf'));
  await buildPdf(longText, path.join(FIXTURES, 'sample-protocol-long.pdf'));
  await buildPdf(hemCohortText, path.join(FIXTURES, 'sample-protocol-hem-cohort.pdf'));

  await browser.close();
})();
