"""Run with python3 -m unittest discover -s tests -v from repository root."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import scaffold


class ScaffoldTests(unittest.TestCase):
    def test_every_template_generates_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            for template, fields in scaffold.TEMPLATES.items():
                source = scaffold.ROOT / template
                original = (source / "main.tex").read_bytes()
                destination = Path(temp) / template
                values = {field: f"Test {field}" for field in fields}
                scaffold.scaffold_document(template, destination, values)
                self.assertTrue((destination / "main.tex").is_file())
                self.assertTrue((destination / "Makefile").is_file())
                self.assertEqual((source / "main.tex").read_bytes(), original)
                rendered = (destination / "main.tex").read_text(encoding="utf-8")
                for field, macro in fields.items():
                    self.assertIn(
                        f"\\newcommand{{\\{macro}}}{{Test {field}}}", rendered
                    )
                for file in source.rglob("*"):
                    if file.is_file():
                        self.assertTrue(
                            (destination / file.relative_to(source)).is_file()
                        )

    def test_special_characters_are_escaped_as_plain_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "document"
            value = r"Taxes & Growth_50% #1 $ {test} ~ ^ \\"
            scaffold.scaffold_document("paper", output, {"title": value})
            contents = (output / "main.tex").read_text(encoding="utf-8")
            expected = scaffold.escape_latex(value)
            self.assertIn(r"\newcommand{\papertitle}{" + expected + "}", contents)

    def test_prevents_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "existing"
            output.mkdir()
            (output / "notes.tex").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                scaffold.scaffold_document("paper", output, {})
            self.assertEqual((output / "notes.tex").read_text(), "keep")

    def test_prevents_destination_inside_source(self) -> None:
        with self.assertRaises(ValueError):
            scaffold.scaffold_document("paper", scaffold.ROOT / "paper" / "new", {})

    def test_rejects_unsupported_metadata_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "document"
            with self.assertRaisesRegex(ValueError, "Unsupported metadata"):
                scaffold.scaffold_document("cv", output, {"journal": "Wrong"})
            self.assertFalse(output.exists())

    def test_rejects_multiline_values_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "document"
            with self.assertRaisesRegex(ValueError, "single-line"):
                scaffold.scaffold_document("paper", output, {"author": "A\nB"})
            self.assertFalse(output.exists())

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "document"
            scaffold.scaffold_document(
                "assignment", output, {"title": "Set 1"}, dry_run=True
            )
            self.assertFalse(output.exists())

    def test_makefile_uses_lualatex_for_beamer(self) -> None:
        self.assertIn("-lualatex", scaffold.makefile_for("beamer_presentation"))
        self.assertIn("-pdf", scaffold.makefile_for("paper"))

    def test_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "Unknown template"):
                scaffold.scaffold_document("unknown", Path(temp) / "document", {})


if __name__ == "__main__":
    unittest.main()
