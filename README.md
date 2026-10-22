# Three Claude skills for Arizona litigators

| Skill | What it does | Try saying |
|---|---|---|
| **az-esi-disclosure** | Checks whether a disclosure of electronically stored information is complete, and drafts the deficiency letter. Includes the full Rules 6(a), 16, 26, 26.1, 26.2, 34, 37, and 45.2, notes on 18 Arizona and 2 federal cases, and the full text of 11 of the Arizona opinions. | "Is their ESI disclosure complete?" (attach it and the complaint) |
| **raji** | Answers jury-instruction questions from the RAJI text, which is included. | "What are the elements of defamation under RAJI?" |
| **shred** | Reads your draft the way opposing counsel will, then grades it. | "Shred this" (attach the draft) |

## Setup (5 minutes, once)

1. **Turn on code execution.** On claude.ai: Settings → Capabilities → **Code execution and file creation**. Skills need it. On a Team or Enterprise plan, your admin turns it on.
2. **Download the three .zip files** from the latest release on this repository's Releases page. Don't unzip them.
3. **Upload each one.** Customize → Skills → **+** → Create skill → **Upload a skill**. Pick the .zip, then switch the skill on.
4. **Use it.** Start a new chat and ask in plain English. You don't need a slash command. Claude picks up the skill when your request fits it.

## Good to know

- **Rules and cases are dated.** The rule text is current through September 1, 2026. The case notes are current as of October 8, 2026 for most cases and October 15, 2026 for the preservation and expert-disclosure cases; `authorities.md` dates each group. KeyCite or Shepardize every case before you rely on it.
- **raji includes the RAJI (Civil) chapters**, extracted from the State Bar of Arizona's chapter PDFs on May 7, 2026 and checked word by word against them on October 15, 2026. Each answer gives the chapter's edition year, so check the State Bar's RAJI page for anything newer.
- **You are the lawyer.** These skills mark gaps and unverified points rather than filling them in. Read every draft before it goes out.
- **Client material.** What you upload goes to Claude under your plan's terms. The skills label their output as work product or privileged, but a label doesn't make it so; follow your own confidentiality rules about what you upload.
- **Don't see a skill working?** Check that it's switched on under Customize → Skills, and start a new chat.

## For maintainers

- Test every script: `python3 -m unittest discover tests` (Python 3 standard library only).
- Build the uploads: `python3 tools/build.py` writes `dist/<skill>.zip`.
- Release: push a tag such as `v1.1.0`; the release workflow tests, builds, and attaches the zips.
- Model checks: run the cases in `evals/README.md` and record the run in `CHANGELOG.md`.
