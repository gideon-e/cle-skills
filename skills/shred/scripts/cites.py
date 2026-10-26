#!/usr/bin/env python3
"""List the case, statute, and rule cites in a draft, and whether a source contains each.

Usage: python3 cites.py <draft> [--sources FILE ...]
Python 3 standard library only; nothing to install. The draft and the sources may be
text, Markdown, or .docx. A .pdf can't be read here: extract its text to a .txt file first.

Prints one line per cite, in the order the draft gives them:
  SOURCED     line N  <cite>  a source contains this exact cite (for a case, its reporter cite)
  NAMED       line N  <cite>  a source names the case but not this reporter cite
  UNSOURCED   line N  <cite>  no source contains it
  SHORT FORM  line N  <cite>  "Roe, 999 Ariz. at 5" or "Id."; says whether a full cite
                              to the same volume and reporter appears earlier in the draft
then a count. Exits 0 after the inventory, 2 if a file can't be read.

What it catches: "<party> v. <party>, <vol> <reporter> <page>" and "In re <name>, ...";
A.R.S., U.S.C., and any other "§ N" statute; Restatement sections; Arizona and federal
rules, any "R. ... P. N" rule set, and bare "Rule N". It can miss a cite in another form,
so the reader still checks the draft for cites this list lacks. A SOURCED cite only means a
document the user gave contains it; whether the case holds what the draft says is the
reader's call.
"""
import argparse, pathlib, re, sys, zipfile

REPORTER = r"\d{1,4} (?:[A-Z][A-Za-z.']*\.?\s?){1,4}(?:\d[a-z]{1,2} )?\d{1,5}"
SUB = r"(?:\([A-Za-z0-9]+\))*"
PATTERNS = [
    ("case", re.compile(r"((?:[A-Z][\w.'&-]*,? ){1,6}v\. (?:[\w.'&-]+,? ){1,8}?)(" + REPORTER + r")(?! at)")),
    ("case", re.compile(r"(In re (?:[\w.'&-]+,? ){1,8}?)(" + REPORTER + r")(?! at)")),
    ("short", re.compile(r"\b[A-Z][\w.'-]+, (\d{1,4} (?:[A-Z][A-Za-z.']*\.?\s?){1,4}(?:\d[a-z]{1,2} )?)at \d+")),
    ("short", re.compile(r"\bId\.(?: at \d+)?")),
    ("statute", re.compile(r"A\.R\.S\. §§? ?\d+-\d+(?:\.\d+)?" + SUB)),
    ("statute", re.compile(r"\d+ U\.S\.C\. §§? ?\d+[a-z]?(?:-\d+)?" + SUB)),
    ("statute", re.compile(r"Restatement \([A-Z][a-z]+\) of [A-Z][\w ]+? §§? ?\d+[A-Za-z]?")),
    ("statute", re.compile(r"§§? ?\d+(?:[-.:]\d+)*[A-Za-z]?" + SUB)),
    ("rule", re.compile(r"(?:(?:Ariz|Fed|[A-Z][a-z]+)\. R\. (?:[A-Z][a-z]*\. )*(?:P|Evid)\.|Rule) \d+(?:\.\d+)?" + SUB)),
]
SIGNAL = re.compile(r"^(?:(?:See|Also|Cf\.|But|Accord|Compare|And|As|Under|In(?! re\b)),? )+")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("§ ", "§").replace("–", "-")
    return re.sub(r"\s+", " ", s).lower()


def read(path):
    p = pathlib.Path(path)
    if p.suffix.lower() == ".pdf":
        raise ValueError(f"{path}: a .pdf can't be read here; extract its text to a .txt file first")
    if p.suffix.lower() == ".docx":
        with zipfile.ZipFile(p) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    return p.read_text(errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--sources", nargs="*", default=[])
    a = ap.parse_args()
    try:
        draft = read(a.draft)
        corpus = norm(" ".join(read(s) for s in a.sources))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        sys.exit(print(f"Error: {e}", file=sys.stderr) or 2)

    # One flat string, so a cite split across two lines is still found; `offsets` maps
    # a position in it back to the draft's line number.
    parts = [re.sub(r"\s+", " ", l).strip() for l in draft.splitlines()]
    offsets, pos = [], 0
    for p in parts:
        offsets.append(pos)
        pos += len(p) + 1
    flat = " ".join(parts)

    def line_of(i):
        return max(n for n, o in enumerate(offsets, 1) if o <= i)

    hits = []
    for kind, pat in PATTERNS:
        for m in pat.finditer(flat):
            if any(s <= m.start() < e for s, e, *_ in hits):
                continue
            hits.append((m.start(), m.end(), kind, m))
    hits.sort()

    seen, full_reporters, counts = set(), [], {}
    for start, _, kind, m in hits:
        cite = m.group(0).strip(" ,")
        if kind == "case":
            cite = SIGNAL.sub("", cite)
        key = norm(cite)
        if key in seen:
            continue
        seen.add(key)
        if kind == "case":
            rep = norm(m.group(2))
            full_reporters.append(rep)
            name = norm(m.group(1)).strip(" ,")
            status = "SOURCED" if rep in corpus else "NAMED" if name and name.split(",")[0] in corpus else "UNSOURCED"
        elif kind == "short":
            vol = norm(m.group(1)).strip() if m.groups() else ""
            earlier = any(r.startswith(vol) for r in full_reporters) if vol else bool(full_reporters)
            status = "SHORT FORM"
            cite += " (full cite earlier)" if earlier else " (no matching full cite earlier)"
        else:
            status = "SOURCED" if key in corpus else "UNSOURCED"
        counts[status] = counts.get(status, 0) + 1
        print(f"{status:<11} line {line_of(start)}  {cite}")
    summary = ", ".join(f"{v} {k.lower()}" for k, v in sorted(counts.items()))
    print(f"{len(seen)} cites" + (f": {summary}" if summary else ""))


if __name__ == "__main__":
    main()
