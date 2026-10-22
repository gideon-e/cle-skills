#!/usr/bin/env python3
"""List every case, statute, and rule cite in a draft, and whether a source contains it.

Usage: python3 cites.py <draft.md> [--sources FILE ...]
Python 3 standard library only; nothing to install.

Prints one line per cite, in the order the draft gives them:
  SOURCED    <line>  <cite>   a --sources file contains it (for a case, its reporter cite
                              or "<party> v. <party>")
  UNSOURCED  <line>  <cite>   no source contains it: unverified until someone checks it
then a count. Always exits 0: this is an inventory, not a verdict. Judging whether a case
holds what the draft says it holds is still the reader's job.
"""
import argparse, pathlib, re

REPORTER = r"\d{1,4} (?:[A-Z][A-Za-z.']*\.?\s?){1,4}(?:\d[a-z]{1,2} )?\d{1,5}"
PATTERNS = [
    ("case", re.compile(r"((?:[A-Z][\w.'&-]*,? ){1,6}v\. (?:[\w.'&-]+,? ){1,8}?)(" + REPORTER + r")")),
    ("statute", re.compile(r"A\.R\.S\. §§? ?\d+-\d+(?:\.\d+)?(?:\([A-Za-z0-9]+\))*")),
    ("statute", re.compile(r"\d+ U\.S\.C\. §§? ?\d+[a-z]?(?:-\d+)?(?:\([A-Za-z0-9]+\))*")),
    ("rule", re.compile(r"(?:Ariz\. R\. Civ\. P\.|Fed\. R\. Civ\. P\.|Fed\. R\. Evid\.|Ariz\. R\. Evid\.|Rule) "
                        r"\d+(?:\.\d+)?(?:\([A-Za-z0-9]+\))*")),
]
SIGNAL = re.compile(r"^(?:(?:See|Also|Cf\.|But|Accord|Compare|And|As|Under|In(?! re\b)),? )+")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("§ ", "§").replace("–", "-")
    return re.sub(r"\s+", " ", s).lower()


def found(kind, cite, extra, corpus):
    if kind == "case":
        name, rep = extra
        parties = [p.strip(" ,") for p in name.split(" v. ")]
        short = f"{parties[0].split()[-1]} v. {parties[1].split()[0]}" if len(parties) == 2 else name
        return norm(rep) in corpus or norm(short) in corpus
    return norm(cite) in corpus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--sources", nargs="*", default=[])
    a = ap.parse_args()
    corpus = norm(" ".join(pathlib.Path(s).read_text() for s in a.sources))
    seen, missing = [], 0
    for n, line in enumerate(pathlib.Path(a.draft).read_text().splitlines(), 1):
        for kind, pat in PATTERNS:
            for m in pat.finditer(line):
                cite = m.group(0).strip(" ,")
                if kind == "case":
                    cite = SIGNAL.sub("", cite)
                key = norm(cite)
                if key in seen or (kind == "rule" and any(key in s for s in seen)):
                    continue
                seen.append(key)
                ok = found(kind, cite, m.groups() if kind == "case" else None, corpus)
                missing += not ok
                print(f"{'SOURCED  ' if ok else 'UNSOURCED'}  line {n}  {cite}")
    print(f"{len(seen)} cites, {missing} unsourced")


if __name__ == "__main__":
    main()
