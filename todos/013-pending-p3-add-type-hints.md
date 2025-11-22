---
id: 013
priority: p3
status: completed
category: code-quality
created: 2025-11-22
effort: medium
agents: kieran-python-reviewer
---

# Add Type Hints to All Functions

## Problem Statement

No function in the codebase has type annotations, making it harder to understand function contracts and preventing static analysis.

## Affected Files

- `/home/user/GooglePhotosMatcher/files/main.py`
- `/home/user/GooglePhotosMatcher/files/window.py`
- `/home/user/GooglePhotosMatcher/files/auxFunctions.py`

## Proposed Solution

Example for key functions:

```python
from typing import Optional
import PySimpleGUI as sg

def mainProcess(
    browser_path: str,
    window: sg.Window,
    edited_word: str
) -> None:

def searchMedia(
    path: str,
    title: str,
    media_moved: set[str],
    non_edited_path: str,
    edited_word: str
) -> Optional[str]:

def set_EXIF(
    filepath: str,
    lat: float,
    lng: float,
    altitude: float,
    timestamp: int
) -> None:
```

## Impact

- No static type checking with mypy
- Limited IDE assistance
- Implicit documentation

## Acceptance Criteria

- [ ] All public functions have type annotations
- [ ] `py.typed` marker file added
- [ ] mypy passes with strict mode
