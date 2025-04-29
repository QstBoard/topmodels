"""
Unit tests for the topmodels CLI main entry point.

This module tests various behaviors of the CLI, including argument parsing,
error handling, and dynamic action module loading.
"""

import pytest
import sys
from unittest import mock
from topmodels.cli import main

class TestMainCLI:
    """
    Test suite for the main CLI function in topmodels.

    Covers argument validation, error propagation, and correct module invocation.
    """

    def test_main__raises_value_error_when_no_action(self, monkeypatch):
        """
        Test that ValueError is raised when no action is provided in sys.argv.
        """
        monkeypatch.setattr(sys, "argv", '')
        with pytest.raises(ValueError, match="Invalid action 'None'.*"):
            main()

    def test_main__raises_value_error_when_invalid_action(self, monkeypatch):
        """
        Test that ValueError is raised when an invalid action is provided.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "invalid_action"])
        with pytest.raises(ValueError, match="Invalid action 'invalid_action'.*"):
            main()

    def test__main_raises_import_error_when_module_not_found(self, monkeypatch):
        """
        Test that ImportError is raised when the action module cannot be imported.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "scaffold"])
        with mock.patch("importlib.import_module", side_effect=ImportError("No module")):
            with pytest.raises(ImportError, match="Failed to import action module.*"):
                main()

    def test__main_calls_run_with_args(self, monkeypatch):
        """
        Test that the action module's run() is called with the correct arguments.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "scaffold", "foo", "bar"])
        mock_module = mock.Mock()
        with mock.patch("importlib.import_module", return_value=mock_module) as import_mod:
            main()
            import_mod.assert_called_once_with("topmodels.cli.actions.scaffold")
            mock_module.run.assert_called_once_with(["foo", "bar"])

    def test__main_passes_empty_args_to_run(self, monkeypatch):
        """
        Test that run() is called with an empty list when no extra arguments are provided.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "scaffold"])
        mock_module = mock.Mock()
        with mock.patch("importlib.import_module", return_value=mock_module):
            main()
            mock_module.run.assert_called_once_with([])

    def test__main_import_module_called_with_correct_name(self, monkeypatch):
        """
        Test that import_module is called with the correct action module name.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "scaffold"])
        mock_module = mock.Mock()
        with mock.patch("importlib.import_module", return_value=mock_module) as import_mod:
            main()
            import_mod.assert_called_once_with("topmodels.cli.actions.scaffold")

    def test__main_run_raises_exception_propagates(self, monkeypatch):
        """
        Test that exceptions raised by run() are propagated.
        """
        monkeypatch.setattr(sys, "argv", ["topmodels", "scaffold"])
        mock_module = mock.Mock()
        mock_module.run.side_effect = RuntimeError("run failed")
        with mock.patch("importlib.import_module", return_value=mock_module):
            with pytest.raises(RuntimeError, match="run failed"):
                main()
