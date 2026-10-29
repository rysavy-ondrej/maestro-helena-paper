# Style: ACM

Class `acmart` (TeX Live package `acmart`), format `sigconf` for conference proceedings, `acmsmall` / `acmlarge` / `acmtog` for journals. Bibliography style `ACM-Reference-Format.bst`; `acmart` loads `natbib`, `amsmath`, `graphicx`, `booktabs`, and `hyperref` itself.

| Item | Convention |
| --- | --- |
| Layout (`sigconf`) | Two columns, US Letter; column width 3.33 in (241 pt), text width 7 in (506 pt) |
| Layout (`acmsmall`) | One column; text width 5.48 in (395 pt) |
| References in text | "Figure 1", "Table 1", "Equation (1)", "Section 2" — set in `paper/metadata.yaml` |
| Citations | Numeric in brackets: [1], [1, 2], [1, p. 5] |
| Figure captions | Below the figure; every figure needs a `\Description{...}` for accessibility. `latex/filters/acm-description.lua` adds one from the caption for Markdown figures; raw LaTeX figures need their own |
| Table captions | Above the table |
| Full-width floats | `figure*` / `table*` |
| Front matter | Abstract, `\keywords`, and CCS concepts come **before** `\maketitle` in `latex/main.tex`; CCS concepts are generated at https://dl.acm.org/ccs |
| Abstract | One paragraph, typically up to 200–250 words |
| Length | Venue-specific; often measured excluding references |
| Fonts | Linux Libertine and Inconsolata (class default; packages `libertine`, `newtx`, `inconsolata`); no Type 3 fonts |
| Bibliography | `ACM-Reference-Format` wants full entries: `@inproceedings` with `publisher` and `address`, DOIs, and URLs where available |

## Packages

Do not load `amssymb` (conflicts with the `newtx` math fonts used by the class) or load `hyperref` again; `amsmath` and `booktabs` are already present.

## Submission and camera-ready

- Submission: add `review` (line numbers) and `anonymous` for double-blind review to the class options.
- The template's draft settings (`\setcopyright{none}`, `printacmref=false`, empty copyright footnote) suppress ACM's rights block; for camera-ready, remove them and paste the rights-management commands (`\setcopyright`, `\acmDOI`, `\acmISBN`, `\acmConference`, ...) that ACM sends after the rights form.
- The ACM TAPS publishing system requires accessible figures (`\Description`) and complete metadata.
