# latex-templates

Personal LaTeX templates for various purposes.

## Templates

| Template               | Use for                                       |
| ---------------------- | --------------------------------------------- |
| `assignments/`         | Problem sets, assignments                     |
| `paper/`               | Academic papers, reports                      |
| `lecture_notes/`       | Lecture notes with per-lecture file structure |
| `beamer_presentation/` | Slide decks (Beamer)                          |
| `cv/`                  | Curriculum vitae                              |
| `research_statement/`  | Research statements                           |
| `referee_report/`      | Journal referee reports                       |

## Usage

1. Copy the desired template directory.
2. Edit the metadata commands at the top of `main.tex` (e.g. `\coursename`, `\studentname`).
3. Add content after `\maketitlepage{}` / `\makecoursetitlepage{}` / `\makestatementtitle{}`.
4. Place references in `references.bib` — the bibliography is included automatically when `\cite` is used.
