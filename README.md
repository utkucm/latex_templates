# latex-templates

Personal LaTeX templates for various purposes.

## Templates

| Template               | Use for                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- |
| `assignments/`         | Problem sets, assignments                                                        |
| `paper/`               | Academic papers, reports                                                         |
| `lecture_notes/`       | Lecture notes with per-lecture file structure                                    |
| `beamer_presentation/` | Slide decks (Beamer, moloch theme)                                               |
| `cv/`                  | Curriculum vitae                                                                 |
| `research_statement/`  | Research statements                                                              |
| `referee_report/`      | Referee report (`main.tex`) and confidential editor letter (`editor_letter.tex`) |
| `referee_response/`    | Response to the editor and referees for a revision                               |

## Usage

1. Copy the template directory, including its hidden `.latexmkrc`.
2. Edit the metadata commands at the top of `main.tex` (e.g. `\coursename`, `\papertitle`).
3. Replace the example content. Run `latexmk` inside the directory.

Building from the repository root:

```sh
make                 # build every template
make paper           # build one
make check           # build all, then fail on undefined references or drifted shared blocks
make clean           # remove all generated files, PDFs included
```

## Conventions

- **Citations:** natbib with `apalike`, references in `references.bib`. Use `\citet{key}` for
  "Author (2020)" and `\citep{key}` for "(Author, 2020)".
- **Bibliography:** printed automatically at the end of the document, only if the document cites
  something, so a document without citations has no empty "References" heading. Citations are
  tracked during the current run, so builds that delete `.aux` files work. In Beamer the
  References frame at the end of the body uses the same test.
- **Cross-references:** cleveref (`\cref`, `\Cref`). Theorem-like environments are declared with
  thmtools so that `\cref` names environments sharing a counter correctly.
- **Lectures:** `\newlecture{number}{topic}{date}` starts a new page and sets the heading, TOC
  entry and running header; leave the topic or date empty to omit it.
- **Shared preamble blocks:** blocks between `% >>> shared: NAME` and `% <<< shared: NAME`
  (math macros, conditional bibliography) must be identical in every template that has them.
  Edit one, copy it to the others; `make check` reports any difference.
