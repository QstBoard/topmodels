"""
Unit tests for the topmodels CLI main entry point.
"""
from pathlib import Path
from unittest import mock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from topmodels.__main__ import app

runner = CliRunner()

class TestMainCLI:
    """Test suite for the main CLI entry point."""

    def test_cli_create_default(self, tmp_path: Path) -> None:
        """Test that the CLI creates a project"""
        result = runner.invoke(
            app, [
                'scaffold', 'create',
                '--name', 'test_project', 
                '--version', '0.1.0', 
                '--output', str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        project_dir = tmp_path / 'test_project'
        assert project_dir.exists()

    def test_cli_create_no_default(self, tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
        """Test that the CLI creates a project with default output as the cwd."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(
            app, [
                'scaffold', 'create',
                '--name', 'test_project', 
                '--version', '0.1.0', 
            ]
        )
        assert result.exit_code == 0
        project_dir = tmp_path / 'test_project'
        assert project_dir.exists()
