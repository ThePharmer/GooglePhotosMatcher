#!/usr/bin/env python3
"""Command-line interface for Google Photos Matcher."""
from __future__ import annotations

import argparse
import sys
import os
from typing import Optional, Any

try:
    from logger import setup_logging
except ImportError:
    from .logger import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="google-photos-matcher",
        description="Match Google Photos metadata with media files from Google Takeout"
    )
    parser.add_argument(
        "path",
        help="Path to Google Takeout folder"
    )
    parser.add_argument(
        "-e", "--edited-suffix",
        default="editado",
        help="Suffix for edited photos (default: editado)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Write logs to file"
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=0,
        help="Number of parallel workers (default: auto-detect, use 1 for sequential)"
    )
    return parser


class CLIWindow:
    """Mock window for CLI progress display.

    Implements the same interface as PySimpleGUI window for progress updates,
    allowing mainProcess to work in CLI mode without GUI dependency.
    """

    def __init__(self, quiet: bool = False) -> None:
        self._progress: float = 0
        self._quiet = quiet

    def __getitem__(self, key: str) -> "CLIWindow":
        """Allow subscript access like window['-PROGRESS_BAR-']."""
        return self

    def update(
        self,
        value: Any = None,
        visible: Optional[bool] = None,
        text_color: Optional[str] = None
    ) -> None:
        """Handle progress updates from mainProcess.

        Args:
            value: Progress value (int/float for percentage, str for message)
            visible: Ignored in CLI mode
            text_color: Ignored in CLI mode
        """
        if self._quiet:
            return

        if isinstance(value, (int, float)):
            self._progress = value
            print(f"\rProgress: {value:.1f}%", end="", flush=True)
        elif isinstance(value, str):
            if "finished" in value.lower():
                print(f"\n{value}")
            elif "%" in str(value):
                print(f"\rProgress: {value}", end="", flush=True)
            elif value:  # Other messages (like errors)
                print(f"\n{value}")


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code: 0 for success, 1 for error, 2 for invalid args, 130 for interrupt
    """
    parser = create_parser()
    args = parser.parse_args()

    # Determine log level
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose >= 2:
        log_level = "DEBUG"
    elif args.verbose == 1:
        log_level = "INFO"
    else:
        log_level = "WARNING"

    logger = setup_logging(level=log_level, log_file=args.log_file)

    # Validate path
    if not os.path.isdir(args.path):
        logger.error(f"Invalid path: {args.path}")
        return 2

    # Import here to avoid circular imports and GUI dependency
    # main.py now uses TYPE_CHECKING for PySimpleGUI, so no GUI dependency at runtime
    try:
        from main import mainProcess
    except ImportError:
        from .main import mainProcess

    window = CLIWindow(quiet=args.quiet)

    try:
        result = mainProcess(args.path, window, args.edited_suffix, dry_run=args.dry_run, max_workers=args.workers)

        # Check for errors in result
        if result.get("error"):
            logger.error(f"Process error: {result['error']}")
            return 1

        # Return 1 if there were any errors during processing
        if result.get("error_count", 0) > 0 and result.get("success_count", 0) == 0:
            return 1

        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
