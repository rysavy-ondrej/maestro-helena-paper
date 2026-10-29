---
name: paper-write
description: Draft, expand, or revise sections of a research paper written in Pandoc Markdown for LaTeX output (IEEE, ACM, Springer, Elsevier, or a venue template) — prose, citations, equations, cross-references, and raw LaTeX where needed. Use when the user asks to write, rewrite, edit, shorten, or polish paper text or the abstract.
---

# Write paper sections

Sources of truth: `paper/abstract.md`, `paper/sections/*.md`, guided by `paper/outline.md`, the rules in `AGENTS.md`, and the publisher conventions in `STYLE.md` (citation form, reference prefixes, abstract length). Read the outline, the neighbouring sections, and the bibliography before writing so terminology and claims stay consistent.

Draw on `drafts/00-raw/` for ideas, reading notes, and preliminary results, but rewrite rather than paste, and do not carry over anything unverified: numbers from `preliminary-results.md` need confirmation from the user or a reproducible source, and works from `literature.md` must be imported into `references/references.bib` (paper-citations skill) before they are cited. Never edit snapshot folders `drafts/01-*` and later; to reuse text from an earlier draft, copy it into `paper/`.

## Hard rules

- **No fabrication.** Never invent results, numbers, datasets, quotations, or references. Where content is missing, write `[TODO: what is needed]`; where a claim needs support you do not have, write `[CITATION NEEDED]`. Tell the user what you left open.
- **Cite only existing keys** from `references/references.bib`. To add a reference, use the paper-citations skill.
- **Never edit `latex/generated/`.** Edit Markdown only; change `latex/main.tex` only for metadata or packages.
- Keep each top-level section in its own file.

## Pandoc Markdown conventions

**Line breaks.** One sentence per line, for clean diffs. Blank line between paragraphs.

**Headings.** `#` = section, `##` = subsection, `###` = subsubsection. Label sections you reference: `## Threat Model {#sec:threat-model}`.

**Citations** (converted to `\cite{}`; shown for a numeric style — the bibliography style in `STYLE.md` decides the final form):

| Write | Output |
| --- | --- |
| `[@smith2025]` | [1] |
| `[@smith2025; @jones2026]` | [1], [2] |
| `[@smith2025, p. 5]` | [1, p. 5] |
| `Smith et al. [@smith2025]` | Smith et al. [1] |

Always use the bracketed form. Do not use bare `@smith2025` or prefixes such as `[see @smith2025]` — with numeric styles they lose text or break. Exception: author–year styles (e.g. Elsevier `elsarticle-harv`), where `STYLE.md` says when to use bare `@key` for "Smith (2020)". Put the citation before the period; in numeric styles, avoid citations as grammatical nouns ("as shown in [1]", not "[1] shows").

**Cross-references** (pandoc-crossref): `@fig:name`, `@tbl:name`, `@eq:name`, `@sec:name` produce the venue's prefixes from `paper/metadata.yaml` (IEEE: "Fig. 1", "Table I"; ACM: "Figure 1", "Table 1"; LNCS: "Fig. 1", "Sect. 2"). Capitalize at sentence start: `@Fig:name`.

**Math.** Inline `$x_i$`; display equations with a label when referenced:

```markdown
$$
C(x) = \frac{1}{N}\sum_{i=1}^{N} p_i(x)
$$ {#eq:confidence}
```

Use standard `amsmath` commands. Multi-line alignment needs a raw block (below).

**Figures and tables.** See the paper-figures and paper-tables skills. Every figure and table must be referenced in the text before or near where it appears.

**Lists.** Markdown lists become `itemize`/`enumerate`. Contribution lists in the introduction are a common use.

**Raw LaTeX** for what Markdown cannot express — aligned equations, algorithms, two-column figures, complex tables:

````markdown
```{=latex}
\begin{align}
  a &= b + c \label{eq:sum}\\
  d &= e
\end{align}
```
````

Reference labels defined in raw LaTeX with the same prefixes the venue uses, e.g. `Eq.\ \eqref{eq:sum}`, `Fig.\ \ref{fig:x}` (or `Figure\ \ref{fig:x}` for ACM), `Table\ \ref{tbl:x}` (`\ ` is a non-breaking space in Pandoc Markdown). Packages a raw block needs (e.g. `algorithm`, `algpseudocode`) must be added to `latex/main.tex`.

**Avoid:** code blocks with a language class (` ```python `) — they emit `Shaded` environments the template does not define; use a plain fence or a raw `verbatim`/`lstlisting` block. Avoid HTML (dropped in LaTeX output) and Unicode symbols where a LaTeX command exists (`$\alpha$`, not α; `--` for ranges).

## Style (formal scientific English)

Venue conventions (abbreviations such as "Fig." vs. "Figure", abstract length, required statements) are in `STYLE.md`; general rules:

- State the claim, then the evidence. Prefer precise, quantified, verifiable statements; hedge only where uncertainty is real.
- Define abbreviations at first use in the abstract and again in the body. Keep terminology consistent across sections (check the outline and earlier sections).
- Avoid contractions, rhetorical questions, and filler ("very", "clearly", "it is worth noting that").
- Use "we" for the authors' actions; past tense for what was done in experiments, present tense for what the results show.
- Numbers: units with a thin space via math or `\,` in raw LaTeX; consistent decimals; percentages as "12.5%".
- The abstract (`paper/abstract.md`) is one paragraph within the venue's word limit (`STYLE.md`; typically 150–250 words), without citations, equations, or cross-references.

## After writing

Run `./build.sh` (paper-build skill) after substantive changes and fix what you introduced. Summarize changes and list every `[TODO]` / `[CITATION NEEDED]` you added. When a draft reaches a milestone (all sections drafted, ready for co-author review, submitted), offer to take a snapshot (`./build.sh snapshot NN-label`).
