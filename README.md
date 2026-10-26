# Three Claude skills for Arizona litigators

| Skill | What it does | Try saying |
|---|---|---|
| **az-esi-disclosure** | Checks whether a disclosure of electronically stored information is complete, and drafts the deficiency letter. Includes the full Rules 6(a), 16, 26, 26.1, 26.2, 34, 37, and 45.2, notes on 18 Arizona and 2 federal cases, and the full text of 11 of the Arizona opinions. | "Is their ESI disclosure complete?" (attach it and the complaint) |
| **raji** | Answers jury-instruction questions from the RAJI text, which is included. | "What are the elements of defamation under RAJI?" |
| **shred** | Reads your draft the way opposing counsel will, then grades it. | "Shred this" (attach the draft) |

## Install

Each skill is a plain folder under `skills/` that follows the open
[Agent Skills](https://agentskills.io) format, so any agent that reads skills can use it.

- **Claude Code:** `/plugin marketplace add gideon-e/cle-skills`, then
  `/plugin install cle-skills@cle-skills`.
- **Codex:** add this repository as a plugin marketplace; it ships a Codex manifest too.
- **claude.ai:** turn on Settings → Capabilities → **Code execution and file creation**,
  download the three .zip files from the latest release, and upload each under
  Customize → Skills → **+** → **Upload a skill**. Don't unzip them.
- **Any other agent:** copy a folder from `skills/` into the agent's skills folder.

Then ask in plain English. Claude picks up a skill when the request fits it.

## Good to know

- **Rules and cases are dated.** The rule text is current through September 1, 2026. The case notes are current as of October 8, 2026 for most cases and October 15, 2026 for the rest; `authorities.md` dates each group. KeyCite or Shepardize every case before you rely on it.
- **raji includes the RAJI (Civil) chapters**, extracted from the State Bar of Arizona's chapter PDFs on May 7, 2026 and checked word by word against them on October 15, 2026. Each answer gives the chapter's edition year, so check the State Bar's RAJI page for anything newer.
- **You are the lawyer.** These skills mark gaps and unverified points rather than filling them in. Read every draft before it goes out.
- **Client material.** What you upload goes to Claude under your plan's terms. The skills label their output as work product or privileged, but a label doesn't make it so; follow your own confidentiality rules about what you upload.
- **Don't see a skill working?** Check that it's switched on under Customize → Skills, and start a new chat.

## License

The code and the skill instructions are MIT ([LICENSE](LICENSE)). The legal text bundled
with them is not ours to license:

- **Arizona Rules of Civil Procedure** (`skills/az-esi-disclosure/references/rules.md`)
  and **court opinions** (`skills/az-esi-disclosure/references/cases/`) are law, which no
  one can copyright (*Georgia v. Public.Resource.Org, Inc.*, 590 U.S. 255 (2020)). The
  opinion text is from the Harvard Caselaw Access Project's page scans.
- **RAJI (Civil)** (`skills/raji/chapters/`) is published by the State Bar of Arizona's
  Civil Jury Instructions Committee and remains the State Bar's.

## For maintainers

Only `skills/` reaches users. Everything else is for building and testing them.

- Test: `python3 -m unittest discover tests` (Python 3 standard library only).
- Release: bump the version in both `plugin.json` files, add a `CHANGELOG.md` entry, and
  push a tag such as `v1.0.0`. The release workflow tests, builds the zips
  (`tools/build.py`), and attaches them.
- Model checks: `evals/README.md`.
