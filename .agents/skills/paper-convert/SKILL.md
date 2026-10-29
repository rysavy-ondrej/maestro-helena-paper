---
name: paper-convert
description: Run and troubleshoot the Pandoc Markdown-to-LaTeX conversion of a paper project, or import an existing paper (LaTeX, Word, other Markdown) into the Markdown section structure. Use when generated LaTeX looks wrong, Pandoc fails, citations or cross-references do not convert, or the user wants to migrate an existing manuscript.
---

# Convert between Markdown and LaTeX

## Markdown → LaTeX (the build's conversion stage)

`./build.sh` regenerates these on every build (the Pandoc step alone: `make latex`, with the tools from `./build.sh doctor` on `PATH`):

- `latex/generated/abstract.tex` from `paper/abstract.md`
- `latex/generated/body.tex` from `paper/sections/*.md` (concatenated in file-name order)

Options (see the `Makefile`): `--top-level-division=section`, `--natbib` (citations become `\citep{}` etc., mapped to `\cite{}` by `latex/pandoc-compat.tex`), `--metadata-file=paper/metadata.yaml` (crossref prefixes), `--filter pandoc-crossref`, and `--lua-filter=latex/filters/tables.lua`.

**Never edit files in `latex/generated/`** — fix the Markdown, `metadata.yaml`, the filter, or `latex/main.tex` / `latex/pandoc-compat.tex`.

### Inspecting the output

After a build, check `latex/generated/body.tex` for these symptoms:

| Symptom in generated LaTeX | Cause | Fix |
| --- | --- | --- |
| Literal `{#fig:...}` / `{#eq:...}` text | pandoc-crossref not run | Install pandoc-crossref; check `./build.sh doctor` |
| `??` or `¿fig:x?` | Reference to an undefined label | Fix the label/reference name |
| `\citeauthor`, `\citeyear`, `\citep[see][]{...}` | Bare `@key` or citation prefix | Use `[@key]` form only |
| `\begin{longtable}` | Table filter not applied | Check the `--lua-filter` path |
| `\begin{Shaded}` / `\begin{Highlighting}` | Code block with a language class | Use a plain fence or raw `verbatim` |
| `\textasciitilde{}` where `~` was intended | `~` in Markdown is literal | Use `\ ` (non-breaking space) |
| Raw LaTeX appears escaped (`\textbackslash`) | Raw LaTeX not recognized | Put it in a ```` ```{=latex} ```` block |
| HTML missing | HTML is dropped in LaTeX output | Use Markdown or raw LaTeX |

Version issues: pandoc-crossref must be built for the installed Pandoc version (it warns otherwise). `\pandocbounded` (Pandoc ≥ 3.2) is defined in `latex/pandoc-compat.tex`; if Pandoc emits another undefined helper macro, add a definition there (copy it from `pandoc -D latex`).

## Importing an existing paper into Markdown

Use when the user has a manuscript in LaTeX, Word, or another Markdown dialect and wants to move to this workflow. Start from an initialized project (paper-init skill).

1. **Convert** to Pandoc Markdown:
   ```
   pandoc old/paper.tex -f latex -t markdown --wrap=none -o $TMPDIR/imported.md
   pandoc old/paper.docx -t markdown --wrap=none --extract-media=figures/imported -o $TMPDIR/imported.md
   ```
   For LaTeX, run from the manuscript's directory so `\input` files resolve.
2. **Split** at top-level headings into `paper/sections/NN-name.md`; put the abstract into `paper/abstract.md`. Add `{#sec:...}` labels to headings.
3. **Bibliography:** copy the existing `.bib` into `references/references.bib` (for Word, extract references and import them via the paper-citations skill — do not transcribe them by hand).
4. **Cross-references:** convert `\label`/`\ref` to pandoc-crossref syntax (`{#fig:x}`, `@fig:x`); rename labels to the `fig:`, `tbl:`, `eq:`, `sec:` prefixes and update every reference.
5. **Figures:** move images to `figures/` and use project-root-relative paths.
6. **What Pandoc cannot convert** (custom macros, `figure*`, complex tables, algorithms, TikZ): keep as ```` ```{=latex} ```` blocks; move needed packages and macro definitions to `latex/main.tex`.
7. **One sentence per line:** reflow paragraphs after import.
8. Set title, authors, and keywords in `latex/main.tex`.
9. Build (`./build.sh`) and compare the PDF with the original page by page. Report anything lost or changed.

## Markdown → other formats

For quick previews or co-author review without LaTeX:

```
pandoc paper/abstract.md paper/sections/*.md --filter pandoc-crossref --citeproc \
  --bibliography=references/references.bib --metadata-file=paper/metadata.yaml -o $TMPDIR/paper.docx
```

`--filter pandoc-crossref` must come **before** `--citeproc`; otherwise citeproc treats `@fig:` references as missing citations. Raw LaTeX blocks (and references to labels defined in them) are dropped in non-LaTeX output. These are review copies only; the submission PDF always comes from `make pdf`.
