"""Batch complexity scoring — mirrors the Clinical Trial Complexity Assessor.

Rubric, weights, truncation limit and decision matrix are read from the tool's
index.html at runtime (see rubric.py), so scores stay consistent with the app.
Model calls go to Anthropic using ANTHROPIC_API_KEY from the macOS Keychain.
"""
import json, subprocess, sys, urllib.request, pathlib, argparse, re, time
import rubric

DOCS = [pathlib.Path("/Users/jhodges/Documents/HEM Protocols"),
        pathlib.Path("/Users/jhodges/Library/Mobile Documents/com~apple~CloudDocs/CTM Activity/HEM Protocols")]
# extra filename spellings to also match (source typos, or exports whose name
# extends the mnemonic). Additive - the mnemonic itself is always tried too.
ALIAS = {"RUHPIS": ["RUPHIS"], "ASHRCDC": ["ASGRCDC", "ASHRCData"], "ATHN": ["ATHNdataset"], "4WARDXP": ["4WARDXP_ocr"]}
EXTS = (".pdf", ".docx", ".doc", ".rtf", ".html", ".htm", ".txt")  # textutil handles all but pdf
OUT  = pathlib.Path(__file__).resolve().parent / "results"
DEFAULT_MODEL = "claude-opus-5"   # --model claude-sonnet-5 for ~2.5x cheaper

def api_key():
    r = subprocess.run(["security","find-generic-password","-s","ANTHROPIC_API_KEY","-w"],
                       capture_output=True, text=True)
    if r.returncode: sys.exit("ANTHROPIC_API_KEY not found in Keychain")
    k = r.stdout.strip()
    if not k.startswith("sk-ant-"):
        sys.exit(f"Keychain 'ANTHROPIC_API_KEY' holds a {len(k)}-char value beginning "
                 f"'{k[:4]}…' - not an Anthropic key (expected sk-ant-...).\n"
                 f"  Fix with:  key-set ANTHROPIC_API_KEY")
    return k

def workspace_id(cli_value):
    """Org-scoped keys need anthropic-workspace-id. Flag > env > Keychain."""
    import os
    if cli_value: return cli_value
    if os.environ.get("ANTHROPIC_WORKSPACE_ID"): return os.environ["ANTHROPIC_WORKSPACE_ID"]
    r = subprocess.run(["security","find-generic-password","-s","ANTHROPIC_WORKSPACE_ID","-w"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

def normalize_text(text):
    """Port of normalizeExtractedText() in index.html.

    pdftotext -layout pads columns with long space runs, the same artefact
    pdf.js produces by joining text items with ' '. Collapsing it cuts token
    cost and leaves more of a long protocol under the character cap.
    """
    text = re.sub(r"[ \t\u00a0]+", " ", text)   # collapse padding runs
    text = re.sub(r" *\n *", "\n", text)        # trim each line
    text = re.sub(r"\n{3,}", "\n\n", text)     # cap blank-line runs
    return text.strip()

def extract_text(path):
    p = str(path)
    if p.lower().endswith(".pdf"):
        r = subprocess.run(["pdftotext","-layout",p,"-"], capture_output=True, text=True)
    else:  # textutil handles docx, html, htm, txt, rtf, doc
        r = subprocess.run(["textutil","-convert","txt","-stdout",p], capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        raise RuntimeError(f"text extraction failed for {path.name}")
    txt = normalize_text(r.stdout)
    # iRIS exports sometimes yield a viewer stub or an unfinished PDF-generation
    # placeholder instead of the document. Scoring those returns plausible but
    # meaningless numbers, so refuse them explicitly.
    STUBS = ("the document is being generated into a pdf",
             "please wait ... the document is being generated")
    low = txt[:4000].lower()
    for sig in STUBS:
        if sig in low:
            raise RuntimeError(f"{path.name} is an iRIS placeholder, not the protocol "
                               f"(re-export from iRIS)")
    return txt

def build_prompt(text, dims, dim6, max_chars):
    items = []
    for d in dims + [dim6]:
        for it in d["items"]:
            items.append({"id": it["id"], "criterion": it["name"], "dimension": d["name"],
                          "scale": " | ".join(f"{i}: {o['d']}" for i, o in enumerate(it["opts"]))})
    truncated = len(text) > max_chars
    text = text[:max_chars]
    note = ("\n[Protocol text truncated to %s characters due to context limits — "
            "focus on the content provided.]" % f"{max_chars:,}") if truncated else ""
    n = len(items)
    return (f"You are an expert clinical trial feasibility analyst. Read the protocol text below and "
        f"score each of the {n} complexity criteria on a 0-3 scale. The last 7 items (6.x) cover "
        f"study-design modality and data/specimen complexity (qualitative methods, EMR abstraction, "
        f"biospecimens, PROs, longitudinal scale) — for a standard interventional drug/device trial "
        f"these will usually score 0; only score them higher if the protocol actually describes that "
        f"kind of work.\n\nSCORING CRITERIA ({n} items):\n{json.dumps(items, indent=2)}\n\n"
        'Return ONLY a valid JSON object with exactly this structure:\n'
        '{\n  "scores": {\n    "<item_id>": { "score": <integer 0-3>, '
        '"rationale": "<1-2 sentence evidence-based explanation>" }\n  }\n}\n\nRules:\n'
        f"- Include all {n} item IDs exactly as listed above\n"
        "- Base every score strictly on content found in the protocol\n"
        "- If evidence is absent for an item, default to 0 and note it in the rationale\n"
        f"- Do not add any text outside the JSON object{note}\n\nPROTOCOL TEXT:\n{text}"), truncated, n

def call_claude(prompt, key, model, wsid=None, max_tokens=32000):
    body = json.dumps({"model": model, "max_tokens": max_tokens,
        "messages": [{"role":"user","content":prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01",
                 **({"anthropic-workspace-id": wsid} if wsid else {})})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=900) as fh:
                data = json.load(fh)
        except (TimeoutError, urllib.error.URLError) as e:
            if attempt < 2:
                print(f"    {type(e).__name__}, retrying in 10s"); time.sleep(10); continue
            raise
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403):
                try:    msg = json.load(e).get("error", {}).get("message", "")
                except Exception: msg = e.reason
                sys.exit(f"\nAnthropic API {e.code}: {msg}\n"
                         f"  Aborting the batch - this affects every request, not just this protocol.")
            if e.code in (429, 500, 502, 503, 529) and attempt < 2:
                wait = 5 * (2 ** attempt)
                print(f"    transient {e.code}, retrying in {wait}s")
                time.sleep(wait); continue
            raise
        txt = "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
        if re.search(r"\{.*\}", txt, re.S):
            break
        last = (data.get("stop_reason"), len(txt), data.get("usage",{}).get("output_tokens"))
        if attempt < 2:
            print(f"    no JSON in response (stop_reason={last[0]}, {last[1]} chars) - re-asking")
            time.sleep(2); continue
    else:
        raise RuntimeError(f"no JSON after 3 attempts (last: stop_reason={last[0]}, "
                           f"text={last[1]} chars, out_tokens={last[2]})")
    if False:
      try:
        pass
      except urllib.error.HTTPError as e:
        try:    err = json.load(e).get("error", {}).get("message", "")
        except Exception: err = e.reason
        hint = ("  The key is org-scoped. Either pass --workspace-id wrkspc_... (or store it:\n"
                "    security add-generic-password -U -a \"$USER\" -s ANTHROPIC_WORKSPACE_ID -w \"wrkspc_...\"\n"
                "  ) or create a workspace-scoped key in the Console."
                if "workspace" in err.lower() else
                "  The harness reads the key from Keychain service 'ANTHROPIC_API_KEY'.")
        sys.exit(f"\nAnthropic API {e.code}: {err}\n{hint}")
    txt = "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
    usage = data.get("usage",{})
    stop = data.get("stop_reason")
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise RuntimeError(f"no JSON in response (stop_reason={stop}, "
                           f"text={len(txt)} chars, out_tokens={usage.get('output_tokens')})"
                           + ("  -- hit max_tokens; raise --max-tokens" if stop=="max_tokens" else ""))
    try:
        return json.loads(m.group(0)), usage
    except json.JSONDecodeError as e:
        raise RuntimeError(f"malformed JSON (stop_reason={stop}, {len(txt)} chars): {e}")

def compute(scores, dims, dim6, matrix, total_max_wt):
    raw = {d["id"]: sum(scores.get(it["id"],{}).get("score",0) for it in d["items"]) for d in dims}
    wt  = sum(raw[d["id"]] * d["weight"] for d in dims)
    overall = round(wt / total_max_wt * 100)
    d5 = raw[5]
    dec = next((m for m in matrix if m["oMin"] <= overall <= m["oMax"] and m["d5Min"] <= d5 <= m["d5Max"]), None)
    flags = [d["name"] for d in dims if raw[d["id"]] > d["rfThresh"]]
    raw6 = sum(scores.get(it["id"],{}).get("score",0) for it in dim6["items"])
    return dict(raw=raw, weighted=round(wt,1), overall=overall, dim5_raw=d5,
                decision=dec["dec"] if dec else "?", decision_desc=dec["desc"] if dec else "",
                red_flags=flags, dim6_raw=raw6, dim6_max=dim6["maxRaw"])

def find_docs(mnemonic):
    """Rank candidates so a short mnemonic can't steal a longer one's file.

    1 = filename stem is exactly the mnemonic      (ATHN.pdf -> ATHN)
    2 = stem before "_SJCRH" is the mnemonic       (SCDIC-II_SJCRH-HEM_... -> SCDIC-II)
    3 = mnemonic appears as a whole token          (Study_Document_TOPMed_... -> TOPMED)
    Rank 3 is only used when nothing better exists, so "ATHN" prefers ATHN.pdf
    over "ATHN TRANSCENDS_SJCRH-...pdf" (which is rank 3 for ATHN, rank 1 for its own).
    """
    norm = lambda s: re.sub(r"[^a-z0-9]","",s.lower())
    mn = norm(mnemonic)
    aliases = {norm(a) for a in ALIAS.get(mnemonic.upper(), [])}
    cands = {}
    for d in DOCS:
        if not d.exists(): continue
        for f in d.iterdir():
            if f.suffix.lower() not in EXTS: continue
            base = f.name[: -len(f.suffix)]
            toks = [norm(t) for t in re.split(r"[^A-Za-z0-9]+", base) if t]
            nb, sj = norm(base), norm(base.split("_SJCRH")[0])
            ranks = []
            for w in {mn} | aliases:
                if nb == w:  ranks.append(1)
                if sj == w:  ranks.append(2)
            # an explicit alias token beats a bare-mnemonic token, so "ATHN" resolves
            # to ATHNdataset_... rather than stealing "ATHN TRANSCENDS_...pdf"
            if aliases & set(toks): ranks.append(3)
            if mn in toks:          ranks.append(4)
            if any(t.startswith(w) for w in ({mn} | aliases) if len(w) >= 4 for t in toks):
                ranks.append(5)
            if ranks:
                r = min(ranks)
                cands[f] = min(cands.get(f, 99), r)
    if not cands: raise FileNotFoundError(f"no protocol document for {mnemonic}")
    cands = [(r, f) for f, r in cands.items()]
    # rank order, then largest first - a stub cover page loses to the real document
    return [f for _, f in sorted(cands, key=lambda c: (c[0], -c[1].stat().st_size))]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mnemonics", nargs="+")
    ap.add_argument("--dry-run", action="store_true", help="build prompt, report size, make no API call")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"default {DEFAULT_MODEL}")
    ap.add_argument("--workspace-id", default=None, help="for org-scoped keys (wrkspc_...)")
    ap.add_argument("--force", action="store_true", help="rescore even if results/<mn>.json exists")
    ap.add_argument("--max-chars", type=int, default=None,
                    help="override the tool's MAX_CHARS (default: value in index.html)")
    ap.add_argument("--doc", default=None, help="force a specific document path (single mnemonic only)")
    ap.add_argument("--max-tokens", type=int, default=32000, help="response cap (default 32000)")
    ap.add_argument("--min-chars", type=int, default=8000, help="refuse documents shorter than this (default 8000)")
    a = ap.parse_args()
    dims, dim6, matrix, total_max_wt, max_chars = rubric.load()
    if a.max_chars: max_chars = a.max_chars
    OUT.mkdir(exist_ok=True)
    key = None if a.dry_run else api_key()
    wsid = workspace_id(a.workspace_id)
    if wsid and not a.dry_run: print(f"workspace: {wsid[:14]}…")
    failed = []
    for mn in a.mnemonics:
      if not a.force and not a.dry_run and (OUT / f"{mn}.json").exists():
        print(f"\n=== {mn} ===\n  already scored - skipping (use --force to redo)"); continue
      try:
        doc = text = None; rejected = []
        cands = [pathlib.Path(a.doc)] if a.doc else find_docs(mn)
        for cand in cands:
            try:
                t = extract_text(cand)
                if len(t) < a.min_chars:
                    rejected.append(f"{cand.name} ({len(t):,} chars < {a.min_chars:,})"); continue
                doc, text = cand, t; break
            except RuntimeError as ex:
                rejected.append(f"{cand.name} ({ex})"); continue
        if doc is None:
            raise RuntimeError("no usable document; rejected: " + "; ".join(dict.fromkeys(rejected)))
        for rj in dict.fromkeys(rejected): print(f"  skipped {rj}")
        prompt, trunc, n = build_prompt(text, dims, dim6, max_chars)
        print(f"\n=== {mn} ===\n  doc: {doc.name}\n  extracted: {len(text):,} chars"
              f"{'  (TRUNCATED to %s)' % f'{max_chars:,}' if trunc else ''}\n  prompt: {len(prompt):,} chars, {n} items")
        if a.dry_run: continue
        t0 = time.time()
        resp, usage = call_claude(prompt, key, a.model, wsid, a.max_tokens)
        sc = resp.get("scores", resp)
        missing = [it["id"] for d in dims+[dim6] for it in d["items"] if it["id"] not in sc]
        res = compute(sc, dims, dim6, matrix, total_max_wt)
        print(f"  model: {a.model}  {time.time()-t0:.0f}s  in={usage.get('input_tokens')} out={usage.get('output_tokens')}")
        if missing: print(f"  !! missing item scores: {missing}")
        print(f"  OVERALL {res['overall']}/100   weighted {res['weighted']}/{total_max_wt}   -> {res['decision']}")
        for d in dims:
            print(f"     D{d['id']} {d['name'][:38]:<40} raw {res['raw'][d['id']]:>2}/{d['maxRaw']}"
                  f"  (rf>{d['rfThresh']}){'  <-- RED FLAG' if d['name'] in res['red_flags'] else ''}")
        print(f"     D6 supplemental{'':<26} raw {res['dim6_raw']:>2}/{res['dim6_max']}")
        (OUT / f"{mn}.json").write_text(json.dumps(
            {"mnemonic":mn,"document":doc.name,"model":a.model,"score_basis":("full_protocol (OCR)" if "ocr" in doc.name.lower() else "full_protocol"),"truncated":trunc,
             "usage":usage,"result":res,"scores":sc}, indent=2), encoding="utf-8")
        print(f"  wrote results/{mn}.json")
      except SystemExit: raise
      except Exception as ex:
        failed.append((mn, f"{type(ex).__name__}: {ex}"))
        print(f"  !! FAILED {mn}: {type(ex).__name__}: {ex}")
    if failed:
        print(f"\n{len(failed)} failed:")
        for mn, e in failed: print(f"   {mn}: {e}")

if __name__ == "__main__":
    main()
