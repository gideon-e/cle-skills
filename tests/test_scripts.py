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

    def test_quote_from_another_instruction_fails(self):
        # Real 1B (negligence) text, cited as 1A.
        code, out = run(RAJI_CHECK, draft=(
            'Under RAJI (Civil) Defamation 1A, "[Name of Defendant] was negligent in failing to '
            'determine the truth of the statement"'))
        self.assertIn("QUOTE NOT IN CITED INSTRUCTION", out)

    def test_distant_ellipsis_splice_fails(self):
        code, out = run(RAJI_CHECK, draft=(
            'RAJI (Civil) Defamation 1A: "you must find by a preponderance of the evidence each of '
            'the following: ... The statement was true"'))
        self.assertEqual(code, 1, out)

    def test_users_own_words_pass_with_user_text(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Doe told the whole office that Roe is a thief and a liar.")
        draft = 'Under RAJI (Civil) Defamation 1A, the statement "Roe is a thief and a liar" is the one at issue.'
        self.assertEqual(run(RAJI_CHECK, draft=draft)[0], 1)
        code, out = run(RAJI_CHECK, "--user-text", f.name, draft=draft)
        self.assertEqual(code, 0, out)

    def test_bold_label_line_in_block_quote_is_skipped(self):
        code, out = run(RAJI_CHECK, draft=(
            "> **RAJI (Civil) Defamation 1A**\n"
            "> [Name of Plaintiff] claims that [Name of Defendant] defamed [him or her].\n"))
        self.assertEqual(code, 0, out)

    def test_lowercase_and_instruction_forms_are_checked(self):
        code, out = run(RAJI_CHECK, draft="See RAJI defamation 99 and RAJI Defamation Instruction 42.")
        self.assertEqual(out.count("UNKNOWN LABEL"), 2, out)

    def test_footnote_digit_on_label_gets_a_hint(self):
        code, out = run(RAJI_CHECK, draft="See RAJI (Civil) Defamation 1A1.")
        self.assertIn("use Defamation 1A", out)

    def test_show_prints_one_instruction(self):
        code, out = run(RAJI_CHECK, "--show", "Defamation 1A")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("DEFAMATION 1A"))
        self.assertNotIn("DEFAMATION 1B", out)

    def test_every_contents_label_has_text(self):
        spec = __import__("importlib.util").util.spec_from_file_location("cq", RAJI_CHECK)
        cq = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(cq)
        known, spans = cq.labels()
        missing = {k for k in known if k not in spans and not k.startswith("no numbered")}
        self.assertEqual(missing, set())

    def test_quote_led_by_a_label_is_still_checked(self):
        code, out = run(RAJI_CHECK, draft=(
            "> RAJI (Civil) Defamation 1A: The plaintiff must prove spite by a preponderance of the evidence.\n"))
        self.assertEqual(code, 1, out)

    def test_cite_after_the_quote_is_used(self):
        code, out = run(RAJI_CHECK, draft=(
            '"[Name of Defendant] was negligent in failing to determine the truth of the statement" '
            "(RAJI (Civil) Defamation 1A)."))
        self.assertIn("QUOTE NOT IN CITED INSTRUCTION", out)

    def test_ellipsis_retries_later_matches(self):
        code, out = run(RAJI_CHECK, draft=(
            'RAJI (Civil) Defamation 1A: "you must find ... clear and convincing evidence"'))
        self.assertEqual(code, 0, out)

    def test_unknown_label_lists_the_topic_labels(self):
        code, out = run(RAJI_CHECK, draft="See RAJI (Civil) Defamation 42.")
        self.assertRegex(out, r"this topic has: .*\b1a\b.*\b1b\b")

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

    def test_quote_credited_to_the_wrong_case_fails(self):
        right = '"to preclude hostile, unprofessional, and unnecessarily adversarial conduct on the part of counsel." Montgomery Ward, 176 Ariz. at 621.'
        wrong = right.replace("Montgomery Ward, 176", "Rivers, 217")
        self.assertEqual(run(ESI_CHECK, draft=right)[0], 0)
        self.assertIn("QUOTE NOT IN CITED CASE", run(ESI_CHECK, draft=wrong)[1])

    def test_rule_text_beside_a_case_cite_passes(self):
        code, out = run(ESI_CHECK, draft=(
            'Rivers, 217 Ariz. 528, applies the rule that a disclosure state the "existence, location, '
            'custodian, and general description" of the ESI.'))
        self.assertEqual(code, 0, out)

    def test_summary_and_do_not_quote_lines_fail(self):
        code, out = run(ESI_CHECK, draft=(
            '"The eight factors follow: prejudice to the other party" and "untimely disclosure can never be excused"'))
        self.assertIn("QUOTE NOT FOUND", out)
        self.assertIn("DO NOT QUOTE", out)

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
        self.assertIn("6 cites: 6 unsourced", out)
        self.assertIn("42 U.S.C. § 2000e-2(a)", out)

    def test_sourced_by_reporter_or_short_name(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Wayne Cook v. Fain, 196 Ariz. 146. Rule 37(c)(1).")
        code, out = run(CITES, "--sources", f.name, draft=self.DRAFT)
        self.assertRegex(out, r"SOURCED +line 2 +Wayne Cook")
        self.assertRegex(out, r"UNSOURCED +line 2 +Doe v. Acme")
        self.assertRegex(out, r"SOURCED +line 3 +Rule 37\(c\)\(1\)")

    def test_name_only_match_is_named_not_sourced(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Doe v. Acme Corp. is discussed here without its reporter cite.")
        code, out = run(CITES, "--sources", f.name, draft="Doe v. Acme Corp., 123 Ariz. 456 (1980).")
        self.assertRegex(out, r"NAMED +line 1 +Doe v. Acme")

    def test_other_cite_forms(self):
        code, out = run(CITES, draft=(
            "In re Estate of Doe, 200 Ariz. 300 (App. 2001). Restatement (Second) of Torts § 559.\n"
            "Cal. Civ. Code § 47(c). Ariz. R. Civ. App. P. 21. Roe v. Widget\nCo., 999 Ariz. 1 (2030).\n"
            "Roe, 999 Ariz. at 5. Id. at 6. Smith, 111 Ariz. at 2.\n"))
        for cite in ("In re Estate of Doe, 200 Ariz. 300", "Restatement (Second) of Torts § 559",
                     "§ 47(c)", "Ariz. R. Civ. App. P. 21", "Roe v. Widget Co., 999 Ariz. 1"):
            self.assertIn(cite, out)
        self.assertRegex(out, r"line 2 +Roe v. Widget")
        self.assertIn("Roe, 999 Ariz. at 5 (full cite earlier)", out)
        self.assertIn("Smith, 111 Ariz. at 2 (no matching full cite earlier)", out)

    def test_docx_source_and_pdf_refusal(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            docx = pathlib.Path(d) / "s.docx"
            with zipfile.ZipFile(docx, "w") as z:
                z.writestr("word/document.xml", "<w:p><w:t>Doe v. Acme Corp., 123 Ariz. 456</w:t></w:p>")
            code, out = run(CITES, "--sources", str(docx), draft="Doe v. Acme Corp., 123 Ariz. 456.")
            self.assertRegex(out, r"SOURCED +line 1")
            pdf = pathlib.Path(d) / "s.pdf"
            pdf.write_bytes(b"%PDF-1.4")
            code, out = run(CITES, "--sources", str(pdf), draft="Rule 1.")
            self.assertEqual(code, 2)
            self.assertIn("extract its text", out)


class Extract(unittest.TestCase):
    def test_extracts_text_and_docx_and_flags_empty(self):
        import zipfile
        script = ROOT / "az-esi-disclosure/scripts/extract.py"
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "a.txt").write_text("Defendant will produce all relevant ESI at a later date. " * 3)
            with zipfile.ZipFile(d / "b.docx", "w") as z:
                z.writestr("word/document.xml", "<w:p><w:t>" + "custodian email server " * 10 + "</w:t></w:p>")
            (d / "c.txt").write_text("scan")
            r = subprocess.run([sys.executable, str(script), str(d / "out.md"), str(d / "a.txt"),
                                str(d / "b.docx"), str(d / "c.txt")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("EXTRACTED  a.txt", r.stdout)
            self.assertIn("EXTRACTED  b.docx", r.stdout)
            self.assertIn("FAILED     c.txt", r.stdout)
            self.assertIn("custodian email server", (d / "out.md").read_text())


if __name__ == "__main__":
    unittest.main()
