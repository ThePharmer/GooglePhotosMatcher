---
id: 006
priority: p2
status: pending
category: bug
created: 2025-11-22
effort: small
agents: code-simplicity-reviewer
---

# Fix Hardcoded "editado" Ignoring User Parameter

## Problem Statement

Line 25 in `auxFunctions.py` hardcodes `"-editado."` even though the `editedWord` parameter should be used. This causes the user's custom suffix to be ignored in certain code paths.

```python
# auxFunctions.py:25
realTitle = str(title.rsplit('.', 1)[0] + "-editado." + title.rsplit('.', 1)[1])  # HARDCODED!
```

## Affected Files

- `/home/user/GooglePhotosMatcher/files/auxFunctions.py` (line 25)

## Proposed Solution

```python
realTitle = f"{title.rsplit('.', 1)[0]}-{editedWord}.{title.rsplit('.', 1)[1]}"
```

## Impact

- User's custom edited suffix is ignored for truncated filenames
- Internationalization broken for certain file patterns
- Inconsistent behavior

## Acceptance Criteria

- [ ] All occurrences use the `editedWord` parameter
- [ ] No hardcoded language-specific strings
- [ ] Custom suffix works for all code paths
