#!/usr/bin/env python3
"""Extract the text of the user's documents into one file for check_quotes.py --user-text.

Usage: python3 extract.py <out.md> <file> [<file> ...]
Python 3 standard library for .txt, .md, and .docx. A .pdf is read with the `pdftotext`
command or the `pypdf` package if either is already installed; nothing is installed here.

Prints one line per file, EXTRACTED or FAILED with the reason. Quote nothing from a file
that FAILED. Exits 1 if any file failed, 0 otherwise.
"""
import pathlib, re, shutil, subprocess, sys, zipfile


def pdf_text(p):
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    try:
        import pypdf
    except ImportError:
        raise ValueError("no pdftotext or pypdf available to read a .pdf")
    return "\n".join(page.extract_text() or "" for page in pypdf.PdfReader(str(p)).pages)


def text_of(p):
    suffix = p.suffix.lower()
    if suffix == ".docx":
        with zipfile.ZipFile(p) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        return re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    if suffix == ".pdf":
        return pdf_text(p)
    return p.read_text(errors="replace")


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    out, failed, chunks = pathlib.Path(argv[0]), 0, []
    for name in argv[1:]:
        p = pathlib.Path(name)
        try:
            text = text_of(p)
            if len(text.split()) < 20:
                raise ValueError("almost no text came out; it may be a scan or an image")
            chunks.append(f"# {p.name}\n\n{text}")
            print(f"EXTRACTED  {p.name}  {len(text.split())} words")
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
            failed += 1
            print(f"FAILED     {p.name}  {e}")
    out.write_text("\n\n".join(chunks))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
