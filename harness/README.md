# Batch scoring harness

Applies the rubric in `../index.html` to protocol documents at portfolio scale.
The browser tool scores one protocol interactively; this scores many
unattended.

**The rubric is not reimplemented here.** `rubric.py` parses `DIMS`, `DIM6`,
`MATRIX`, `TOTAL_MAX_WT` and `MAX_CHARS` out of `index.html` at runtime, so the
tool and the harness cannot drift apart. Change an item in the tool and the
harness picks it up with no code change.

## Requirements

- Python 3.9+ (stdlib only — no packages to install)
- `pdftotext` (poppler) for PDFs; `textutil` (macOS) for docx/doc/rtf/html/txt
- An Anthropic API key in the macOS Keychain under service `ANTHROPIC_API_KEY`

## Usage

```bash
python3 score.py PROTOCOL [PROTOCOL ...]      # score one or more protocols
python3 score.py PROTO --dry-run              # build the prompt, make no API call
python3 score.py PROTO --force                # rescore even if a result exists
python3 score.py PROTO --doc /path/to.pdf     # force a specific document
python3 score.py PROTO --max-chars 250000     # override the tool's MAX_CHARS
python3 rubric.py                             # print the parsed rubric and verify totals
```

Results are written per protocol to `results/<MNEMONIC>.json` as they complete,
which makes batches resumable — an already-scored protocol is skipped unless
`--force` is passed.

Edit `DOCS` in `score.py` to point at your protocol directories.

## What it guards against

Input-quality failures in this domain produce **plausible but wrong scores
rather than errors**, so each is detected and refused:

| Failure | Detection |
|---|---|
| Document-viewer stub exported instead of the protocol | minimum-length floor (`--min-chars`, default 8000) plus signature match |
| PDF whose fonts carry no Unicode mapping (extracts as mojibake) | caught by the length floor; fix with `ocrmypdf --force-ocr` |
| Filename collision resolving to a *different* study's protocol | candidate ranking — an explicit alias outranks a bare mnemonic token |
| Model answering in prose instead of JSON | automatic re-ask, up to 3 attempts |
| Credit exhaustion or auth failure mid-batch | 400-class response aborts the whole batch rather than failing per protocol |

## Not in this repository

`results/` is deliberately excluded. Result files contain scoring rationales
that quote protocol text, including sponsor protocols under confidentiality
agreement. Keep them alongside the portfolio workbook, not here.

See `../research/Updated Research/automated-scoring-methods.md` for the failure
modes in detail, measured reproducibility, and limitations.
