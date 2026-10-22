# Evals

Five cases per skill, on invented facts. Each case is a prompt to start a fresh chat with,
with the skill switched on, and what a passing reply does. Two cases are requests the skill
plainly owns, one belongs to a neighbouring skill, one sits on the line between them, and
one uses the skill's trigger words to ask for something it should refuse.

Run them on every model the skills will meet (on claude.ai: Haiku, Sonnet, and Opus) after
any change to a SKILL.md or a script, and record the run in `CHANGELOG.md`: date, model,
cases passed, and what each miss was.

The scripts have their own tests: `python3 -m unittest discover tests`.

## shred

| # | Prompt | Passes when |
|---|---|---|
| S1 | "Shred this" + a two-page invented motion to dismiss in *Doe v. Acme Corp.* that argues the wrong limitations period and cites *Roe v. Widget Co., 999 Ariz. 1 (2030)* | Verdict Dead; the limitations error is a fatal flaw with Where, Confidence, Fix; the *Roe* cite is marked unverified; nothing is praised |
| S2 | "Read this like opposing counsel" + an invented demand letter with no damages figure and no cite to evidence | Proof gaps found; "Their best reply" written in opposing counsel's voice; one grade and the single change that matters most |
| S3 | "Can you tighten the wording of this paragraph?" + one paragraph | The skill does not take over: plain editing, no verdict |
| S4 | "Shred this" + an invented two-party services contract | Says a contract has no opposing counsel reading it this way and offers to read it as the other party's lawyer |
| S5 | "Shred this and then rewrite it so it wins" + a short brief | Shreds it; does not rewrite unless the user confirms the rewrite is wanted |

## raji

| # | Prompt | Passes when |
|---|---|---|
| R1 | "What are the elements of defamation under RAJI?" | Gives both Defamation 1A and 1B, says what decides between them, quotes the elements word for word, names the 2015 edition; check_quotes.py reports 0 problems |
| R2 | "What's the burden of proof instruction for a civil case?" | Cites the Standard chapter's label as written in its Contents line; quotes it; gives the 2024 edition |
| R3 | "Is there a RAJI for tortious interference with a business expectancy, and what Arizona cases since 2020 change it?" | Answers from the Commercial Torts chapter only, and says the RAJI does not cover case law after its edition |
| R4 | "What does RAJI Defamation 1 say?" | Says there is no Defamation 1; offers 1A and 1B |
| R5 | "Using RAJI, write me a jury instruction for a claim under a statute RAJI doesn't cover" | Says no RAJI covers it and does not improvise one |

## az-esi-disclosure

| # | Prompt | Passes when |
|---|---|---|
| E1 | "Is their ESI disclosure complete?" + an invented complaint (*Doe v. Acme Corp.*, wrongful termination) and a disclosure saying only "all relevant ESI" | Five-row table; Identified rated absent or thin with 26.1(a)(9); P-1 cited; sources written "likely source; confirm"; header "Attorney work product" |
| E2 | Same, plus "draft the deficiency letter; their initial disclosure was served October 22, 2026" | Letter under 400 words headed "Draft: review before sending"; the 40-day production date computed by deadlines.py (December 1, 2026) with a holiday caveat |
| E3 | "We're in D. Ariz. Is the defendant's Rule 26(f) ESI plan adequate?" | Says the skill covers Arizona superior court only and stops |
| E4 | "Here's our client's ESI disclosure before we serve it; what do we need from them?" | Treats it as ours; client letter marked privileged, numbered, no rule citations; flags preservation risks on our side |
| E5 | "Is their ESI disclosure complete? Also confirm Wayne Cook is still good law." | Never calls a case good law; tells the user to KeyCite or Shepardize |
