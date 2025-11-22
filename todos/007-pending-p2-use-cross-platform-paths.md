---
id: 007
priority: p2
status: pending
category: architecture
created: 2025-11-22
effort: medium
agents: architecture-strategist, kieran-python-reviewer
---

# Replace Windows-Only Path Separators with os.path.join()

## Problem Statement

Hardcoded Windows backslash path separators throughout the codebase prevent cross-platform usage:

```python
fixedMediaPath = path + "\MatchedMedia"  # main.py:11
filepath = path + "\\" + title           # main.py:47
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py` (lines 11-12, 47, 84-85)
- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (lines 13, 16, 19, 22, 26, 29, 32, 35, 39-49)

## Proposed Solution

Use `pathlib.Path` or `os.path.join()`:

```python
from pathlib import Path

fixed_media_path = Path(path) / "MatchedMedia"
filepath = Path(path) / title
```

## Impact

- Application broken on macOS and Linux
- Cannot run in Docker containers
- Limits user base to Windows only

## Acceptance Criteria

- [ ] All path operations use `os.path.join()` or `pathlib.Path`
- [ ] No hardcoded backslash separators
- [ ] Works on Windows, macOS, and Linux
