#!/usr/bin/env python3
"""Create independent LaTeX projects from this repository's source templates.

No dependencies beyond Python's standard library are required.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# CLI metadata field -> existing \newcommand macro in each source template.
TEMPLATES: dict[str, dict[str, str]] = {
    "assignments": {
        "course": "coursename",
        "title": "assignmenttitle",
        "author": "studentname",
        "student-id": "studentid",
        "date": "duedate",
    },
    "paper": {
        "title": "papertitle",
        "subtitle": "papersubtitle",
        "author": "authorname",
        "email": "authoremail",
        "affiliation": "affiliation",
        "date": "paperdate",
    },
    "lecture_notes": {
        "course": "coursename",
        "course-number": "coursenumber",
        "instructor": "instructor",
        "author": "noteauthor",
        "semester": "semester",
    },
    "beamer_presentation": {
        "title": "talkTitle",
        "subtitle": "talkSubtitle",
        "author": "authorname",
        "affiliation": "affiliation",
        "date": "talkdate",
        "event": "eventname",
    },
    "cv": {
        "author": "cvname",
        "department": "cvdepartment",
        "institution": "cvinstitution",
        "address": "cvaddress",
        "email": "cvemail",
        "phone": "cvphone",
        "website": "cvwebsite",
    },
    "research_statement": {
        "title": "titletext",
        "author": "authortext",
        "affiliation": "affiliation",
        "date": "datetext",
    },
    "referee_report": {
        "title": "manuscripttitle",
        "journal": "journalname",
        "manuscript-id": "manuscriptid",
        "date": "reportdate",
    },
}

ALIASES = {
    "assignment": "assignments",
    "slides": "beamer_presentation",
    "beamer": "beamer_presentation",
    "lecture-notes": "lecture_notes",
    "research-statement": "research_statement",
    "referee-report": "referee_report",
}

# Character-wise escaping avoids interpreting user metadata as TeX code.
LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(value: str) -> str:
    """Escape a single-line plain-text metadata value for use in LaTeX."""
    if any(char in value for char in "\r\n\x00"):
        raise ValueError("Metadata values must be single-line text without NUL characters")
    return "".join(LATEX_ESCAPES.get(char, char) for char in value)


def render_metadata(contents: str, macros: dict[str, str], values: dict[str, str]) -> str:
    """Replace only the known metadata command definitions, preserving the document body."""
    for field, value in values.items():
        macro = macros[field]
        expression = re.compile(
            r"(?m)^([ \t]*\\newcommand\{\\"
            + re.escape(macro)
            + r"\}\{)([^{}\r\n]*)(\})"
        )
        contents, count = expression.subn(
            lambda match: match.group(1) + escape_latex(value) + match.group(3),
            contents,
        )
        if count != 1:
            raise ValueError(
                f"Expected exactly one \\newcommand{{\\{macro}}} in main.tex; found {count}"
            )
    return contents


def makefile_for(template: str) -> str:
    mode = "-lualatex" if template == "beamer_presentation" else "-pdf"
    return (
        ".PHONY: all clean\n"
        "LATEXMK ?= latexmk\n"
        f"MODE := {mode}\n\n"
        "all:\n\t$(LATEXMK) $(MODE) -interaction=nonstopmode -file-line-error main.tex\n\n"
        "clean:\n\t$(LATEXMK) -C main.tex\n"
    )


def scaffold_document(
    template: str,
    output: Path,
    values: dict[str, str],
    *,
    dry_run: bool = False,
) -> Path:
    """Copy a template without modifying its source or overwriting any destination."""
    template = ALIASES.get(template, template)
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template {template!r}. Run python3 scaffold.py list.")
    unsupported = set(values) - set(TEMPLATES[template])
    if unsupported:
        raise ValueError(
            f"Unsupported metadata for {template}: {', '.join(sorted(unsupported))}"
        )

    source = ROOT / template
    if not source.is_dir():
        raise FileNotFoundError(f"Template directory missing: {source}")
    destination = output.expanduser().resolve(strict=False)
    if destination == source or source in destination.parents:
        raise ValueError("Destination cannot be inside the source template directory")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")

    # Preflight substitutions before writing anything to disk.
    main_text = (source / "main.tex").read_text(encoding="utf-8")
    rendered = render_metadata(main_text, TEMPLATES[template], values)
    if dry_run:
        print(f"Would create {destination} from {template}/")
        for path in sorted(source.rglob("*")):
            if path.is_file():
                print(f"  {path.relative_to(source)}")
        print("  Makefile")
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    # Stage on the same filesystem so a rendering error leaves no partial document.
    with tempfile.TemporaryDirectory(prefix=".latex-scaffold-", dir=destination.parent) as temp:
        staged = Path(temp) / "document"
        shutil.copytree(source, staged)
        (staged / "main.tex").write_text(rendered, encoding="utf-8")
        (staged / "Makefile").write_text(makefile_for(template), encoding="utf-8")
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Destination already exists: {destination}")
        staged.rename(destination)
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List template types and their metadata fields")
    new = commands.add_parser("new", help="Generate a document from an existing template")
    new.add_argument("template", choices=sorted([*TEMPLATES, *ALIASES]))
    new.add_argument("--output", "-o", type=Path, required=True, help="New destination directory")
    new.add_argument("--dry-run", action="store_true", help="Show files without writing")
    for field in sorted({field for fields in TEMPLATES.values() for field in fields}):
        new.add_argument("--" + field, help=f"Plain-text metadata: {field}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list":
        for name, fields in TEMPLATES.items():
            print(f"{name}: " + ", ".join("--" + field for field in fields))
        return 0
    fields = {
        field: getattr(args, field.replace("-", "_"))
        for field in {field for values in TEMPLATES.values() for field in values}
    }
    specified = {field: value for field, value in fields.items() if value is not None}
    try:
        destination = scaffold_document(
            args.template, args.output, specified, dry_run=args.dry_run
        )
    except (ValueError, FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not args.dry_run:
        print(f"Created {destination}\nBuild: cd {destination} && make")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
