---
name: az-esi-disclosure
description: Checks an Arizona Rule 26.1 ESI disclosure for gaps, ours or theirs, and drafts the letter to opposing counsel or our client. Use for "is this ESI disclosure complete" or an ESI meet-and-confer.
---

# Arizona ESI disclosure check

Arizona requires more ESI disclosure, earlier, than federal practice does, and parties
routinely under-disclose it. Cite only this skill's references. If they don't answer a
question, say so, and don't fill the gap from memory.

It covers civil cases in Arizona superior court under the Arizona Rules of Civil
Procedure. A case in federal court (Fed. R. Civ. P. 26(f)), family court, or justice
court runs on rules this skill doesn't bundle: say so, and stop.

**Start with `references/index.md`.** It maps each issue to the rule subsection, the cases, and
the deficiency patterns. Open only what it points to.

- `references/deficiency-patterns.md`: 19 common ways an ESI disclosure falls short.
- `references/rules.md`: the full text of Rules 6(a), 16, 26, 26.1, 26.2, 34, 37, and 45.2,
  current through September 1, 2026.
- `references/authorities.md`: 18 Arizona cases and 2 federal ones (persuasive only), with
  checked quotes and pins, and the rule version each case decided.
- `references/cases/<case>, <vol> Ariz. <page> (<year>).md`: the full text of 11 of those
  opinions, one heading per reporter page.

## Whose disclosure

- **Theirs:** the check, then on request a deficiency letter to opposing counsel.
- **Ours, before serving:** the same check, then a letter to the client listing what we need.
  Also flag preservation risks on our side: a hold sent late or to too few people, accounts
  disabled, or auto-delete left running.

If the user hasn't said whose it is, ask once. Without the complaint, infer the likely
sources from what the user tells you about the claims and say that you did.

## The check

Rate each line **complete**, **thin** (say what's missing), or **absent**, citing the rule.

1. **Identified (26.1(a)(8)-(9)).** Each likely source, with its existence, location,
   custodian, and description. Infer the sources from the claims, and write each inferred
   one as "likely source; confirm". Never assume what a system holds.
2. **Withheld (26.1(h); 26(b)(6)).** Is anything withheld for privilege? If so, is there a log?
3. **Produced (26.1(c)(2)-(3)).** Due within 40 days of the initial disclosure, in the form
   requested, or native or reasonably usable.
4. **Conferred (26.1(c)(1)).** Has the ESI conference been held, with someone who knows the
   systems?
5. **Preserved (37(g); 45.2).** Any sign of lost ESI or a late or narrow hold.

**Dates.** Compute every deadline with `python3 scripts/deadlines.py` (run it with no
arguments for usage); never count by hand. It counts forward (`period`) and backward
(`before`) under Rule 6(a), backs a weekend set date up a day (`date`), and skips any
holidays passed with `--holidays`; it knows no holidays of its own, so ask the user for the
court's or tell them to check. If the user states a deadline and the script disagrees,
show both computations and mark it as their call. Extra days for the method of service
aren't in `rules.md`; flag them as a question rather than adding them.

## Output: short and plain

The user wants a memo they can read in one minute. No preamble and no summary of their facts.

```
Attorney work product.

Bottom line: <one sentence>.

| Check | Rating | What's missing | Rule |
(the five lines above, one row each)

Top three gaps
1. <gap>: <what to get or ask for>. <rule>; <pattern P-N>; <case, decided under which rule version, if one fits>.
2. ...
3. ...

Deadlines: <date math, one line each>.
Your call: <judgment calls left to the lawyer, one line>.
```

Then the letter, only if the user asked for it. Keep it to one page and head it "Draft:
review before sending".
- **To opposing counsel:** each gap with its rule and the specific item demanded, a reply
  date, a proposed conference with someone who knows their systems, and one sentence on
  37(c)(1) exclusion and the 26(d) joint statement. Firm, not hostile.
- **To our client:** marked "Privileged and confidential: attorney-client communication".
  What to preserve today, then what to send us, as a numbered list in plain words with no
  rule citations, and a reply date.

## Check before replying

1. Extract the text of the user's documents with code into `docs.md`; don't retype it. If
   a document can't be extracted (a scan, an image), quote nothing from it and say so.
2. Save the memo and the letter as files and run, with `scripts/` in this skill's folder
   (Python 3 standard library only; nothing to install):
   `python3 scripts/check_quotes.py memo.md --user-text docs.md --max-words 350`
   `python3 scripts/check_quotes.py letter.md --user-text docs.md --max-words 400`
   It checks every quotation, block quotes included, against `rules.md`, the bundled
   opinions, the **Quote:** lines of `authorities.md` (never its Holding summaries), and
   `docs.md`; it also rejects "good law" and filler.
3. On QUOTE NOT FOUND, go back to the source and fix the words, or drop the quotation. If a
   draft is too long, cut it; don't summarize it. Return to step 2 until both report
   0 problems, then reply.

## Always

- When you cite a case, say which rule version it decided. Tell the user to KeyCite or
  Shepardize before relying on it; `authorities.md` gives the date its notes were current.
- The user is the lawyer. Mark every judgment call as theirs.
