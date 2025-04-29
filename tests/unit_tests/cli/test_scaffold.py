"""Unit tests for the scaffold CLI actions in topmodels.

This module tests the CLI parser, template rendering, error handling, and argument parsing
for the project scaffolding functionality.
"""

from pathlib import Path
from unittest import mock

import pytest
from pytest import MonkeyPatch

from topmodels.cli.actions import scaffold as scaffold_mod

class TestScaffold:
    """Test suite for the scaffold CLI actions."""

    def test__build_parser_returns_default_parser_value(self) -> None:
        """Test that the parser returns the correct default values."""
        parser = scaffold_mod.build_parser()
        args = parser.parse_args([])
        assert parser.prog == "scaffold"
        assert parser.description == "Scaffold a new ML project"
        assert args.name == "sandboxML"
        assert args.version == "0.1.0"
        assert args.output == "."

    def test__scaffold_raises_if_template_dir_missing(
        self,
        tmp_path: Path,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that scaffold raises FileNotFoundError if the template directory is missing."""
        missing_template_dir = tmp_path / "does_not_exist"
        fake_path = mock.MagicMock(spec=Path)
        fake_path.parent.parent.parent = missing_template_dir

        monkeypatch.setattr(scaffold_mod, "Path", mock.MagicMock(return_value=fake_path))

        assert not missing_template_dir.exists()
        with pytest.raises(FileNotFoundError):
            scaffold_mod.scaffold(str(tmp_path), "foo", "0.1.0")

    def test__scaffold_renders_templates(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that scaffold renders templates and writes the correct output files."""
        template_dir = tmp_path / "conf" / "project_templates" / "root_ml_project"
        template_dir.mkdir(parents=True)

        template_file = template_dir / "README.md-jy2"
        template_file.write_text("{{ project_name }} {{ project_version }}", encoding="utf-8")

        scaffold_mod.scaffold(str(tmp_path), "foo", "1.2.3")
        output_file = tmp_path / "foo" / "README.md"
        assert output_file.exists()
        assert "foo" in output_file.read_text(encoding="utf-8")
        assert "1.2.3" in output_file.read_text(encoding="utf-8")

    def test__run_calls_scaffold_with_parsed_args(self, monkeypatch):
        """Test that run() calls scaffold() with parsed arguments."""
        mock_scaffold = mock.Mock()
        monkeypatch.setattr(scaffold_mod, "scaffold", mock_scaffold)
        args = ["-n", "abc", "-v", "1.0.0", "-o", "/tmp"]
        scaffold_mod.run(args)
        mock_scaffold.assert_called_once_with(
            location="/tmp", 
            name="abc", 
            version="1.0.0"
        )

    def test__run_defaults(self, monkeypatch):
        """Test that run() uses default arguments when none are provided."""
        mock_scaffold = mock.Mock()
        monkeypatch.setattr(scaffold_mod, "scaffold", mock_scaffold)
        scaffold_mod.run([])
        mock_scaffold.assert_called_once_with(
            location=".", 
            name="sandboxML", 
            version="0.1.0"
        )