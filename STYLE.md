# Style: Generic Article

Standard `article` class with `natbib` (numeric, sorted and compressed) and `unsrtnat.bst`. Use for preprints (arXiv), technical reports, theses chapters, and venues without a LaTeX template.

| Item | Convention |
| --- | --- |
| Layout | One column, 11 pt, 1 in margins, US Letter (`geometry`); text width 6.5 in |
| References in text | "Figure 1", "Table 1", "Eq. (1)", "Section 2" — set in `paper/metadata.yaml` |
| Citations | Numeric in brackets: [1], [1, 2]; `natbib` is loaded, so bare `@key` gives "Smith et al. [1]" — keep to the bracketed form for portability |
| Figure captions | Below the figure |
| Table captions | Above the table |
| Abstract | One paragraph, 150–250 words |
| Fonts | Computer Modern via `lmodern` (scalable) |

## arXiv

arXiv compiles the LaTeX sources itself: upload `latex/main.tex`, `latex/pandoc-compat.tex`, `latex/generated/`, the figures, and the generated `build/main.bbl`, keeping the relative paths (or flatten them and adjust `\input`/`\graphicspath`).
