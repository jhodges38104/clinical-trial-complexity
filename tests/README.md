# Tests

An end-to-end check of the protocol upload and AI auto-scoring pipeline — the
app's most involved path, and the one most likely to break silently.

`e2e-upload.js` drives the real page in headless Chromium: it uploads a DOCX and
a PDF, confirms the extracted text reaches the prompt, that all 43 criteria come
back through the review modal, that applying them moves the scoring engine, that
a protocol beyond the 80,000-character prompt cap gets truncated rather than
silently overflowing the request, and that a blank/placeholder protocol is
refused before ever reaching the model. The OpenAI call is intercepted and
answered locally, so **the run needs no API key and costs nothing**.

## Running

```bash
npm install --no-save playwright http-server
node tests/make-fixtures.js            # build the DOCX + PDF fixtures
npx http-server -p 8899 -s &           # serve the repo root

node tests/e2e-upload.js                                        # hosted index.html
TARGET_PAGE=/offline-bundle/index.html node tests/e2e-upload.js # offline bundle
```

Both targets should report `32/32 checks passed`.

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

A `sample-protocol-blank` variant — a short placeholder cover page with no real
protocol content — exercises the opposite edge: `analyzeProtocol()`'s guard
against sending near-empty text (under 50 characters once normalized) to the
model at all.

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
