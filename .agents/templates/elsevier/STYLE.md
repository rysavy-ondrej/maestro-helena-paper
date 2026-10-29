# Style: Elsevier

Class `elsarticle` (TeX Live package `elsarticle`) for Elsevier journals. Bibliography style `elsarticle-num.bst` (numeric); for author–year journals use `elsarticle-harv.bst` and change the citation rules below. Some journals provide their own template — check the Guide for Authors.

| Item | Convention |
| --- | --- |
| Layout | Submission: `preprint,12pt`, one column; final look: `final,5p,times,twocolumn` |
| Figure sizes | Single column 90 mm, 1.5 columns 140 mm, full width 190 mm (Elsevier artwork guidelines) |
| References in text | "Fig. 1", "Table 1", "Eq. (1)", "Section 2" — set in `paper/metadata.yaml` |
| Citations | Numeric in brackets: [1], [1, 2]; with `elsarticle-harv`, author–year (Smith, 2020) — then bare `@key` gives "Smith (2020)" |
| Figure captions | Below the figure |
| Table captions | Above the table |
| Front matter | All inside `frontmatter`: `\title`, `\author[label]`, `\affiliation[label]{organization=..., city=..., country=...}`, `\ead`, `\cortext`, abstract, `keyword` environment with `\sep` |
| Abstract | One paragraph, typically up to 250 words, no citations |
| Highlights | Many journals require 3–5 bullet highlights (max 85 characters each) — `highlights` environment or a separate file |
| Graphical abstract | Some journals require one, submitted as a separate file |
| Length | Journal-specific (Guide for Authors) |
| Fonts | `lmodern` for the preprint layout, `times` option for the final layout; no Type 3 fonts |

## Submission

- Most Elsevier journals review the single-column preprint PDF; check whether the journal is double-blind (then provide a separate title page and anonymize the manuscript).
- Declarations required by most journals: CRediT author statement, declaration of competing interests, data availability, and use of generative AI in writing — add them as unnumbered sections before the references (raw LaTeX `\section*{...}`).
