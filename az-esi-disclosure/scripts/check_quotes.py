#!/usr/bin/env python3
"""Check a draft before it reaches the user: quotations, citation labels, banned phrases, length.

Usage: python3 check_quotes.py <draft.md> [--user-text FILE ...] [--max-words N]
Python 3 standard library only; nothing to install. Run it from anywhere: it finds this
skill's sources from its own location.

Sources, found next to this script:
  chapters/*.md                        (raji)
  references/rules.md, references/cases/*.md, and only the **Quote:** lines of
  references/authorities.md            (az-esi-disclosure; summaries are not quotable)
  every --user-text file               (the user's own documents, extracted with code)

Checks, one line per problem:
  QUOTE NOT FOUND  a quotation of 4+ words, in "double quotes" or a > block quote, that no
                   single source contains word for word. Fragments split by an ellipsis must
                   all appear, in order, in the same source. Footnote digits stuck to a word
                   in the source ("proof1", "[person]:1") may be kept or dropped, and a
                   quote may run across a "## p. N" page heading.
  UNKNOWN LABEL    a "RAJI (Civil) <Topic> <N>" cite naming no instruction in any chapter's
                   Contents line (raji only).
  BANNED           a phrase from BANNED below.
  TOO LONG         over --max-words.

Exits 1 if there is any problem, 0 if the draft is clean. New checks go in this file.
This file is identical in every skill that ships it; tests/ checks that.
"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNED = {
    "good law": "never call a case good law; tell the user to KeyCite or Shepardize it",
    "it is important to note": "filler", "it's important to note": "filler",
    "it is worth noting": "filler", "it's worth noting": "filler", "in conclusion": "filler",
    "in summary": "filler", "as an initial matter": "filler", "needless to say": "filler",
    "it should be noted": "filler", "this is crucial": "filler", "plays a crucial role": "filler",
    "a key consideration": "filler", "in today's": "filler", "delve": "filler",
    "navigate the complexities": "filler", "robust": "filler", "comprehensive overview": "filler",
    "i hope this helps": "filler", "let me know if you have any questions": "filler",
    "great question": "filler",
}
LABEL = re.compile(r"RAJI(?: \(Civil\))?(?: \d+(?:st|nd|rd|th))?\s+"
                   r"([A-Z][A-Za-z’'–—\- ]*?[A-Za-z])\s+(\d+[A-Za-z]?\d*)\b")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("―", "-").replace("**", "")
    s = re.sub(r"-\s*\n\s*", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def drop_footnotes(s):
    return re.sub(r"(?<=[a-z\]\):;,])\d{1,2}(?= |$)", "", s)


def sources(user_texts):
    raw = {}
    for p in sorted((ROOT / "chapters").glob("*.md")):
        raw[p.name] = p.read_text()
    ref = ROOT / "references"
    for p in [ref / "rules.md", *sorted((ref / "cases").glob("*.md"))]:
        if p.exists():
            raw[p.name] = p.read_text()
    auth = ref / "authorities.md"
    if auth.exists():
        raw[auth.name] = "\n".join(l for l in auth.read_text().splitlines() if "**Quote:**" in l)
    for u in user_texts:
        raw[u] = pathlib.Path(u).read_text()
    raw = {k: re.sub(r"^## p\. \d+[ \t]*$", "", v, flags=re.M) for k, v in raw.items()}
    return [(norm(v), drop_footnotes(norm(v))) for v in raw.values()]


def labels():
    found = set()
    for p in (ROOT / "chapters").glob("*.md"):
        for line in p.read_text().splitlines()[:15]:
            if line.startswith("**Contents:**"):
                for item in line[len("**Contents:**"):].split(" · "):
                    found.add(norm(re.sub(r"\s*\(.*$", "", item)))
    return found


def in_order(parts, text):
    i = 0
    for p in parts:
        i = text.find(p, i)
        if i < 0:
            return False
        i += len(p)
    return True


def quotations(draft):
    found = re.findall(r"[\"“]([^\"“”]+)[\"”]", draft)
    block = []
    for line in draft.splitlines() + [""]:
        if line.lstrip().startswith(">"):
            block.append(line.lstrip()[1:].strip())
        elif block:
            found.append(" ".join(block))
            block = []
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--user-text", action="append", default=[],
                    help="a file holding the user's own documents, which may be quoted")
    ap.add_argument("--max-words", type=int)
    a = ap.parse_args()

    draft = pathlib.Path(a.draft).read_text()
    srcs = sources(a.user_text)
    problems = 0

    quotes = quotations(draft)
    for q in quotes:
        if len(q.split()) < 4 or q.lstrip().startswith("RAJI"):
            continue
        parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:\.\.\.|…)\s*", norm(q))]
        parts = [p for p in parts if p]
        bare = [drop_footnotes(p) for p in parts]
        if not any(in_order(parts, raw) or in_order(bare, clean) for raw, clean in srcs):
            problems += 1
            print("QUOTE NOT FOUND: " + q[:110])

    known = labels()
    if known:
        for topic, num in LABEL.findall(draft):
            if norm(f"{topic} {num}") not in known:
                problems += 1
                print(f"UNKNOWN LABEL: {topic} {num} (no chapter's Contents line has it; "
                      "a trailing digit may be a footnote marker)")

    low = norm(draft)
    for phrase, why in BANNED.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            problems += 1
            print(f"BANNED: \"{phrase}\" ({why})")

    words = len(re.findall(r"\b\w[\w'-]*\b", draft))
    if a.max_words and words > a.max_words:
        problems += 1
        print(f"TOO LONG: {words} words; cap is {a.max_words}. Cut, don't summarize.")

    print(f"{len(quotes)} quotations, {words} words, {problems} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
