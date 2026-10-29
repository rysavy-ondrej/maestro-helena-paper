#!/usr/bin/env python3
"""Static checks for a paper-forge project.

Usage: validate.py [PROJECT_DIR] [--max-pages N] [--anonymous]
       validate.py [PROJECT_DIR] --diagnose build/build.log

Checks Markdown sources against the bibliography, figures, and cross-reference
labels, then inspects the LaTeX/BibTeX logs and PDF from the last build.
Exits with status 1 if any error is found. With --diagnose, summarizes why the
last `make pdf` failed. Normally run through ./build.sh.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

CROSSREF_PREFIXES = ("fig:", "tbl:", "eq:", "sec:", "lst:")
IMAGE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")
RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg")

CITE_RE = re.compile(r"(?<![\w.@\\])-?@(?:\{([^}]+)\}|([A-Za-z0-9_][\w:.#$%&+?<>~/-]*))")
LATEX_CITE_RE = re.compile(r"\\(?:no)?cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
LABEL_DEF_RE = re.compile(r"\{#((?:fig|tbl|eq|sec|lst):[\w.:-]+)")
LATEX_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
LATEX_REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}")
IMAGE_RE = re.compile(r"!\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*<?([^)\s>]+)")
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]+)\}")
TODO_RE = re.compile(r"\[TODO\b|\bTODO:|\bFIXME\b|\[CITATION NEEDED\]", re.IGNORECASE)
RAW_LATEX_FENCE_RE = re.compile(r"(```+|~~~+)\s*\{=latex\}")
FENCE_RE = re.compile(r"^(```+|~~~+)[^\n]*\n.*?^\1\s*$", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
BIB_ENTRY_RE = re.compile(r"^\s*@(\w+)\s*[{(]\s*([^,\s]+)\s*,", re.M)
SELF_REFERENCE_RE = re.compile(r"\bour (?:previous|prior|earlier) (?:work|paper|study)\b|\bwe previously\b", re.I)


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, message):
        self.items.append((level, where, message))

    def count(self, level):
        return sum(1 for item in self.items if item[0] == level)

    def print(self):
        order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
        for level, where, message in sorted(self.items, key=lambda i: order[i[0]]):
            location = f"{where}: " if where else ""
            print(f"{level:<8}{location}{message}")
        print(f"\n{self.count('ERROR')} error(s), {self.count('WARNING')} warning(s), "
              f"{self.count('INFO')} note(s)")


def blank(match):
    """Replace matched text with spaces, keeping newlines so offsets stay valid."""
    return re.sub(r"[^\n]", " ", match.group(0))


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


class Source:
    def __init__(self, path, root):
        self.path = path
        self.rel = path.relative_to(root).as_posix()
        self.text = path.read_text(encoding="utf-8")
        without_comments = HTML_COMMENT_RE.sub(blank, self.text)
        # LaTeX commands are scanned in prose and raw LaTeX blocks, not in other code.
        self.latex_view = FENCE_RE.sub(
            lambda m: m.group(0) if RAW_LATEX_FENCE_RE.match(m.group(0)) else blank(m),
            without_comments)
        self.markdown_view = INLINE_CODE_RE.sub(blank, FENCE_RE.sub(blank, without_comments))

    def where(self, offset):
        return f"{self.rel}:{line_of(self.text, offset)}"


def load_sources(root):
    paths = []
    abstract = root / "paper" / "abstract.md"
    if abstract.exists():
        paths.append(abstract)
    paths.extend(sorted((root / "paper" / "sections").glob("*.md")))
    return [Source(p, root) for p in paths]


def parse_bib(path, report):
    entries = {}
    if not path.exists():
        report.add("ERROR", None, f"Bibliography not found: {path}")
        return entries
    text = path.read_text(encoding="utf-8")
    matches = [m for m in BIB_ENTRY_RE.finditer(text)
               if m.group(1).lower() not in ("comment", "string", "preamble")]
    rel = path.name
    for i, m in enumerate(matches):
        key = m.group(2)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.start():end]
        where = f"references/{rel}:{line_of(text, m.start())}"
        if key in entries:
            report.add("ERROR", where, f"Duplicate BibTeX key '{key}'")
        entries[key] = body
        fields = {f.lower() for f in re.findall(r"[,{]\s*(\w+)\s*=", body)}
        missing = [f for f in ("title", "year") if f not in fields]
        if not fields & {"author", "editor"}:
            missing.insert(0, "author")
        if missing:
            report.add("WARNING", where, f"Entry '{key}' is missing: {', '.join(missing)}")
        if re.search(r"\bTODO\b|\bFIXME\b|placeholder", body, re.I):
            report.add("WARNING", where, f"Entry '{key}' looks like a placeholder")
        if "doi" not in fields and m.group(1).lower() in ("article", "inproceedings"):
            report.add("INFO", where, f"Entry '{key}' has no DOI")
    return entries


def check_sources(root, sources, bib, report):
    cited = set()
    label_defs = {}
    label_refs = []

    for src in sources:
        for m in CITE_RE.finditer(src.markdown_view):
            key = (m.group(1) or m.group(2)).rstrip(".:;,?!/-")
            lowered = key[0].lower() + key[1:] if key else key
            if lowered.startswith(CROSSREF_PREFIXES):
                label_refs.append((lowered, src.where(m.start())))
            else:
                cited.add(key)
                if key not in bib:
                    report.add("ERROR", src.where(m.start()),
                               f"Citation key '{key}' not found in references.bib")

        for m in LATEX_CITE_RE.finditer(src.latex_view):
            for key in (k.strip() for k in m.group(1).split(",")):
                if not key or key == "*":
                    continue
                cited.add(key)
                if key not in bib:
                    report.add("ERROR", src.where(m.start()),
                               f"Citation key '{key}' not found in references.bib")

        for m in LABEL_DEF_RE.finditer(src.markdown_view):
            define_label(label_defs, m.group(1), src.where(m.start()), report)
        for m in LATEX_LABEL_RE.finditer(src.latex_view):
            define_label(label_defs, m.group(1), src.where(m.start()), report)
        for m in LATEX_REF_RE.finditer(src.latex_view):
            for key in m.group(1).split(","):
                label_refs.append((key.strip(), src.where(m.start())))

        image_paths = [(m.group(1), m.start()) for m in IMAGE_RE.finditer(src.markdown_view)]
        image_paths += [(m.group(1), m.start()) for m in INCLUDEGRAPHICS_RE.finditer(src.latex_view)]
        for image, offset in image_paths:
            check_image(root, image, src.where(offset), report)

        for lineno, line in enumerate(src.markdown_view.splitlines(), 1):
            if TODO_RE.search(line):
                report.add("WARNING", f"{src.rel}:{lineno}", f"Unresolved marker: {line.strip()[:80]}")

    referenced = set()
    for key, where in label_refs:
        referenced.add(key)
        if key not in label_defs:
            report.add("ERROR", where, f"Reference to undefined label '{key}'")
    for key, where in label_defs.items():
        if key.startswith(("fig:", "tbl:")) and key not in referenced:
            report.add("WARNING", where, f"'{key}' is never referenced in the text")

    for key in sorted(set(bib) - cited):
        report.add("INFO", None, f"BibTeX entry '{key}' is never cited")


def define_label(label_defs, key, where, report):
    if key in label_defs:
        report.add("ERROR", where, f"Label '{key}' already defined at {label_defs[key]}")
    else:
        label_defs[key] = where


def check_image(root, image, where, report):
    if re.match(r"[a-z]+://", image):
        report.add("ERROR", where, f"Remote image cannot be typeset: {image}")
        return
    path = root / image
    candidates = [path] if path.suffix else [path.with_suffix(ext) for ext in IMAGE_EXTENSIONS]
    found = next((c for c in candidates if c.exists()), None)
    if found is None:
        hint = " (paths are relative to the project root)" if image.startswith("..") else ""
        report.add("ERROR", where, f"Figure not found: {image}{hint}")
    elif found.suffix.lower() in RASTER_EXTENSIONS:
        report.add("INFO", where, f"Raster figure {image}; prefer vector PDF for plots and diagrams")


def check_freshness(root, sources, report):
    body = root / "latex" / "generated" / "body.tex"
    if not body.exists():
        report.add("INFO", None, "latex/generated/body.tex does not exist; run `make pdf`")
        return None
    newest = max((s.path.stat().st_mtime for s in sources), default=0)
    log = root / "build" / "main.log"
    if not log.exists():
        report.add("INFO", None, "build/main.log not found; build checks skipped (run `make pdf`)")
        return None
    if log.stat().st_mtime < newest:
        report.add("WARNING", None, "Sources changed after the last build; build checks may be stale")
    return log


GENERATED_SYMPTOMS = [
    (re.compile(r"\{\\#(?:fig|tbl|eq|sec):"), "ERROR", "literal crossref label; is pandoc-crossref running?"),
    (re.compile(r"\\begin\{longtable\}"), "ERROR", "longtable breaks two-column layouts; is the table filter running?"),
    (re.compile(r"\\begin\{Shaded\}"), "ERROR", "highlighted code block; remove the language class from the fence"),
    (re.compile(r"\\textasciitilde\{\}"), "WARNING", "literal '~'; use '\\ ' for a non-breaking space"),
    (re.compile(r"\\cite(?:author|year)"), "WARNING", "author/year citation; use the [@key] form"),
]


def check_generated(root, report):
    for path in sorted((root / "latex" / "generated").glob("*.tex")):
        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, level, message in GENERATED_SYMPTOMS:
                if pattern.search(line):
                    report.add(level, f"{rel}:{lineno}", f"Conversion problem: {message}")


def check_log(root, log, report, max_pages):
    text = log.read_text(encoding="latin-1")
    for m in re.finditer(r"^! (.*)$", text, re.M):
        report.add("ERROR", "build/main.log", f"LaTeX error: {m.group(1)}")
    for kind in ("Citation", "Reference"):
        keys = sorted(set(re.findall(rf"LaTeX Warning: {kind} [`']([^']+)' .*?undefined", text)))
        for key in keys:
            report.add("ERROR", "build/main.log", f"Undefined {kind.lower()} '{key}' in PDF")
    for m in re.finditer(r"^LaTeX Warning: File [`']([^']+)' not found", text, re.M):
        report.add("ERROR", "build/main.log", f"File not found: {m.group(1)}")
    for m in re.finditer(r"Missing character: There is no (.+?) in font", text):
        report.add("WARNING", "build/main.log", f"Missing character {m.group(1)}")
    if "Label(s) may have changed" in text:
        report.add("WARNING", "build/main.log", "Labels may have changed; rerun `make pdf`")

    overfull = [(float(w), m) for w, m in
                re.findall(r"^Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\) (.*)$", text, re.M)]
    significant = [o for o in overfull if o[0] > 1.0]
    if significant:
        worst = sorted(significant, reverse=True)[:5]
        detail = "; ".join(f"{w:.1f}pt {where}" for w, where in worst)
        report.add("WARNING", "build/main.log",
                   f"{len(significant)} overfull hbox(es) > 1pt; worst: {detail}")

    bitmap = sorted(set(re.findall(r"([a-z0-9]+)\.\d+pk\b", text)))
    if bitmap:
        report.add("ERROR", "build/main.log",
                   f"Bitmap (Type 3) fonts embedded: {', '.join(bitmap[:5])}; "
                   "load lmodern or a Type 1 font package")

    pages = re.search(r"Output written on .*?\((\d+) pages?", text)
    if pages:
        count = int(pages.group(1))
        if max_pages and count > max_pages:
            report.add("ERROR", "build/main.pdf", f"{count} pages exceeds the limit of {max_pages}")
        else:
            report.add("INFO", "build/main.pdf", f"{count} page(s)")

    blg = log.with_suffix(".blg")
    if blg.exists():
        blg_text = blg.read_text(encoding="latin-1")
        for m in re.finditer(r'I didn\'t find a database entry for "([^"]+)"', blg_text):
            report.add("ERROR", "build/main.blg", f"No BibTeX entry for '{m.group(1)}'")
        for m in re.finditer(r"^Warning--(.*)$", blg_text, re.M):
            report.add("WARNING", "build/main.blg", m.group(1).strip())


def check_fonts(root, report):
    pdf = root / "build" / "main.pdf"
    if not pdf.exists() or not shutil.which("pdffonts"):
        return
    out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
    for line in out.splitlines()[2:]:
        if "Type 3" in line:
            report.add("ERROR", "build/main.pdf",
                       f"Type 3 font (rejected by most publishers' PDF checks): {line.split()[0]}")
        cols = line.split()
        if len(cols) >= 5 and cols[-5] == "no":
            report.add("ERROR", "build/main.pdf", f"Font not embedded: {cols[0]}")


def check_anonymity(root, sources, report):
    for src in sources:
        for m in SELF_REFERENCE_RE.finditer(src.markdown_view):
            report.add("WARNING", src.where(m.start()),
                       f"Possible self-identification: '{m.group(0)}'")
        if re.search(r"^#+\s*Acknowledg", src.markdown_view, re.M | re.I):
            report.add("WARNING", src.rel, "Acknowledgments section in an anonymous submission")
    main = root / "latex" / "main.tex"
    if main.exists():
        tex = main.read_text(encoding="utf-8")
        author = re.search(r"\\author\{(.*?)\}\s*\n\s*\n", tex, re.S)
        if author and re.search(r"[\w.]+@[\w.]+", author.group(1)):
            report.add("WARNING", "latex/main.tex", "Author block contains e-mail addresses")


def locate_source(root, latex_line):
    """Find the Markdown or LaTeX source line that produced a line of generated LaTeX."""
    words = re.findall(r"[A-Za-z]{3,}", re.sub(r"\\[A-Za-z]+", " ", latex_line))
    candidates = sorted((root / "paper").rglob("*.md")) + sorted((root / "latex").glob("*.tex"))
    # Generated lines can start mid-word (e.g. the end of a citation key), and
    # Markdown has extra tokens (citations, link targets) between the words.
    for n in (6, 5, 4, 3, 2):
        if len(words) < n:
            continue
        pattern = re.compile(r"\W+(?:\S+\W+){0,3}".join(map(re.escape, words[-n:])))
        for path in candidates:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    return f"{path.relative_to(root).as_posix()}:{lineno}"
    return None


def diagnose(root, build_log):
    """Summarize why `make pdf` failed: stage, first error, and source location."""
    text = build_log.read_text(encoding="utf-8", errors="replace") if build_log.exists() else ""
    failed = re.search(r"make: \*\*\* \[([^\]]+)\]", text)
    target = failed.group(1) if failed else ""

    if target.startswith("figures/"):
        script = target.replace("figures/", "figures/src/").rsplit(".", 1)[0] + ".py"
        lines = [l for l in text.splitlines() if l.strip()]
        error = next((l for l in reversed(lines) if re.match(r"\w*(Error|Exception)\b", l.strip())), lines[-2] if len(lines) > 1 else "")
        print(f"FAILED figures: {script}: {error.strip()}")
        return

    if target.startswith("latex/generated/"):
        messages = [l for l in text.splitlines()
                    if l.strip() and not l.startswith(("pandoc ", "mkdir ", "make")) and not l.startswith("  ")]
        print(f"FAILED pandoc: {target}")
        for line in messages[-5:]:
            print(f"  {line.strip()}")
        return

    log = root / "build" / "main.log"
    if log.exists():
        latex = log.read_text(encoding="latin-1")
        error = re.search(r"^! (.*?)$(.*?)^l\.(\d+) (.*?)$", latex, re.M | re.S)
        if error:
            message, context, line_text = error.group(1), error.group(2), error.group(4)
            print(f"FAILED latex: {message.strip()}")
            missing = re.search(r"File [`']([^']+)' not found", message)
            where = None
            if missing:
                print(f"  missing file: {missing.group(1)} (figure path, or a TeX package to install)")
                where = locate_source(root, missing.group(1).replace("/", " "))
            where = where or locate_source(root, line_text + " " + context)
            print(f"  at: {where or 'unknown source'} (generated line: {line_text.strip()[:100]})")
            return
        first = re.search(r"^! (.*)$", latex, re.M)
        if first:
            print(f"FAILED latex: {first.group(1).strip()}")
            return

    blg = root / "build" / "main.blg"
    if blg.exists():
        bib = blg.read_text(encoding="latin-1")
        errors = re.findall(r"^(.*)---line (\d+) of file (.*)$", bib, re.M)
        if errors or "I couldn't open" in bib:
            print("FAILED bibtex: see build/main.blg")
            for message, lineno, path in errors[:5]:
                print(f"  {path}:{lineno}: {message.strip()}")
            return

    print("FAILED: unrecognized error; last lines of build/build.log:")
    for line in text.splitlines()[-15:]:
        print(f"  {line}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("project", nargs="?", default=".", help="project root (default: .)")
    parser.add_argument("--max-pages", type=int, help="fail if the PDF has more pages")
    parser.add_argument("--anonymous", action="store_true", help="check double-blind anonymity")
    parser.add_argument("--diagnose", metavar="BUILD_LOG", help="summarize a failed build and exit")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    if not (root / "paper").is_dir():
        sys.exit(f"{root} does not look like a paper project (no paper/ directory)")
    if args.diagnose:
        diagnose(root, Path(args.diagnose))
        return

    report = Report()
    sources = load_sources(root)
    if not sources:
        report.add("ERROR", None, "No Markdown sources in paper/")
    bib = parse_bib(root / "references" / "references.bib", report)
    check_sources(root, sources, bib, report)
    if args.anonymous:
        check_anonymity(root, sources, report)
    check_generated(root, report)
    log = check_freshness(root, sources, report)
    if log:
        check_log(root, log, report, args.max_pages)
        check_fonts(root, report)
    elif args.max_pages:
        report.add("WARNING", None, "Page limit not checked: no build log")

    report.print()
    sys.exit(1 if report.count("ERROR") else 0)


if __name__ == "__main__":
    main()
