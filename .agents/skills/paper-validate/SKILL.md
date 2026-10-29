---
name: paper-validate
description: Run mechanical pre-submission checks on a Markdown/LaTeX paper project — citation keys vs. BibTeX, broken cross-references, missing figures, unreferenced figures/tables, TODO markers, LaTeX/BibTeX warnings, page limit, embedded fonts, and double-blind anonymity. Use before submission, after large edits, or when the user asks to check, validate, or lint the paper.
argument-hint: "[--max-pages N] [--anonymous]"
---

# Validate the paper

## 1. Run the checker

```
./build.sh check [--max-pages N] [--anonymous]
```

Take `--max-pages` and `--anonymous` from the arguments, or from the `## Venue` section of `AGENTS.md` if present. If the build is stale or missing, run `./build.sh` first (paper-build skill) so the log checks are current. The checker is `scripts/validate.py` in the project; projects without it can copy it from the plugin's `templates/common/scripts/`.

The script reports `ERROR`, `WARNING`, and `INFO` lines with `file:line` locations and exits non-zero if any error is found.

| Check | Source |
| --- | --- |
| Cited keys (`[@key]`, `\cite{}`) exist in `references.bib` | Markdown |
| Duplicate BibTeX keys, entries missing author/title/year, placeholder entries, entries without DOI, uncited entries | `references.bib` |
| `@fig:`/`@tbl:`/`@eq:`/`@sec:` and `\ref{}` point to defined labels; duplicate labels; figures/tables never referenced | Markdown |
| Image files exist (project-root-relative); raster images flagged | Markdown |
| `[TODO`, `TODO:`, `FIXME`, `[CITATION NEEDED]` markers | Markdown |
| Conversion problems: literal crossref labels, `longtable`, highlighted code, stray `\textasciitilde`, author/year citations | `latex/generated/*.tex` |
| LaTeX errors, undefined citations/references, missing files and characters, overfull boxes > 1pt, page count vs. limit | `build/main.log` |
| BibTeX missing entries and warnings | `build/main.blg` |
| Type 3 or non-embedded fonts (requires `pdffonts` from poppler) | `build/main.pdf` |
| With `--anonymous`: self-identifying phrases, acknowledgments section, e-mails in the author block | Markdown, `latex/main.tex` |

## 2. Venue checks the script does not cover

Check these manually against the venue's call for papers and `latex/main.tex`:

- Everything listed under "Submission and camera-ready" in `STYLE.md`.
- Correct document class options for the venue (e.g. IEEE `conference`/`journal`/`compsoc`, ACM `sigconf`/`acmsmall` with `review,anonymous`, Elsevier `preprint`/`final`) and paper size (US Letter for IEEE and ACM; A4 for many European venues).
- Whether references count toward the page limit.
- Double-blind: author block replaced with anonymous text, no identifying URLs or repository links, self-citations in third person, no acknowledgments or funding information.
- Camera-ready: real author names and affiliations; the publisher's rights block (IEEE `\IEEEpubid`, ACM `\setcopyright`/`\acmDOI` commands from the rights form, Springer copyright form); ORCIDs where requested; no page numbers if the venue forbids them.
- Abstract length within the venue's limit (count words in `paper/abstract.md`).
- Keywords present and from the venue's list if one is required.
- Publisher PDF checks if required (IEEE PDF eXpress, ACM TAPS, Elsevier/Springer submission systems): fonts embedded, no Type 3 fonts, figure descriptions for ACM.
- Required declarations (Elsevier: competing interests, CRediT, data availability, generative AI use; many journals: funding, data and code availability).

## 3. Report

Summarize: error and warning counts, then each error with location and the fix, then warnings grouped by kind. Distinguish what must be fixed before submission from what is advisory (INFO). Offer to fix the issues — citations via paper-citations, text via paper-write, build problems via paper-build. Never fix problems by editing `latex/generated/`.
