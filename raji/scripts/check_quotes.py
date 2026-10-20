#!/usr/bin/env python3
"""Check a draft before it reaches the user: quotes, length, and filler.

Usage: python3 check_quotes.py <draft.md> [--user-text <file>] [--max-words N]
Python 3 standard library only; nothing to install.

1. Every quotation of 4+ words must appear word for word in this skill's chapters/*.md
   or in the --user-text file.
2. With --max-words, the draft must be at or under N words.
3. Filler phrases listed in FILLER below are flagged.

Prints one line per problem and exits 1 if there is any, 0 if the draft is clean.
"""
import argparse, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent.parent / "chapters"
FILLER = [
    "it is important to note", "it's important to note", "it is worth noting", "it's worth noting",
    "in conclusion", "in summary", "as an initial matter", "needless to say", "it should be noted",
    "this is crucial", "plays a crucial role", "a key consideration", "in today's", "delve",
    "navigate the complexities", "robust", "comprehensive overview", "i hope this helps",
    "let me know if you have any questions", "great question",
]


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"-\s*\n\s*", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--user-text", help="file holding the user's own documents, which may be quoted")
    ap.add_argument("--max-words", type=int)
    a = ap.parse_args()

    draft = pathlib.Path(a.draft).read_text()
    sources = sorted(HERE.glob("*.md"))
    corpus = " ".join(p.read_text() for p in sources if p.exists())
    if a.user_text:
        corpus += " " + pathlib.Path(a.user_text).read_text()
    corpus = norm(corpus)

    problems = 0
    quotes = re.findall(r"[\"“]([^\"“”]+)[\"”]", draft)
    for q in quotes:
        if len(q.split()) < 4:
            continue
        parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:\.\.\.|…)\s*", norm(q)) if p.strip()]
        if not all(p in corpus for p in parts):
            problems += 1
            print("QUOTE NOT FOUND: " + q[:110])

    words = len(re.findall(r"\b\w[\w'-]*\b", draft))
    if a.max_words and words > a.max_words:
        problems += 1
        print(f"TOO LONG: {words} words; cap is {a.max_words}. Cut, don't summarize.")

    low = norm(draft)
    for f in FILLER:
        if f in low:
            problems += 1
            print(f"FILLER: \"{f}\"")

    print(f"{len(quotes)} quotations, {words} words, {problems} problems")
    sys.exit(1 if problems else 0)


main()
