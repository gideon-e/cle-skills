#!/usr/bin/env python3
"""Check a draft before it reaches the user: quotations, citation labels, banned phrases, length.

Usage: python3 check_quotes.py <draft.md> [--user-text FILE ...] [--max-words N]
       python3 check_quotes.py --show "Defamation 1A"     (raji: print one instruction)
Python 3 standard library only; nothing to install. Run it from anywhere: it finds this
skill's sources from its own location.

Sources, found next to this script:
  chapters/*.md                        (raji)
  references/rules.md, references/cases/*.md, and only the quoted words on the
  **Quote:** lines of references/authorities.md   (az-esi-disclosure; our summaries,
                                       Holdings, and lead-ins are not quotable)
  every --user-text file               (the user's own documents, extracted with code)

Checks, one line per problem:
  QUOTE NOT FOUND   a quotation of 4+ words, in "double quotes" or a > block quote, that no
                    single source contains word for word. Fragments split by an ellipsis
                    must all appear, in order and within 400 characters of each other,
                    in the same source; quote parts further apart separately.
                    Footnote digits stuck to a word in the source ("proof1", "[person]:1")
                    may be kept or dropped, and a quote may run across a "## p. N" heading.
                    Quotations under 4 words are not checked.
  QUOTE NOT IN CITED INSTRUCTION
                    (raji) the quote is real but not in the instruction cited most recently
                    before it.
  QUOTE NOT IN CITED CASE
                    (az-esi-disclosure) the quote is real but not from the case whose
                    "<vol> Ariz." cite comes right after it (or just before it).
  DO NOT QUOTE      (az-esi-disclosure) a passage authorities.md marks **Do not quote:**.
  UNKNOWN LABEL     (raji) a "RAJI (Civil) <Topic> <N>" cite naming no instruction in any
                    chapter's Contents line.
  BANNED            a phrase from BANNED below.
  TOO LONG          over --max-words.

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
                   r"([A-Za-z][A-Za-z’'–—\- ]*?[A-Za-z])\s+(?:Instruction\s+)?(\d+[A-Za-z]?\d*)\b")
HEADING = re.compile(r"^([A-Z][A-Z ,’'–—\-&]+?) (\d+[A-Za-z]?\d*)\s*$")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("―", "-").replace("**", "")
    s = re.sub(r"-\s*\n\s*", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def drop_footnotes(s):
    return re.sub(r"(?<=[a-z\]\):;,])\d{1,2}(?= |$)", "", s)


def pair(text):
    return norm(text), drop_footnotes(norm(text))


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
        lines = auth.read_text().splitlines()
        raw[auth.name] = "\n".join(q for l in lines if l.startswith("- **Quote:**")
                                   for q in re.findall(r"[\"“]([^\"“”]+)[\"”]", l))
    raw = {k: re.sub(r"^## p\. \d+[ \t]*$", "", v, flags=re.M) for k, v in raw.items()}
    users = [pair(pathlib.Path(u).read_text()) for u in user_texts]
    return [pair(v) for v in raw.values()], users


def do_not_quote():
    """The passages authorities.md marks **Do not quote:**, whatever source they come from."""
    auth = ROOT / "references" / "authorities.md"
    if not auth.exists():
        return []
    return [q for l in auth.read_text().splitlines() if l.startswith("- **Do not quote:**")
            for q in re.findall(r"[\"“]([^\"“”]+)[\"”]", l)]


def case_texts():
    """(az-esi-disclosure) For each case in authorities.md, keyed "<vol> ariz.": its quoted
    words there plus its bundled opinion, if any."""
    ref = ROOT / "references"
    if not (ref / "authorities.md").exists():
        return {}
    out, key = {}, None
    for l in (ref / "authorities.md").read_text().splitlines():
        if l.startswith("### "):
            m = re.search(r"(\d+) Ariz\. \d+", l)
            key = f"{m.group(1)} ariz." if m else None
            if key:
                out[key] = ""
        elif key and l.startswith("- **Quote:**"):
            out[key] += " ".join(re.findall(r"[\"“]([^\"“”]+)[\"”]", l)) + "\n"
    for p in (ref / "cases").glob("*.md"):
        m = re.search(r"(\d+) Ariz\. \d+", p.name)
        if m and f"{m.group(1)} ariz." in out:
            out[f"{m.group(1)} ariz."] += re.sub(r"^## p\. \d+[ \t]*$", "", p.read_text(), flags=re.M)
    return {k: pair(v) for k, v in out.items()}


CASE_CITE = re.compile(r"(\d+) Ariz\. (?:at )?\d+")


def cited_case(draft, start, end, cases):
    """The case a quotation is attributed to: the Ariz. cite right after it, else just before."""
    after = CASE_CITE.search(draft, end, end + 120)
    before = [m for m in CASE_CITE.finditer(draft, max(0, start - 300), start)]
    m = after or (before[-1] if before else None)
    key = f"{m.group(1)} ariz." if m else None
    return key if key in cases else None


def labels():
    """Every label in the chapters' Contents lines, and the text of each instruction."""
    known, spans = set(), {}
    for p in (ROOT / "chapters").glob("*.md"):
        lines = p.read_text().splitlines()
        for line in lines[:15]:
            if line.startswith("**Contents:**"):
                for item in line[len("**Contents:**"):].split(" · "):
                    known.add(norm(re.sub(r"\s*\(.*$", "", item)))
        heads = []
        for i, line in enumerate(lines):
            m = HEADING.match(line.strip())
            if m:
                label = norm(f"{m.group(1)} {m.group(2)}")
                if label not in known and label[:-1] in known:  # a footnote digit on the heading
                    label = label[:-1]
                if label in known:
                    heads.append((i, label))
        for (i, label), nxt in zip(heads, heads[1:] + [(len(lines), None)]):
            spans[label] = spans.get(label, "") + "\n" + "\n".join(lines[i:nxt[0]])
    return known, spans


def in_order(parts, text, gap=400):
    i, first = 0, None
    for p in parts:
        j = text.find(p, i)
        if j < 0 or (first is not None and j - i > gap):
            return False
        first = j if first is None else first
        i = j + len(p)
    return True


def matches(q, srcs):
    parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:\.\.\.|…)\s*", norm(q))]
    parts = [p for p in parts if p]
    bare = [drop_footnotes(p) for p in parts]
    return any(in_order(parts, raw) or in_order(bare, clean) for raw, clean in srcs)


def quotations(draft):
    """(position, text) for each double-quoted span and each > block quote."""
    found = [(m.start(), m.group(1)) for m in re.finditer(r"[\"“]([^\"“”]+)[\"”]", draft)]
    block, pos, start = [], 0, 0
    for line in draft.splitlines(keepends=True) + [""]:
        s = line.strip()
        if s.startswith(">"):
            body = s[1:].strip()
            if not block:
                start = pos
            if not (re.fullmatch(r"\*\*.*\*\*", body) or body.startswith("RAJI")):
                block.append(body)
        elif block:
            found.append((start, " ".join(block)))
            block = []
        pos += len(line)
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", nargs="?")
    ap.add_argument("--user-text", action="append", default=[],
                    help="a file holding the user's own documents, which may be quoted")
    ap.add_argument("--max-words", type=int)
    ap.add_argument("--show", metavar="LABEL", help='print one RAJI instruction, e.g. "Defamation 1A"')
    a = ap.parse_args()
    known, spans = labels()

    if a.show:
        label = norm(a.show)
        label = label if label in spans else label[:-1] if label[:-1] in spans else None
        if not label:
            sys.exit(f"UNKNOWN LABEL: {a.show}")
        print(spans[label].strip())
        sys.exit(0)
    if not a.draft:
        ap.error("a draft file is required")

    draft = pathlib.Path(a.draft).read_text()
    srcs, users = sources(a.user_text)
    problems = 0

    cites = []
    for m in LABEL.finditer(draft):
        topic, num = m.groups()
        label = norm(f"{topic} {num}")
        topic_known = any(k.rsplit(" ", 1)[0] == norm(topic) for k in known)
        if label in known:
            cites.append((m.start(), m.end(), label))
        elif topic_known or topic.istitle():
            problems += 1
            hint = f"; use {topic} {num[:-1]}" if label[:-1] in known else ""
            print(f"UNKNOWN LABEL: {topic} {num} (no chapter's Contents line has it{hint})")

    banned_quotes = [pair(b) for b in do_not_quote()]
    cases = case_texts()
    rules_md = ROOT / "references" / "rules.md"
    rules = [pair(rules_md.read_text())] if rules_md.exists() else []  # a rule quoted beside a case cite
    quotes = quotations(draft)
    for pos, q in quotes:
        if banned_quotes and matches(q, banned_quotes):
            problems += 1
            print("DO NOT QUOTE (authorities.md says why): " + q[:90])
            continue
        if len(q.split()) < 4 or q.lstrip().startswith("RAJI"):
            continue
        if users and matches(q, users):
            continue
        if not matches(q, srcs):
            problems += 1
            print("QUOTE NOT FOUND: " + q[:110])
            continue
        case = cited_case(draft, pos, pos + len(q) + 2, cases)
        if case and not matches(q, [cases[case]]) and not matches(q, rules):
            problems += 1
            print(f"QUOTE NOT IN CITED CASE ({case.title()}): " + q[:90])
            continue
        before = [c for c in cites if c[1] <= pos]
        if before and before[-1][2] in spans and not matches(q, [pair(spans[before[-1][2]])]):
            problems += 1
            print(f"QUOTE NOT IN CITED INSTRUCTION ({before[-1][2].title()}): " + q[:90])

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
