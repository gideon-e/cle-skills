---
name: az-esi-disclosure
description: Checks an Arizona Rule 26.1 ESI disclosure for gaps, ours or theirs, and drafts the letter to opposing counsel or our client. Use for "is this ESI disclosure complete" or an ESI meet-and-confer.
license: MIT (https://github.com/gideon-e/cle-skills/blob/main/LICENSE) for the instructions, notes, and scripts. The rule text and court opinions in references/ are public law.
---

# Arizona ESI disclosure check

Arizona requires more ESI disclosure, earlier, than federal practice does, and parties
routinely under-disclose it. Every rule and case you cite comes from this skill's
references; where they are silent, say so and leave the gap open.

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
   one as "likely source; confirm". Say what a system holds only from the user's documents.
2. **Withheld (26.1(h); 26(b)(6)).** Is anything withheld for privilege? If so, is there a log?
3. **Produced (26.1(c)(2)-(3)).** Due within 40 days of the initial disclosure, in the form
   requested, or native or reasonably usable.
4. **Conferred (26.1(c)(1)).** Has the ESI conference been held, with someone who knows the
   systems?
5. **Preserved (37(g); 45.2).** Any sign of lost ESI or a late or narrow hold.

**Dates.** Compute every deadline with `python3 scripts/deadlines.py` (run it with no
arguments for usage) and paste its line into the memo. It knows no holidays, so ask the
user for the court's and pass them with `--holidays`. If the user states a deadline and
the script disagrees, show both computations and mark it as their call. Extra days for the
method of service aren't in `rules.md`; flag them as a question rather than adding them.

## Output: short and plain

The user wants a memo they can read in one minute, opening on the bottom line.

```
Attorney work product.

Bottom line: <one sentence>.

| Check | Rating | What's missing | Rule |
(the five lines above, one row each)

Top three gaps
1. <gap>: <what to get or ask for>. <rule>; <pattern P-N>; <case, decided under which rule version, if one fits>.
2. ...
3. ...

Deadlines: <deadlines.py output, one line each>.
Your call: <judgment calls left to the lawyer, one line>.
Law current through: rules September 1, 2026; case notes as dated in authorities.md.
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

1. Run `python3 scripts/extract.py docs.md <each document the user gave you>`, and quote
   the user's documents only from `docs.md`. A document it reports FAILED gets no
   quotation; tell the user which one.
2. Save the memo and the letter as files and run, with `scripts/` in this skill's folder
   (Python 3 standard library only; nothing to install):
   `python3 scripts/check_quotes.py memo.md --user-text docs.md --max-words 350`
   `python3 scripts/check_quotes.py letter.md --user-text docs.md --max-words 400`
   Its docstring lists what it checks and what it skips.
3. On a quote problem, go back to the source and fix the words or the cite, or drop the
   quotation. On BANNED, rewrite the sentence. On TOO LONG, cut whole lines until it
   fits. Return to step 2 until both report 0 problems, then reply. When a draft
   is wrong in a way the check missed, tell the user and suggest reporting it as an issue
   on the gideon-e/cle-skills repository, so the check can be added.

## Always

- Quotation marks go only around words that appear exactly in a reference file or in the
  user's documents, however short the quote.
- Tell the user to KeyCite or Shepardize every case before relying on it. Where
  `authorities.md` marks an old-to-new rule mapping [CONFIRM MAPPING], say the mapping is
  unconfirmed wherever you rely on it.
- The user is the lawyer. Mark every judgment call as theirs.
