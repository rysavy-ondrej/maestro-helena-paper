---
name: paper-tables
description: Create and format tables for a Markdown/LaTeX research paper — Markdown pipe tables for simple data, raw LaTeX booktabs tables for complex layouts, captions, labels, and cross-references. Use when the user asks for a table, results table, comparison table, or to fix table layout.
---

# Tables

Two ways to write a table:

| Table | Write as |
| --- | --- |
| Simple grid, fits one column, no merged rows | Markdown pipe table |
| Merged cells, multi-row headers, full page width, decimal alignment, generated from data | Raw LaTeX block |

## Markdown tables

```markdown
: Detection accuracy on the test set. {#tbl:accuracy}

| Method   | Precision | Recall |    F1 |
|:---------|----------:|-------:|------:|
| Baseline |     0.812 |  0.774 | 0.793 |
| Ours     |     0.861 |  0.840 | 0.850 |
```

- The caption line (`: Caption. {#tbl:label}`) goes directly before or after the table, separated by a blank line.
- Alignment comes from the colons in the separator row. Right-align numeric columns.
- Reference with `@tbl:accuracy` → "Table I" (IEEE) or "Table 1".
- `latex/filters/tables.lua` converts these into a `table` float with a `booktabs` `tabular` and the caption above (the convention of IEEE, ACM, Springer, and Elsevier). Pandoc's default `longtable` output is not used because it fails in two-column layouts. The filter supports column spans but not row spans.
- Inline Markdown (emphasis, math, citations) inside cells works. Bold the best result per column with `**0.850**` only if the paper uses that convention consistently.

## Raw LaTeX tables

Use for anything beyond a simple grid. Reference with `Table\ \ref{tbl:name}`.

````markdown
```{=latex}
\begin{table*}[t]
  \centering
  \caption{Comparison with prior work across datasets.}
  \label{tbl:comparison}
  \begin{tabular}{l cc cc}
    \toprule
    & \multicolumn{2}{c}{Dataset A} & \multicolumn{2}{c}{Dataset B} \\
    \cmidrule(lr){2-3} \cmidrule(lr){4-5}
    Method & F1 & Time (s) & F1 & Time (s) \\
    \midrule
    Baseline~\cite{smith2025} & 0.79 & 12.1 & 0.71 & 30.4 \\
    Ours & 0.85 & 9.8 & 0.80 & 22.7 \\
    \bottomrule
  \end{tabular}
\end{table*}
```
````

- `table` = one column, `table*` = full text width (floats to the top of a page).
- Use `booktabs` rules only (`\toprule`, `\midrule`, `\cmidrule`, `\bottomrule`); no vertical lines.
- In raw blocks, cite with `\cite{key}` — Markdown citations are not processed inside raw LaTeX.
- Extra packages (`multirow`, `siunitx`, `threeparttable` for table notes) must be added to `latex/main.tex`.
- If a table is too wide: shorten headers, use abbreviations defined in a table note, reduce precision, switch to `table*`, or as a last resort `\resizebox{\linewidth}{!}{...}` (shrinks the font; avoid if possible).

## Tables generated from data

For results that change as experiments rerun, generate the `tabular` from data instead of typing numbers: a script (e.g. `tables/src/results.py`) writes `tables/results.tex`, and the Markdown includes it in a raw block:

````markdown
```{=latex}
\begin{table}
  \centering
  \caption{Results.}\label{tbl:results}
  \input{tables/results.tex}
\end{table}
```
````

`\input` paths are relative to the project root (set up in `latex/pandoc-compat.tex`). Add a Makefile rule for the generated table if it should rebuild automatically.

## Rules

- **Numbers must come from real results** — the user's data or experiment outputs. Never invent or "illustrate" values; use `[TODO]` cells and tell the user.
- Every table has a caption and label and is referenced in the text.
- Report units in headers, consistent decimal places, and what the best value means (higher/lower is better) in the caption when not obvious.
- Caption placement and numbering come from the class: IEEE uses Roman numerals (Table I), the others Arabic (Table 1).

Build with `./build.sh`, check that the table fits (no overfull-box warning in the check summary), and look at it with `./build.sh preview`.
