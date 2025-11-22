---
id: 017
priority: p1
status: pending
category: infrastructure
created: 2025-11-22
effort: small
agents: architecture-strategist, kieran-python-reviewer
---

# Replace print() with Proper Logging

## Problem Statement

The codebase uses `print()` statements for debugging and error reporting. This makes it difficult to:
- Control verbosity levels
- Save logs to files
- Debug issues in production

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (multiple print statements)
- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (line 201)

## Proposed Solution

1. Create a logging configuration module:

```python
# files/logger.py
import logging
import sys

def setup_logging(level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger("GooglePhotosMatcher")
    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

2. Replace print statements:

```python
# Before
print(titleOriginal + " not found")

# After
logger.warning(f"Media not found: {titleOriginal}")
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed processing info |
| INFO | Progress updates, success messages |
| WARNING | Missing files, skipped items |
| ERROR | Processing failures, exceptions |

## Impact

- Difficult to diagnose issues
- No persistent log history
- Cannot adjust verbosity

## Acceptance Criteria

- [ ] All print() replaced with appropriate log levels
- [ ] Log file output option added
- [ ] Log level configurable (DEBUG/INFO/WARNING/ERROR)
- [ ] Timestamps included in log output
