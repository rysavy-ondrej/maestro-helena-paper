# Style: Springer LNCS

Class `llncs` (TeX Live package `llncs`) for Lecture Notes in Computer Science and related proceedings series (LNAI, LNBI, CCIS). Bibliography style `splncs04.bst`. For Springer Nature journals, use the journal's `sn-jnl` template instead (paper-init skill, venue template).

| Item | Convention |
| --- | --- |
| Layout | One column; text width 12.2 cm (4.8 in), text height 19.3 cm; do not change margins or font size |
| References in text | "Fig. 1", "Table 1", "Eq. (1)", "Sect. 2" — set in `paper/metadata.yaml`; spell out "Figure"/"Section" at the start of a sentence |
| Citations | Numeric in brackets: [1], [1,2], [1, p. 5] |
| Figure captions | Below the figure: "Fig. 1. Caption." |
| Table captions | Above the table: "Table 1. Caption." |
| Section headings | Numbered; at most three levels (`#`, `##`, `###`), `####` gives a run-in heading |
| Front matter | `\title`, `\titlerunning`, `\author` with `\inst{}` and optional `\orcidID{}`, `\institute`, `\authorrunning` in `latex/main.tex` |
| Abstract | 150–250 words; keywords inside the abstract with `\keywords{A \and B}` |
| Length | Venue-specific, commonly 12–16 pages including references |
| Figures | Width up to 12.2 cm; fonts in figures at least 8 pt; vector graphics |
| Fonts | Computer Modern via `lmodern` (scalable); no Type 3 fonts |

## Submission and camera-ready

- Double-blind: replace authors and institutes with "Anonymous" text, remove ORCIDs and acknowledgments.
- Camera-ready: ORCID iDs are encouraged; submit sources (Springer accepts LaTeX + PDF); the copyright form is signed separately.
- Springer asks for references with DOIs where available.
