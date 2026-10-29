---
name: paper-review
description: Critically review a research paper written in this project the way a conference or journal peer reviewer would — contributions, novelty, soundness, evidence for claims, related work, clarity, and presentation for the target venue — and produce a prioritized list of actionable issues. Use when the user asks for a review, feedback, critique, or pre-submission check of the paper's content.
---

# Review the paper

This is a **content** review. Mechanical checks (missing citations, broken references, page limits, fonts) belong to the paper-validate skill; run it as well for a full pre-submission check.

Do not edit the paper during a review unless the user asks. The output is a review.

## Read everything first

`paper/abstract.md`, all `paper/sections/*.md` in order, `paper/outline.md` (intended contributions), `AGENTS.md` (venue), `STYLE.md` (publisher conventions), `references/references.bib`, and the figures (open the PDFs, or `build/paper.pdf` if it exists, to judge them as a reader sees them).

If snapshots exist in `drafts/` (`01-*` and later), compare the current paper with the latest one (`diff -ru drafts/<latest>/paper paper`) and check whether a review saved in that snapshot was addressed. Note regressions: removed evidence, claims that grew stronger without new support. Check `drafts/00-raw/` for promising material (ideas, preliminary results) that the paper does not use yet.

## What to assess

1. **Contribution and novelty.** Are contributions stated explicitly in the introduction? Are they significant and distinct from cited prior work? Would a reviewer ask "how is this different from [X]?"
2. **Claims vs. evidence.** List every claim in the abstract, introduction, and conclusion. For each, locate the supporting evidence (result, figure, table, proof, citation). Flag claims that are unsupported, overstated, or inconsistent with the reported numbers.
3. **Soundness of method and experiments.** Baselines appropriate and fairly tuned? Datasets, metrics, and splits described? Statistical significance, variance, or confidence intervals reported? Ablations for the components claimed to matter? Enough detail to reproduce? Threats to validity / limitations discussed?
4. **Related work.** Organized by theme rather than as a list; positions this work against each theme; obvious omissions (name the area — do not invent specific papers; suggest the user search, or use the paper-citations skill to find and verify candidates).
5. **Structure and flow.** Does each section do its job? Does the introduction motivate → gap → contribution → organization? Are results interpreted, not just reported? Does the conclusion avoid new claims?
6. **Figures and tables.** Each necessary, referenced, readable at print size, captions self-contained, axes labeled with units.
7. **Writing.** Consistent terminology, abbreviations defined, precise language, no filler, appropriate tense. Note recurring problems with one or two examples rather than every instance.
8. **Abstract.** Self-contained, states problem, approach, key quantitative result, and significance within the word limit.

## Output

```markdown
# Review: <title>

## Summary
<3–5 sentences: what the paper claims and does, as a reviewer would summarize it>

## Assessment
Strengths: ...
Weaknesses: ...
Likely reviewer verdict and main reason: ...

## Issues
### Major (could lead to rejection)
1. **<short title>** — `paper/sections/05-results.md:42`
   Problem: ...
   Suggested fix: ...

### Minor
...

### Writing and presentation
...

## Questions a reviewer would ask
- ...
```

Rules:

- Every issue cites a location (`file:line`) and gives a concrete, actionable fix.
- Order by impact on acceptance, not by position in the paper.
- Be specific and honest; do not pad with praise or soften major problems.
- Do not suggest adding results or references that do not exist; say what kind of evidence is missing.

Print the review in the conversation. If the user wants it saved, write it to `reviews/review-YYYY-MM-DD.md` (not under `paper/`). For a milestone review, offer to take a snapshot first (`./build.sh snapshot NN-internal-review`) and save the review as `REVIEW.md` inside that snapshot, so the reviewed version and the review stay together. Offer to address the issues with the paper-write skill.
