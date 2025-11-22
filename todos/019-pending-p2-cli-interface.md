---
id: 019
priority: p2
status: pending
category: feature
created: 2025-11-22
effort: medium
agents: architecture-strategist, kieran-python-reviewer
---

# Add Command-Line Interface

## Problem Statement

The application requires a GUI to run, making it unsuitable for:
- Server/headless environments
- Batch processing scripts
- CI/CD pipelines
- SSH sessions

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (refactor mainProcess)
- New file: `/home/user/GooglePhotosMatcher/files/cli.py`

## Proposed Solution

1. Create CLI entry point using argparse:

```python
# files/cli.py
import argparse
import sys
from main import mainProcess

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="google-photos-matcher",
        description="Match Google Photos metadata with media files"
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
        "-n", "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v, -vv, -vvv)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )
    return parser

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    # ... process with headless progress reporting
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

2. Add entry point to pyproject.toml:

```toml
[project.scripts]
google-photos-matcher = "files.cli:main"
```

3. Refactor mainProcess to support headless mode (pass None for window)

## Impact

- Cannot automate processing
- Requires desktop environment
- No scriptability

## Acceptance Criteria

- [ ] `python -m files.cli /path/to/takeout` works
- [ ] All GUI features available via flags
- [ ] Progress shown in terminal (percentage, ETA)
- [ ] Exit codes: 0=success, 1=partial failure, 2=error
- [ ] Works without PySimpleGUI installed (optional dep)
