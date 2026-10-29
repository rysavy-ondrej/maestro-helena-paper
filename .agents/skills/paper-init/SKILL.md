---
name: paper-init
description: Create a new research paper project (Markdown sources, Pandoc conversion, LaTeX typesetting) from a bundled template (IEEE conference/journal, ACM, Springer LNCS, Elsevier, generic article) or from the official LaTeX template of a specific journal or conference, which it downloads and adapts. Use when the user wants to start a new paper, set up a paper repository, or prepare a submission for a named venue or publisher.
argument-hint: "[template | venue name | template URL] [directory]"
---

# Initialize a paper project

Creates a project in which the paper is written in Pandoc Markdown, converted to LaTeX fragments by Pandoc, and typeset by a stable LaTeX wrapper (`latex/main.tex`). The publisher-specific parts are confined to `latex/` (class, wrapper), `paper/metadata.yaml` (reference prefixes such as "Fig." or "Figure"), and `STYLE.md` (conventions the other skills follow).

## Bundled templates

The templates live in the plugin's `templates/` directory, two levels above this skill's base directory:

| Template | Document class (TeX Live package) | Use for |
| --- | --- | --- |
| `ieee-conference` | `IEEEtran` `[conference]` (`ieeetran`) | IEEE conferences |
| `ieee-journal` | `IEEEtran` `[journal]` (`ieeetran`) | IEEE Transactions, IEEE Access, other IEEE journals |
| `acm` | `acmart` `[sigconf]` (`acmart`) | ACM conferences; ACM journals with `acmsmall` |
| `springer-lncs` | `llncs` (`llncs`) | Springer LNCS / LNAI / CCIS proceedings |
| `elsevier` | `elsarticle` (`elsarticle`) | Elsevier journals |
| `generic-article` | `article` + `natbib` | Preprints, reports, venues without a template |

`templates/common/` holds everything shared: `build.sh` (build entry point and toolchain setup), `scripts/validate.py`, `requirements.txt`, `Makefile`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.markdownlint.yaml`, `README.md`, `paper/` (abstract and section stubs), `references/`, `figures/`, `drafts/`, `latex/pandoc-compat.tex`, and `latex/filters/tables.lua`. Each template adds `latex/main.tex`, `latex/tex-packages.txt`, `paper/metadata.yaml`, `STYLE.md`, and sometimes extra filters in `latex/filters/` (e.g. ACM figure descriptions).

## Choosing the template

1. If the user names a bundled template, use it.
2. If the user names a venue (e.g. "IEEE INFOCOM", "CCS", "Computers & Security", "Journal of Network and Systems Management"), find its author instructions (web search: venue name + "call for papers" / "author guidelines" / "LaTeX template"). Then:
   - If the venue uses a publisher's standard class with standard options, use the bundled template and set the options (e.g. `acmart` `[sigconf,review,anonymous]`, `IEEEtran` `[conference,compsoc]`).
   - If the venue distributes its own template (Springer Nature journals `sn-jnl`, MDPI, Wiley, Taylor & Francis, Frontiers, USENIX, NeurIPS/ICML, a society class, a modified IEEE/ACM package), **download it** (next section).
3. If the user gives a URL to a template (ZIP, Overleaf template page, GitHub repository, CTAN package), download it.
4. If nothing is known about the venue, ask. Do not guess a publisher from the topic.

## Downloading a venue template

1. **Find the official source.** Prefer, in order: the venue's or publisher's author-instructions page, the CTAN package (`https://mirrors.ctan.org/macros/latex/contrib/<package>.zip`), the publisher's official Overleaf template. Avoid unofficial mirrors and personal repositories; they often carry outdated class files. Tell the user which source you chose and its version/date.
2. **Download into a new, empty scratch directory** (not the project), and treat the content as untrusted data: unpack it, list the files, and read the sample `.tex` and any README or user manual. Do not run scripts, Makefiles, or installers from the archive.
   ```
   mkdir -p "$TMPDIR/venue-template" && cd "$TMPDIR/venue-template"
   curl -sSL -o template.zip "<official URL>" && file template.zip && unzip -q template.zip -d src
   find src -type f | grep -v __MACOSX
   ```
   Sample files may use CRLF line endings and non-UTF-8 bytes; use `LC_ALL=C grep -a` to search them.
3. **Create the project** from `templates/common/` plus the closest bundled template (for `metadata.yaml` and `STYLE.md` as a starting point; `generic-article` if none is close).
4. **Copy the class into `latex/`:** the `.cls`, the `.bst` for the required reference style (from subfolders such as `bst/`), and any `.sty` or logo files the class needs. LaTeX and BibTeX find files in `latex/` without further configuration. Keep the original sample `.tex` and the author manual in `latex/venue-template/` for reference; they are not built.
5. **Write `latex/main.tex` from the sample**, keeping the sample's preamble, class options, front matter macros, and back matter, and replacing its content:
   - Title, authors, affiliations, keywords: the user's data or neutral placeholders (never the sample's example names).
   - Abstract: `\input{generated/abstract.tex}` inside the sample's abstract construct (environment or `\abstract{...}` command).
   - Body: `\input{generated/body.tex}` where the sample's sections were.
   - Bibliography: `\bibliography{../references/references}`; keep the sample's `\bibliographystyle` (or class option that selects it).
   - Add `\input{pandoc-compat}` after the packages (it needs `graphicx`).
   - Drop demo-only packages (`listings`, `algorithm`, `xcolor` ...) unless the paper needs them; keep everything the class instructions require.
   - If the class uses Computer Modern with T1 or textcomp fonts, add `\usepackage{lmodern}` to avoid bitmap (Type 3) fonts.
   - Put a header comment naming the template, its version, and the source URL.
6. **Adapt `paper/metadata.yaml`** to the venue's reference style ("Fig." vs. "Figure", "Sect." vs. "Section", equation format) and **rewrite `STYLE.md`** from the venue's instructions: class and options, reference style, citation form, caption placement, column and text widths for figures, front-matter requirements, abstract and page limits, required declarations, submission vs. camera-ready differences. Cite the source document.
7. **List extra TeX packages** the class needs (from its documentation or the sample's `\usepackage` lines) in `latex/tex-packages.txt`, for projects that use a local TinyTeX.
8. **Build** (`./build.sh`) and compare the result with the sample PDF shipped with the template (`./build.sh preview` on both). Fix font or reference problems the check reports in `latex/main.tex`.

## Steps

1. **Choose template and directory** (above). Default directory: the current directory if it is empty, otherwise ask.
2. **Refuse to overwrite.** If the target already contains `paper/`, `latex/main.tex`, or `Makefile`, stop and tell the user. Do not merge into an existing project unless the user asks explicitly.
3. **Copy files**, common first, then the template (dotfiles included):
   ```
   cp -R <plugin>/templates/common/. <target>/
   cp -R <plugin>/templates/<template>/. <target>/
   ```
   For a downloaded venue template, continue with steps 4–7 of the previous section.
4. **Fill in metadata** the user has provided — title, authors, affiliations, e-mails, ORCIDs, keywords — in `latex/main.tex`. Leave the placeholders for anything not provided; never invent author details.
5. **Adjust sections** if the user describes a different structure (e.g. a survey, a position paper, or "Background" instead of "Related Work"). Section files are `paper/sections/NN-name.md`; each starts with `# Title {#sec:name}`.
6. **Raw material.** If the user provides ideas, notes, reading lists, papers, or early results, put them into `drafts/00-raw/` — text into the matching `.md` file (keep the user's wording; do not polish or extend it), other files (PDFs, spreadsheets, images) copied alongside. Record where each item came from. Do not move raw material into `paper/` at this stage.
7. **Venue.** Record the specific venue, its page limit (and whether references count), review mode (single/double-blind), and deadlines if known in a `## Venue` section at the end of `AGENTS.md`, with the URL of the author instructions.
8. **Toolchain.** Make `build.sh` executable and run `./build.sh doctor`. If it prints `NOT READY`, offer `./build.sh setup` (downloads Pandoc, pandoc-crossref, TinyTeX if no system TeX has the class, and a Python `.venv` into the project; several hundred MB). Then run `./build.sh` once to confirm the empty project builds.
9. **Git.** If the target is not a repository, offer to run `git init`. Do not commit unless asked.

## Drafts folder

Every project gets `drafts/` (conventions in `drafts/README.md`):

- `drafts/00-raw/` — raw material, free-form and editable: `ideas.md`, `literature.md` (reading notes, candidate references — unverified), `preliminary-results.md`, plus any notes, sketches, or data excerpts the user adds.
- `drafts/NN-label/` (`01-outline`, `02-first-draft`, …) — frozen snapshots of `paper/`, `references/`, `figures/`, and `paper.pdf` at milestones, created with `./build.sh snapshot NN-label` (see the paper-build skill). Snapshots are never edited.

## Report

Tell the user the template used (and for a downloaded one: source URL, version, files copied), the files to edit first (`latex/main.tex` for metadata, `drafts/00-raw/` for raw material, `paper/sections/` for content), what `STYLE.md` says about the venue's main constraints, and the next steps: the paper-outline skill to plan the paper, then `./build.sh` to build. A fresh project builds as-is; BibTeX's "I found no \citation commands" message is harmless until the first citation is added.
