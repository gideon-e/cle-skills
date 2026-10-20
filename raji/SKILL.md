---
name: raji
description: Answers questions about Arizona civil jury instructions (RAJI) from the instruction text, never memory. Use for the elements of a claim, the burden of proof, or what a RAJI says.
---

# Arizona civil jury instructions (RAJI)

Models often make up RAJI numbers and paraphrase elements wrong. This skill works only from the instruction text itself.

## Get the text first

1. Use `chapters.md` in this folder to find the chapter that fits the question.
2. Open that chapter's file in `chapters/<file>`. Its first line after the header lists every
   instruction in the chapter; read the one you need. When you need only one instruction, search the file for its label (for example `DEFAMATION 1`).
3. A number stuck to the end of a word or label (`Proof1`, `9A1`) is a footnote marker, not part of the label. Cite `9A1` as Instruction 9A.
4. If no chapter covers the question, say so and stop. Don't write elements from memory.

## Answer from the text

- Start with the answer in one sentence.
- Quote the operative language word for word. Anything in quotation marks must appear in the file exactly as written; mark any words you cut with an ellipsis. Cite it the way the chapter labels it (for example, "RAJI (Civil) Defamation 1").
- For elements, give a numbered list in the instruction's own words, and say who has the burden and what standard applies.
- Give the Use Note and Source points that change how the instruction is used, such as when to give it, what to modify, and which case it is based on.
- If the instruction points to another instruction, read that one too before answering.
- Say what the RAJI does not cover. If the question goes beyond it (case law after the chapter's date, a claim with no RAJI), say that, and don't improvise an instruction.
- Note the chapter's edition year. A RAJI is a pattern instruction, not a statute, and courts can depart from it.

## Useful extras, when asked

- An element chart: one row per element, with columns for "our evidence" and "gap."
- A proposed modified instruction, with every change from the pattern shown in brackets.

## Check before replying

Save your answer as a file and run `python3 scripts/check_quotes.py <answer.md>` (Python 3
standard library only; nothing to install). Fix every QUOTE NOT FOUND and rerun until it
reports 0 problems. Then reply.
