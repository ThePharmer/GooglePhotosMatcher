---
id: 009
priority: p2
status: pending
category: maintainability
created: 2025-11-22
effort: large
agents: architecture-strategist, code-simplicity-reviewer, kieran-python-reviewer
---

# Refactor searchMedia() to Reduce Cyclomatic Complexity

## Problem Statement

The `searchMedia()` function has 8 levels of nested if-else blocks (42 lines), making it nearly impossible to understand, test, or maintain.

```python
if not os.path.exists(filepath):
    if not os.path.exists(filepath):
        if not os.path.exists(filepath):
            if not os.path.exists(filepath):
                # 8 LEVELS DEEP!
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (lines 10-51)

## Proposed Solution

Flatten using a list of candidate paths:

```python
def searchMedia(path: str, title: str, media_moved: set,
                non_edited: str, edited_word: str) -> Optional[str]:
    title = fixTitle(title)
    base, ext = os.path.splitext(title)

    # Define search patterns in priority order
    candidates = [
        f"{base}-{edited_word}{ext}",      # Edited version
        f"{base}(1){ext}",                  # Duplicate naming
        title,                              # Original name
        f"{base[:47]}-{edited_word}{ext}", # Truncated + edited
        f"{base[:47]}(1){ext}",            # Truncated + duplicate
        f"{base[:47]}{ext}",               # Truncated
    ]

    for candidate in candidates:
        filepath = os.path.join(path, candidate)
        if os.path.exists(filepath) and candidate not in media_moved:
            return candidate

    return checkIfSameName(title, media_moved)
```

## Impact

- Cyclomatic complexity: ~15 → ~5
- Unmaintainable code pattern
- Cannot add new filename patterns easily
- Impossible to unit test

## Acceptance Criteria

- [ ] Maximum 2-3 levels of nesting
- [ ] Clear list of filename patterns to try
- [ ] Each pattern documented
- [ ] Unit tests for each pattern variation
- [ ] Estimated LOC reduction: ~25 lines
