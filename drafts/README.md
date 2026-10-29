# Drafts

| Folder | Content |
| --- | --- |
| `00-raw/` | Raw material: ideas, literature notes, preliminary results, sketches, data excerpts. Free-form; edit at will. |
| `NN-label/` | Frozen snapshot of the paper at a milestone, e.g. `01-outline`, `02-first-draft`, `03-full-draft`, `04-internal-review`, `05-submitted`, `06-camera-ready`. |

Create a snapshot after building:

```
./build.sh
./build.sh snapshot 02-first-draft
```

A snapshot contains copies of `paper/`, `references/`, `figures/`, and `paper.pdf` (if built), plus a `NOTES.md` describing the state of the draft. Snapshots are never edited; the next stage gets the next number. Compare stages with `diff -ru drafts/02-first-draft/paper paper`.
