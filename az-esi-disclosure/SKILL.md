---
name: az-esi-disclosure
description: Checks an Arizona Rule 26.1 ESI disclosure for gaps, ours or theirs, and drafts the letter to opposing counsel or our client. Use for "is this ESI disclosure complete" or an ESI meet-and-confer.
---

# Arizona ESI disclosure check

Arizona requires more ESI disclosure, earlier, than federal practice does, and parties
routinely under-disclose it. Cite only this skill's references. If they don't answer a
question, say so, and don't fill the gap from memory.

**Start with `references/index.md`.** It maps each issue to the rule subsection, the cases, and
the deficiency patterns. Open only what it points to.

- `references/deficiency-patterns.md`: 19 common ways an ESI disclosure falls short.
- `references/rules.md`: the full text of Rules 6(a), 16, 26, 26.1, 26.2, 34, 37, and 45.2,
  current through September 1, 2026.
- `references/authorities.md`: 18 Arizona cases and 2 federal ones (persuasive only), with
  checked quotes and pins.
- `references/cases/`: the full text of 11 of those opinions.

## Whose disclosure

- **Theirs:** the check, then on request a deficiency letter to opposing counsel.
- **Ours, before serving:** the same check, then a letter to the client listing what we need.
  Also flag preservation risks on our side: a hold sent late or to too few people, accounts
  disabled, or auto-delete left running.

If the user hasn't said whose it is, ask once.

## The check

Rate each line **complete**, **thin** (say what's missing), or **absent**, citing the rule.

1. **Identified (26.1(a)(8)-(9)).** Each likely source, with its existence, location,
   custodian, and description. Infer the sources from the claims.
2. **Withheld (26.1(h); 26(b)(6)).** Is anything withheld for privilege? If so, is there a log?
3. **Produced (26.1(c)(2)-(3)).** Due within 40 days of the initial disclosure, in the form
   requested, or native or reasonably usable.
4. **Conferred (26.1(c)(1)).** Has the ESI conference been held, with someone who knows the
   systems?
5. **Preserved (37(g); 45.2).** Any sign of lost ESI or a late or narrow hold.

**Dates.** Compute every deadline with `python3 scripts/deadlines.py` (Python 3 standard
library only; run it with no arguments for usage); never count by hand. Check any deadline the user states. Rule 6(a) governs a "time period" counted in days. A stipulated or ordered calendar
date that falls on a weekend isn't a counted period: tell the user to serve by the business day
before. `rules.md` has no holiday list, so tell the user to check holidays.

## Output: short and plain

The user wants a memo they can read in one minute. No preamble and no summary of their facts.

```
Bottom line: <one sentence>.

| Check | Rating | What's missing | Rule |
(the five lines above, one row each)

Top three gaps
1. <gap>: <what to get or ask for>. <rule>; <pattern P-N>; <case, if one fits>.
2. ...
3. ...

Deadlines: <date math, one line each>.
Your call: <judgment calls left to the lawyer, one line>.
```

Then the letter, only if the user asked for it. Keep it to one page:
- **To opposing counsel:** each gap with its rule and the specific item demanded, a reply
  date, a proposed conference with someone who knows their systems, and one sentence on
  37(c)(1) exclusion and the 26(d) joint statement. Firm, not hostile.
- **To our client:** what to preserve today, then what to send us, as a numbered list in plain
  words with no rule citations, and a reply date.

Before replying, save the user's documents, the memo, and the letter as three files, then run
`python3 scripts/check_quotes.py memo.md --user-text docs.md --max-words 350` and
`python3 scripts/check_quotes.py letter.md --user-text docs.md --max-words 400`.
Both scripts are Python 3 standard library only; nothing to install.
If either check fails, fix the draft and rerun it. Repeat until both report 0 problems, then
reply. If a draft is too long, cut it; don't summarize it.

## Always

- Quotation marks go only around words that appear exactly in a reference file or in the
  user's documents.
- When you cite a case, say which rule version it decided. Never call a case "good law"; tell
  the user to KeyCite or Shepardize first. Case notes are current as of October 2026.
- Never assume what a system holds. Write "likely source; confirm."
- The user is the lawyer. Mark every judgment call as theirs.
