---
name: paper-citations
description: Find, verify, add, and clean up BibTeX references for a Markdown/LaTeX research paper — DOI/arXiv import, duplicate and missing-key checks, unused entries, citation placement. Use when the user asks to cite something, add references, fix the bibliography, or check citations.
---

# Manage citations

All references live in `references/references.bib`. Markdown cites them as `[@key]`; Pandoc turns these into `\cite{key}` and BibTeX formats the bibliography with the venue's style (`IEEEtran`, `ACM-Reference-Format`, `splncs04`, `elsarticle-num`, ...; see `STYLE.md`).

## Never fabricate

Every entry must correspond to a real, verifiable publication. Do not write BibTeX from memory. Obtain metadata from an authoritative source (DOI resolver, Crossref, arXiv, DBLP, the publisher page) or from a file the user supplies. If a work cannot be found, say so and leave `[CITATION NEEDED]` in the text instead of an entry.

## Literature notes

`drafts/00-raw/literature.md` holds reading notes and candidate references. They are leads, not citations: import each one through the steps below before citing it, and when an entry is imported, note its BibTeX key next to it in `literature.md`. When the user asks for a literature review or related-work material, record what you find there (with DOI or URL and a one-line summary) rather than in the paper.

## Adding a reference

1. **By DOI** (preferred) — content negotiation returns BibTeX:
   ```
   curl -sLH "Accept: application/x-bibtex" "https://doi.org/10.1109/ACCESS.2025.1234567"
   ```
2. **By title/author** — search Crossref, then fetch the DOI as above:
   ```
   curl -s "https://api.crossref.org/works?rows=5&query.bibliographic=<url-encoded title and first author>" \
     | python3 -c 'import json,sys; [print(i.get("DOI"), "|", (i.get("title") or [""])[0], "|", i.get("container-title"), "|", i.get("issued",{}).get("date-parts")) for i in json.load(sys.stdin)["message"]["items"]]'
   ```
   Confirm the match (title, authors, year, venue) before using it. If several candidates match, ask the user.
3. **arXiv** — `https://arxiv.org/bibtex/<id>`. Its `year` is the date of the *latest* version; take the original year from `<published>` in `https://export.arxiv.org/api/query?id_list=<id>`. Several styles (e.g. `IEEEtran`) ignore `eprint`, so add `howpublished = {arXiv:<id>}`. If a peer-reviewed version exists, prefer it and tell the user.

DBLP and Google Scholar block scripted requests; use them only through a browser or ask the user. If network access fails, tell the user and ask for the BibTeX or DOI rather than guessing.

DOI BibTeX arrives as a single line with a `Name_Year` key, Unicode en-dashes in `pages`, and noise fields (`url`, `ISSN`, `publisher`, `month`). Always reformat it according to the rules below before adding it.

## Normalizing entries

- **Key:** `firstauthorlastnameYEARfirstword`, lowercase ASCII (e.g. `smith2025automated`). Keep existing keys unchanged — they are cited in the text.
- **Duplicates:** before adding, search the `.bib` for the same DOI or title. Reuse the existing key.
- **Fields:** `author`, `title`, `year`, and the venue (`journal` or `booktitle`) are required; add `volume`, `number`, `pages`, `doi` when available. Use `--` in page ranges (never `–`). One field per line, aligned.
- **Proceedings titles:** follow the venue's form; IEEE prefers `Proc. {IEEE} Symposium on Security and Privacy`, ACM and Springer the full name, without the year either way.
- **Style-specific fields:** `ACM-Reference-Format` warns without `publisher` and `address` for proceedings and uses `doi`/`url`; `splncs04` and `elsarticle-num` print DOIs. Check `build/main.blg` for warnings after a build.
- **Capitalization:** protect proper nouns and acronyms in titles with braces: `title = {{LLM}-Based Triage of {IDS} Alerts}`.
- **Encoding:** use LaTeX escapes for accented characters (`{\v{c}}`, `{\'e}`) — the template uses BibTeX, which is not Unicode-safe.
- **Types:** `@article` (journal), `@inproceedings` (conference), `@book`, `@techreport`, `@misc` (preprints, software, datasets; include `howpublished` / `url` and `note = {Accessed: YYYY-MM-DD}` for web resources).
- Strip noise fields from imports (`abstract`, `keywords`, `file`, `urldate` when not needed, `month` duplicates).
- Keep entries sorted by key or append consistently — follow the existing file's order.

## Citing in text

Use `[@key]` or `[@a; @b]`, before the sentence-ending period. See the paper-write skill for allowed forms. When placing citations for existing claims, cite the work that actually supports the claim; if you are unsure it does, ask or mark it.

## Checking

Run `./build.sh check` (no build needed for source checks) to find cited keys missing from the `.bib`, unused entries, duplicates, entries missing required fields, and placeholders. After `make pdf`, `build/main.blg` lists BibTeX warnings (e.g. empty fields).

Report what was added (key + full reference), what was changed, and anything that could not be verified.
