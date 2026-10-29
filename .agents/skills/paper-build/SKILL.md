---
name: paper-build
description: Build the paper PDF with the project's ./build.sh, set up its local toolchain, report the cause of a failed build with its Markdown source location, render page previews, and freeze milestone snapshots in drafts/. Use when the user asks to build, compile, or render the paper, when the build fails, or when they want to save a draft version.
---

# Build the paper

Every project has `./build.sh` in its root. It does all the work; this skill runs it and acts on its one-line verdict. Do not run `pandoc`, `latexmk`, or `make` directly, and do not dig through logs unless the script's report is insufficient.

| Command | Does | Prints at the end |
| --- | --- | --- |
| `./build.sh` | Regenerates LaTeX from Markdown, builds figures, runs LaTeX + BibTeX, runs the checks | `BUILD OK: build/paper.pdf, N page(s); check: E error(s), W warning(s)` or `FAILED <stage>: ...` + `BUILD FAILED` |
| `./build.sh doctor` | Shows which tools are used | `READY` or `NOT READY: run ./build.sh setup` |
| `./build.sh setup` | Installs the project-local toolchain (below) | `READY` |
| `./build.sh check [--max-pages N] [--anonymous]` | Full list of check findings | `E error(s), W warning(s), N note(s)` |
| `./build.sh preview [file.pdf]` | Renders pages to `build/preview/*.png` | the PNG paths |
| `./build.sh figures` | Rebuilds `figures/<name>.pdf` from `figures/src/<name>.py` | — |
| `./build.sh snapshot NN-label` | Freezes the paper into `drafts/NN-label/` | `SNAPSHOT OK: drafts/NN-label` |
| `./build.sh clean` | Removes `build/` and `latex/generated/` | — |

Exit status: 0 success, 1 build or check failure, 2 environment not ready.

## Toolchain

`./build.sh` uses project-local tools first, then the system:

- `.tools/bin/` — Pandoc and pandoc-crossref, pinned to matching versions.
- `.tools/TinyTeX/` — a small TeX Live, installed only if no system TeX provides the document class (or with `setup --tinytex`). Packages from `latex/tex-packages.txt` are installed at setup; packages missing during a build are installed automatically.
- `.venv/` — Python for figure scripts, checks, and previews (`requirements.txt`).

Platforms: macOS (Apple Silicon, Intel) and Linux (x86_64, arm64, including WSL). Prerequisites are basic system tools: `bash`, `curl`, `make`, `perl`, `tar` with `xz`, `python3` (Debian/Ubuntu: `sudo apt install curl make perl xz-utils python3`; macOS: `xcode-select --install`). Setup downloads roughly 300–500 MB; `PAPER_FORGE_TOOLS` and `PAPER_FORGE_VENV` let several projects share one installation.

## Procedure

1. **Build:** `./build.sh`.
2. **If it prints `NOT READY`** (exit 2): tell the user that `./build.sh setup` will download the toolchain into the project, and run it once they agree. If setup stops with a `missing:` message, give the user the install command it prints (system packages need their action). Then build again.
3. **If it prints `BUILD OK`:** report the page count and check summary. If the check reports errors or warnings, run `./build.sh check` and fix them (see the paper-validate skill).
4. **If it prints `BUILD FAILED`:** the line(s) above it name the stage and the source location:
   - `FAILED latex: <error>` + `at: paper/sections/<file>.md:<line>` — fix that Markdown line (table below), then rebuild.
   - `FAILED latex: ... File 'x' not found` — a wrong figure path (paths are project-root-relative), or a TeX package that could not be installed automatically.
   - `FAILED figures: figures/src/<name>.py: <exception>` — fix the figure script or its data.
   - `FAILED pandoc: ...` — Markdown syntax or filter problem; see the paper-convert skill.
   - `FAILED bibtex: ...` — malformed entry in `references/references.bib` at the reported line.
   - `at: unknown source` or `FAILED: unrecognized error` — only then read `build/build.log` and the first `!` error in `build/main.log`.
   Fix the cause in the sources and rebuild. Repeat at most three times before reporting to the user what remains.
5. **Look at the result** when figures, tables, or layout changed: `./build.sh preview`, then view the PNGs of the affected pages.

**Never edit `latex/generated/`** to fix a build — it is regenerated on every build. Fix the Markdown, bibliography, figures, or `latex/main.tex`.

## Common LaTeX errors

| Error | Likely cause | Fix |
| --- | --- | --- |
| `Undefined control sequence` | Macro from a package not loaded, or a typo in raw LaTeX | Fix the macro, or add the package to `latex/main.tex` |
| `Missing $ inserted` | `_`, `^`, `&`, `%`, `#` in raw LaTeX, or math outside `$...$` | Markdown / raw block |
| `Misplaced alignment tab character &` / `Extra alignment tab` | Wrong number of `&` in a raw table or `align` | Raw LaTeX block |
| `Something's wrong--perhaps a missing \item` | Empty list | Markdown |
| `Unicode character ... not set up for use with LaTeX` | Unicode symbol in Markdown | LaTeX equivalent (`$\alpha$`, `--`) |
| `Environment Shaded undefined` | Code fence with a language class | Plain fence |

## Snapshot a milestone

At a milestone (outline agreed, first full draft, internal review, submission, camera-ready):

1. Pick the next number after the highest existing `drafts/NN-*` (`00` is reserved for raw material) and a short lowercase label, e.g. `02-first-draft`.
2. Build first (`./build.sh`) so the PDF matches the sources. If the build fails, snapshot only with the user's agreement and say so in the notes.
3. `./build.sh snapshot NN-label` — copies `paper/`, `references/`, `figures/`, and `build/paper.pdf`; refuses to overwrite an existing snapshot.
4. Write `drafts/NN-label/NOTES.md`: date, milestone, page count, what changed since the previous snapshot (summarize `diff -ru drafts/<previous>/paper paper`), and open issues.

Snapshots are read-only history; never edit or rebuild inside them. Do not commit unless the user asks.

## Projects without build.sh

Projects created before `build.sh` existed: copy `build.sh`, `requirements.txt`, and `scripts/validate.py` from the plugin's `templates/common/`, and `latex/tex-packages.txt` from the matching template (the plugin's `templates/` directory is two levels above this skill's base directory). Add `.tools/` and `.venv/` to `.gitignore`.
