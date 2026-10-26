"""Each skill folder meets the Agent Skills spec, every file SKILL.md names exists, and the
plugin manifests agree."""
import json, pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = sorted(p.parent for p in ROOT.glob("skills/*/SKILL.md"))


class Layout(unittest.TestCase):
    def test_three_skills(self):
        self.assertEqual([p.name for p in SKILLS], ["az-esi-disclosure", "raji", "shred"])

    def test_frontmatter(self):
        for s in SKILLS:
            text = (s / "SKILL.md").read_text()
            m = re.match(r"---\nname: (.+)\ndescription: (.+)\nlicense: (.+)\n---\n", text)
            self.assertIsNotNone(m, s.name)
            self.assertEqual(m.group(1), s.name)
            self.assertLessEqual(len(m.group(2)), 1024, s.name)
            self.assertLess(len(text.splitlines()), 500, s.name)

    def test_named_paths_exist(self):
        for s in SKILLS:
            for path in re.findall(r"`((?:scripts|references|chapters)/[^`<>*]+?)`", (s / "SKILL.md").read_text()):
                self.assertTrue((s / path.split()[0]).exists(), f"{s.name}: {path}")

    def test_every_chapter_is_listed_and_has_contents(self):
        body = (ROOT / "skills/raji/SKILL.md").read_text()
        for p in (ROOT / "skills/raji/chapters").glob("*.md"):
            self.assertIn(f"`chapters/{p.name}`", body)
            self.assertTrue(p.read_text().splitlines()[8].startswith("**Contents:**"), p.name)

    def test_long_references_open_with_contents(self):
        for p in ROOT.glob("skills/*/references/**/*.md"):
            lines = p.read_text().splitlines()
            if len(lines) > 100:
                self.assertTrue(any(l.startswith("**Contents:**") for l in lines[:40]), p.name)

    def test_manifests_agree(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["name"], codex["name"])
        self.assertIn(f"## {claude['version']}", (ROOT / "CHANGELOG.md").read_text())


if __name__ == "__main__":
    unittest.main()
