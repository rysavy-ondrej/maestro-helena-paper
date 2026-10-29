# Style: IEEE Journal

Class `IEEEtran` with the `[journal]` option (TeX Live package `ieeetran`). Bibliography style `IEEEtran.bst`, citations through the `cite` package. Some journals (IEEE Access, Computer Society Transactions) provide modified templates — use theirs when available (paper-init skill, venue template).

| Item | Convention |
| --- | --- |
| Layout | Two columns, US Letter; column width 3.5 in (88.9 mm), text width 7.16 in (182 mm) |
| References in text | "Fig. 1", "Table I" (Roman), "Eq. (1)", "Section II" (Roman) — set in `paper/metadata.yaml` |
| Citations | Numeric in brackets: [1], [1], [2], [1, p. 5]; not grammatical nouns |
| Figure captions | Below the figure: "Fig. 1. Caption." |
| Table captions | Above the table, Roman numerals (automatic) |
| Full-width floats | `figure*` / `table*`, top of a page only |
| Front matter | Author names with `\IEEEmembership`, affiliations in `\thanks`, running heads via `\markboth` |
| First paragraph | Optionally a drop cap: start the introduction with a raw `\IEEEPARstart{T}{his}` |
| Abstract | One paragraph, 150–250 words, no citations, equations, or abbreviations if possible |
| Keywords | `IEEEkeywords` environment ("Index Terms"), from the IEEE Taxonomy where required |
| Length | Journal-specific (often 10–14 pages, with overlength page charges) |
| Back matter | Optional author biographies (`IEEEbiography`) for camera-ready |
| Fonts | Times (automatic); figures 8 pt serif; no Type 3 fonts |

## Submission and camera-ready

- Most IEEE journals are single-blind: authors stay in the submission. Check the journal's instructions.
- Use the `peerreview` or `draftcls,onecolumn` options only if the journal asks for them.
