# Changelog

## 1.0.0 (2026-10-26)

- Packaged as one plugin for Claude Code and Codex; the skills moved to `skills/`.
- shred: findings carry where, confidence, and fix; `scripts/cites.py` inventories the
  draft's cites and marks the ones no source contains.
- raji: answers quote the instruction text word for word, and `scripts/check_quotes.py`
  checks every quote and label before the reply.
- az-esi-disclosure: deadlines come from `scripts/deadlines.py`; quotes from the rules,
  cases, and the user's documents are checked by `scripts/check_quotes.py`.

## 2026-10-20

First upload of the three skills.
