"""Behavior tests for every script the skills ship. Run: python3 -m unittest discover tests"""
import pathlib, re, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAJI_CHECK = ROOT / "raji/scripts/check_quotes.py"
ESI_CHECK = ROOT / "az-esi-disclosure/scripts/check_quotes.py"
DEADLINES = ROOT / "az-esi-disclosure/scripts/deadlines.py"
CITES = ROOT / "shred/scripts/cites.py"
# Quotes authorities.md checked against the page image, whose OCR text is garbled.
OCR_GARBLED = {
    "the willfulness or inadvertence of a party’s (or attorney’s) conduct.",  # "■willfulnessor"
    "Delay, standing alone, does not necessarily establish prejudice.",  # two columns interleaved
}


def run(script, *args, draft=None):
    with tempfile.TemporaryDirectory() as d:
        if draft is not None:
            p = pathlib.Path(d) / "draft.md"
            p.write_text(draft)
            args = (str(p),) + args
        r = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class RajiCheck(unittest.TestCase):
    def test_real_quote_and_label_pass(self):
        code, out = run(RAJI_CHECK, draft=(
            'Under RAJI (Civil) Defamation 1A, "[Name of Defendant] made, said, or wrote a '
            'defamatory statement of fact about [Name of Plaintiff]" is the first element.'))
        self.assertEqual(code, 0, out)

    def test_invented_quote_fails(self):
        code, out = run(RAJI_CHECK, draft='"The defendant must pay triple damages always."')
        self.assertEqual(code, 1)
        self.assertIn("QUOTE NOT FOUND", out)

    def test_invented_block_quote_fails(self):
        code, out = run(RAJI_CHECK, draft="> The defendant must pay triple damages always.\n")
        self.assertIn("QUOTE NOT FOUND", out)

    def test_quote_may_drop_footnote_digit(self):
        code, out = run(RAJI_CHECK, draft=(
            '"of [any] [name of defendant] [party] [person]: 1. The nature, extent, and duration"'))
        self.assertEqual(code, 0, out)

    def test_made_up_label_fails(self):
        code, out = run(RAJI_CHECK, draft="See RAJI (Civil) Defamation 1 for the elements.")
        self.assertIn("UNKNOWN LABEL: Defamation 1", out)

    def test_labels_missing_before_now_present(self):
        code, out = run(RAJI_CHECK, draft=(
            "RAJI (Civil) Standard 5a, RAJI (Civil) Standard 5b, RAJI (Civil) Personal Injury Damages 1."))
        self.assertEqual(code, 0, out)

    def test_good_law_banned(self):
        code, out = run(RAJI_CHECK, draft="That case is still good law.")
        self.assertIn("BANNED", out)


class EsiCheck(unittest.TestCase):
    def test_copies_identical(self):
        self.assertEqual(RAJI_CHECK.read_bytes(), ESI_CHECK.read_bytes())

    def test_holding_summary_is_not_quotable(self):
        # Allstate's Holding line in authorities.md is a summary, not the court's words.
        code, out = run(ESI_CHECK, draft='"Good cause is read broadly and weighs the reason for the late disclosure"')
        self.assertIn("QUOTE NOT FOUND", out)

    def test_quote_across_page_break(self):
        code, out = run(ESI_CHECK, draft=(
            'Good cause "gives trial judges a modicum of discretion to ensure that cases are not '
            'ordinarily won or lost on the basis of harmless missed deadlines."'))
        self.assertEqual(code, 0, out)

    def test_user_text_is_quotable(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Defendant will produce all relevant ESI at a later date.")
        code, out = run(ESI_CHECK, "--user-text", f.name,
                        draft='They wrote that they "will produce all relevant ESI at a later date."')
        self.assertEqual(code, 0, out)

    def test_word_cap(self):
        code, out = run(ESI_CHECK, "--max-words", "3", draft="one two three four five")
        self.assertIn("TOO LONG", out)

    def test_every_bundled_case_quote_is_in_its_opinion(self):
        ref = ROOT / "az-esi-disclosure/references"
        spec = __import__("importlib.util").util.spec_from_file_location("cq", ESI_CHECK)
        cq = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(cq)
        opinions = {re.search(r"(\d+ Ariz\. \d+)", p.name).group(1): cq.norm(
            re.sub(r"^## p\. \d+[ \t]*$", "", p.read_text(), flags=re.M))
            for p in (ref / "cases").glob("*.md")}
        case, checked = None, 0
        for line in (ref / "authorities.md").read_text().splitlines():
            if line.startswith("### "):
                m = re.search(r"(\d+ Ariz\. \d+)", line)
                case = m.group(1) if m else None
            if case in opinions and "**Quote:**" in line:
                for q in re.findall(r"[\"“]([^\"“”]+)[\"”]", line):
                    if len(q.split()) < 4:
                        continue
                    parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:\.\.\.|…)\s*", cq.norm(q))]
                    parts = [p for p in parts if p]
                    text = opinions[case]
                    ok = cq.in_order(parts, text) or cq.in_order(
                        [cq.drop_footnotes(p) for p in parts], cq.drop_footnotes(text))
                    if q in OCR_GARBLED:
                        continue
                    self.assertTrue(ok, f"{case}: {q[:80]}")
                    checked += 1
        self.assertGreater(checked, 30)


class Deadlines(unittest.TestCase):
    def test_forty_day_production(self):
        code, out = run(DEADLINES, "period", "2026-10-22", "40")
        self.assertIn("Tuesday, December 1, 2026", out)
        self.assertIn("No holidays applied", out)

    def test_short_period_skips_weekend_and_listed_holiday(self):
        code, out = run(DEADLINES, "period", "2026-11-06", "3", "--holidays", "2026-11-11")
        self.assertIn("= Thursday, November 12, 2026", out)

    def test_long_period_rolls_off_weekend(self):
        code, out = run(DEADLINES, "period", "2026-10-01", "30")  # Oct 31, 2026 is a Saturday
        self.assertIn("= Monday, November 2, 2026", out)

    def test_before_an_event_moves_earlier(self):
        code, out = run(DEADLINES, "before", "2026-12-15", "30")  # Nov 15, 2026 is a Sunday
        self.assertIn("= Friday, November 13, 2026", out)

    def test_set_date_on_weekend(self):
        code, out = run(DEADLINES, "date", "2026-11-14")
        self.assertIn("serve by Friday, November 13, 2026", out)

    def test_bad_input_prints_usage(self):
        for args in (("period", "2026-12-15", "-60"), ("period", "2026-13-01", "4"), ("period", "x", "y"), ()):
            code, out = run(DEADLINES, *args)
            self.assertEqual(code, 1, args)
            self.assertIn("Usage:", out)


class Cites(unittest.TestCase):
    DRAFT = ("Doe sues under A.R.S. § 23-1501(A)(3) and Ariz. R. Civ. P. 26.1(a)(9).\n"
             "See Wayne Cook Enters., Inc. v. Fain Props. Ltd. P'ship, 196 Ariz. 146, 149 (App. 1999); "
             "Doe v. Acme Corp., 123 Ariz. 456 (1980).\n"
             "Also Rule 37(c)(1) and 42 U.S.C. § 2000e-2(a).\n")

    def test_inventory_without_sources(self):
        code, out = run(CITES, draft=self.DRAFT)
        self.assertEqual(code, 0)
        self.assertIn("6 cites, 6 unsourced", out)
        self.assertIn("42 U.S.C. § 2000e-2(a)", out)

    def test_sourced_by_reporter_or_short_name(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Wayne Cook v. Fain, 196 Ariz. 146. Rule 37(c)(1).")
        code, out = run(CITES, "--sources", f.name, draft=self.DRAFT)
        self.assertRegex(out, r"SOURCED +line 2 +Wayne Cook")
        self.assertRegex(out, r"UNSOURCED +line 2 +Doe v. Acme")
        self.assertRegex(out, r"SOURCED +line 3 +Rule 37\(c\)\(1\)")


if __name__ == "__main__":
    unittest.main()
