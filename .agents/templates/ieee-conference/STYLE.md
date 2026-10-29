# Style: IEEE Conference

Class `IEEEtran` with the `[conference]` option (TeX Live package `ieeetran`). Bibliography style `IEEEtran.bst`, citations through the `cite` package.

| Item | Convention |
| --- | --- |
| Layout | Two columns, US Letter; column width 3.5 in (88.9 mm), text width 7.16 in (182 mm) |
| References in text | "Fig. 1", "Table I" (Roman), "Eq. (1)", "Section II" (Roman) — set in `paper/metadata.yaml` |
| Citations | Numeric in brackets: [1], [1], [2], [1, p. 5]; not grammatical nouns ("in [1]", not "[1] shows") |
| Figure captions | Below the figure: "Fig. 1. Caption." |
| Table captions | Above the table, Roman numerals, small caps (automatic) |
| Full-width floats | `figure*` / `table*`, top of a page only |
| Section headings | Roman numerals, small caps (automatic); at most three levels |
| Abstract | One paragraph, typically 150–250 words, no citations or equations |
| Keywords | `IEEEkeywords` environment in `latex/main.tex` ("Index Terms") |
| Length | Typically 4–8 pages; check whether references count |
| Fonts | Times (automatic); figures 8 pt serif; no Type 3 fonts (IEEE PDF eXpress) |
| Units and numbers | SI units; "Fig." abbreviated except at sentence start ("Figure 1 shows ...") |

## Submission and camera-ready

- Double-blind venues: replace the author block with "Anonymous Authors" and remove identifying text, acknowledgments, and self-references in the first person.
- Camera-ready: real authors; copyright notice if the venue requires it (`\IEEEoverridecommandlockouts` is loaded; add `\IEEEpubid{...}` per the venue's instructions); check the final PDF with IEEE PDF eXpress if required.
- Venue-specific class options (e.g. `compsoc`) and page limits go into `latex/main.tex` and the `## Venue` section of `AGENTS.md`.
