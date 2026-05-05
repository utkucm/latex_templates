# latex-templates

Personal LaTeX templates for various purposes.

## Templates

| Template | Description |
|---|---|
| `assignments/` | Problem set / homework template with numbered problems, parts, solution boxes, and auto bibliography |
| `beamer_presentation/` | Minimal formal Beamer presentation with custom dark navy theme, section dividers, and a thank-you slide |
| `cv/` | Minimal formal academic CV with two-column date/content entries and small-caps section headers |
| `lecture_notes/` | Multi-lecture notes template with per-lecture counters, TOC, and header navigation |
| `research_statement/` | Clean research statement template with Times-style font |
| `paper/` | Math-heavy economics working paper with APA citations, per-section theorem/equation numbering, and standard section skeleton |

## Requirements

A full TeX distribution is required (e.g. [TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/)). The following packages must be available:

`amsmath`, `amssymb`, `amsthm`, `mathtools`, `bm`, `geometry`, `lmodern`, `microtype`, `parskip`, `fancyhdr`, `hyperref`, `cleveref`, `apacite`, `booktabs`, `enumitem`, `xcolor`, `tcolorbox`, `listings`, `graphicx`, `etoolbox`

Additionally: `newtxtext` (research statement, cv), `titlesec` (cv), `tikz` (beamer), `datetime`, `environ` (lecture notes).

## Building

```bash
# compile a specific template
make assignments
make beamer_presentation
make cv
make lecture_notes
make research_statement

# compile all
make all

# clean build artifacts
make clean
```

Or compile manually:

```bash
cd assignments && latexmk -pdf main.tex
```

## Usage

1. Copy the desired template directory.
2. Edit the metadata commands at the top of `main.tex` (e.g. `\coursename`, `\studentname`).
3. Add content after `\maketitlepage{}` / `\makecoursetitlepage{}` / `\makestatementtitle{}`.
4. Place references in `references.bib` — the bibliography is included automatically when `\cite` is used.
