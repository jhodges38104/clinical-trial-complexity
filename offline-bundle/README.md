# Clinical Trial Complexity Assessor — Local Setup

A fully offline web application for scoring clinical trial complexity and making go/no-go participation decisions.

---

## Quick Start

### Option A — Double-click launcher (recommended)

| OS | File to double-click |
|----|----------------------|
| **Windows** | `start.bat` |
| **macOS / Linux** | `start.sh` (first run: `chmod +x start.sh` in Terminal) |

The launcher starts a local web server and opens the app at **http://localhost:8080** in your default browser.

> **Requires Python 3** — download free from https://python.org if not already installed.

---

### Option B — Direct file open (no server needed)

Just double-click **`index.html`** to open it in your browser.

> Note: PDF upload may not work in some browsers when opened via `file://` (Chrome/Edge CORS restriction). Use Option A (local server) if PDF upload shows errors.

---

## What's inside

```
clinical-trial-complexity-local/
├── index.html          ← The app (single file, fully self-contained)
├── lib/
│   ├── tailwind.min.js         ← CSS framework (offline)
│   ├── chart.umd.min.js        ← Radar chart (offline)
│   ├── pdf.min.js              ← PDF parsing (offline)
│   ├── pdf.worker.min.js       ← PDF.js background worker (offline)
│   └── mammoth.browser.min.js  ← DOCX parsing (offline)
├── start.sh            ← macOS/Linux launcher
├── start.bat           ← Windows launcher
└── README.md           ← This file
```

**No internet connection required** — all libraries are bundled locally.

---

## AI Protocol Upload Feature

The "Analyze Protocol" button lets you upload a PDF or DOCX protocol and have OpenAI's GPT-4o-mini auto-score all 34 checklist items.

**This feature requires an OpenAI API key** (internet connection needed for AI calls only):
1. Obtain a key at https://platform.openai.com/api-keys
2. Click **"Analyze Protocol (AI)"** and enter your `sk-...` key when prompted
3. The key is stored only for your current browser session and is never saved to disk

All assessment scoring, PDF rendering, and DOCX parsing work **fully offline** without an API key.

---

## Features

- 34-item scored checklist across 5 weighted dimensions
- Semicircle complexity gauge + radar chart
- Go / Conditional Go / No-Go decision badge with override flags
- Decision matrix reference table
- Export assessment as JSON
- Print-ready view
- Drag-and-drop PDF/DOCX protocol upload with AI auto-scoring

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| PDF upload fails with CORS error | Use `start.sh` / `start.bat` instead of opening `index.html` directly |
| `start.sh` won't run on Mac | Run `chmod +x start.sh` in Terminal first |
| Port 8080 already in use | Edit `start.sh`/`start.bat` and change `PORT=8080` to another number (e.g. 8090) |
| AI analysis returns error | Check your OpenAI API key; ensure you have internet access for AI calls |
