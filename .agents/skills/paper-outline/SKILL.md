---
name: paper-outline
description: Plan or restructure a research paper — research questions, contributions, section-by-section key points, and the evidence (figures, tables, experiments, citations) each claim needs. Writes paper/outline.md and aligns the section files. Use when starting a paper, reorganizing sections, or checking that the structure supports the contributions.
---

# Outline a paper

The outline is the plan the other skills write against. It lives in `paper/outline.md`, which is **not** built into the PDF (only `paper/abstract.md` and `paper/sections/*.md` are).

## Gather input

Work from what exists: the raw material in `drafts/00-raw/` (ideas, literature notes, preliminary results), the user's description, data, existing sections, `AGENTS.md` (venue, page limit), and `references/references.bib`. Treat raw material as unverified: a result in `preliminary-results.md` becomes planned evidence with status "preliminary", and a paper in `literature.md` becomes a needed citation until it is imported via the paper-citations skill. If the user gives new raw ideas while outlining, add them to `drafts/00-raw/ideas.md` as well. Ask the user only for what you cannot infer and is essential: the core problem, the main contribution, and the target venue. Never invent results, datasets, or prior work to fill gaps; record them as open items.

## Outline format

Write `paper/outline.md`:

```markdown
# Outline: <working title>

Venue: <venue, page limit, double-blind yes/no>

## Problem and gap
<2–4 sentences>

## Research questions
- RQ1: ...

## Contributions
1. ... (supported by: @sec:methodology, @fig:architecture)

## Sections
### 01 Introduction  (~0.75 page)
- Key points, in order
- Citations needed: [have: @smith2025] [need: survey of LLM alert triage]

### 03 Methodology  (~1.5 pages)
- ...
- Figures/tables: fig:architecture (system diagram, full column width)

## Evidence status
| Claim | Evidence | Status |
| --- | --- | --- |
| Agents improve accuracy | tbl:results | experiment pending |

## Open items
- [ ] ...
```

Guidelines:

- Every contribution must point to the section and evidence that supports it, and every planned figure/table must support a claim.
- Allocate a page budget per section that sums to the venue's limit (from `AGENTS.md`/`STYLE.md`; e.g. IEEE conferences 4–8 two-column pages, LNCS 12–16 one-column pages; check whether references count).
- Typical empirical structure: Introduction, Related Work, Methodology, Experimental Setup, Results, Discussion (optional, may include threats to validity), Conclusion. Adapt for surveys, systems, or position papers.
- The Introduction should end with an explicit contribution list and a paper-organization paragraph.

## Align the section files

After the outline is agreed, make `paper/sections/` match it:

- One file per top-level section, named `NN-short-name.md` (two-digit prefix sets the order).
- Each file starts with `# Section Title {#sec:short-name}`.
- For new, empty sections, add the key points as a `[TODO: ...]` list so drafting can start from them.
- When renaming or removing a file that contains text, use `git mv` and never delete written content without the user's agreement. Update `@sec:` references affected by renames.

Then offer to freeze the agreed plan as the first snapshot (`./build.sh snapshot 01-outline`, see the paper-build skill) and suggest the paper-write skill for drafting.
