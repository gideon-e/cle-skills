"""Each skill folder is a valid claude.ai upload and every file SKILL.md names exists."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


class Layout(unittest.TestCase):
    def test_three_skills(self):
        self.assertEqual([p.name for p in SKILLS], ["az-esi-disclosure", "raji", "shred"])

    def test_frontmatter(self):
        for s in SKILLS:
            text = (s / "SKILL.md").read_text()
            m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
            self.assertIsNotNone(m, s.name)
            self.assertEqual(m.group(1), s.name)
            self.assertLessEqual(len(m.group(2)), 1024, s.name)
            self.assertLess(len(text.splitlines()), 500, s.name)

    def test_named_paths_exist(self):
        for s in SKILLS:
            for path in re.findall(r"`((?:scripts|references|chapters)/[^`<>*]+?)`", (s / "SKILL.md").read_text()):
                self.assertTrue((s / path.split()[0]).exists(), f"{s.name}: {path}")

    def test_every_chapter_is_listed_and_has_contents(self):
        body = (ROOT / "raji/SKILL.md").read_text()
        for p in (ROOT / "raji/chapters").glob("*.md"):
            self.assertIn(f"`chapters/{p.name}`", body)
            self.assertTrue(p.read_text().splitlines()[8].startswith("**Contents:**"), p.name)

    def test_long_references_open_with_contents(self):
        for p in ROOT.glob("*/references/**/*.md"):
            lines = p.read_text().splitlines()
            if len(lines) > 100:
                self.assertTrue(any(l.startswith("**Contents:**") for l in lines[:40]), p.name)


if __name__ == "__main__":
    unittest.main()
