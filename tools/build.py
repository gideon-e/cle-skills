#!/usr/bin/env python3
"""Zip each skill for upload to claude.ai: dist/<skill>.zip, with the skill folder at the root.

Usage: python3 tools/build.py
Python 3 standard library only. Run the tests first: python3 -m unittest discover tests
"""
import pathlib, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
for skill in sorted(p.parent for p in ROOT.glob("*/SKILL.md")):
    out = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(skill.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, f.relative_to(ROOT))
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")
