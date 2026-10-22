# Changelog

## Unreleased

Quality pass: each skill audited against Anthropic's skill-authoring rules and graded before
and after against a build checklist and a legal skill design framework.

### shred
- Scope: names the drafts it fits, and offers another reading for a contract or client letter.
- Judges the draft under the law that controls it, and treats not knowing that law as a finding.
- New `scripts/cites.py` lists every cite in the draft and whether a document the user gave contains it; unsourced cites are marked unverified.
- Every finding carries where, confidence (High, Medium, Low), and fix; a fixed report shape with a work-product header; a re-read before replying.
- Removed a contradiction about covering every category when the draft is Dead.

### raji
- The chapter table moved into SKILL.md; `chapters.md` is gone.
- Fixed the sample cite (Defamation 1 does not exist; 1A and 1B do), and when the choice between instructions turns on a fact, both are given.
- `check_quotes.py` now also checks block quotes, accepts quotes with or without footnote digits, and checks every "RAJI (Civil)" label against the chapters' Contents lines.
- Contents lines: added Standard 5a and 5b; chapter 9's first instruction is listed as Personal Injury Damages 1, the label chapter 10 cites (its heading reads 10).
- Corrected the extraction date (May 7, 2026; checked October 15, 2026).

### az-esi-disclosure
- Scope: Arizona superior court civil cases only; federal, family, and justice court stop.
- `deadlines.py`: counts backward for a period before an event (Rule 6(a)(4)), takes the court's holidays with `--holidays`, refuses zero or negative days and bad dates with a usage line.
- `check_quotes.py` (shared with raji): quotes from `authorities.md` only its **Quote:** lines, never the Holding summaries; checks block quotes; quotes may cross a page break; rejects "good law".
- Opinions in `references/cases/`: reporter-page headings and a Contents line; the preceding opinion's text on the first page removed from six of them.
- Memo headed "Attorney work product", client letter marked privileged, every letter headed as a draft.
- Removed the reference to `scripts/rules_toc.py`, which was never shipped; added Rule 34 to the title of `rules.md`; corrected the README's rule and case counts.

### Repository
- `tests/`: behavior tests for every script, and layout tests for every skill.
- `tools/build.py` and a release workflow that attaches the three zips to a tagged release.
- `evals/README.md`: five cases per skill on invented facts.

### Models tested
None yet in this pass. The evals have not been run.

## 2026-10-20

First upload of the three skills.
