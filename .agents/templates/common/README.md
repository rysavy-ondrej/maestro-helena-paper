# Research Paper

The paper is written in Pandoc Markdown, converted to LaTeX with Pandoc, and typeset with LaTeX.

| Path | Content |
| --- | --- |
| `paper/abstract.md` | Abstract |
| `paper/sections/` | One Markdown file per section, built in file-name order |
| `paper/metadata.yaml` | Pandoc and pandoc-crossref settings |
| `references/references.bib` | BibTeX database |
| `figures/` | Figures (vector PDF preferred); `figures/src/<name>.py` builds `figures/<name>.pdf` |
| `latex/main.tex` | LaTeX template: title, authors, keywords, document class |
| `latex/generated/` | Pandoc output; do not edit |
| `build/paper.pdf` | Final PDF |
| `drafts/00-raw/` | Raw material: ideas, literature notes, preliminary results |
| `drafts/NN-label/` | Frozen snapshots of the paper at milestones (`./build.sh snapshot NN-label`) |

## Build

```
./build.sh setup     # once: local Pandoc, pandoc-crossref, TinyTeX (if needed), Python .venv
./build.sh           # build/paper.pdf + checks; prints BUILD OK or the cause of a failure
./build.sh help      # all commands (check, preview, figures, snapshot, doctor, clean)
```

Works on macOS and Linux (including WSL). Prerequisites: `bash`, `curl`, `make`, `perl`, `xz`, `python3`. A system TeX Live with the document class from `STYLE.md` is used if present.

See `AGENTS.md` for authoring rules.
