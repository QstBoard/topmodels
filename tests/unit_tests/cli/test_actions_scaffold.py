"""Unit tests for the scaffold CLI actions in topmodels.

This module tests the CLI parser, template rendering, error handling, and argument parsing
for the project scaffolding functionality.
"""

from pathlib import Path

import pytest
from pytest import MonkeyPatch

import topmodels.cli.actions.scaffold as scaffold_mod
from topmodels.cli.actions.scaffold import Scaffold


@pytest.fixture()
def fake_scaffold(tmp_path: Path, monkeypatch: MonkeyPatch) -> Scaffold:
    """Fixture to create a fake template directory for testing."""
    fake_mod = tmp_path / 'level1' / 'level2' / 'level3' / 'scaffold.py'
    fake_mod.parent.mkdir(parents=True, exist_ok=True)

    tpl_dir = tmp_path / 'level1' / 'conf' / 'project_templates' / 'root_ml_project'
    tpl_dir.mkdir(parents=True, exist_ok=True)
    t = tpl_dir / 'README.md-jy2'

    t.write_text('{{ project_name }} {{ project_version }}', encoding="utf-8")
    monkeypatch.setattr(scaffold_mod, '__file__', str(fake_mod))
    return Scaffold(name="dummyML", version="0.1.0", output=tmp_path)


class TestScaffold:
    """Test suite for the scaffold CLI actions."""

    def test_scaffold_creates_dummy_template(
        self,
        tmp_path: Path,
        fake_scaffold: Scaffold
    ) -> None:
        """Test that scaffold creates a dummy template in the output directory."""
        fake_scaffold()
        project_dir = tmp_path / "dummyML"
        assert project_dir.exists()

    def test_scaffold_create_expected_directories(self, tmp_path: Path) -> None:
        """Test that scaffold creates the expected directory in the output directory."""
        scaffold = Scaffold(name='test_project', version='0.1.0', output=tmp_path)
        scaffold()
        project_dir = tmp_path / 'test_project'
        assert project_dir.exists()
        assert (project_dir / 'app').exists()
        assert (project_dir / 'core').exists()

    def test_scaffold_create_expected_files(self, tmp_path: Path) -> None:
        """Test that scaffold creates the expected files in the output directory."""
        scaffold = Scaffold(name='test_project', version='0.1.0', output=tmp_path)
        scaffold()
        test_project_dir = tmp_path / 'test_project'
        assert (test_project_dir / 'README.md').exists()
        assert (test_project_dir / 'requirements.txt').exists()
        assert (test_project_dir / '__main__.py').exists()
        assert (test_project_dir / '.gitignore').exists()

    def test_scaffold_mandatory_attributes(self, tmp_path: Path) -> None:
        """Test that scaffold creates the project in the current working directory if no output is specified."""
        pass
