"""Extract the scoring rubric directly from the tool's index.html.

Single-sourcing the rubric means the harness can never drift from the app:
if the checklist changes in index.html, this picks it up automatically.
"""
import json, re, pathlib

BUNDLE = pathlib.Path(__file__).resolve().parent.parent / "complexitytool_offline-bundle" / "index.html"

def _block(src, decl):
    """Return the JS literal following `decl`, via bracket matching."""
    i = src.index(decl) + len(decl)
    while src[i] in " =\n\t": i += 1
    open_ch = src[i]; close_ch = {"[": "]", "{": "}"}[open_ch]
    depth, j, in_str, esc = 0, i, False, False
    while j < len(src):
        c = src[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == open_ch: depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0: return src[i:j+1]
        j += 1
    raise ValueError(f"unterminated block for {decl}")

def _to_json(js):
    # strip // comments that are not inside a string
    out, in_str, esc, k = [], False, False, 0
    while k < len(js):
        c = js[k]
        if in_str:
            out.append(c)
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True; out.append(c)
            elif c == "/" and k+1 < len(js) and js[k+1] == "/":
                while k < len(js) and js[k] != "\n": k += 1
                continue
            else: out.append(c)
        k += 1
    js = "".join(out)
    js = re.sub(r'([\{\[,])(\s*)([A-Za-z_]\w*)\s*:', r'\1\2"\3":', js)  # quote bare keys
    js = re.sub(r',(\s*[\}\]])', r'\1', js)                              # drop trailing commas
    return json.loads(js)

def load():
    src = BUNDLE.read_text(encoding="utf-8")
    dims = _to_json(_block(src, "const DIMS"))
    dim6 = _to_json(_block(src, "const DIM6"))
    matrix = _to_json(_block(src, "const MATRIX"))
    import re as _re
    total = float(_re.search(r"const TOTAL_MAX_WT\s*=\s*([\d.]+)", src).group(1))
    maxch = int(_re.search(r"const MAX_CHARS\s*=\s*([\d_]+)", src).group(1).replace("_", ""))
    return dims, dim6, matrix, total, maxch

if __name__ == "__main__":
    dims, dim6, matrix, total, maxch = load()
    print(f"dimensions: {len(dims)}   TOTAL_MAX_WT: {total} (sum of maxWt: {sum(d['maxWt'] for d in dims):.1f})   MAX_CHARS: {maxch:,}")
    for d in dims:
        print(f"  {d['id']}. {d['name'][:44]:<46} w={d['weight']:<4} items={len(d['items']):<3} "
              f"maxRaw={d['maxRaw']:<3} rfThresh={d['rfThresh']}")
    print(f"  6. {dim6['name'][:44]:<46} items={len(dim6['items'])} maxRaw={dim6['maxRaw']} (supplemental)")
    print(f"total scored items: {sum(len(d['items']) for d in dims) + len(dim6['items'])}")
    decs = sorted(set(m["dec"] for m in matrix))
    print(f"decision matrix cells: {len(matrix)}  decisions: {decs}")
    # every item must have exactly four 0-3 options
    bad = [it["id"] for d in dims+[dim6] for it in d["items"]
           if [o["s"] for o in it["opts"]] != [0,1,2,3]]
    print("items with non-standard 0-3 scale:", bad or "none")
