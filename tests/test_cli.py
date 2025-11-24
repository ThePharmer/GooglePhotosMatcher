"""Tests for CLI module."""
from __future__ import annotations

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from typing import Any

# Add files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'files'))

from cli import create_parser, CLIWindow, main


class TestCreateParser:
    """Tests for argument parser creation."""

    def test_creates_parser(self) -> None:
        """Parser should be created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "google-photos-matcher"

    def test_path_is_required(self) -> None:
        """Path argument should be required."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parses_path(self) -> None:
        """Parser should accept path argument."""
        parser = create_parser()
        args = parser.parse_args(["/some/path"])
        assert args.path == "/some/path"

    def test_default_edited_suffix(self) -> None:
        """Default edited suffix should be 'editado'."""
        parser = create_parser()
        args = parser.parse_args(["/path"])
        assert args.edited_suffix == "editado"

    def test_custom_edited_suffix(self) -> None:
        """Parser should accept custom edited suffix."""
        parser = create_parser()
        args = parser.parse_args(["/path", "-e", "edited"])
        assert args.edited_suffix == "edited"

    def test_verbose_flag(self) -> None:
        """Parser should accept verbose flags."""
        parser = create_parser()

        args = parser.parse_args(["/path"])
        assert args.verbose == 0

        args = parser.parse_args(["/path", "-v"])
        assert args.verbose == 1

        args = parser.parse_args(["/path", "-vv"])
        assert args.verbose == 2

    def test_quiet_flag(self) -> None:
        """Parser should accept quiet flag."""
        parser = create_parser()
        args = parser.parse_args(["/path", "-q"])
        assert args.quiet is True

    def test_log_file_option(self) -> None:
        """Parser should accept log file option."""
        parser = create_parser()
        args = parser.parse_args(["/path", "--log-file", "output.log"])
        assert args.log_file == "output.log"

    def test_dry_run_flag(self) -> None:
        """Parser should accept dry-run flag."""
        parser = create_parser()
        args = parser.parse_args(["/path", "-n"])
        assert args.dry_run is True

        args = parser.parse_args(["/path", "--dry-run"])
        assert args.dry_run is True


class TestCLIWindow:
    """Tests for CLIWindow mock window."""

    def test_getitem_returns_self(self) -> None:
        """Subscript access should return self for chaining."""
        window = CLIWindow()
        assert window['-PROGRESS_BAR-'] is window
        assert window['-PROGRESS_LABEL-'] is window

    def test_update_with_percentage(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Update with float should print progress."""
        window = CLIWindow()
        window.update(50.5)
        captured = capsys.readouterr()
        assert "50.5%" in captured.out

    def test_update_with_finish_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Update with 'finished' message should print on new line."""
        window = CLIWindow()
        window.update("Matching process finished with 5 successes")
        captured = capsys.readouterr()
        assert "finished" in captured.out
        assert captured.out.startswith("\n")

    def test_quiet_mode_suppresses_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Quiet mode should suppress all output."""
        window = CLIWindow(quiet=True)
        window.update(50.0)
        window.update("Some message")
        captured = capsys.readouterr()
        assert captured.out == ""


class TestMain:
    """Tests for main entry point."""

    def test_invalid_path_returns_2(self) -> None:
        """Invalid path should return exit code 2."""
        with patch('sys.argv', ['cli.py', '/nonexistent/path']):
            exit_code = main()
            assert exit_code == 2

    def test_valid_path_calls_main_process(self, tmp_path: Any) -> None:
        """Valid path should call mainProcess."""
        with patch('sys.argv', ['cli.py', str(tmp_path)]):
            with patch('main.mainProcess') as mock_process:
                mock_process.return_value = {
                    'success_count': 5,
                    'error_count': 0,
                    'dry_run': False
                }
                exit_code = main()
                assert exit_code == 0
                mock_process.assert_called_once()

    def test_all_errors_returns_1(self, tmp_path: Any) -> None:
        """All errors and no successes should return exit code 1."""
        with patch('sys.argv', ['cli.py', str(tmp_path)]):
            with patch('main.mainProcess') as mock_process:
                mock_process.return_value = {
                    'success_count': 0,
                    'error_count': 5,
                    'dry_run': False
                }
                exit_code = main()
                assert exit_code == 1

    def test_dry_run_passed_to_main_process(self, tmp_path: Any) -> None:
        """Dry-run flag should be passed to mainProcess."""
        with patch('sys.argv', ['cli.py', str(tmp_path), '-n']):
            with patch('main.mainProcess') as mock_process:
                mock_process.return_value = {
                    'success_count': 3,
                    'error_count': 0,
                    'dry_run': True
                }
                main()
                # Check dry_run=True was passed
                call_args = mock_process.call_args
                assert call_args.kwargs.get('dry_run') is True
