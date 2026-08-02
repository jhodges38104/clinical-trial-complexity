# Clinical Trial Complexity Assessment Tool

An interactive web app for scoring clinical trial protocol complexity and supporting
go / no-go participation decisions. The scoring framework synthesizes evidence from
published complexity tools (OPAL, the Protocol Complexity Tool, TRACAT, Pharm-CAT) and
public feasibility checklists — see [`research/`](research/) for the full writeup.

**Live app:** https://jhodges38104.github.io/clinical-trial-complexity/

## What's here

| Path | What it is |
|---|---|
| [`index.html`](index.html) | The main interactive assessment app (34-item checklist, 5 weighted dimensions, complexity gauge, radar chart, PDF/DOCX protocol upload with optional AI auto-scoring). Loads its JS dependencies from CDN — this is what GitHub Pages serves. |
| [`cards/`](cards/) | Two standalone, self-contained reference pages: a laminated quick card and a printable quick-reference card. No external dependencies. |
| [`offline-bundle/`](offline-bundle/README.md) | A fully offline, no-internet distributable of the app — same functionality as `index.html`, but with all JS libraries vendored locally. Includes double-click launchers (`start.sh` / `start.bat`) — see its [README](offline-bundle/README.md) for setup. Download this if you need to run the tool with no internet connection. |
| [`research/`](research/) | Source-of-truth Markdown reports: the complexity-tool landscape review, the checklist methodology report, and the Excel-vs-web-app scoring validation report. |
| [`data/`](data/) | The Excel scoring-engine workbook and the underlying literature-review dataset (122 sources, CSV + RIS for reference-manager import) that the checklist is built on. |

## Deliverables

Word (`.docx`) and print-ready PDF versions of the reports and cards are not committed to
this repo (binary re-exports of the Markdown in `research/` would just go stale against
it). They're attached instead to this repo's [Releases](../../releases) page — see
`release-assets/` locally if you're regenerating and re-uploading them.

## Validation

The web app's scoring engine has been checked against the Excel workbook across
low/medium/high complexity test scenarios with full concordance — see
[`research/validation-report.md`](research/validation-report.md).
