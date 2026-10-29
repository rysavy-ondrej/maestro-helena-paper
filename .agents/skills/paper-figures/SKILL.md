---
name: paper-figures
description: Create, regenerate, and insert figures for a Markdown/LaTeX research paper (IEEE, ACM, Springer, Elsevier, or a venue template) — reproducible vector plots from Python scripts, diagrams, sizing for one- or two-column layouts, captions, labels, and cross-references. Use when the user asks for a figure, plot, chart, diagram, or to fix figure size, placement, or quality.
---

# Figures

Figures live in `figures/`. Plots are generated reproducibly: `figures/src/<name>.py` writes `figures/<name>.pdf`, and `./build.sh figures` (also part of `./build.sh`) rebuilds any figure whose script changed, using the project's `.venv` (`requirements.txt`; add packages there if a script needs them).

## Inserting a figure (single column)

```markdown
![Architecture of the proposed system.](figures/architecture.pdf){#fig:architecture width=100%}
```

- Paths are **relative to the project root** (`figures/...`), not to the Markdown file.
- `width=100%` → full column width (`\linewidth`). Use smaller percentages for narrow figures.
- Reference it in the text with `@fig:architecture` ("Fig. 1"), before or near the figure.
- Captions: a sentence fragment or full sentence, ending with a period. Caption placement and numbering follow the class (below the figure in all bundled templates).
- ACM requires a figure description for accessibility; the ACM template's filter adds `\Description{}` from the caption, raw LaTeX figures need their own.

## Two-column (full-width) figures

Markdown cannot express `figure*`. Use a raw block and reference with `Fig.\ \ref{fig:pipeline}`:

````markdown
```{=latex}
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/pipeline.pdf}
  \caption{End-to-end processing pipeline.}
  \label{fig:pipeline}
\end{figure*}
```
````

In two-column layouts (IEEE, ACM `sigconf`, Elsevier `twocolumn`), `figure*` floats only to the top of a page, on the page after it is defined or later. Subfigures likewise need raw LaTeX (`\usepackage{subcaption}` in `latex/main.tex`).

## Generating plots (Python / matplotlib)

Create `figures/src/<name>.py` that takes the output path as `sys.argv[1]`:

```python
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],  # match the body font (STYLE.md)
    "mathtext.fontset": "stix",  # Times-like math
    "font.size": 8,              # figure text at 8pt next to the 10pt body
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "pdf.fonttype": 42,          # embed TrueType; publishers reject Type 3 fonts
    "ps.fonttype": 42,
})

fig, ax = plt.subplots(figsize=(3.5, 2.2))   # width = column or text width from STYLE.md
# ... plot from data files, e.g. data/results.csv — never hard-code invented numbers ...
fig.tight_layout()
fig.savefig(sys.argv[1], bbox_inches="tight")
```

Rules:

- **Data must be real.** Read results from the project's data files or experiment outputs. If no data exists, do not invent it; create the script with a clearly marked loader and tell the user what data is needed.
- Design at final size so fonts are not scaled down to unreadable sizes. Widths per template (details in `STYLE.md`):

  | Template | Column | Full width |
  | --- | --- | --- |
  | IEEE | 3.5 in | 7.16 in |
  | ACM `sigconf` | 3.33 in | 7.0 in |
  | ACM `acmsmall` | 5.48 in | — |
  | Springer LNCS | 4.8 in (12.2 cm) | — |
  | Elsevier | 90 mm / 140 mm | 190 mm |
  | Generic article | 6.5 in | — |

  For other classes, print the width once with a raw `\typeout{column=\the\columnwidth, text=\the\textwidth}` and read it from `build/main.log`.
- Match fonts to the body: Times-like for IEEE and Elsevier `times`, Libertine-like or sans for ACM, Computer Modern for LNCS (`"font.serif": ["CMU Serif", ...]` or `"mathtext.fontset": "cm"`).
- Legible in grayscale: distinguish series by marker/line style as well as color; use a colorblind-safe palette.
- Label axes with quantity and unit; avoid titles inside the plot (the caption is the title).
- Run `./build.sh figures`, then **look at the result**: `./build.sh preview figures/<name>.pdf` renders it to `build/preview/<name>-1.png`; view that PNG. Check for text overflowing boxes, elements clipped at the edges (`bbox_inches="tight"` does not rescue patches drawn outside the axis limits), overlapping labels, and legends covering data.

## Diagrams

- Prefer vector: draw.io/diagrams.net or Inkscape exported to PDF, or TikZ in a raw LaTeX block (add `\usepackage{tikz}` to `latex/main.tex`).
- SVG → PDF: `rsvg-convert -f pdf -o figures/x.pdf figures/x.svg` or `inkscape figures/x.svg --export-filename=figures/x.pdf`.
- Commit diagram sources (e.g. `figures/src/architecture.drawio`) next to the exported PDF.

## Raster images

Screenshots and photos are acceptable as PNG/JPEG at ≥300 dpi at final size. Never rasterize plots or diagrams.

## Checklist

Each figure: exists at the referenced path, has a label and caption, is referenced in the text, fits the column (no overfull boxes), uses embedded non-Type-3 fonts, and is readable at print size. The paper-validate skill checks paths, labels, references, and fonts.
