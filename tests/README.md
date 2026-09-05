# Tests

An end-to-end check of the protocol upload and AI auto-scoring pipeline — the
app's most involved path, and the one most likely to break silently.

`e2e-upload.js` drives the real page in headless Chromium: it uploads a DOCX and
a PDF, confirms the extracted text reaches the prompt, that all 43 criteria come
back through the review modal, that applying them moves the scoring engine, that
a protocol beyond the 80,000-character prompt cap gets truncated rather than
silently overflowing the request, and that a structurally different
non-interventional protocol (chart abstraction, biobanking, PROs, a qualitative
substudy) flows through the same pipeline and lands scores in the supplemental
Dimension 6 items the oncology fixture never touches. It also uploads a legacy
Word 97-2003 `.doc` file — a format the upload zone accepts by extension but
can't actually parse — and confirms that fails with clear guidance instead of
a misleading error. The OpenAI call is intercepted and answered locally, so
**the run needs no API key and costs nothing**.

## Running

```bash
npm install --no-save playwright http-server
node tests/make-fixtures.js            # build the DOCX + PDF fixtures
npx http-server -p 8899 -s &           # serve the repo root

node tests/e2e-upload.js                                        # hosted index.html
TARGET_PAGE=/offline-bundle/index.html node tests/e2e-upload.js # offline bundle
```

Both targets should report `34/34 checks passed`.

### On a network that blocks CDNs

`index.html` pulls Tailwind, Chart.js, pdf.js, and mammoth from jsDelivr and
`cdn.tailwindcss.com`. Where those hosts are blocked, set `STUB_CDN=1` to serve
the offline bundle's vendored copies in their place:

```bash
STUB_CDN=1 node tests/e2e-upload.js
```

### On a sandbox with a pre-installed Chromium

If the installed `playwright` package's pinned browser revision doesn't match
what's actually on disk (`browserType.launch: Executable doesn't exist at ...`),
point both scripts at the sandbox's own binary instead of downloading one:

```bash
PLAYWRIGHT_CHROMIUM_PATH=/path/to/chrome node tests/make-fixtures.js
PLAYWRIGHT_CHROMIUM_PATH=/path/to/chrome node tests/e2e-upload.js
```

## Fixtures

`fixtures/sample-protocol.txt` is a synthetic Phase II oncology protocol written
to exercise the checklist — it deliberately contains signals for the harder
dimensions (intensive PK sampling, mandatory biopsies, ePRO devices, CRS
monitoring with overnight hospitalization, central imaging review, 5-year
follow-up).

`make-fixtures.js` also builds a `sample-protocol-long` variant: the same
protocol padded with clearly-labeled filler text past the app's 80,000-character
prompt cap, ending in a canary string that must never survive into the captured
prompt. It exists to exercise `buildPrompt()`'s truncation path, which the plain
fixture (well under the cap) never touches.

`fixtures/sample-protocol-hem-cohort.txt` is a second, structurally different
synthetic protocol: a non-interventional sickle cell disease natural history
and biorepository study, written to exercise the supplemental Dimension 6 /
HEM CTM addendum content (retrospective chart abstraction, prospective EHR
linkage, biobanking, a PRO battery, and an embedded qualitative substudy) that
the oncology fixture — an interventional drug trial — never describes, and so
never exercises end-to-end through the upload → extract → prompt → review
pipeline.

`fixtures/sample-protocol-legacy.doc` is not a protocol at all — it's a
minimal buffer carrying the real 8-byte OLE2 Compound File Binary magic
number that every genuine Word 97-2003 `.doc` starts with, padded past a
plausible header size. `make-fixtures.js` generates it directly (no protocol
text, no ZIP writer) because it exists purely to exercise the app's
format-detection path: `.doc` is accepted by the upload zone's extension
allow-list, but mammoth only parses the OOXML zip format `.docx` uses, so a
real legacy `.doc` used to fail deep inside `extractDOCX()` with a generic,
misleading error. The app now checks for the OLE2 signature up front and
fails fast with guidance to re-save as `.docx` or PDF instead.

The `.docx` and `.pdf` fixtures are generated from committed `.txt`/inline
source rather than committed themselves, so they can't drift from the text
they're built out of. The PDFs are printed through headless Chromium so they
carry a real text layer — which is what pdf.js has to parse in the app.

## What the degraded-mode checks cover

The last three checks load the page with the CDN hosts blocked. Tailwind is what
normally supplies `.hidden`; without it — and without a local definition — the
three `.modal-overlay` elements render at `display: flex` and cover the page, so
nothing is clickable and the app appears frozen with no error shown. Both
`index.html` and the offline bundle now define `.hidden` in their own stylesheet
so this degrades to "unstyled but usable" instead.
