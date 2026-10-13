---
name: latex-slides
description: Turn a rough slide outline (plain text or markdown, one block per slide, may reference image files by path/filename) into a LaTeX beamer presentation — either a single .tex file or a full compilable project folder with images. Use this skill whenever the user pastes a slide-by-slide outline and asks for LaTeX/beamer slides, mentions "投影片", "slides", "beamer", or gives an outline with image references intended for a presentation — even if they don't explicitly say "skill" or "LaTeX". Content is primarily Traditional Chinese (xelatex + ctex/xeCJK).
---

# LaTeX Slides (Beamer)

Converts a user-supplied slide outline into a LaTeX beamer deck. The user writes outlines like this (numbers may skip — treat as ordering hints, not literal indices):

```
Slide 1｜Title
* 標題：...
* 副標：...

Slide 4｜實驗一：單 AP 距離量測穩定性
* Box plot：...
* 表格：...
* 結論 bullet：...
```

## Language & toolchain

Default output language is **Traditional Chinese**, compiled with `xelatex` using `ctex` (which pulls in `xeCJK`) and a CJK-capable font (`fontspec`, e.g. `Noto Sans CJK TC` / `Noto Serif CJK TC` if available, else let fontspec fall back to a system CJK font). Do not silently translate the user's bullets to English — keep their wording, only lightly tighten grammar/punctuation for slide readability.

```latex
\documentclass[aspectratio=169]{beamer}
\usepackage{ctex}          % pulls in xeCJK, sets up Chinese
\usepackage{fontspec}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{amsmath}
```
Compile with `xelatex` (not `pdflatex` — pdflatex can't do CJK via ctex/xeCJK).

**Check this environment before promising a compiled PDF.** Run `kpsewhich ctex.sty xeCJK.sty beamer.sty metropolis.sty` first.
- If `beamer.sty` / `ctex.sty` are missing and there's no network access to install them (common in this sandboxed environment), skip the compile step, say so plainly, and tell the user to compile locally or on Overleaf — do NOT claim it compiled if you never ran xelatex successfully.
- If the toolchain is present, actually run `xelatex` (twice, for references/TOC) after writing the file and fix any errors before delivering.

## Theme (no template supplied — use a clean default)

User has no house template, so default to something clean and non-flashy suited for technical/research content:
- Prefer `\usetheme{metropolis}` if `metropolis.sty` is found (kpsewhich check above).
- Otherwise fall back to `\usetheme{Madrid}` or `\usetheme{Berlin}` with muted colors (`\usecolortheme{seahorse}` or similar) — avoid loud defaults.
- `aspectratio=169` (16:9) unless the user says otherwise.
- Page numbers in the footer. No decorative clipart.
- Tables: always `booktabs` (`\toprule/\midrule/\bottomrule`), never default grid lines.

## Parsing the outline

- One `Slide N｜Title` block → one frame. The `N` is just an ordering hint from the user's notes (they often skip numbers for slides they haven't drafted yet, e.g. jumping 2→4) — renumber sequentially in the actual deck. If a gap looks like it might be a real missing slide the user forgot to send rather than an intentional skip, ask instead of guessing.
- Bullets become `\begin{itemize}` items. Keep bullet fidelity — don't invent extra content or elaborate beyond what's written. Structural boilerplate (title page fields, section dividers) is fine to add; invented technical claims are not.
- Text like「待補充」/ "TODO" / placeholder notes → keep as a visible TODO marker in the slide (e.g. `\textcolor{red}{[待補充]}`) or a `% TODO:` comment if it's a note-to-self rather than slide content, not a fabricated number.
- Mentions of "表格" → real `tabular` with booktabs, using whatever rows/columns the outline implies. If the outline doesn't give the actual data values, leave cells as `TODO` rather than inventing numbers.
- Mentions of "散點圖" / "Box plot" / chart types without an actual image path → insert a placeholder `\includegraphics` pointing at a TODO filename, or a framed empty box with a caption, and flag it to the user as something they still need to supply.

## Images

The user gives paths/filenames, not necessarily uploaded inline. Before referencing an image:
1. Check if it exists (`view` or `bash ls`/`test -f`).
2. If found, copy/reference it relative to the deck (e.g. into an `images/` subfolder if using a project folder) and use `\includegraphics[width=\linewidth]{...}` (or `width=0.48\linewidth` for two side-by-side figures via `minipage`).
3. If not found, don't fail silently — insert a placeholder box + `% TODO: image not found: <path>` comment, and list all missing images back to the user at the end of your reply.

Layout patterns:
- Single figure + bullets: figure on its own line or two-column frame (`\begin{columns}`) with bullets on one side.
- "1-2 張關鍵截圖" comparison (e.g. before/after) → two `minipage`/`subfigure` side by side with short captions.
- Multi-panel comparisons (e.g. 3 frequency bands) → consider a grid via `\includegraphics` in a table or `subcaption` package.

## Output: single .tex vs. project folder

Decide per-deck, don't ask every time:
- **Single self-contained `.tex`**: no images, or only a couple of images referable via simple relative paths, no bibliography.
- **Project folder** (`main.tex`, `images/`, optionally `references.bib`, `Makefile`/`latexmk` config): several images to organize, a bibliography, or the deck is clearly a multi-experiment report like the FTM-eval example above.
- State which one you chose and why in one line of your reply — don't make the user guess.

## Workflow

1. Parse the outline into an ordered slide list; note any placeholder/TODO content and any slide-number gaps worth flagging.
2. Resolve image paths (see above); collect a list of anything missing.
3. Draft the `.tex` (or project folder) following the structure/theme defaults above.
4. Run the `kpsewhich` toolchain check; if compilable, run `xelatex` (twice) and fix errors until it compiles cleanly. If not compilable in this environment, say so.
5. Deliver the file(s), and in your reply briefly note: theme used, single-file-vs-folder choice, any TODO/placeholder content left for the user, and any missing images.
