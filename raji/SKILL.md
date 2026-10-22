---
name: raji
description: Answers questions about Arizona civil jury instructions (RAJI) from the instruction text, never memory. Use for the elements of a claim, the burden of proof, or what a RAJI says.
---

# Arizona civil jury instructions (RAJI)

Models often make up RAJI numbers and paraphrase elements wrong. This skill works only from
the civil instruction text in `chapters/`. If no chapter covers the question, say so and
stop; RAJI (Criminal), federal model instructions, and other states' instructions are not
here.

## Get the text first

1. Pick the chapter from the table below and open its file.
2. Line 9 of each file is its **Contents** line, listing the instructions by label. Print
   the one you need with `python3 scripts/check_quotes.py --show "Defamation 1A"`, which
   gives the instruction with its Use Note and Source.
3. A number stuck to the end of a word or label (`Proof1`, `9A1`) is a footnote marker, not
   part of the label. Cite `9A1` as Instruction 9A.
4. If the instruction points to another instruction, read that one too.

| Chapter | Topic | Edition | File |
|---|---|---|---|
| 1 | Preliminary | 2020 | `chapters/1-preliminary-2020.md` |
| 2 | Standard | 2024 | `chapters/2-standard-2024.md` |
| 3 | Fault | 2013 | `chapters/3-fault-2013.md` |
| 4 | Negligence | 2018 | `chapters/4-negligence-instructions-2018.md` |
| 5 | Medical negligence | 2020 | `chapters/5-med-negligence-2020.md` |
| 6 | Product liability | 2020 | `chapters/6-product-liability-2020.md` |
| 7 | Insurance bad faith | 2022 | `chapters/7-bad-faith-instructions_2022.md` |
| 8 | Premises liability | 2013 | `chapters/8-premises-liability-2013.md` |
| 9 | Personal injury damages | 2025 | `chapters/9-personal-injury-damages-2025.md` |
| 10 | Personal injury damages-only trials | 2023 | `chapters/10-personal-injury-damages-only-trials-2023.md` |
| 11 | Verdict forms | 2013 | `chapters/11-verdict-forms-2013.md` |
| 12 | Contracts | 2015 | `chapters/12-contracts-2015.md` |
| 13 | Eminent domain | 2013 | `chapters/13-eminent-domain-2013.md` |
| 14 | Employment | 2015 | `chapters/14-employment-2015.md` |
| 15 | Commercial torts | 2017 | `chapters/15-commercial-torts-2017.md` |
| 16 | Intentional torts | 2015 | `chapters/16-intentional-torts-2015.md` |
| 17 | Agency | 2013 | `chapters/17-agency-2013.md` |
| 18 | Defamation | 2015 | `chapters/18-defamation-2015.md` |
| 19 | Residential eviction actions | 2013 | `chapters/19-residential-eviction-actions-2013.md` |
| 20 | Invasion of privacy | 2023 | `chapters/20-privacy-instructions-2023.md` |
| 22 | Adult guardianship | 2025 | `chapters/22-adult-guardianship-instructions-2025.md` |
| 22 | Nuisance damages | 2017 | `chapters/22-nuisance-damages-2017.md` |
| 22a | Adult Protective Services Act | 2025 | `chapters/22a-apsa-raji-instructions-2025-06-04.md` |

Two chapters share 22, as in the State Bar's file names. Text extracted from the State
Bar's PDFs May 7, 2026; checked word by word October 15, 2026. Chapters 11 and 22 (adult
guardianship) have no numbered labels; search their text.

## Answer from the text

- Start with the answer in one sentence.
- Quote the operative language word for word. Anything in quotation marks must appear in
  the file exactly as written; mark any words you cut with an ellipsis. Cite by the
  chapter's label, outside quotation marks, before the quote: RAJI (Civil) Defamation 1A.
- For elements, give a numbered list in the instruction's own words, and say who has the
  burden and what standard applies.
- Give the Use Note and Source points that change how the instruction is used: when to
  give it, what to modify, which case it rests on.
- When the choice between instructions turns on a fact or a ruling (actual malice or
  negligence, 1A or 1B), give both and say what decides it. Which one to request is the
  lawyer's call; if the user's facts point one way, say so and say it is a read, not a
  finding.
- Say what the RAJI does not cover: case law after the chapter's edition, a claim with no
  RAJI. Don't improvise an instruction.
- Give the chapter's edition year. A RAJI is a pattern instruction, not a statute, and
  courts can depart from it; check the State Bar's RAJI page for a newer edition.

## Useful extras, when asked

- An element chart: one row per element, with columns for "our evidence" and "gap". Head
  it "Attorney work product".
- A proposed modified instruction, with every change from the pattern shown in brackets.

## Check before replying

Save your answer as a file and run `python3 scripts/check_quotes.py <answer.md>`, with
`scripts/` in this skill's folder (Python 3 standard library only; nothing to install).
Add `--user-text <file>` with the user's own documents, extracted with code, when you quote
them. It checks every quotation of 4 or more words, block quotes included, against the
chapters and against the instruction cited before it; every "RAJI (Civil) <label>" cite
against the Contents lines; and filler.

- On a quote problem, print the instruction with `--show` and re-read it; fix the words or
  the cite, never just the quotation marks.
- On UNKNOWN LABEL, take the right label from the Contents line. On BANNED, rewrite the
  sentence.
- Rerun until it reports 0 problems. Then reply, and end with one line saying the quotes
  and labels were checked against the chapter text and the choice of instruction was not.

When an answer is wrong in a way the check missed, tell the user and propose the check to
add to `scripts/check_quotes.py`.
